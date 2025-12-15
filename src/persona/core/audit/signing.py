"""
HMAC-SHA256 signing for audit record integrity (F-123).

Optional cryptographic signing to verify record authenticity.
"""

import hmac
import json
from hashlib import sha256

from persona.core.audit.models import AuditRecord


def sign_record(record: AuditRecord, signing_key: str) -> str:
    """Generate HMAC-SHA256 signature for audit record.

    Args:
        record: Audit record to sign.
        signing_key: Secret key for HMAC.

    Returns:
        Hexadecimal signature string.
    """
    # Create canonical JSON representation (exclude signature field)
    record_dict = record.model_dump(exclude={"signature"}, mode="json")
    canonical_json = json.dumps(record_dict, sort_keys=True, separators=(",", ":"))

    # Generate HMAC-SHA256 signature
    signature = hmac.new(
        signing_key.encode("utf-8"),
        canonical_json.encode("utf-8"),
        sha256,
    ).hexdigest()

    return signature


def verify_signature(record: AuditRecord, signing_key: str) -> bool:
    """Verify HMAC-SHA256 signature of audit record.

    Args:
        record: Audit record to verify.
        signing_key: Secret key for HMAC.

    Returns:
        True if signature is valid, False otherwise.
    """
    if not record.signature:
        return False

    expected_signature = sign_record(record, signing_key)
    return hmac.compare_digest(record.signature, expected_signature)
