### Requirement: Provider selection via CLI
The CLI SHALL accept a `--provider` flag with allowed values `ollama`, `ollama-cloud`, and `gemini`. When omitted, the provider SHALL default to `ollama`.

#### Scenario: Default provider
- **WHEN** the user runs the CLI without `--provider`
- **THEN** the system uses the `ollama` provider with `http://localhost:11434` as the endpoint

#### Scenario: Explicit provider selection
- **WHEN** the user runs `--provider gemini`
- **THEN** the system configures LangExtract to use the Gemini provider

#### Scenario: Invalid provider
- **WHEN** the user runs `--provider foobar`
- **THEN** the CLI exits with an error listing valid providers (`ollama`, `ollama-cloud`, `gemini`)

### Requirement: Provider-specific default models
Each provider SHALL have a default model used when `--model` is not specified. The defaults SHALL be:
- `ollama`: `llama3.1:latest`
- `ollama-cloud`: `llama3.1:latest`
- `gemini`: `gemini-2.0-flash`

The `--model` flag SHALL override the default for any provider.

#### Scenario: Default model for ollama
- **WHEN** the user runs `--provider ollama` without `--model`
- **THEN** the system uses `llama3.1:latest`

#### Scenario: Default model for gemini
- **WHEN** the user runs `--provider gemini` without `--model`
- **THEN** the system uses `gemini-2.0-flash`

#### Scenario: Model override
- **WHEN** the user runs `--provider gemini --model gemini-2.5-pro`
- **THEN** the system uses `gemini-2.5-pro` instead of the default

### Requirement: Ollama local provider configuration
When `--provider ollama` is selected, the system SHALL configure LangExtract with `model_url` set to `http://localhost:11434`, `fence_output` enabled, and `num_ctx` in `language_model_params`.

#### Scenario: Local Ollama extraction
- **WHEN** the user runs `--provider ollama --model gemma3:27b`
- **THEN** the system calls `lx.extract()` with `model_id="gemma3:27b"`, `model_url="http://localhost:11434"`, and Ollama-specific params

### Requirement: Ollama cloud provider configuration
When `--provider ollama-cloud` is selected, the system SHALL use `https://ollama.com` as the default endpoint URL. The URL MAY be overridden via `--provider-url` flag or `OLLAMA_CLOUD_URL` env var. The `OLLAMA_API_KEY` env var MUST be set; if missing, the system SHALL exit with an error. The API key SHALL be passed as `api_key` in `language_model_params`.

#### Scenario: Cloud Ollama with default URL
- **WHEN** the user runs `--provider ollama-cloud --model gemma3:27b` without `--provider-url`
- **THEN** the system calls `lx.extract()` with `model_url="https://ollama.com"` and `model_id="gemma3:27b"`

#### Scenario: Cloud Ollama with URL override
- **WHEN** the user runs `--provider ollama-cloud --provider-url https://my-ollama.cloud:7860`
- **THEN** the system calls `lx.extract()` with `model_url="https://my-ollama.cloud:7860"` instead of the default

#### Scenario: Cloud Ollama missing API key
- **WHEN** `OLLAMA_API_KEY` is not set and the user runs `--provider ollama-cloud`
- **THEN** the system exits with an error stating that `OLLAMA_API_KEY` is required

#### Scenario: Cloud Ollama with API key
- **WHEN** `OLLAMA_API_KEY` is set and `--provider ollama-cloud` is selected
- **THEN** the API key is included in `language_model_params` for authentication

### Requirement: Gemini provider configuration
When `--provider gemini` is selected, the system SHALL configure LangExtract for Gemini. The `GEMINI_API_KEY` env var MUST be set; if missing, the system SHALL exit with an error. The system SHALL NOT pass `model_url` or `num_ctx` to LangExtract for Gemini.

#### Scenario: Gemini with valid API key
- **WHEN** `GEMINI_API_KEY` is set and the user runs `--provider gemini`
- **THEN** the system calls `lx.extract()` with `model_id="gemini-2.0-flash"` and `api_key` from the env var

#### Scenario: Gemini missing API key
- **WHEN** `GEMINI_API_KEY` is not set and the user runs `--provider gemini`
- **THEN** the system exits with an error stating that `GEMINI_API_KEY` is required

### Requirement: Remove legacy model-url flag
The `--model-url` CLI flag and `OLLAMA_BASE_URL` env var SHALL be removed. The `--provider-url` flag SHALL replace them, applicable only to the `ollama-cloud` provider.

#### Scenario: Provider URL flag replaces model-url
- **WHEN** the user runs `--provider-url https://example.com`
- **THEN** the URL is used as the endpoint for `ollama-cloud` provider

#### Scenario: Provider URL ignored for local ollama
- **WHEN** the user runs `--provider ollama --provider-url https://example.com`
- **THEN** the system ignores `--provider-url` and uses `http://localhost:11434`
