## Why

The project is currently hardcoded to use Ollama (local) as the only model provider. Users should be able to choose between local Ollama models, remote Ollama-compatible endpoints (e.g., cloud-hosted Ollama), and the Gemini API — giving flexibility to trade off cost, speed, and quality without changing code.

## What Changes

- **BREAKING**: The `--model-url` flag and `OLLAMA_BASE_URL` env var are replaced by a provider-aware configuration (`--provider` flag with provider-specific options)
- Add a `--provider` CLI flag to select between `ollama` (default), `ollama-cloud`, and `gemini`
- For `ollama` provider: use local Ollama endpoint (current behavior, stays default)
- For `ollama-cloud` provider: use a remote Ollama-compatible API endpoint with optional API key authentication
- For `gemini` provider: use Google Gemini API via LangExtract's built-in Gemini provider, requiring a `GEMINI_API_KEY`
- Provider selection configures LangExtract's `model_id` and connection parameters accordingly
- Each provider may have different default models (e.g., `llama3.1:latest` for Ollama, `gemini-2.0-flash` for Gemini)

## Capabilities

### New Capabilities

- `model-provider`: Provider abstraction that maps CLI flags to LangExtract configuration — covers provider selection, per-provider defaults, API key handling, and model URL routing

### Modified Capabilities

_(none — no existing specs)_

## Impact

- **Code**: `extract.py` (`_build_config`) and `main.py` (CLI arg parsing) need changes
- **Dependencies**: No new dependencies — LangExtract already has built-in Gemini and Ollama providers
- **Environment**: Gemini provider requires `GEMINI_API_KEY` env var; Ollama cloud may require `OLLAMA_CLOUD_API_KEY`
- **CLI**: `--model-url` replaced by `--provider` + `--provider-url`; `--model` stays as-is
