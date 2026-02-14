"""Quick test: extract characters from first ~10 pages of a PDF."""

import json
import sys
from dotenv import load_dotenv
import os

load_dotenv()

from extract import extract_text_from_pdf, extract_characters, extract_relationships

pdf = sys.argv[1] if len(sys.argv) > 1 else "horus-rising.pdf"

model_id = os.getenv("OLLAMA_MODEL", "llama3.1:latest")
model_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

# Extract only first ~10 pages worth of text (~5000 chars)
print(f"Reading PDF: {pdf}")
full_text = extract_text_from_pdf(pdf)
sample = full_text[:5000]
print(f"Using sample of {len(sample)} chars (from {len(full_text)} total)\n")
print("--- Sample text (first 500 chars) ---")
print(sample[:500])
print("---\n")

print(f"Using Ollama model: {model_id} at {model_url}")
print("Extracting characters (1 pass for speed)...")
import langextract as lx
from extract import CHARACTER_PROMPT, CHARACTER_EXAMPLES, _build_config

# Use 1 pass instead of 3 for quick test
config = _build_config(model_id, model_url)
result = lx.extract(
    text_or_documents=sample,
    prompt_description=CHARACTER_PROMPT,
    examples=CHARACTER_EXAMPLES,
    extraction_passes=1,
    **config,
)

print(f"\nFound {len(result.extractions)} raw extractions:\n")
for i, ext in enumerate(result.extractions):
    attrs = ext.attributes or {}
    print(f"  {i+1}. {ext.extraction_text}")
    print(f"     class: {ext.extraction_class}")
    for k, v in attrs.items():
        print(f"     {k}: {v}")
    print()
