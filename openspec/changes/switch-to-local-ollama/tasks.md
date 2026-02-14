## 1. Refactor _build_config() Function

- [x] 1.1 Remove ModelConfig import and provider loading logic from _build_config()
- [x] 1.2 Remove /v1 endpoint appending logic that wraps model_url
- [x] 1.3 Remove OpenAI provider wrapping and provider_kwargs configuration
- [x] 1.4 Replace function body to return simple kwargs dict with model_id, model_url, fence_output=False, use_schema_constraints=False
- [x] 1.5 Update _build_config() signature to remove api_key parameter (no longer needed for local Ollama)
- [x] 1.6 Keep resolver_params with _LENIENT_HANDLER and suppress_parse_errors for compatibility

## 2. Update extract_characters() Function Defaults

- [x] 2.1 Change default model_id parameter from "gemini-2.5-flash" to "llama3.1:latest"
- [x] 2.2 Change default model_url parameter to "http://localhost:11434"
- [x] 2.3 Remove api_key parameter from function signature
- [x] 2.4 Update _build_config() call to pass only model_id and model_url

## 3. Update extract_relationships() Function Defaults

- [x] 3.1 Change default model_id parameter from "gemini-2.5-flash" to "llama3.1:latest"
- [x] 3.2 Change default model_url parameter to "http://localhost:11434"
- [x] 3.3 Remove api_key parameter from function signature
- [x] 3.4 Update _build_config() call to pass only model_id and model_url

## 4. Update Function Documentation

- [x] 4.1 Update _build_config() docstring to reflect local Ollama usage instead of cloud APIs
- [x] 4.2 Update extract_characters() docstring to mention local Ollama as default
- [x] 4.3 Update extract_relationships() docstring to mention local Ollama as default

## 5. Testing and Validation

- [x] 5.1 Test extraction with a sample PDF to verify local Ollama connectivity
- [x] 5.2 Verify character extraction produces valid output with llama3.1:latest
- [x] 5.3 Verify relationship extraction produces valid output with llama3.1:latest
- [x] 5.4 Confirm extraction works without API keys or internet connectivity
- [x] 5.5 Add error handling test for when Ollama service is not running
