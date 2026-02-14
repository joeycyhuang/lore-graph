## Context

This is a greenfield project. We have a PDF of "Horus Rising" (a Warhammer 40k novel) and want to extract its characters and relationships, then visualize them interactively. The project uses Python 3.14 with `uv` and a local `index.html` for visualization.

Google's LangExtract library uses Gemini LLMs to extract structured entities from unstructured text. It supports custom entity classes defined through prompts and few-shot examples, handles long documents via chunking, and outputs grounded extractions with source offsets.

## Goals / Non-Goals

**Goals:**
- Extract characters (name, faction, role, description) from Warhammer 40k PDFs using LangExtract
- Extract relationships between characters (type, description) from the same text
- Output a single JSON file containing nodes and edges
- Render an interactive force-directed graph in a standalone `index.html`
- Support hovering on nodes (character info) and edges (relationship info)

**Non-Goals:**
- No web server or backend API — this is purely local file-based
- No database or persistent storage beyond the JSON output
- No support for real-time PDF uploads — PDFs are processed via CLI
- No multi-book relationship merging — each PDF produces its own graph
- No editing or manual correction of extracted data in the UI

## Decisions

### 1. Two-pass extraction with LangExtract

**Decision**: Run two separate LangExtract extraction passes — one for characters, one for relationships.

**Rationale**: LangExtract works best with focused prompts and clear few-shot examples. Extracting characters and relationships in a single pass creates ambiguity. Two passes let us:
- Define precise examples for each entity type
- Get better extraction quality from the LLM
- Keep the code modular and debuggable

**Alternative considered**: Single-pass extraction with multiple entity classes. Rejected because mixed entity types in one prompt reduce quality and make few-shot examples harder to construct.

### 2. PDF text extraction via PyMuPDF (pymupdf)

**Decision**: Use PyMuPDF to extract raw text from PDFs before passing to LangExtract.

**Rationale**: LangExtract operates on text strings, not PDF files directly. PyMuPDF is fast, well-maintained, has no system dependencies, and handles the layout of novel-style PDFs well. It can be installed via `uv add pymupdf`.

**Alternative considered**: pdfplumber — heavier, more focused on tabular data extraction. PyMuPDF is simpler for prose text.

### 3. JSON data format

**Decision**: Output a single `data.json` with `{ "nodes": [...], "edges": [...] }` structure.

```json
{
  "nodes": [
    { "id": "loken", "name": "Garviel Loken", "faction": "Luna Wolves", "role": "Captain, 10th Company", "description": "..." }
  ],
  "edges": [
    { "source": "loken", "target": "abaddon", "type": "rivalry", "description": "..." }
  ]
}
```

**Rationale**: This maps directly to D3-force's expected data format. A single file keeps things simple — the `index.html` just fetches one file.

### 4. D3-force with vanilla JS in a single HTML file

**Decision**: Use a single `index.html` that loads D3.js v7 from CDN, fetches `data.json`, and renders the force-directed graph. All CSS and JS inline.

**Rationale**: No build step, no framework, no server. Open the file via a simple local HTTP server (e.g., `python -m http.server`) and it works. D3-force is the standard for force-directed graphs and handles our scale (dozens to low-hundreds of nodes) easily.

**Alternative considered**: vis.js or Cytoscape.js — both are heavier and less flexible for custom styling. D3 gives full control over the visualization.

### 5. Gemini model selection

**Decision**: Default to `gemini-2.5-flash` for extraction.

**Rationale**: Flash is fast and cheap, sufficient for entity extraction. Users can switch to `gemini-2.5-pro` for better quality if needed. The model ID is passed to `lx.extract()`.

## Risks / Trade-offs

- **[Extraction quality]** LLM-based extraction may miss minor characters or hallucinate relationships → Mitigation: Careful few-shot examples grounded in Warhammer 40k context; two-pass approach improves focus
- **[Gemini API key required]** LangExtract with Gemini models requires a Google AI API key → Mitigation: Document setup clearly; key is read from environment variable `GOOGLE_API_KEY`
- **[PDF text quality]** Some PDFs may have poor text extraction (scanned images, unusual formatting) → Mitigation: PyMuPDF handles most novel PDFs well; out of scope to support OCR
- **[Large documents]** Long novels may hit LLM context limits → Mitigation: LangExtract handles chunking internally, but very long books may need tuning of chunk parameters
- **[Character deduplication]** Same character may be referred to by different names (e.g., "Loken", "Garviel", "Captain Loken") → Mitigation: Post-processing deduplication step based on LLM output attributes
