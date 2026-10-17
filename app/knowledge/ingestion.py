
import hashlib
import logging
from pathlib import Path

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.db.models import KnowledgeChunk, KnowledgeDocument
from app.db.session import SessionLocal
from app.knowledge.chunker import count_approx_tokens, split_into_chunks
from app.knowledge.loader import load_document
from app.knowledge.parser import normalize_text


logger = logging.getLogger(__name__)


def ingest_document(path: Path, root: Path) -> str:
    loaded = load_document(path, root)

    content_hash = hashlib.sha256(loaded.raw_bytes).hexdigest()

    with SessionLocal() as db:
        try:
            result = persist_document(db, loaded, content_hash)
            db.commit()
            return result

        except Exception:
            db.rollback()
            logger.exception(
                "Failed to ingest %s",
                loaded.source_uri,
            )
            record_failed_document(db, loaded)
            raise


def persist_document(
    db: Session,
    loaded,
    content_hash: str,
) -> str:
    document = db.scalar(
        select(KnowledgeDocument)
        .where(KnowledgeDocument.source_uri == loaded.source_uri)
        .with_for_update()
    )

    if (
        document is not None
        and document.content_hash == content_hash
        and document.status == "ready"
    ):
        return "skipped"

    # Prepare all content before modifying persisted chunks.
    normalized = normalize_text(loaded.content)

    chunks = split_into_chunks(normalized)

    if not chunks:
        raise ValueError("No valid chunks generated")

    if document is None:
        document = KnowledgeDocument(
            title=loaded.title,
            source_uri=loaded.source_uri,
            source_type=loaded.source_type,
            status="pending",
        )
        db.add(document)
        db.flush()

    document.status = "processing"

    # Replace previous content only within the same transaction.
    db.execute(
        delete(KnowledgeChunk)
        .where(KnowledgeChunk.document_id == document.id)
    )

    for index, content in enumerate(chunks):
        db.add(
            KnowledgeChunk(
                document_id=document.id,
                chunk_index=index,
                content=content,
                token_count=count_approx_tokens(content),
                chunk_metadata={
                    "source_uri": loaded.source_uri,
                    "source_type": loaded.source_type,
                    "chunking_strategy": "character_v1",
                },
            )
        )

    document.title = loaded.title
    document.source_type = loaded.source_type
    document.content_hash = content_hash
    document.status = "ready"

    logger.info(
        "Ingested %s (%d chunks)",
        loaded.source_uri,
        len(chunks),
    )

    return "ingested"


def record_failed_document(db: Session, loaded) -> None:
    """
    Best-effort failure tracking.

    Preserve a previously ready version if a replacement fails.
    """
    try:
        document = db.scalar(
            select(KnowledgeDocument)
            .where(KnowledgeDocument.source_uri == loaded.source_uri)
            .with_for_update()
        )

        if document is None:
            document = KnowledgeDocument(
                title=loaded.title,
                source_uri=loaded.source_uri,
                source_type=loaded.source_type,
                status="failed",
            )
            db.add(document)

        elif document.status != "ready":
            document.status = "failed"

        db.commit()

    except Exception:
        db.rollback()
        logger.exception(
            "Could not record ingestion failure for %s",
            loaded.source_uri,
        )
