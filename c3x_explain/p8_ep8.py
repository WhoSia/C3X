"""Read-only, non-causal EP8 engine observation adapter for the PGN commentator.

This adapter deliberately never emits C3X_CAUSAL_CONTRAST.
Its input is an experimental result, not a signed independent causal certificate.
"""
from __future__ import annotations

SCHEMA="c3x-013-p8-ep8-three-arm-conditional-reply-v2"
STATUS="DEVELOPMENTAL_REAL_ENGINE_COMPARISON_NOT_CAUSAL"
PROVENANCE="CONVENTIONAL_HEURISTIC_COMMENTARY"
ENGINES=("Stockfish","Ethereal_classical")

def observation_index(packets):
    result={}
    for p in packets:
        if p.get("schema")!=SCHEMA or p.get("status")!=STATUS:
            raise ValueError("P8 EP8 observation schema/status authority mismatch")
        source=p.get("source") or {}
        if source.get("rank")!=111 or source.get("ply")!=48 or not source.get("game_url"):
            raise ValueError("P8 EP8 original source/provenance missing")
        if set(p.get("engines") or {})!=set(ENGINES):
            raise ValueError("P8 EP8 must retain both independent engine implementations")
        fen=p.get("root_fen")
        if not isinstance(fen,str) or len(fen.split())!=6:
            raise ValueError("P8 EP8 missing full six-field root FEN")
        result.setdefault(fen,[]).append(p)
    return result

def _stable(entries,depth,branch,arm):
    vals=[]
    for t in entries:
        item=t["branches"][branch][arm]
        if item.get("depth_completed") != (depth-1 if arm=="cold_equal_FEN_after_capture_depth_minus_one" else depth):
            return None
        if item.get("mate_white") is not None or item.get("score_white_cp") is None:
            return None
        vals.append((item["score_white_cp"],item.get("first_move")))
    return vals[0] if len(vals)==2 and vals[0]==vals[1] else None

def observation_atoms_for_board(index, board, played_uci):
    # FEN is matched exactly, including clocks (not just its first four fields).
    import chess
    fen=board.fen(en_passant="fen")
    packets=index.get(fen,[])
    if played_uci not in ("b2b3","b2b4"):
        return []
    key="a" if played_uci=="b2b3" else "b"
    atoms=[]
    for packet in packets:
        for name in ENGINES:
            engine=packet["engines"][name]
            binary=engine.get("binary_sha256")
            if not isinstance(binary,str) or len(binary)!=64:
                raise ValueError("P8 EP8 binary provenance SHA missing")
            for depth in (8,12,16):
                trial=engine["depths"][str(depth)]["trials"]
                if len(trial)!=2:raise ValueError("P8 EP8 repeats missing")
                free=_stable(trial,depth,key,"free_opponent_reply")
                forced=_stable(trial,depth,key,"forced_convergence_reply_via_go_searchmoves")
                if free is None or forced is None:
                    # Abstain, rather than cherry-pick an unstable depth result.
                    continue
                b=board.copy(stack=False)
                m=chess.Move.from_uci(played_uci)
                if m not in b.legal_moves:raise ValueError("P8 EP8 illegal root move")
                b.push(m)
                reply=chess.Move.from_uci("c4b3")
                if reply not in b.legal_moves:raise ValueError("P8 EP8 illegal conditional reply")
                source=packet["source"]
                label="Stockfish" if name=="Stockfish" else "Ethereal"
                text=(f"In this frozen {label} depth-{depth} experiment, after {played_uci} "
                      f"the free reply was {free[1]} (White score {free[0]} cp), "
                      f"while restricting Black to c4b3 produced a White score of {forced[0]} cp. "
                      "These are conditional search observations, not a demonstrated explanation of move preference.")
                atoms.append({"type":"opponent_reply_observation",
                    "provenance":PROVENANCE,
                    "authority":"developmental_engine_conditional_search_observation",
                    "claim":{"stage":"C3X 0.13 P8-EP8","source_game_url":source["game_url"],
                             "root_fen":fen,"root_move":played_uci,
                             "reply_constraint":"c4b3","engine":name,"binary_sha256":binary,
                             "depth":depth,"free_score_white_cp":free[0],"forced_score_white_cp":forced[0],
                             "free_first_reply":free[1],"repeats":2,
                             "causal_certificate":None},
                    "text":text})
    return atoms
