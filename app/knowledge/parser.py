import re


def normalize_text(content: str) -> str:
    if not isinstance(content, str):
        raise TypeError("Document content must be a string")

    # Standardize Windows, macOS, and Linux line endings.
    content = content.replace("\r\n", "\n").replace("\r", "\n")

    # Remove null bytes and non-printable control characters,
    # but retain newlines and tabs.
    content = "".join(
        character
        for character in content
        if character in ("\n", "\t")
        or (ord(character) >= 32 and ord(character) != 127)
    )

    # Remove trailing whitespace per line.
    lines = [line.rstrip() for line in content.split("\n")]
    content = "\n".join(lines)

    # Collapse excessive blank lines.
    content = re.sub(r"\n{3,}", "\n\n", content)

    content = content.strip()

    if not content:
        raise ValueError("Document is empty after normalization")

    return content
