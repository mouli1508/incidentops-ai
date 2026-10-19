
import argparse

from app.ai.rag import ask_knowledge


def main():
    parser = argparse.ArgumentParser(
        description="Ask questions using enterprise knowledge"
    )

    parser.add_argument(
        "question",
        type=str,
        help="IT troubleshooting question",
    )

    parser.add_argument(
        "--limit",
        type=int,
        default=4,
        help="Maximum retrieved chunks",
    )

    args = parser.parse_args()

    result = ask_knowledge(
        question=args.question,
        limit=args.limit,
    )

    print("\n" + "=" * 60)
    print("INCIDENTOPS AI - KNOWLEDGE ASSISTANT")
    print("=" * 60)

    print(f"\nQuestion: {result.question}")
    print(f"\nAI Answer:\n{result.answer}")

    print("\nRetrieved Evidence:")

    if not result.sources:
        print("No sources found.")
        return

    for source in result.sources:
        print(
            f"\n[{source['source_id']}] "
            f"{source['document_title']}"
        )
        print(f"URI: {source['source_uri']}")
        print(f"Chunk: {source['chunk_index']}")
        print(f"Similarity: {source['similarity']}")

    print("\nAnswer grounding has not yet been verified.")


if __name__ == "__main__":
    main()
