
from dataclasses import dataclass
from pathlib import Path


SUPPORTED_EXTENSIONS = {".md", ".txt"}
MAX_FILE_BYTES = 5 * 1024 * 1024  # 5 MB


@dataclass(frozen=True)
class LoadedDocument:
    title: str
    source_uri: str
    source_type: str
    content: str
    raw_bytes: bytes


def discover_documents(root: Path) -> list[Path]:
    root = root.resolve(strict=True)

    if not root.is_dir():
        raise ValueError(f"Not a directory: {root}")

    files = []

    for path in root.rglob("*"):
        if path.is_symlink():
            continue

        if not path.is_file():
            continue

        if path.suffix.lower() not in SUPPORTED_EXTENSIONS:
            continue

        files.append(path)

    return sorted(files)


def load_document(path: Path, root: Path) -> LoadedDocument:
    root = root.resolve(strict=True)

    # Reject symlinks and paths escaping the knowledge root.
    if path.is_symlink():
        raise ValueError(f"Symlink not supported: {path}")

    path = path.resolve(strict=True)
    relative_path = path.relative_to(root)

    if path.suffix.lower() not in SUPPORTED_EXTENSIONS:
        raise ValueError(f"Unsupported file type: {path.suffix}")

    if not path.is_file():
        raise ValueError(f"Not a file: {path}")

    if path.stat().st_size > MAX_FILE_BYTES:
        raise ValueError(f"File exceeds 5 MB limit: {path}")

    raw_bytes = path.read_bytes()

    if len(raw_bytes) > MAX_FILE_BYTES:
        raise ValueError(f"File exceeds 5 MB limit: {path}")

    try:
        content = raw_bytes.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise ValueError(f"Invalid UTF-8 document: {path}") from exc

    return LoadedDocument(
        title=path.stem.replace("_", " ").replace("-", " ").title(),
        source_uri=f"knowledge://{relative_path.as_posix()}",
        source_type="runbook" if "runbooks" in relative_path.parts
            else "knowledge_article",
        content=content,
        raw_bytes=raw_bytes,
    )
