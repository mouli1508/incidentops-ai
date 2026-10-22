import argparse
from uuid import UUID

from app.investigation.service import investigate_ticket


def main():
    parser = argparse.ArgumentParser(
        description="Investigate an enterprise support ticket"
    )

    parser.add_argument(
        "ticket_id",
        type=UUID,
        help="UUID of the ticket to investigate",
    )

    args = parser.parse_args()

    try:
        result = investigate_ticket(args.ticket_id)

    except LookupError as exc:
        print(f"ERROR: {exc}")
        raise SystemExit(1) from exc

    print("\n" + "=" * 60)
    print("INCIDENTOPS AI — TICKET INVESTIGATION")
    print("=" * 60)

    print(f"\nTicket: {result.ticket_id}")
    print(f"Status: {result.status}")

    print("\nTicket Context:")
    for key, value in result.ticket_context.items():
        print(f"  {key}: {value}")

    print("\nAI Investigation:")
    print(result.summary)

    print("\nKnowledge Sources:")
    for source in result.sources:
        print(
            f"  [{source['source_id']}] "
            f"{source['document_title']} "
            f"(chunk {source['chunk_index']})"
        )

    print(
        "\nHuman review required. "
        "No ticket or incident records were modified."
    )


if __name__ == "__main__":
    main()
