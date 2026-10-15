
from uuid import uuid4

from sqlalchemy import select, func

from app.db.models import KnowledgeDocument, KnowledgeChunk
from app.db.session import SessionLocal


def main():
    source_uri = f"test://vpn-runbook-{uuid4()}"

    with SessionLocal() as db:
        try:
            # 1. Create knowledge document
            document = KnowledgeDocument(
                title="VPN Troubleshooting Runbook",
                source_uri=source_uri,
                source_type="runbook",
                status="pending",
            )

            db.add(document)
            db.flush()

            print(f"Created document: {document.id}")

            # 2. Create two chunks
            chunk_1 = KnowledgeChunk(
                document_id=document.id,
                chunk_index=0,
                content="VPN error 809 indicates a connectivity problem.",
                token_count=9,
                chunk_metadata={"section": "symptoms"},
            )

            chunk_2 = KnowledgeChunk(
                document_id=document.id,
                chunk_index=1,
                content="Verify the VPN gateway and firewall configuration.",
                token_count=9,
                chunk_metadata={"section": "resolution"},
            )

            db.add_all([chunk_1, chunk_2])

            # 3. Mark document ready
            document.status = "ready"

            db.commit()

            # 4. Read document and its chunks
            stored_document = db.scalar(
                select(KnowledgeDocument).where(
                    KnowledgeDocument.source_uri == source_uri
                )
            )

            assert stored_document is not None
            assert stored_document.status == "ready"

            chunks = db.scalars(
                select(KnowledgeChunk)
                .where(
                    KnowledgeChunk.document_id == stored_document.id
                )
                .order_by(KnowledgeChunk.chunk_index)
            ).all()

            assert len(chunks) == 2

            print(f"Document status: {stored_document.status}")
            print(f"Retrieved chunks: {len(chunks)}")

            for chunk in chunks:
                print(f"Chunk {chunk.chunk_index}: {chunk.content}")

            # 5. Verify cascade deletion
            document_id = stored_document.id

            db.delete(stored_document)
            db.commit()

            remaining = db.scalar(
                select(func.count())
                .select_from(KnowledgeChunk)
                .where(KnowledgeChunk.document_id == document_id)
            )

            assert remaining == 0

            print("Cascade deletion verified.")
            print("Knowledge database test PASSED.")

        except Exception:
            db.rollback()
            raise

        finally:
            # Clean up test document if an assertion failed
            test_document = db.scalar(
                select(KnowledgeDocument).where(
                    KnowledgeDocument.source_uri == source_uri
                )
            )

            if test_document is not None:
                db.delete(test_document)
                db.commit()


if __name__ == "__main__":
    main()
