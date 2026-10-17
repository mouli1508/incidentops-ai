
import argparse

from app.knowledge.search import search_knowledge


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("query")
    parser.add_argument("--limit", type=int, default=3)

    args = parser.parse_args()

    results = search_knowledge(
        query=args.query,
        limit=args.limit,
    )

    if not results:
        print("No matching chunks found.")
        return

    for i, result in enumerate(results, start=1):
        print(f"\nResult {i}")
        print(f"Document: {result['document_title']}")
        print(f"Source: {result['source_uri']}")
        print(f"Similarity: {result['similarity']}")
        print(f"Content:\n{result['content'][:500]}")
        print("-" * 60)


if __name__ == "__main__":
    main()
