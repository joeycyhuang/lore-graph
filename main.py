"""CLI entry point for Warhammer 40k character relationship extraction."""

import argparse
import glob
import os
import sys

from dotenv import load_dotenv

from extract import (
    extract_text_from_pdf,
    extract_characters,
    extract_relationships,
    deduplicate_characters,
    build_graph_data,
    build_provider_config,
    write_graph_json,
)


def _resolve_pdfs(path: str) -> list[str]:
    """Resolve a file or directory path to a sorted list of PDF paths."""
    if os.path.isdir(path):
        pdfs = sorted(glob.glob(os.path.join(path, "*.pdf")))
        if not pdfs:
            print(f"Error: No PDF files found in {path}", file=sys.stderr)
            sys.exit(1)
        return pdfs
    return [path]


def main():
    load_dotenv()

    parser = argparse.ArgumentParser(
        description="Extract character relationships from Warhammer 40k PDFs"
    )
    parser.add_argument("pdf", help="Path to a PDF file or directory of PDFs")
    parser.add_argument(
        "--output", "-o", default="data/data.json", help="Output JSON path (default: data/data.json)"
    )
    parser.add_argument(
        "--model", "-m", default=None, help="Model ID (default depends on provider)"
    )
    parser.add_argument(
        "--provider", default="ollama", choices=["ollama", "ollama-cloud", "gemini"],
        help="Model provider (default: ollama)"
    )
    parser.add_argument(
        "--provider-url", default=None, help="Override provider endpoint URL (only for ollama-cloud)"
    )
    parser.add_argument(
        "--demo", action="store_true", help="Demo mode: only process first ~10K chars per book"
    )
    args = parser.parse_args()

    # Provider-specific default models
    default_models = {
        "ollama": "llama3.1:latest",
        "ollama-cloud": "llama3.1:latest",
        "gemini": "gemini-2.0-flash",
    }
    model_id = args.model or os.getenv("OLLAMA_MODEL", default_models[args.provider])

    # Validate required env vars per provider
    if args.provider == "ollama-cloud" and not os.getenv("OLLAMA_API_KEY"):
        print("Error: OLLAMA_API_KEY env var is required for ollama-cloud provider", file=sys.stderr)
        sys.exit(1)
    if args.provider == "gemini" and not os.getenv("GEMINI_API_KEY"):
        print("Error: GEMINI_API_KEY env var is required for gemini provider", file=sys.stderr)
        sys.exit(1)

    config = build_provider_config(args.provider, model_id, provider_url=args.provider_url)

    pdfs = _resolve_pdfs(args.pdf)
    all_characters = []
    all_relationships = []

    for i, pdf_path in enumerate(pdfs, 1):
        book_name = os.path.basename(pdf_path)
        print(f"\nProcessing book {i}/{len(pdfs)}: {book_name}")

        text = extract_text_from_pdf(pdf_path)
        if args.demo:
            text = text[:10000]
            print(f"  Demo mode: using first {len(text)} characters")
        else:
            print(f"  Extracted {len(text)} characters of text")

        print(f"  Extracting characters using {args.provider}/{model_id}...")
        characters = extract_characters(text, config)
        print(f"  Found {len(characters)} characters")
        all_characters.extend(characters)

        print(f"  Extracting relationships using {args.provider}/{model_id}...")
        relationships = extract_relationships(text, config)
        print(f"  Found {len(relationships)} relationships")
        all_relationships.extend(relationships)

    print(f"\nDeduplicating {len(all_characters)} characters across {len(pdfs)} book(s)...")
    all_characters = deduplicate_characters(all_characters)
    print(f"Deduplicated to {len(all_characters)} unique characters")

    graph = build_graph_data(all_characters, all_relationships)
    write_graph_json(graph, args.output)

    print("Done! Open index.html to view the graph.")


if __name__ == "__main__":
    main()
