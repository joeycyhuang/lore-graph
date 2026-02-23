## Context

The project currently hardcodes Ollama local as the sole model provider. `_build_config()` in `extract.py` builds kwargs for `lx.extract()` assuming Ollama, and `main.py` exposes `--model` and `--model-url` CLI flags tied to that assumption.

LangExtract already ships three built-in providers (Gemini, Ollama, OpenAI) with pattern-based auto-routing: `model_id` starting with `gemini` routes to Gemini, patterns like `llama`/`gemma`/`mistral` route to Ollama, and `gpt-4`/`gpt-5` route to OpenAI. The Ollama provider accepts any `model_url` (not restricted to localhost) and supports API key auth for proxied/cloud instances.

## Goals / Non-Goals

**Goals:**
- Let users select between `ollama`, `ollama-cloud`, and `gemini` providers via CLI
- Each provider configures `lx.extract()` with appropriate params (url, api_key, model defaults)
- Keep `ollama` as the default so existing workflows don't break
- Keep the implementation simple — a single config-building function per provider, no class hierarchy

**Non-Goals:**
- OpenAI provider support (can be added later using the same pattern)
- Provider plugin system or dynamic provider discovery
- Changing extraction logic, prompts, or chunking behavior
- Frontend changes

## Decisions

### 1. Provider selection via `--provider` flag, not model_id inference

LangExtract can auto-route based on `model_id` patterns, but this breaks for ambiguous cases (e.g., `gemma3:27b` could be local Ollama or cloud Ollama) and doesn't let users control *where* the model runs.

**Decision:** Add an explicit `--provider` CLI flag (`ollama` | `ollama-cloud` | `gemini`). The provider determines connection params; `--model` still specifies which model.

**Alternative considered:** Rely on LangExtract's auto-routing. Rejected because it can't distinguish local vs cloud Ollama, and makes the user experience confusing.

### 2. Provider config as a dict-returning function, not a class

Each provider needs to produce a dict of kwargs for `lx.extract()`. A simple function per provider (or a single function with a match statement) is sufficient.

**Decision:** Replace `_build_config(model_id, model_url)` with a `build_provider_config(provider, model_id, **overrides)` function that returns the full kwargs dict. Use a match/case on the provider string.

**Alternative considered:** Provider base class with subclasses. Rejected — unnecessary abstraction for 3 simple config variations.

### 3. API keys from environment variables

**Decision:** Follow LangExtract's own conventions:
- Gemini: `GEMINI_API_KEY` (LangExtract checks this natively)
- Ollama cloud: `OLLAMA_API_KEY` env var, passed as `api_key` in `language_model_params`
- Local Ollama: no key needed

No `--api-key` CLI flag — keys shouldn't appear in shell history.

### 4. Provider-specific defaults

| Provider | Default model | Default URL | Auth |
|----------|--------------|-------------|------|
| `ollama` | `llama3.1:latest` | `http://localhost:11434` | None |
| `ollama-cloud` | `llama3.1:latest` | `https://ollama.com` (override via `--provider-url` or `OLLAMA_CLOUD_URL`) | `OLLAMA_API_KEY` (required) |
| `gemini` | `gemini-2.0-flash` | Google's API (managed by LangExtract) | `GEMINI_API_KEY` (required) |

### 5. Remove `--model-url`, add `--provider-url`

**Decision:** Replace `--model-url` / `OLLAMA_BASE_URL` with `--provider-url` / `OLLAMA_CLOUD_URL`. For local Ollama the default is always localhost. For Gemini the URL is managed by LangExtract. `--provider-url` is an optional override for `ollama-cloud` (defaults to `https://ollama.com`).

### 6. LangExtract config differences by provider

For Gemini, the key differences from Ollama config:
- No `model_url` — LangExtract handles the endpoint
- `api_key` passed directly to `lx.extract()`
- No `num_ctx` in `language_model_params` (Gemini manages context windows)
- `use_schema_constraints` can stay False for consistency
- `fence_output` stays True

For Ollama cloud, identical to local Ollama except `model_url` points to the remote endpoint and `api_key` is passed in `language_model_params`.

## Risks / Trade-offs

**LangExtract's Gemini provider may need `google-genai` SDK installed** → Check if it's already a dependency of langextract; if not, add it. Mitigation: test import at startup, give clear error.

**Ollama cloud endpoints vary in API compatibility** → Some cloud Ollama providers may not support all features (e.g., `num_ctx`). Mitigation: document known-working providers; keep config minimal.

**Breaking change to CLI flags** → Users with scripts using `--model-url` will need to update. Mitigation: the project is local-only with a small user base (likely just the author); document in commit message.
