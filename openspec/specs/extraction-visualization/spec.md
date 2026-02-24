### Requirement: Save annotated documents as JSONL
The extraction pipeline SHALL save the annotated document results from `lx.extract()` as a `.jsonl` file in the output directory using `lx.io.save_annotated_documents()`. The file SHALL be written to `data/extraction_results.jsonl`.

#### Scenario: Successful extraction saves JSONL
- **WHEN** the extraction pipeline completes character and relationship extraction
- **THEN** a file `data/extraction_results.jsonl` SHALL exist containing the annotated documents from all processed chunks

#### Scenario: JSONL contains all extraction results
- **WHEN** multiple PDF chunks are processed
- **THEN** the JSONL file SHALL contain annotated documents from every chunk that produced results

### Requirement: Generate visualization HTML from JSONL
The extraction pipeline SHALL generate an interactive HTML visualization from the saved `.jsonl` file using `lx.visualize()`. The output SHALL be written to `data/visualization.html`.

#### Scenario: Visualization HTML is generated after JSONL
- **WHEN** the JSONL file has been saved
- **THEN** the pipeline SHALL call `lx.visualize()` with the JSONL path and write the resulting HTML string to `data/visualization.html`

#### Scenario: Visualization HTML is self-contained
- **WHEN** `data/visualization.html` is opened in a browser
- **THEN** it SHALL render the extraction results with animated entity highlighting without requiring any other local files

### Requirement: Visualization generation is skippable
The CLI SHALL accept a `--no-viz` flag that skips JSONL saving and visualization generation.

#### Scenario: Default behavior generates visualization
- **WHEN** the user runs the extraction without `--no-viz`
- **THEN** both `extraction_results.jsonl` and `visualization.html` SHALL be generated in the output directory

#### Scenario: No-viz flag skips visualization
- **WHEN** the user runs the extraction with `--no-viz`
- **THEN** neither `extraction_results.jsonl` nor `visualization.html` SHALL be generated

### Requirement: Link to visualization from index.html
The `index.html` page SHALL include a visible link to open the generated visualization HTML.

#### Scenario: Visualization link is present
- **WHEN** the user opens `index.html` in a browser
- **THEN** a link/button to open the extraction visualization SHALL be visible in the UI

#### Scenario: Clicking visualization link opens the file
- **WHEN** the user clicks the visualization link
- **THEN** `data/visualization.html` SHALL open in a new browser tab
