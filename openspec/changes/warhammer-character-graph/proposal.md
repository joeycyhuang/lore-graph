## Why

Warhammer 40k novels have rich casts of characters with complex relationships (alliances, rivalries, command hierarchies, betrayals). Manually tracking these is tedious. We want to automatically extract characters and their relationships from PDF novels and visualize them as an interactive force-directed graph, making it easy to explore the social web of a story.

## What Changes

- Add a Python extraction pipeline using Google's LangExtract to parse Warhammer 40k PDFs, identify characters, and determine their relationships
- Output structured JSON with character nodes (name, description, faction, role) and relationship edges (type, description)
- Add a local `index.html` with D3-force visualization that renders the character graph
- Interactive hover tooltips: nodes show character info, edges show relationship descriptions
- Add project dependencies via `uv` (LangExtract, any PDF parsing deps)

## Capabilities

### New Capabilities
- `pdf-extraction`: Python pipeline to extract text from PDFs and use LangExtract to identify characters and their relationships, outputting structured JSON
- `graph-visualization`: Local index.html using D3-force to render an interactive force-directed graph with hover tooltips for nodes and edges

### Modified Capabilities
<!-- No existing capabilities to modify -->

## Impact

- **Dependencies**: Add `langextract` and supporting PDF libraries via `uv`; D3.js loaded via CDN in index.html
- **New files**: Python extraction script, `index.html` for visualization, output JSON data file
- **Existing code**: `main.py` will be updated to serve as the extraction entry point
