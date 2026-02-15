## 1. CLI Changes

- [x] 1.1 Update `main.py` argument parsing: detect if `pdf` arg is a directory, find all `*.pdf` files sorted alphabetically, error if no PDFs found
- [x] 1.2 Add progress output: print `Processing book N/M: filename.pdf` before each book

## 2. Batch Processing Loop

- [x] 2.1 Loop over each PDF: extract text, extract characters, extract relationships, collecting all results
- [x] 2.2 Support `--demo` flag in batch mode (truncate each book's text independently)

## 3. Merge and Output

- [x] 3.1 Deduplicate characters globally across all books using existing `deduplicate_characters()`
- [x] 3.2 Build unified graph with merged characters and all relationships, write to output path

## 4. Verification

- [x] 4.1 Test: `uv run main.py data/series/ --demo` processes all 3 PDFs and writes merged `data/data.json`
- [x] 4.2 Test: `uv run main.py data/series/horus-rising.pdf --demo` still works (single-file backward compat)
