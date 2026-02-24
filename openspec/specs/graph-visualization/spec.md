### Requirement: Load and render force-directed graph
The `index.html` SHALL load `data.json` and render all character nodes and relationship edges as a force-directed graph using D3-force.

#### Scenario: Graph renders with data
- **WHEN** `index.html` is opened via a local HTTP server and `data.json` exists
- **THEN** all character nodes appear as circles and all relationships appear as lines connecting them, arranged by D3-force simulation

#### Scenario: Missing data file
- **WHEN** `data.json` is not found or fails to load
- **THEN** the page displays an error message indicating the data file could not be loaded

### Requirement: Node visual encoding
Each node SHALL be rendered as a circle with a label showing the character's name. Nodes SHALL be color-coded by faction.

#### Scenario: Nodes display names
- **WHEN** the graph renders
- **THEN** each node displays the character's name as a text label adjacent to the circle

#### Scenario: Nodes colored by faction
- **WHEN** characters belong to different factions
- **THEN** nodes of the same faction share the same color, and a legend maps faction names to colors

### Requirement: Node hover tooltip
The system SHALL display a tooltip when the user hovers over a character node, showing the character's name, faction, role, and description.

#### Scenario: Hover over a character node
- **WHEN** the user hovers their cursor over a character node
- **THEN** a tooltip appears near the cursor showing the character's name, faction, role, and description

#### Scenario: Mouse leaves node
- **WHEN** the user moves their cursor away from a character node
- **THEN** the tooltip disappears

### Requirement: Edge hover tooltip
The system SHALL display a tooltip when the user hovers over a relationship edge, showing the relationship type and description.

#### Scenario: Hover over a relationship edge
- **WHEN** the user hovers their cursor over a relationship edge (line)
- **THEN** a tooltip appears showing the relationship type and description, along with the names of the two connected characters

#### Scenario: Mouse leaves edge
- **WHEN** the user moves their cursor away from a relationship edge
- **THEN** the tooltip disappears

### Requirement: Interactive graph manipulation
Nodes SHALL be draggable. The user SHALL be able to drag individual nodes to rearrange the graph layout, with the force simulation resuming after release.

#### Scenario: Drag a node
- **WHEN** the user clicks and drags a node
- **THEN** the node follows the cursor and connected edges update in real-time

#### Scenario: Release a dragged node
- **WHEN** the user releases a dragged node
- **THEN** the force simulation resumes and the graph settles into a new equilibrium

### Requirement: Zoom and pan
The graph SHALL support zoom (mouse wheel) and pan (click-and-drag on background) to navigate large graphs.

#### Scenario: Zoom in and out
- **WHEN** the user scrolls the mouse wheel over the graph
- **THEN** the graph zooms in or out centered on the cursor position

#### Scenario: Pan the view
- **WHEN** the user clicks and drags on the graph background (not a node)
- **THEN** the entire graph view pans in the drag direction

### Requirement: Standalone HTML file
The `index.html` SHALL be a single self-contained file with inline CSS and JavaScript. D3.js SHALL be loaded from a CDN. No build step or framework required.

#### Scenario: Open without build tools
- **WHEN** the user serves the project directory with `python -m http.server` and opens `index.html`
- **THEN** the graph loads and functions correctly with no additional build steps
