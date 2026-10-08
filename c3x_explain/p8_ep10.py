"""P8-EP10 read-only bounded engineering mechanism diagnostic for PGN commentary.

This is not a first-class human-chess strategic explanation certificate.
"""
from __future__ import annotations

SCHEMA="c3x-013-p8ep10-single-event-fixed-grid-ceclub-v1"
STATUS="EXPLORATORY_SOURCE_LOCAL_SINGLE_EXECUTION_EVENT_COURT"
FEN="2rq1rk1/p4ppp/bp1bnn2/3pN3/2pP3P/1P2PPP1/PB2NRB1/R2Q2K1 w - - 1 17"
PROVENANCE="CONVENTIONAL_HEURISTIC_COMMENTARY"
PAIR=("f3f4","g3g4")
ANCHOR_SHA="9a228208c1692e096300d92f25ac9f087dfec3de99485921a071592d5d184077"

def mechanism_index(packets):
    out={}
    for p in packets:
        if p.get("schema")!=SCHEMA or p.get("status")!=STATUS:
            raise ValueError("EP10 provenance schema/status invalid")
        if p.get("root_FEN")!=FEN or tuple(p.get("pair",()))!=PAIR:
            raise ValueError("EP10 source FEN/pair mismatch")
        if not p.get("sham_exact_all") or not p.get("negative_control_exact_all"):
            raise ValueError("EP10 sham or no-op sentinel failure")
        if p.get("original_chess_concept_proven") is not False or p.get("causal_certificate_authorized") is not False:
            raise ValueError("EP10 attempted scientific authority promotion")
        if p.get("C3X_014")!="UNOPENED_UNNAMED":
            raise ValueError("Invalid EP10 stage state")
        if len(p.get("rows",[]))!=4:
            raise ValueError("EP10 frozen two-depth/two-cold-run panel missing")
        out.setdefault(FEN,[]).append(p)
    return out

def mechanism_atoms_for_board(idx,board,played_uci):
    if board.fen(en_passant="fen")!=FEN or played_uci not in PAIR:
        return []
    import chess
    if any(chess.Move.from_uci(m) not in board.legal_moves for m in PAIR):
        raise ValueError("EP10 root UCI pair illegal on supplied PGN board")
    atoms=[]
    for p in idx.get(FEN,[]):
        entries={}
        for d in (8,12):
            rows=sorted((x for x in p["rows"] if x["depth"]==d),key=lambda x:x["repeat"])
            if len(rows)!=2 or [x["repeat"] for x in rows]!=[1,2]:
                raise ValueError("EP10 cold repeats incomplete")
            values=[]
            for row in rows:
                if not row.get("sham_exact"):raise ValueError("EP10 per-row sham failure")
                baseline=row["ep10_NONE"]
                target=row.get("scan",{}).get("MAIN:32")
                if target is None or target["target"].get("blocked")!=1 or target["target"].get("actual_ordinal")!=32:
                    raise ValueError("EP10 selected event missing or not singular")
                if target["target"].get("actual_site")!=1:
                    raise ValueError("EP10 event is not native MAIN path")
                gap0=baseline.get("gap_white_cp");gap1=target.get("gap_white_cp")
                if not isinstance(gap0,int) or not isinstance(gap1,int):
                    return []   # Mate/non-comparable score: abstain, do not invent a cp gap.
                values.append((baseline["bestmove"],gap0,target["bestmove"],gap1))
            if values[0]!=values[1]:
                return []   # Unstable repeated measurements: abstain.
            entries[d]=values[0]
        before=entries[12];d8=entries[8]
        if before[0]==before[2]:
            observation=f"remained {before[0]}"
        else:
            observation=f"switched from {before[0]} to {before[2]}"
        txt=(f"In a frozen Stockfish 16 implementation test on this earlier CECLUB position, "
             f"blocking one main-search TT early return (eligible occurrence 32) {observation} "
             f"at depth 12; the measured f3f4-minus-g3g4 gap changed from "
             f"{before[1]:+d} to {before[3]:+d} cp. "
             f"At depth 8 the preferred move was {d8[0]} before and {d8[2]} after the same ordinal intervention. "
             "This describes local engine search behavior, not a verified chess-strategic reason.")
        atoms.append({"type":"engine_path_sensitivity_observation",
            "provenance":PROVENANCE,
            "authority":"exploratory_source_local_engine_tt_return_diagnostic",
            "claim":{"stage":"C3X 0.13 P8-EP10","engine":"Stockfish 16",
                "root_fen":FEN,"played_root_move":played_uci,"pair":list(PAIR),
                "source_game":"https://lichess.org/broadcast/ceclub-primera-division-linares-2026/round-6/HLnCaWdO/0YxrjUCr",
                "input_file_sha256":ANCHOR_SHA,
                "treatment":"MAIN early bound TT return occurrence ordinal32",
                "depth12":list(before),"depth8":list(d8),"cold_repeats":2,
                "new_source":False,"independent_engine":False,
                "human_chess_concept_certificate":None},
            "text":txt})
    return atoms
