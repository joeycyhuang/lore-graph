## 1. CLI changes in main.py

- [x] 1.1 Remove `--model-url` argument and `OLLAMA_BASE_URL` env var usage
- [x] 1.2 Add `--provider` argument with choices `ollama`, `ollama-cloud`, `gemini` (default: `ollama`)
- [x] 1.3 Add `--provider-url` argument for optionally overriding the default endpoint URL
- [x] 1.4 Resolve provider-specific default model when `--model` is not given (`llama3.1:latest` for ollama/ollama-cloud, `gemini-2.0-flash` for gemini)
- [x] 1.5 Add validation: exit with error if `ollama-cloud` selected without `OLLAMA_API_KEY` env var
- [x] 1.6 Add validation: exit with error if `gemini` selected without `GEMINI_API_KEY` env var

## 2. Provider config in extract.py

- [x] 2.1 Replace `_build_config(model_id, model_url)` with `build_provider_config(provider, model_id, provider_url=None)` using match/case
- [x] 2.2 Implement `ollama` case: `model_url="http://localhost:11434"`, `fence_output=True`, `num_ctx` in `language_model_params`
- [x] 2.3 Implement `ollama-cloud` case: default `model_url="https://ollama.com"` (override via `provider_url`), pass `OLLAMA_API_KEY` in `language_model_params`
- [x] 2.4 Implement `gemini` case: pass `api_key` from `GEMINI_API_KEY`, omit `model_url` and `num_ctx`
- [x] 2.5 Update `extract_characters` and `extract_relationships` signatures to accept a config dict instead of `model_id`/`model_url`

## 3. Integration and wiring

- [x] 3.1 Update `main.py` to call `build_provider_config()` and pass the result to extraction functions
- [x] 3.2 Update print statements to show provider and model info (e.g., "Extracting characters using gemini/gemini-2.0-flash...")

## 4. Verify

- [x] 4.1 Test `--provider ollama` works with local Ollama (default behavior preserved)
- [x] 4.2 Test `--provider gemini` with `GEMINI_API_KEY` set
- [x] 4.3 Test error cases: missing API key for gemini, missing API key for ollama-cloud, invalid provider
