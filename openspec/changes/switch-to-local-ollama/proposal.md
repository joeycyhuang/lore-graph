## Why

The current implementation uses cloud-based LLM APIs through a custom OpenAI provider endpoint, which requires API keys, internet connectivity, and incurs usage costs. Switching to local Ollama enables offline operation, eliminates API costs, ensures data privacy, and provides faster response times with a locally-hosted `llama3.1:latest` model already running at `localhost:11434`.

## What Changes

- Replace cloud-based OpenAI provider configuration with direct Ollama integration
- Simplify `_build_config()` function in `extract.py` to use LangExtract's native Ollama support
- Remove `/v1` endpoint wrapping and complex provider configuration
- Disable output fencing and schema constraints for compatibility with local models
- Update default model from `gemini-2.5-flash` to `llama3.1:latest`
- Update model URL default to point to local Ollama instance at `http://localhost:11434`

## Capabilities

### New Capabilities
- `local-ollama-integration`: Support for running character and relationship extraction using local Ollama models, including simplified configuration and compatibility settings for local inference

### Modified Capabilities

(None - this is the first capability being added to the project)

## Impact

**Code Changes:**
- `extract.py`: Complete refactor of `_build_config()` function (lines 132-167)
- `extract.py`: Update default parameters in `extract_characters()` and `extract_relationships()` functions

**Dependencies:**
- Requires Ollama running locally (already confirmed at `localhost:11434`)
- Requires `llama3.1:latest` model pulled in Ollama (already available)

**Behavior Changes:**
- Extraction will run entirely offline
- No API keys needed
- Response times may vary based on local hardware vs cloud latency
