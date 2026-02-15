## Why

The CLI currently processes one PDF at a time. To build a complete relationship graph across an entire Warhammer 40k book series (e.g., the three Horus Heresy novels in `data/series/`), the user must run the command repeatedly and manually merge results. We need batch processing that extracts characters and relationships from all PDFs in a directory and merges them into a single unified `data.json`.

## What Changes

- Add a batch mode to the CLI that accepts a directory glob (e.g., `data/series/*`) instead of a single PDF
- Process each PDF sequentially, extracting characters and relationships from each
- Deduplicate characters across all books (same character appearing in multiple novels)
- Merge all relationships into a single graph
- Write the combined result to `data.json` (or specified output path)

## Capabilities

### New Capabilities
- `batch-extract`: Process multiple PDFs from a directory, merge characters and relationships across books into a single unified graph output

### Modified Capabilities

## Impact

- `main.py`: New CLI argument to accept a directory/glob instead of a single PDF
- `extract.py`: No changes needed - existing extraction functions work per-text, caller handles merging
- `data/data.json`: Output will contain merged data from all books in the series
