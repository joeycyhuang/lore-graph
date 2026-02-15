## Context

The CLI (`main.py`) currently accepts a single PDF path and outputs one `data.json`. The `data/series/` directory contains multiple Horus Heresy novels. Users need to extract characters and relationships across all books and merge them into a single graph. The existing `extract.py` functions operate on text strings and are reusable as-is.

## Goals / Non-Goals

**Goals:**
- Accept a directory path or glob pattern to process multiple PDFs in one run
- Merge characters across books using existing deduplication logic
- Combine all relationships into a single unified graph output
- Maintain backward compatibility with single-PDF mode

**Non-Goals:**
- Per-book output files (one merged output only)
- Parallel PDF processing (sequential is fine for 3-5 books)
- Tracking which book a character/relationship came from

## Decisions

**1. CLI interface: positional arg accepts both files and directories**
The `pdf` positional argument will accept either a single PDF path or a directory path. When given a directory, it processes all `*.pdf` files found within it (sorted alphabetically for deterministic order). This avoids adding a separate subcommand and keeps usage simple.

Alternative considered: separate `--batch` flag or subcommand. Rejected because auto-detecting file vs directory is simpler and more intuitive.

**2. Merge strategy: extract per-book, deduplicate globally**
Each PDF is extracted independently (characters + relationships), then all characters are merged via the existing `deduplicate_characters()` function across the full set. This reuses existing logic without modification.

**3. Output path: default to `data/data.json`**
Keep the existing `--output` flag behavior, defaulting to `data/data.json`.

## Risks / Trade-offs

- [Large series = long runtime] → Acceptable for local tool; progress output per book helps user track
- [Cross-book deduplication may over-merge characters with common name parts] → Existing issue with `deduplicate_characters`, out of scope for this change
