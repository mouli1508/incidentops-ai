import re


def count_approx_tokens(text: str) -> int:
    """
    Approximate token count, not a model-specific tokenizer.
    """
    return len(re.findall(r"\w+|[^\w\s]", text))


def split_into_chunks(
    text: str,
    chunk_size: int = 1000,
    overlap: int = 150,
) -> list[str]:
    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive")

    if overlap < 0 or overlap >= chunk_size:
        raise ValueError("overlap must be >= 0 and < chunk_size")

    if not text.strip():
        return []

    chunks = []
    start = 0

    while start < len(text):
        end = min(start + chunk_size, len(text))

        # Prefer to split at a whitespace boundary.
        if end < len(text):
            boundary = text.rfind(
                " ",
                start + chunk_size // 2,
                end,
            )
            if boundary > start:
                end = boundary + 1

        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        if end >= len(text):
            break

        # Guarantee forward progress.
        start = max(start + 1, end - overlap)

    return chunks
