## Context

The current implementation in `extract.py` uses cloud-based LLM APIs through a custom configuration that wraps Ollama cloud endpoints in an OpenAI provider. The `_build_config()` function (lines 132-167) adds `/v1` to the base URL and uses the OpenAI provider with custom provider_kwargs. This approach was designed for cloud APIs but is unnecessarily complex for local Ollama instances.

LangExtract natively supports Ollama with a simplified configuration. The official documentation recommends using direct model_id and model_url parameters without provider wrapping, along with disabling output fencing and schema constraints for compatibility with local models.

## Goals / Non-Goals

**Goals:**
- Replace cloud API configuration with LangExtract's native Ollama support
- Simplify `_build_config()` to remove OpenAI provider wrapping and `/v1` endpoint manipulation
- Enable offline character/relationship extraction using local `llama3.1:latest` model
- Maintain extraction quality comparable to cloud models
- Update function defaults to point to local Ollama instance at `http://localhost:11434`

**Non-Goals:**
- Supporting both cloud and local models simultaneously (can be added later if needed)
- Automatic fallback to cloud models if Ollama is unavailable
- Multi-model support or model selection UI
- Changing the extraction pipeline logic or output format
- Modifying the frontend visualization or data schema

## Decisions

### Decision 1: Use LangExtract's Native Ollama Support

**Chosen Approach:** Use direct `model_id` and `model_url` parameters as shown in LangExtract's official Ollama documentation.

**Rationale:**
- Simpler configuration with fewer layers of abstraction
- Follows official best practices from LangExtract docs
- Eliminates need for OpenAI provider wrapping and `/v1` endpoint manipulation
- Reduces potential for configuration errors

**Alternatives Considered:**
- Keep OpenAI provider pointing at Ollama's `/v1` endpoint: Rejected because it adds unnecessary complexity and doesn't follow LangExtract's recommended pattern for local Ollama

### Decision 2: Disable Fencing and Schema Constraints

**Chosen Approach:** Set `fence_output=False` and `use_schema_constraints=False` in the `lx.extract()` calls.

**Rationale:**
- Required for compatibility with local models per LangExtract documentation
- Local models may not reliably wrap outputs in JSON fences
- The lenient format handler already in place handles non-fenced outputs

**Alternatives Considered:**
- Keep strict fencing enabled: Rejected because official docs explicitly recommend disabling for Ollama

### Decision 3: Use llama3.1:latest as Default Model

**Chosen Approach:** Change default model from `gemini-2.5-flash` to `llama3.1:latest`.

**Rationale:**
- Already pulled and available locally (4.9GB)
- Sufficient capability for entity extraction tasks
- Balance between model size and extraction quality

**Alternatives Considered:**
- Use smaller model like `gemma2:2b`: Rejected in favor of better quality, though users can override
- Keep Gemini as default: Rejected because it defeats the purpose of switching to local

### Decision 4: Simplify _build_config() Function

**Chosen Approach:** Refactor `_build_config()` to return simple kwargs dict with `model_id`, `model_url`, `fence_output`, and `use_schema_constraints`.

**Rationale:**
- Removes ModelConfig complexity when using local Ollama
- Cleaner separation between local and cloud configurations
- Easier to maintain and understand

**Implementation:**
```python
def _build_config(model_id: str, model_url: str | None) -> dict:
    """Build kwargs for lx.extract using local Ollama."""
    return {
        "model_id": model_id,
        "model_url": model_url,
        "fence_output": False,
        "use_schema_constraints": False,
        "resolver_params": {
            "format_handler": _LENIENT_HANDLER,
            "suppress_parse_errors": True,
        },
    }
```

## Risks / Trade-offs

**[Risk: Model Quality Variance]**
- Local `llama3.1:latest` may extract entities differently than `gemini-2.5-flash`
- **Mitigation:** Test on sample PDFs and compare output quality. Users can switch models if needed.

**[Risk: Hardware Dependency]**
- Extraction speed depends on local machine capabilities (CPU/GPU, RAM)
- Large PDFs may be slower on limited hardware
- **Mitigation:** Document minimum hardware requirements. Consider adding batch size controls if performance issues arise.

**[Risk: Ollama Service Availability]**
- Script will fail if Ollama service is not running
- No automatic fallback to cloud models
- **Mitigation:** Add clear error messaging when Ollama is unreachable. Document how to start Ollama service.

**[Trade-off: Simplicity vs Flexibility]**
- Removing cloud model support makes configuration simpler but less flexible
- **Accepted because:** Project conventions favor simplicity; cloud support can be re-added if needed without breaking changes
