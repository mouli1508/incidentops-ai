
import pytest

from app.knowledge.loader import (
    discover_documents,
    load_document,
)
from app.knowledge.parser import normalize_text
from app.knowledge.chunker import split_into_chunks


# --------------------------------------------------
# Test 1: Load a valid Markdown document
# --------------------------------------------------
def test_document_loading(tmp_path):
    runbooks = tmp_path / "runbooks"
    runbooks.mkdir()

    file_path = runbooks / "vpn_guide.md"
    file_path.write_text(
        "# VPN Guide\n\nCheck gateway status.",
        encoding="utf-8",
    )

    document = load_document(file_path, tmp_path)

    assert document.title == "Vpn Guide"
    assert document.source_uri == "knowledge://runbooks/vpn_guide.md"
    assert document.source_type == "runbook"
    assert "Check gateway status" in document.content


# --------------------------------------------------
# Test 2: Discover only supported documents
# --------------------------------------------------
def test_document_discovery(tmp_path):
    (tmp_path / "guide.md").write_text(
        "Valid Markdown content",
        encoding="utf-8",
    )

    (tmp_path / "notes.txt").write_text(
        "Valid text content",
        encoding="utf-8",
    )

    (tmp_path / "ignore.csv").write_text(
        "Unsupported content",
        encoding="utf-8",
    )

    documents = discover_documents(tmp_path)

    assert len(documents) == 2
    assert {path.name for path in documents} == {
        "guide.md",
        "notes.txt",
    }


# --------------------------------------------------
# Test 3: Normalize text and line endings
# --------------------------------------------------
def test_normalization():
    content = "First line\r\n\r\n\r\nSecond line  \r\n"

    result = normalize_text(content)

    assert result == "First line\n\nSecond line"


# --------------------------------------------------
# Test 4: Reject empty documents
# --------------------------------------------------
def test_empty_document():
    with pytest.raises(ValueError, match="empty"):
        normalize_text("   \n\n   ")


# --------------------------------------------------
# Test 5: Split large documents into chunks
# --------------------------------------------------
def test_chunking():
    content = "VPN gateway authentication connectivity " * 100

    chunks = split_into_chunks(
        content,
        chunk_size=200,
        overlap=30,
    )

    assert len(chunks) > 1
    assert all(chunk for chunk in chunks)
    assert all(len(chunk) <= 200 for chunk in chunks)


# --------------------------------------------------
# Test 6: Keep small documents as a single chunk
# --------------------------------------------------
def test_small_document():
    chunks = split_into_chunks(
        "Short troubleshooting guide",
        chunk_size=1000,
    )

    assert chunks == ["Short troubleshooting guide"]


# --------------------------------------------------
# Test 7: Reject invalid chunk configuration
# --------------------------------------------------
def test_invalid_chunk_configuration():
    with pytest.raises(ValueError):
        split_into_chunks(
            "Sample content",
            chunk_size=100,
            overlap=100,
        )


# --------------------------------------------------
# Test 8: Reject files that are not valid UTF-8
# --------------------------------------------------
def test_invalid_utf8(tmp_path):
    file_path = tmp_path / "invalid.txt"
    file_path.write_bytes(b"\xff\xfe\xff")

    with pytest.raises(ValueError, match="Invalid UTF-8"):
        load_document(file_path, tmp_path)
