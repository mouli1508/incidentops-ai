
from sqlalchemy import select

from app.db.models import KnowledgeChunk, KnowledgeDocument
from app.db.session import SessionLocal
from app.knowledge.embeddings import embed_query


def search_knowledge(query: str, limit: int = 5) -> list[dict]:
    if not 1 <= limit <= 20:
        raise ValueError("limit must be between 1 and 20")

    query_vector = embed_query(query)

    distance = KnowledgeChunk.embedding.cosine_distance(
        query_vector
    )

    with SessionLocal() as db:
        rows = db.execute(
            select(
                KnowledgeChunk,
                KnowledgeDocument.title,
                KnowledgeDocument.source_uri,
                distance.label("distance"),
            )
            .join(
                KnowledgeDocument,
                KnowledgeChunk.document_id == KnowledgeDocument.id,
            )
            .where(
                KnowledgeChunk.embedding.is_not(None),
                KnowledgeDocument.status == "ready",
            )
            .order_by(distance)
            .limit(limit)
        ).all()

        return [
            {
                "document_title": title,
                "source_uri": source_uri,
                "chunk_index": chunk.chunk_index,
                "content": chunk.content,
                "similarity": round(1 - float(score), 4),
            }
            for chunk, title, source_uri, score in rows
        ]
