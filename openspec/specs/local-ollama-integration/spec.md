### Requirement: System can extract using local Ollama models
The system SHALL support character and relationship extraction using locally-hosted Ollama models without requiring cloud API access. The system MUST use LangExtract's native Ollama integration with direct model_id and model_url parameters.

#### Scenario: Extract characters using local Ollama
- **WHEN** `extract_characters()` is called with `model_id="llama3.1:latest"` and `model_url="http://localhost:11434"`
- **THEN** the system SHALL send extraction requests to the local Ollama instance and return extracted character data

#### Scenario: Extract relationships using local Ollama
- **WHEN** `extract_relationships()` is called with `model_id="llama3.1:latest"` and `model_url="http://localhost:11434"`
- **THEN** the system SHALL send extraction requests to the local Ollama instance and return extracted relationship data

### Requirement: System uses simplified Ollama configuration
The system SHALL configure Ollama integration without OpenAI provider wrapping or endpoint manipulation. The `_build_config()` function MUST return a simple kwargs dictionary with `model_id`, `model_url`, `fence_output`, and `use_schema_constraints` parameters.

#### Scenario: Build configuration for local Ollama
- **WHEN** `_build_config()` is called with `model_id="llama3.1:latest"` and `model_url="http://localhost:11434"`
- **THEN** the function SHALL return a dictionary containing `model_id`, `model_url`, `fence_output=False`, `use_schema_constraints=False`, and `resolver_params` without ModelConfig or provider wrapping

#### Scenario: Configuration does not append /v1 endpoint
- **WHEN** `_build_config()` is called with `model_url="http://localhost:11434"`
- **THEN** the function SHALL use the URL directly without appending "/v1"

### Requirement: System operates offline without API keys
The system SHALL perform character and relationship extraction entirely offline when using local Ollama models. The system MUST NOT require API keys or internet connectivity for extraction operations.

#### Scenario: Extract without API key
- **WHEN** `extract_characters()` or `extract_relationships()` is called with local Ollama configuration and no `api_key` parameter
- **THEN** the system SHALL successfully extract data without requiring authentication

#### Scenario: Extract without internet connectivity
- **WHEN** extraction is performed with local Ollama while offline
- **THEN** the system SHALL complete extraction using only the local Ollama instance

### Requirement: System disables fencing and schema constraints for Ollama
The system SHALL disable output fencing and schema constraints when using Ollama models to ensure compatibility with local model responses. The extraction calls MUST set `fence_output=False` and `use_schema_constraints=False`.

#### Scenario: Extraction uses lenient parsing
- **WHEN** `lx.extract()` is called via `extract_characters()` or `extract_relationships()`
- **THEN** the call SHALL include `fence_output=False` and `use_schema_constraints=False` parameters

#### Scenario: Extraction uses lenient format handler
- **WHEN** extraction is performed with local Ollama
- **THEN** the system SHALL use the `_LENIENT_HANDLER` format handler to parse non-fenced model outputs

### Requirement: System defaults to local Ollama configuration
The extraction functions SHALL use local Ollama as the default configuration. The `extract_characters()` and `extract_relationships()` functions MUST default to `model_id="llama3.1:latest"` and `model_url="http://localhost:11434"`.

#### Scenario: Extract characters with defaults
- **WHEN** `extract_characters(text)` is called without explicit model parameters
- **THEN** the system SHALL use `model_id="llama3.1:latest"` and `model_url="http://localhost:11434"`

#### Scenario: Extract relationships with defaults
- **WHEN** `extract_relationships(text)` is called without explicit model parameters
- **THEN** the system SHALL use `model_id="llama3.1:latest"` and `model_url="http://localhost:11434"`
