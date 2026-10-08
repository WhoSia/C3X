"""Fail-closed certificate file admission for the user-facing C3X commentary CLI.

Only a repository-reviewed, exact-byte file on the allowlist may become a
candidate causal certificate. This checks provenance admission, not scientific
truth; no C3X 0.12 certificates are approved at initial release.
"""
from __future__ import annotations
import hashlib
import json
import re
from pathlib import Path
from typing import Any

SCHEMA="c3x-012-causal-certificate-trust-manifest-v1"
APPROVED="ADMITTED_BOUNDED_LOCAL_C3X_CAUSAL"
SHA256=re.compile(r"[0-9a-f]{64}\Z")
MANIFEST=Path(__file__).resolve().parents[1]/"c3x"/"ontology"/"c3x-012-causal-certificate-trust.json"

def _certificates(value: Any)->list[dict[str,Any]]:
    if isinstance(value,dict) and isinstance(value.get("causal_explanation_certificates"),list):
        value=value["causal_explanation_certificates"]
    elif not isinstance(value,list):
        value=[value]
    if not value or any(not isinstance(item,dict) for item in value):
        raise ValueError("INVALID_CAUSAL_CERTIFICATE_PAYLOAD")
    return value

def admitted_certificates(paths:list[str],manifest_path:Path|None=None)->list[dict[str,Any]]:
    """Read and admit exact-byte human-reviewed certificates, or raise.

    manifest_path injection is for testability. The public CLI never accepts
    a caller-supplied trust-store path; it uses the repository-owned manifest.
    """
    if not paths:
        return []
    trusted=Path(manifest_path) if manifest_path is not None else MANIFEST
    try:
        conf=json.loads(trusted.read_text(encoding="utf-8"))
    except (OSError,json.JSONDecodeError) as exc:
        raise ValueError("CAUSAL_TRUST_MANIFEST_UNAVAILABLE") from exc
    if not isinstance(conf,dict) or conf.get("schema")!=SCHEMA or not isinstance(conf.get("approved"),list):
        raise ValueError("INVALID_CAUSAL_TRUST_MANIFEST")
    approved={}
    for item in conf["approved"]:
        if not isinstance(item,dict):
            raise ValueError("INVALID_CAUSAL_TRUST_ENTRY")
        digest=item.get("sha256")
        ids=item.get("certificate_ids")
        stage=item.get("scientific_stage")
        receipt=item.get("review_receipt_sha256")
        if (not isinstance(digest,str) or not SHA256.fullmatch(digest)
            or not isinstance(ids,list) or not ids
            or any(not isinstance(x,str) or not x for x in ids)
            or len(ids)!=len(set(ids))
            or not isinstance(stage,str) or not stage
            or not isinstance(receipt,str) or not SHA256.fullmatch(receipt)
            or item.get("status")!=APPROVED or digest in approved):
            raise ValueError("INVALID_CAUSAL_TRUST_ENTRY")
        approved[digest]=item
    out=[]
    seen_files=set()
    seen_ids=set()
    for rawpath in paths:
        path=Path(rawpath)
        try:
            blob=path.read_bytes()
        except OSError as exc:
            raise ValueError("CAUSAL_CERTIFICATE_FILE_UNREADABLE") from exc
        digest=hashlib.sha256(blob).hexdigest()
        if digest in seen_files:
            raise ValueError("DUPLICATE_CAUSAL_CERTIFICATE_FILE")
        item=approved.get(digest)
        if item is None:
            raise ValueError("UNREVIEWED_CAUSAL_CERTIFICATE_FILE:"+digest)
        try:
            records=_certificates(json.loads(blob.decode("utf-8-sig")))
        except (UnicodeError,json.JSONDecodeError) as exc:
            raise ValueError("INVALID_CAUSAL_CERTIFICATE_JSON") from exc
        ids=[z.get("certificate_id") for z in records]
        if (any(not isinstance(i,str) or not i for i in ids) or len(ids)!=len(set(ids))
            or sorted(ids)!=sorted(item["certificate_ids"])
            or any(z.get("scientific_stage")!=item["scientific_stage"] for z in records)):
            raise ValueError("CAUSAL_CERTIFICATE_MANIFEST_IDENTITY_MISMATCH")
        if any(i in seen_ids for i in ids):
            raise ValueError("DUPLICATE_CAUSAL_CERTIFICATE_ID")
        seen_files.add(digest)
        seen_ids.update(ids)
        out.extend(records)
    return out
