
from sqlalchemy import select

from app.db.models import KnowledgeChunk
from app.db.session import SessionLocal
from app.knowledge.embeddings import embed_texts


BATCH_SIZE = 32


def main():
    total = 0

    with SessionLocal() as db:
        while True:
            chunks = db.scalars(
                select(KnowledgeChunk)
                .where(KnowledgeChunk.embedding.is_(None))
                .order_by(KnowledgeChunk.created_at, KnowledgeChunk.id)
                .limit(BATCH_SIZE)
            ).all()

            if not chunks:
                break

            vectors = embed_texts(
                [chunk.content for chunk in chunks]
            )

            for chunk, vector in zip(chunks, vectors):
                chunk.embedding = vector

            db.commit()

            total += len(chunks)
            print(f"Embedded {total} chunks")

    print(f"Completed. Total embedded: {total}")


if __name__ == "__main__":
    main()
