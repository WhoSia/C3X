from __future__ import annotations
from typing import Any
import chess

def verified_line_evidence(board:chess.Board,candidate:dict[str,Any],max_plies:int=8)->dict[str,Any]|None:
    """Legally replay a bounded engine PV and report only directly verifiable line facts."""
    pv=list(candidate.get("pv_uci") or [])[:max_plies]
    if not pv:
        return None
    b=board.copy(stack=False);steps=[]
    for i,u in enumerate(pv):
        try:m=chess.Move.from_uci(u)
        except ValueError:return None
        if m not in b.legal_moves:
            return None
        san=b.san(m);capture=b.is_capture(m);check=b.gives_check(m)
        b.push(m)
        steps.append({"ply_offset":i,"uci":u,"san":san,"capture":capture,"check":check,"checkmate":b.is_checkmate()})
        if b.is_game_over(claim_draw=False):
            break
    if not steps:
        return None
    forcing=[s for s in steps if s["capture"] or s["check"] or s["checkmate"]]
    return {
        "schema":"c3x-verified-line-evidence-v1",
        "candidate_uci":candidate.get("uci"),
        "candidate_san":candidate.get("san"),
        "steps":steps,
        "forcing_steps":forcing,
        "all_moves_legally_replayed":True,
        "semantic_scope":"bounded_pv_line_fact_only",
    }

def line_sentence(e:dict[str,Any])->str:
    steps=e.get("steps") or []
    if not steps:return ""
    sans=" ".join(s["san"] for s in steps[:6])
    forcing=e.get("forcing_steps") or []
    if forcing:
        kinds=[]
        if any(s["checkmate"] for s in forcing):kinds.append("mate")
        if any(s["check"] for s in forcing):kinds.append("check")
        if any(s["capture"] for s in forcing):kinds.append("capture")
        return f"In the bounded verified principal variation, the line continues {sans}; the replay contains {', '.join(dict.fromkeys(kinds))}."
    return f"In the bounded verified principal variation, the legally replayed continuation is {sans}."
