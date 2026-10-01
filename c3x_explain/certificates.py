from __future__ import annotations
from typing import Any

CAUSAL_PROVENANCE="C3X_CAUSAL_CONTRAST"

def _board_key(fen: str | None)->str|None:
    if not fen:
        return None
    parts=str(fen).split()
    return " ".join(parts[:4]) if len(parts)>=4 else None

def normalize_certificate(c:dict[str,Any], expected_fen:str|None=None)->dict[str,Any]:
    """Normalize a C3X certificate without enlarging its scientific authority."""
    cid=c.get("certificate_id") or c.get("receipt_sha256")
    if not cid:
        raise ValueError("C3X certificate missing certificate_id/receipt_sha256")
    fen=c.get("position_fen") or c.get("fen") or c.get("original_fen")
    if expected_fen and fen and _board_key(fen)!=_board_key(expected_fen):
        raise ValueError("C3X certificate position mismatch")
    pair=c.get("pair") or c.get("pair_id")
    bound=c.get("bound")
    if not pair or not bound:
        raise ValueError("C3X certificate missing pair/bound")
    atoms=c.get("engine_relative_atoms")
    family=c.get("family")
    if family is None and atoms:
        family="+".join(str(x) for x in atoms)
    return {
        "schema":"c3x-causal-certificate-object-v1",
        "certificate_id":str(cid),
        "source_schema":c.get("schema"),
        "position_key":_board_key(fen or expected_fen),
        "engine":c.get("engine"),
        "pair":pair,
        "bound":bound,
        "family":family,
        "collapse_to":c.get("collapse_to"),
        "structural_signature":c.get("structural_signature"),
        "replication_status":c.get("replication_status"),
        "authority":"engine_preference_causality",
        "authority_ceiling":c.get("authority_ceiling"),
        "g10_scope":c.get("g10_scope"),
        "g10_transportable_law":c.get("g10_transportable_law"),
        "chess_native_consequence":c.get("g10_chess_native_consequence"),
        "provenance_class":CAUSAL_PROVENANCE,
    }

def certificate_claim(c:dict[str,Any], expected_fen:str|None=None)->dict[str,Any]:
    n=normalize_certificate(c,expected_fen)
    return {
        "pair":n["pair"],
        "bound":n["bound"],
        "family":n["family"],
        "collapse_to":n["collapse_to"],
        "certificate_id":n["certificate_id"],
        "chess_native_consequence":n.get("chess_native_consequence"),
        "certificate":n,
    }
