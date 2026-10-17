
# CM Enterprise — VPN Troubleshooting Runbook

Document Owner: Enterprise Network Operations
Category: VPN / Network Connectivity
Severity: SEV3
Last Reviewed: 2026-10-01

## 1. Purpose

This runbook provides troubleshooting instructions for
employees experiencing corporate VPN connectivity failures.

## 2. Common Symptoms

- VPN error 809 during connection establishment.
- Authentication succeeds but VPN tunnel fails.
- Corporate resources are inaccessible.
- VPN connection times out.
- Intermittent connection failures after network changes.

## 3. Initial Investigation

### Step 1: Verify Internet Connectivity

Confirm the employee can access external websites.

If internet connectivity is unavailable, troubleshoot
the local network before investigating the VPN service.

### Step 2: Check VPN Gateway Health

Verify the enterprise VPN gateway is operational.

Review gateway monitoring dashboards and recent
infrastructure alerts.

### Step 3: Validate DNS Resolution

Confirm the corporate VPN hostname resolves to
the expected gateway endpoint.

Example command:

nslookup vpn.cmenterprise.example

### Step 4: Inspect Network and Firewall Settings

Verify that the required VPN transport protocols
are permitted by the employee's network.

For IKEv2/IPsec environments, confirm UDP ports
500 and 4500 are not blocked.

Required ports depend on the actual VPN configuration.

### Step 5: Review Authentication

Check identity-provider authentication logs.

Determine whether authentication failures are caused by:

- Expired credentials.
- MFA failures.
- Conditional-access restrictions.
- Account lockouts.

## 4. Incident Correlation

Before creating a major incident, inspect recent
support tickets for similar symptoms.

If multiple employees are experiencing the same
VPN connectivity problem, investigate whether
the issue is enterprise-wide.

## 5. Escalation

Escalate to Enterprise Network Operations when:

- The VPN gateway is unavailable.
- Multiple employees report identical failures.
- Authentication services are degraded.
- Network connectivity failures persist after
  standard troubleshooting.

## 6. Security Requirements

Never request employee passwords or MFA recovery codes.

Do not disable endpoint protection to troubleshoot VPN.

Do not modify production gateway configurations
without appropriate authorization.

## 7. Resolution Verification

Confirm the employee can:

1. Authenticate successfully.
2. Establish a VPN tunnel.
3. Access authorized corporate resources.
4. Maintain a stable connection.
```

This is synthetic enterprise documentation, intentionally written like an internal IT runbook.

Later, our AI investigator will use this information to justify recommendations instead of generating generic troubleshooting instructions.

## 10. Run the ingestion pipeline

Make sure PostgreSQL is running:

```powershell
cd D:\work\incidentops-ai
docker compose up -d
.\.venv\Scripts\Activate.ps1
```

Execute ingestion:

```powershell
python -u -m scripts.ingest_knowledge
```

Expected output (chunk count depends on the exact text):

```text
Found 1 documents
INFO: Ingested knowledge://runbooks/vpn_troubleshooting.md (N chunks)
[INGESTED] runbooks\vpn_troubleshooting.md

Ingestion summary
Ingested: 1
Skipped:  0
Failed:   0
```

### Verify in PostgreSQL

Open the PostgreSQL command-line interface:

```powershell
docker compose exec postgres psql -U incidentops -d incidentops
```

Check stored documents:

```sql
SELECT
    title,
    source_uri,
    source_type,
    status,
    content_hash
FROM knowledge_documents;
```

Check chunks:

```sql
SELECT
    chunk_index,
    LEFT(content, 100) AS preview,
    token_count
FROM knowledge_chunks
ORDER BY chunk_index;
```

Now run the same ingestion command again:

```powershell
python -u -m scripts.ingest_knowledge
```

Expected result:

```text
Found 1 documents
[SKIPPED] runbooks\vpn_troubleshooting.md

Ingestion summary
Ingested: 0
Skipped:  1
Failed:   0
```

This verifies basic idempotency.

### Test document updates

Open `vpn_troubleshooting.md` and add a new section describing a troubleshooting step.

Run ingestion again. The result should return to `[INGESTED]`.

The system should update the stored document hash and replace its chunks without creating another `knowledge_documents` row.

## 11. Add automated unit tests

Create `tests/test_knowledge_processing.py`.

These tests do not require PostgreSQL. They validate the file loader, parser, and chunker independently.

<CodeBlock language="python" editable>
import pytest

from app.knowledge.loader import (
    discover_documents,
    load_document,
)
from app.knowledge.parser import normalize_text
from app.knowledge.chunker import split_into_chunks


def test_document_loading(tmp_path):
    runbooks = tmp_path / "runbooks"
    runbooks.mkdir()

    file_path = runbooks / "vpn_guide.md"
    file_path.write_text(
        "# VPN Guide\n\nCheck gateway status.",
        encoding="utf-8",
    )

    document = load_document(file_path, tmp_path)

    assert document.source_uri == "knowledge://runbooks/vpn_guide.md"
    assert document.source_type == "runbook"
    assert "Check gateway status" in document.content


def test_document_discovery(tmp_path):
    (tmp_path / "guide.md").write_text("Valid content")
    (tmp_path / "ignore.csv").write_text("Not supported")

    documents = discover_documents(tmp_path)

    assert len(documents) == 1
    assert documents[0].name == "guide.md"


def test_normalization():
    content = "First line\r\n\r\n\r\nSecond line  \r\n"

    result = normalize_text(content)

    assert result == "First line\n\nSecond line"


def test_empty_document():
    with pytest.raises(ValueError):
        normalize_text("   \n\n   ")


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


def test_small_document():
    chunks = split_into_chunks(
        "Short troubleshooting guide",
        chunk_size=1000,
    )

    assert chunks == ["Short troubleshooting guide"]


def test_invalid_chunk_configuration():
    with pytest.raises(ValueError):
        split_into_chunks(
            "Sample content",
            chunk_size=100,
            overlap=100,
        )


def test_invalid_utf8(tmp_path):
    file_path = tmp_path / "invalid.txt"
    file_path.write_bytes(b"\xff\xfe\xff")

    with pytest.raises(ValueError, match="Invalid UTF-8"):
        load_document(file_path, tmp_path)
