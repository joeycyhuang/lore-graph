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
        "--model", "-m", default=None, help="Model ID (default: OLLAMA_MODEL env var or llama3.1:latest)"
    )
    parser.add_argument(
        "--model-url", default=None, help="Custom model endpoint URL (default: OLLAMA_BASE_URL env var or http://localhost:11434)"
    )
    parser.add_argument(
        "--demo", action="store_true", help="Demo mode: only process first ~10K chars per book"
    )
    args = parser.parse_args()

    model_id = args.model or os.getenv("OLLAMA_MODEL", "llama3.1:latest")
    model_url = args.model_url or os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    model_kwargs = {"model_id": model_id, "model_url": model_url}

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

        print(f"  Extracting characters using {model_id}...")
        characters = extract_characters(text, **model_kwargs)
        print(f"  Found {len(characters)} characters")
        all_characters.extend(characters)

        print(f"  Extracting relationships using {model_id}...")
        relationships = extract_relationships(text, **model_kwargs)
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
