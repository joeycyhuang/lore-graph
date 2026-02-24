"""Character and relationship extraction from PDF files using LangExtract."""

import json
import logging
import os
import sys
import textwrap

import pymupdf
import langextract as lx
from langextract import providers
from langextract.core import format_handler as fh
from langextract.data import FormatType
from langextract.factory import ModelConfig

# Suppress noisy tracebacks from expected parse failures on non-JSON model responses
logging.getLogger("langextract.resolver").setLevel(logging.CRITICAL)
logging.getLogger("absl").setLevel(logging.CRITICAL)

# Lenient format handler for non-Gemini models that may return extractions
# as a bare list instead of wrapped in {"extractions": [...]}
_LENIENT_HANDLER = fh.FormatHandler(
    format_type=FormatType.JSON,
    use_wrapper=False,
    wrapper_key=None,
    use_fences=True,
    strict_fences=False,
)


def extract_text_from_pdf(pdf_path: str) -> str:
    """Extract all text from a PDF file."""
    try:
        doc = pymupdf.open(pdf_path)
    except FileNotFoundError:
        print(f"Error: File not found: {pdf_path}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: Could not read PDF: {e}", file=sys.stderr)
        sys.exit(1)

    text = ""
    for page in doc:
        page_text = page.get_text()
        if page_text.strip():
            text += page_text
    doc.close()
    return text


CHARACTER_PROMPT = textwrap.dedent("""\
    Extract named characters from this Warhammer 40,000 novel text.
    Use the exact name text as it first appears. List characters in order of appearance.
    Do NOT extract planets, locations, ships, weapons, or unnamed groups.
    For example, Terra, Cadia, Macragge, Ullanor are planets/places, not characters.
    Use canonical faction names consistently (e.g. "Luna Wolves" not "the Wolves",
    "Ultramarines" not "the XIII Legion").
    Return ONLY a valid JSON object. All values must be strings, numbers, or booleans. Never return null.
""")

CHARACTER_EXAMPLES = [
    lx.data.ExampleData(
        text=(
            "The fleet broke from the warp above Ullanor. Garviel Loken stood "
            "at the embarkation deck as Captain of the Luna Wolves Tenth Company. "
            "Beside him, First Captain Ezekyle Abaddon growled his impatience. "
            "Far below, the greenskin hordes of Urlakk Urg waited."
        ),
        extractions=[
            lx.data.Extraction(
                extraction_class="character",
                extraction_text="Garviel Loken",
                attributes={
                    "faction": "Luna Wolves",
                    "role": "Captain, Tenth Company",
                    "description": "A thoughtful Space Marine captain",
                },
            ),
            lx.data.Extraction(
                extraction_class="character",
                extraction_text="Ezekyle Abaddon",
                attributes={
                    "faction": "Luna Wolves",
                    "role": "First Captain",
                    "description": "An aggressive and ambitious warrior",
                },
            ),
            lx.data.Extraction(
                extraction_class="character",
                extraction_text="Urlakk Urg",
                attributes={
                    "faction": "Orks",
                    "role": "Warlord",
                    "description": "Greenskin warlord on Ullanor",
                },
            ),
        ],
    )
]

RELATIONSHIP_PROMPT = textwrap.dedent("""\
    Extract significant relationships between named characters in this
    Warhammer 40,000 novel text. Use exact character names for source and target.
    Only include relationships between named individuals, not places or groups.
    Do not extract duplicate relationships. If two characters have one relationship,
    extract it once with the most specific type.
    Return ONLY a valid JSON object. All values must be strings, numbers, or booleans. Never return null.
""")

RELATIONSHIP_EXAMPLES = [
    lx.data.ExampleData(
        text=(
            "Loken served under Abaddon in the speartip assaults, though they "
            "often clashed on matters of honour. The Warmaster Horus valued "
            "Loken's counsel, seeing in him a voice of reason among the Mournival."
        ),
        extractions=[
            lx.data.Extraction(
                extraction_class="relationship",
                extraction_text="Loken served under Abaddon",
                attributes={
                    "source_character": "Loken",
                    "target_character": "Abaddon",
                    "type": "subordinate",
                    "description": "Serves under Abaddon but they clash on matters of honour",
                },
            ),
            lx.data.Extraction(
                extraction_class="relationship",
                extraction_text="Horus valued Loken's counsel",
                attributes={
                    "source_character": "Horus",
                    "target_character": "Loken",
                    "type": "mentorship",
                    "description": "Horus values Loken as a voice of reason in the Mournival",
                },
            ),
        ],
    )
]

MAX_CHAR_BUFFER = 10000
MAX_RETRIES = 2
CONTEXT_SIZE = 36768

def build_provider_config(provider: str, model_id: str, provider_url: str | None = None) -> dict:
    """Build kwargs for lx.extract() based on the selected provider."""
    base = {
        "model_id": model_id,
        "fence_output": True,
        "use_schema_constraints": False,
        "resolver_params": {
            "suppress_parse_errors": True,
            "enable_fuzzy_alignment": False,
        },
    }

    match provider:
        case "ollama":
            base["model_url"] = "http://localhost:11434"
            base["language_model_params"] = {"timeout": 600, "num_ctx": CONTEXT_SIZE}
        case "ollama-cloud":
            base["model_url"] = provider_url or os.getenv("OLLAMA_CLOUD_URL", "http://localhost:11434")
            lm_params = {"timeout": 600, "num_ctx": CONTEXT_SIZE}
            api_key = os.getenv("OLLAMA_API_KEY")
            if api_key:
                lm_params["api_key"] = api_key
            base["language_model_params"] = lm_params
        case "gemini":
            base["api_key"] = os.getenv("GEMINI_API_KEY")
            base["language_model_params"] = {"timeout": 600}

    return base

def _chunk_text(text: str, chunk_size: int = MAX_CHAR_BUFFER) -> list[str]:
    """Split text into chunks, breaking at whitespace boundaries."""
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        if end < len(text):
            break_at = text.rfind(" ", start, end)
            if break_at > start:
                end = break_at
        chunks.append(text[start:end])
        start = end
    return chunks

def _extract_chunk(chunk, prompt, examples, config, debug=False):
    """Extract from a single chunk with retries, trimming on context overflow."""
    for attempt in range(MAX_RETRIES + 1):
        try:
            result = lx.extract(
                text_or_documents=chunk,
                prompt_description=prompt,
                examples=examples,
                extraction_passes=1,
                max_char_buffer=len(chunk) + 1,
                max_workers=2,
                batch_length=2,
                **config,
            )
            if debug and result.extractions:
                print(f"    [debug] Got {len(result.extractions)} extractions, classes: {set(e.extraction_class for e in result.extractions)}")
            elif debug:
                print(f"    [debug] Got 0 extractions from result")
            return result
        except Exception as e:
            if debug:
                print(f"    [debug] Attempt {attempt+1} failed: {e}")
            if "exceeded max context length" in str(e) or "prompt too long" in str(e):
                # Trim 10% of the chunk to fit within context window
                trim = max(100, len(chunk) // 10)
                chunk = chunk[:-trim].rstrip()
                if debug:
                    print(f"    [debug] Trimmed chunk to {len(chunk)} chars")
            if attempt == MAX_RETRIES:
                return None
    return None

def extract_characters(text: str, config: dict) -> tuple[list[dict], list]:
    """Extract characters from text using LangExtract.

    Returns a tuple of (characters, annotated_documents).
    """
    chunks = _chunk_text(text)
    characters = []
    annotated_docs = []
    skipped = 0

    for i, chunk in enumerate(chunks):
        result = _extract_chunk(chunk, CHARACTER_PROMPT, CHARACTER_EXAMPLES, config, debug=True)
        if result is None:
            skipped += 1
        else:
            annotated_docs.append(result)
            for extraction in result.extractions:
                if extraction.extraction_class == "character" and extraction.extraction_text.strip():
                    attrs = extraction.attributes or {}
                    characters.append({
                        "name": extraction.extraction_text.strip(),
                        "faction": attrs.get("faction", "Unknown") or "Unknown",
                        "role": attrs.get("role", "Unknown") or "Unknown",
                        "description": attrs.get("description", "") or "",
                    })
        print(f"  Chunk {i+1}/{len(chunks)}: {len(characters)} characters ({skipped} skipped)")

    if not characters:
        print("Warning: No characters found in text.", file=sys.stderr)
    return characters, annotated_docs

def extract_relationships(text: str, config: dict) -> tuple[list[dict], list]:
    """Extract relationships between characters from text using LangExtract.

    Returns a tuple of (relationships, annotated_documents).
    """
    chunks = _chunk_text(text)
    relationships = []
    annotated_docs = []
    skipped = 0

    for i, chunk in enumerate(chunks):
        result = _extract_chunk(chunk, RELATIONSHIP_PROMPT, RELATIONSHIP_EXAMPLES, config, debug=True)
        if result is None:
            skipped += 1
        else:
            annotated_docs.append(result)
            for extraction in result.extractions:
                if extraction.extraction_class == "relationship":
                    attrs = extraction.attributes or {}
                    source = (attrs.get("source_character") or "").strip()
                    target = (attrs.get("target_character") or "").strip()
                    if source and target:
                        relationships.append({
                            "source_character": source,
                            "target_character": target,
                            "type": attrs.get("type", "unknown") or "unknown",
                            "description": attrs.get("description", "") or "",
                        })
        print(f"  Chunk {i+1}/{len(chunks)}: {len(relationships)} relationships ({skipped} skipped)")

    return relationships, annotated_docs

def deduplicate_characters(characters: list[dict]) -> list[dict]:
    """Merge characters that refer to the same person under different name variants.

    Groups characters by matching on surname/last-name overlap, then picks
    the longest (most complete) name as canonical.
    """
    groups: dict[str, list[dict]] = {}

    for char in characters:
        name = char["name"]
        name_parts = name.lower().split()

        merged = False
        for key in list(groups.keys()):
            key_parts = key.lower().split()
            # Match if one name is a subset of the other's parts
            if set(name_parts) & set(key_parts):
                groups[key].append(char)
                merged = True
                break

        if not merged:
            groups[name] = [char]

    deduped = []
    for key, group in groups.items():
        # Use the longest name as canonical
        canonical = max(group, key=lambda c: len(c["name"]))
        # Merge descriptions from all variants
        descriptions = [c["description"] for c in group if c["description"]]
        canonical["description"] = descriptions[0] if descriptions else ""
        # Use most specific faction/role (longest non-Unknown)
        factions = [c["faction"] for c in group if c["faction"] and c["faction"] != "Unknown"]
        if factions:
            canonical["faction"] = max(factions, key=len)
        roles = [c["role"] for c in group if c["role"] and c["role"] != "Unknown"]
        if roles:
            canonical["role"] = max(roles, key=len)
        deduped.append(canonical)

    return deduped

def build_graph_data(characters: list[dict], relationships: list[dict]) -> dict:
    """Assemble characters and relationships into D3-compatible graph JSON."""
    # Build nodes with stable IDs
    nodes = []
    name_to_id: dict[str, str] = {}

    for char in characters:
        node_id = char["name"].lower().replace(" ", "-")
        name_to_id[char["name"]] = node_id
        # Also map partial names to this ID
        for part in char["name"].split():
            if len(part) > 2:  # skip very short parts like "of", "the"
                name_to_id.setdefault(part, node_id)
        nodes.append({
            "id": node_id,
            "name": char["name"],
            "faction": char["faction"],
            "role": char["role"],
            "description": char["description"],
        })

    node_ids = {n["id"] for n in nodes}

    # Build edges, resolving character names to node IDs
    edges = []
    for rel in relationships:
        source_id = _resolve_name(rel["source_character"], name_to_id)
        target_id = _resolve_name(rel["target_character"], name_to_id)
        if source_id in node_ids and target_id in node_ids and source_id != target_id:
            edges.append({
                "source": source_id,
                "target": target_id,
                "type": rel["type"],
                "description": rel["description"],
            })

    return {"nodes": nodes, "edges": edges}


def _resolve_name(name: str, name_to_id: dict[str, str]) -> str:
    """Resolve a character name to its node ID using exact or partial matching."""
    if name in name_to_id:
        return name_to_id[name]
    # Try matching individual parts
    for part in name.split():
        if part in name_to_id:
            return name_to_id[part]
    # Fallback: generate an ID
    return name.lower().replace(" ", "-")


def write_graph_json(data: dict, output_path: str) -> None:
    """Write graph data to a JSON file."""
    with open(output_path, "w") as f:
        json.dump(data, f, indent=2)
    print(f"Wrote {len(data['nodes'])} characters and {len(data['edges'])} relationships to {output_path}")


def save_visualization(annotated_docs: list, output_dir: str = "data") -> None:
    """Save annotated documents as JSONL and generate an HTML visualization."""
    jsonl_name = "extraction_results.jsonl"
    viz_path = os.path.join(output_dir, "visualization.html")

    lx.io.save_annotated_documents(
        annotated_docs,
        output_name=jsonl_name,
        output_dir=output_dir,
    )

    jsonl_path = os.path.join(output_dir, jsonl_name)
    html_content = lx.visualize(jsonl_path)
    if hasattr(html_content, "data"):
        html_content = html_content.data
    with open(viz_path, "w") as f:
        f.write(html_content)
    print(f"Wrote visualization to {viz_path}")
