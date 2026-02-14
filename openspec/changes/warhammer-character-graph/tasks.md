## 1. Project Setup

- [x] 1.1 Add Python dependencies via uv: `langextract`, `pymupdf`
- [x] 1.2 Set up project structure: create `extract.py` module for extraction logic

## 2. PDF Text Extraction

- [x] 2.1 Implement `extract_text_from_pdf(pdf_path: str) -> str` in `extract.py` using PyMuPDF to read all pages and return concatenated text
- [x] 2.2 Add error handling for missing/invalid PDF files with clear error messages

## 3. Character Extraction

- [x] 3.1 Define LangExtract character extraction prompt and few-shot examples with Warhammer 40k context (name, faction, role, description attributes)
- [x] 3.2 Implement `extract_characters(text: str) -> list[dict]` that runs LangExtract character extraction and returns structured character data
- [x] 3.3 Implement character deduplication logic to merge name variants (e.g., "Loken" / "Garviel Loken" / "Captain Loken") into single entries

## 4. Relationship Extraction

- [x] 4.1 Define LangExtract relationship extraction prompt and few-shot examples (source_character, target_character, type, description attributes)
- [x] 4.2 Implement `extract_relationships(text: str) -> list[dict]` that runs LangExtract relationship extraction and returns structured relationship data

## 5. Data Assembly and Output

- [x] 5.1 Implement `build_graph_data(characters, relationships) -> dict` that assembles nodes and edges into D3-compatible JSON structure, generating stable IDs and validating that all edge source/target references match valid node IDs
- [x] 5.2 Write the assembled data to `data.json` with proper formatting

## 6. CLI Entry Point

- [x] 6.1 Update `main.py` with argparse CLI: accept PDF path as positional argument, optional `--output` flag (default `data.json`), and optional `--model` flag (default `gemini-2.5-flash`)
- [x] 6.2 Wire up the full pipeline in main: read PDF → extract characters → extract relationships → deduplicate → build graph → write JSON

## 7. Graph Visualization

- [x] 7.1 Create `index.html` with D3.js v7 loaded from CDN, basic HTML structure, and inline CSS for full-viewport SVG canvas with dark background
- [x] 7.2 Implement data loading: fetch `data.json`, handle missing file with error message displayed on page
- [x] 7.3 Implement D3-force simulation with nodes (circles, color-coded by faction) and edges (lines), including faction color legend
- [x] 7.4 Add text labels to nodes showing character names
- [x] 7.5 Implement node hover tooltip showing name, faction, role, and description
- [x] 7.6 Implement edge hover tooltip showing relationship type, description, and connected character names
- [x] 7.7 Implement node dragging with force simulation resume on release
- [x] 7.8 Implement zoom (mouse wheel) and pan (background drag) via `d3.zoom()`
