## ADDED Requirements

### Requirement: Extract text from PDF
The system SHALL accept a PDF file path as input and extract all readable text content from it using PyMuPDF.

#### Scenario: Valid PDF file
- **WHEN** a valid PDF file path is provided (e.g., `Horus Rising.pdf`)
- **THEN** the system extracts the full text content from all pages and returns it as a single string

#### Scenario: Invalid or missing PDF file
- **WHEN** an invalid or non-existent file path is provided
- **THEN** the system exits with a clear error message indicating the file was not found or could not be read

### Requirement: Extract characters from text
The system SHALL use LangExtract with a character-focused prompt to extract all named characters from the extracted text. Each character SHALL include: `name`, `faction`, `role`, and `description` attributes.

#### Scenario: Character extraction from novel text
- **WHEN** the extracted text is passed to LangExtract with the character extraction prompt and few-shot examples
- **THEN** the system returns a list of character entities, each with `name` (string), `faction` (string), `role` (string), and `description` (string) attributes

#### Scenario: No characters found
- **WHEN** the text contains no identifiable characters
- **THEN** the system returns an empty character list and logs a warning

### Requirement: Extract relationships from text
The system SHALL use LangExtract with a relationship-focused prompt to extract relationships between characters. Each relationship SHALL include: `source_character`, `target_character`, `type`, and `description` attributes.

#### Scenario: Relationship extraction from novel text
- **WHEN** the extracted text is passed to LangExtract with the relationship extraction prompt and few-shot examples
- **THEN** the system returns a list of relationship entities, each with `source_character` (string), `target_character` (string), `type` (string, e.g., "command", "rivalry", "alliance", "betrayal"), and `description` (string) attributes

### Requirement: Deduplicate characters
The system SHALL merge characters that refer to the same person under different names (e.g., "Loken", "Garviel Loken", "Captain Loken") into a single node, using the most complete name as the canonical identifier.

#### Scenario: Same character with multiple name variants
- **WHEN** extraction produces multiple character entries that refer to the same person
- **THEN** the system merges them into one entry, combining their attributes and using the fullest name form

### Requirement: Output structured JSON
The system SHALL output a `data.json` file containing a `nodes` array (characters) and an `edges` array (relationships) in a format compatible with D3-force.

#### Scenario: Successful extraction and output
- **WHEN** character and relationship extraction completes successfully
- **THEN** the system writes a `data.json` file with structure `{ "nodes": [{ "id", "name", "faction", "role", "description" }], "edges": [{ "source", "target", "type", "description" }] }`

#### Scenario: Edge references valid nodes
- **WHEN** a relationship references a character name
- **THEN** the `source` and `target` fields in each edge SHALL match a valid node `id` in the nodes array

### Requirement: CLI entry point
The system SHALL provide a CLI entry point via `main.py` that accepts a PDF file path as an argument and runs the full extraction pipeline.

#### Scenario: Run extraction from command line
- **WHEN** the user runs `uv run main.py "Horus Rising.pdf"`
- **THEN** the system extracts characters and relationships from the PDF and writes `data.json` to the project root

#### Scenario: Run with custom output path
- **WHEN** the user runs `uv run main.py "Horus Rising.pdf" --output custom_output.json`
- **THEN** the system writes the output to the specified path instead of the default `data.json`
