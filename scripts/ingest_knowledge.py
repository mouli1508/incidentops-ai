
import argparse
import logging
from pathlib import Path

from app.knowledge.ingestion import ingest_document
from app.knowledge.loader import discover_documents


DEFAULT_ROOT = Path("data/knowledge")


def main():
    parser = argparse.ArgumentParser(
        description="Ingest enterprise knowledge into PostgreSQL"
    )

    parser.add_argument(
        "--root",
        type=Path,
        default=DEFAULT_ROOT,
        help="Root directory containing knowledge files",
    )

    args = parser.parse_args()
    root = args.root.resolve()

    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s: %(message)s",
    )

    if not root.exists() or not root.is_dir():
        raise SystemExit(
            f"Knowledge directory not found: {root}"
        )

    documents = discover_documents(root)

    print(f"Found {len(documents)} documents")

    counts = {
        "ingested": 0,
        "skipped": 0,
        "failed": 0,
    }

    for path in documents:
        try:
            result = ingest_document(path, root)

            counts[result] += 1

            print(
                f"[{result.upper()}] "
                f"{path.relative_to(root)}"
            )

        except Exception as exc:
            counts["failed"] += 1

            print(
                f"[FAILED] {path.name}: {exc}"
            )

    print("\nIngestion summary")
    print(f"Ingested: {counts['ingested']}")
    print(f"Skipped:  {counts['skipped']}")
    print(f"Failed:   {counts['failed']}")

    if counts["failed"] > 0:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
