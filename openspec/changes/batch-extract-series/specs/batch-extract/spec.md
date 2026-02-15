## ADDED Requirements

### Requirement: CLI accepts a directory of PDFs
The CLI SHALL accept a directory path as the positional `pdf` argument. When a directory is provided, it SHALL find all `*.pdf` files within it and process each one.

#### Scenario: Directory with multiple PDFs
- **WHEN** user runs `uv run main.py data/series/`
- **THEN** the CLI finds all `.pdf` files in `data/series/`, processes each one sequentially, and writes merged results to the output file

#### Scenario: Single PDF still works
- **WHEN** user runs `uv run main.py somebook.pdf`
- **THEN** the CLI processes the single PDF exactly as before (backward compatible)

#### Scenario: Directory with no PDFs
- **WHEN** user runs `uv run main.py empty-dir/`
- **THEN** the CLI prints an error message and exits with a non-zero code

### Requirement: Characters are deduplicated across all books
The CLI SHALL collect characters from all processed PDFs and deduplicate them globally using the existing deduplication logic, so that a character appearing in multiple books results in a single node.

#### Scenario: Same character in two books
- **WHEN** "Garviel Loken" is extracted from both `horus-rising.pdf` and `false-gods.pdf`
- **THEN** the output contains a single "Garviel Loken" node with the most complete attributes

### Requirement: Relationships are merged across all books
The CLI SHALL collect relationships from all processed PDFs and include them all in the final output graph.

#### Scenario: Relationships from multiple books
- **WHEN** relationships are extracted from three PDFs
- **THEN** all relationships from all three books appear in the output edges, with source/target resolved to the deduplicated character nodes

### Requirement: Progress output per book
The CLI SHALL print the name of each PDF as it begins processing, so the user can track progress across a multi-book run.

#### Scenario: Processing three books
- **WHEN** user runs against a directory with three PDFs
- **THEN** the CLI prints a line like `Processing book 1/3: horus-rising.pdf` before each book
