"""Character and relationship extraction from PDF files using LangExtract."""

import json
import logging
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
    Extract all named characters from this Warhammer 40,000 novel text.
    For each character, identify them by the exact text of their name as it
    first appears. Provide attributes for faction, role, and a brief description.
    Only extract characters who are named individuals, not unnamed soldiers or
    generic groups. List characters in order of appearance.
    Return ONLY a valid JSON object. All values must be strings, numbers, or booleans. Never return null.
""")

CHARACTER_EXAMPLES = [
    lx.data.ExampleData(
        text=(
            "Garviel Loken stood at the embarkation deck, watching the stars. "
            "As Captain of the Tenth Company, he commanded respect among the "
            "Luna Wolves. Beside him, First Captain Ezekyle Abaddon growled "
            "his impatience."
        ),
        extractions=[
            lx.data.Extraction(
                extraction_class="character",
                extraction_text="Garviel Loken",
                attributes={
                    "faction": "Luna Wolves",
                    "role": "Captain, Tenth Company",
                    "description": "A thoughtful and principled Space Marine captain",
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
        ],
    )
]

RELATIONSHIP_PROMPT = textwrap.dedent("""\
    Extract all significant relationships between named characters in this
    Warhammer 40,000 novel text. For each relationship, use the exact names
    of the two characters involved. Categorize the relationship type (e.g.,
    command, brotherhood, rivalry, mentorship, alliance, betrayal, friendship,
    enmity, subordinate). Provide a brief description of the relationship.
    List relationships in order of appearance. Only include relationships
    between named individuals.
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
                    "description": "Loken serves under Abaddon in speartip assaults, though they often clash on matters of honour",
                },
            ),
            lx.data.Extraction(
                extraction_class="relationship",
                extraction_text="Horus valued Loken's counsel",
                attributes={
                    "source_character": "Horus",
                    "target_character": "Loken",
                    "type": "mentorship",
                    "description": "Horus values Loken as a voice of reason among the Mournival",
                },
            ),
        ],
    )
]

MAX_CHAR_BUFFER = 50000
MAX_RETRIES = 2
CONTEXT_SIZE = 36768

def _build_config(model_id: str, model_url: str | None) -> dict:
    """Build kwargs for lx.extract using local Ollama.

    Configures LangExtract to use local Ollama models with simplified
    settings optimized for local inference.
    """
    return {
        "model_id": model_id,
        "model_url": model_url,
        "fence_output": True,
        "use_schema_constraints": False,
        "language_model_params": {"timeout": 600, "num_ctx": CONTEXT_SIZE},
        "resolver_params": {
            "suppress_parse_errors": True,
            "enable_fuzzy_alignment": False,
        },
    }




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
    """Extract from a single chunk with retries."""
    for attempt in range(MAX_RETRIES + 1):
        try:
            result = lx.extract(
                text_or_documents=chunk,
                prompt_description=prompt,
                examples=examples,
                extraction_passes=1,
                max_char_buffer=MAX_CHAR_BUFFER + 1,
                max_workers=1,
                batch_length=1,
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
            if attempt == MAX_RETRIES:
                return None
    return None


def extract_characters(
    text: str,
    model_id: str = "llama3.1:latest",
    model_url: str | None = "http://localhost:11434",
) -> list[dict]:
    """Extract characters from text using LangExtract with local Ollama."""
    chunks = _chunk_text(text)
    config = _build_config(model_id, model_url)
    characters = []
    skipped = 0

    for i, chunk in enumerate(chunks):
        result = _extract_chunk(chunk, CHARACTER_PROMPT, CHARACTER_EXAMPLES, config, debug=True)
        if result is None:
            skipped += 1
        else:
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
    return characters


def extract_relationships(
    text: str,
    model_id: str = "llama3.1:latest",
    model_url: str | None = "http://localhost:11434",
) -> list[dict]:
    """Extract relationships between characters from text using LangExtract with local Ollama."""
    chunks = _chunk_text(text)
    config = _build_config(model_id, model_url)
    relationships = []
    skipped = 0

    for i, chunk in enumerate(chunks):
        result = _extract_chunk(chunk, RELATIONSHIP_PROMPT, RELATIONSHIP_EXAMPLES, config, debug=True)
        if result is None:
            skipped += 1
        else:
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

    return relationships


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
