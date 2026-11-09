#!/usr/bin/env python3
"""C3X P42/R21-C: historical exposure BREADTH audit, not new data.

Compare physically frozen Sep16 and eight different October broadcast events.
Checks original-source bytes and exact FEN4 overlap, source-family duplicates.
Different definitions of game SHA cannot silently establish global game
disjointness. This is NOT a prospective held-out cohort.
"""
import argparse,hashlib,json,zipfile
from pathlib import Path
import chess
SEPT_SHA="9372e0fdce2c8499e8d12f6bef5d1bfaef40a2d5b7160cc48513085567c9098d"
OCT_SHA="77ebaa409e7c2099cc6cce3419c2f55ded295d925ab441dc2d13c16b67c2c361"

def digest(x):return hashlib.sha256(x).hexdigest()
def compare(sept,octo):
    if sept.get("phase")!="SOURCE_ONLY_PRE_NATIVE_TREATMENT":
        raise ValueError("R21_C_HOLD_SEPT_ORIGINAL_PHASE")
    if len(sept.get("source_games",[]))!=16 or len(octo.get("sources",[]))!=8:
        raise ValueError("R21_C_HOLD_SOURCE_CASE_COUNT")
    first=sept["source_games"];second=[x["selected"] for x in octo["sources"]]
    if len({x["source_game_sha256"] for x in first})!=16:
        raise ValueError("R21_C_HOLD_SEPT_GAME_DUPLICATE")
    if len({x["full_game_uci_sha256"] for x in second})!=8:
        raise ValueError("R21_C_HOLD_OCT_GAME_DUPLICATE")
    event_ids=[x["source_id"] for x in octo["sources"]]
    if len(set(event_ids))!=8:
        raise ValueError("R21_C_HOLD_OCT_SOURCE_EVENT_DUPLICATE")
    a={x["fen4"] for x in first}
    b=set()
    for x in second:
        board=chess.Board()
        history=x["full_game_uci"]
        if x["fixed_ply"]!=30 or len(history)<30:
            raise ValueError("R21_C_HOLD_OCT_FROZEN_PLY")
        for u in history[:30]:
            m=chess.Move.from_uci(u)
            if m not in board.legal_moves:
                raise ValueError("R21_C_HOLD_ILLEGAL_OCT_HISTORY")
            board.push(m)
        if board.fen(en_passant="fen")!=x["frozen_fen"]:
            raise ValueError("R21_C_HOLD_OCT_FEN_REPLAY_MISMATCH")
        b.add(" ".join(board.fen(en_passant="fen").split()[:4]))
    return {
      "schema":"c3x042-r21-cross-cohort-source-exposure-census-v1",
      "status":"PASS_EXACT_FEN4_AND_SOURCE_FAMILY_EXPOSURE_CENSUS_ONLY",
      "source_sept16_case_count":len(first),
      "source_oct8_event_count":len(event_ids),
      "source_oct8_game_count":len(second),
      "exact_chess_fen4_intersection_count":len(a&b),
      "oct_original_30ply_legal_replay_verified":True,
      "sept_member_sha256":SEPT_SHA,"oct_member_sha256":OCT_SHA,
      "source_game_hash_algorithms_equivalent_proved":False,
      "full_prior_archive_exclusion_proved":False,
      "fresh_prospective_cohort":False,
      "novel_chess_value_evidence":False,
      "mechanistic_causal_mediation_proved":False,
      "claim_ceiling":"Only two archived source samples and FEN4 collision, cannot certify all prior game/event disjointness or original-value strength."
    }

def main():
    p=argparse.ArgumentParser()
    for name in ("sept-source","oct-source","out"):
        p.add_argument("--"+name,required=True)
    q=p.parse_args()
    raw_a=Path(q.sept_source).read_bytes()
    raw_b=Path(q.oct_source).read_bytes()
    if digest(raw_a)!=SEPT_SHA or digest(raw_b)!=OCT_SHA:
        raise ValueError("R21_C_HOLD_ORIGINAL_SOURCE_BYTE_SHA")
    report=compare(json.loads(raw_a),json.loads(raw_b))
    dest=Path(q.out);dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_text(json.dumps(report,sort_keys=True,indent=2)+"\n")
    print("R21_C_HISTORICAL_EXPOSURE_CENSUS",report["status"],report["exact_chess_fen4_intersection_count"])
if __name__=="__main__":
    main()
