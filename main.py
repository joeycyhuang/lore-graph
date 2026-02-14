"""CLI entry point for Warhammer 40k character relationship extraction."""

import argparse
import os

from dotenv import load_dotenv

from extract import (
    extract_text_from_pdf,
    extract_characters,
    extract_relationships,
    deduplicate_characters,
    build_graph_data,
    write_graph_json,
)


def main():
    load_dotenv()

    parser = argparse.ArgumentParser(
        description="Extract character relationships from Warhammer 40k PDFs"
    )
    parser.add_argument("pdf", help="Path to the PDF file to process")
    parser.add_argument(
        "--output", "-o", default="data.json", help="Output JSON path (default: data.json)"
    )
    parser.add_argument(
        "--model", "-m", default=None, help="Model ID (default: OLLAMA_MODEL env var or llama3.1:latest)"
    )
    parser.add_argument(
        "--model-url", default=None, help="Custom model endpoint URL (default: OLLAMA_BASE_URL env var or http://localhost:11434)"
    )
    parser.add_argument(
        "--demo", action="store_true", help="Demo mode: only process first ~100K chars"
    )
    args = parser.parse_args()

    # Resolve from env vars, CLI flags take precedence
    model_id = args.model or os.getenv("OLLAMA_MODEL", "llama3.1:latest")
    model_url = args.model_url or os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

    print(f"Reading PDF: {args.pdf}")
    text = extract_text_from_pdf(args.pdf)
    if args.demo:
        text = text[:10000]
        print(f"Demo mode: using first {len(text)} characters of text")
    else:
        print(f"Extracted {len(text)} characters of text")

    model_kwargs = {"model_id": model_id, "model_url": model_url}

    print(f"Extracting characters using {model_id}...")
    characters = extract_characters(text, **model_kwargs)
    print(f"Found {len(characters)} raw characters")

    print("Deduplicating characters...")
    characters = deduplicate_characters(characters)
    print(f"Deduplicated to {len(characters)} unique characters")

    # Write characters immediately (no relationships yet)
    graph = build_graph_data(characters, [])
    write_graph_json(graph, args.output)
    print(f"Wrote {len(characters)} characters to {args.output} (extracting relationships...)")

    print(f"Extracting relationships using {model_id}...")
    relationships = extract_relationships(text, **model_kwargs)
    print(f"Found {len(relationships)} relationships")

    # Update with relationships
    graph = build_graph_data(characters, relationships)
    write_graph_json(graph, args.output)

    print("Done! Open index.html to view the graph.")


if __name__ == "__main__":
    main()
