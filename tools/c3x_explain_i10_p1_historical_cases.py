"""I10-P1: two PRESEALED real historical chess episodes and transparent comparators.

Do not claim C3X causal novelty, neural model training, actual CCC inference,
teacher-model superiority or participant outcomes from these development cases.
"""
from __future__ import annotations
import argparse
import io
import json
from pathlib import Path
from typing import Any

import chess
import chess.engine
import chess.pgn

from c3x_explain.core import analyze_pgn, heuristic_atoms, move_facts, firewall, score_cp
from c3x_explain.graph import attach_graphs
from c3x_explain.renderer import attach_render_packets
from c3x_explain.realization import attach_realizations
from c3x_explain.verification import attach_verification
from c3x_explain.judgment import judge_moment
from c3x_explain.concepts import candidate_delta
from c3x_explain.tactics import tactical_contrast
from c3x_explain.planning import verified_line_evidence

SOURCE_REVISION="68e1e9b3811e16cad014b590d7443b9063b3eb52"
FREEZE="d2fd9903e126ee74f9e538f3fcbfbf8302af9dd6"
CASES=(
    {
        "id":"KASPAROV_TOPALOV_1999_24_RXD4",
        "source":"https://www.chess.com/blog/Eshwar360/the-best-chess-game-of-all-time-garry-kasparov-vs-veselin-topalov-1999",
        "nature":"NONTRIVIAL_ATTACKING_ROOK_SACRIFICE",
        "played_san":"Rxd4",
        "recorded_reply_san":"cxd4",
        "pgn":"""[Event "Hoogovens Group A, Kasparov–Topalov 1999"]
[Result "*"]

1. e4 d6 2. d4 Nf6 3. Nc3 g6 4. Be3 Bg7 5. Qd2 c6 6. f3 b5
7. Nge2 Nbd7 8. Bh6 Bxh6 9. Qxh6 Bb7 10. a3 e5 11. O-O-O Qe7
12. Kb1 a6 13. Nc1 O-O-O 14. Nb3 exd4 15. Rxd4 c5 16. Rd1 Nb6
17. g3 Kb8 18. Na5 Ba8 19. Bh3 d5 20. Qf4+ Ka7 21. Rhe1 d4
22. Nd5 Nbxd5 23. exd5 Qd6 24. Rxd4 *
""",
    },
    {
        "id":"MORPHY_OPERA_1858_12_O_O_O",
        "source":"https://rookhabit.com/en/games/morphy-opera-1858",
        "nature":"NONTERMINAL_CASTLING_QUIET_COORDINATION",
        "played_san":"O-O-O",
        "recorded_reply_san":"Rd8",
        "pgn":"""[Event "Opera Game, Morphy–Duke/Count 1858"]
[Result "*"]

1. e4 e5 2. Nf3 d6 3. d4 Bg4 4. dxe5 Bxf3 5. Qxf3 dxe5
6. Bc4 Nf6 7. Qb3 Qe7 8. Nc3 c6 9. Bg5 b5
10. Nxb5 cxb5 11. Bxb5+ Nbd7 12. O-O-O *
""",
    },
)

def reconstruct_case(case: dict[str, Any]):
    game=chess.pgn.read_game(io.StringIO(case["pgn"]))
    if game is None or game.errors:
        raise ValueError(f"historical game PGN invalid: {case['id']}: {game.errors if game else None}")
    moves=list(game.mainline_moves())
    if not moves:raise ValueError("no original game moves")
    board=game.board()
    for m in moves[:-1]:
        if m not in board.legal_moves:raise ValueError("illegal original history move")
        board.push(m)
    played=moves[-1]
    if played not in board.legal_moves or board.san(played)!=case["played_san"]:
        raise ValueError("played original SAN mismatch")
    after=board.copy()
    after.push(played)
    reply=after.parse_san(case["recorded_reply_san"])
    assert reply in after.legal_moves
    assert not board.is_game_over(claim_draw=False) and not after.is_game_over(claim_draw=False)
    return board,played,reply,len(moves)

def _choice(info: dict[str, Any],board:chess.Board,rank:int)->dict[str,Any]:
    pv=info.get("pv") or []
    if not pv or pv[0] not in board.legal_moves:raise ValueError("nonlegal or empty real native root PV")
    raw=info.get("score")
    if raw is None:raise ValueError("missing native score")
    return {"rank":rank,"uci":pv[0].uci(),"san":board.san(pv[0]),
            "score_cp":score_cp(raw,board.turn),"depth":info.get("depth"),
            "nodes":info.get("nodes"),"time":info.get("time"),
            "score_bound":bool(info.get("lowerbound") or info.get("upperbound")),
            "score_mate":raw.pov(board.turn).mate(),
            "pv_uci":[m.uci() for m in pv[:10]]}

def _analysis(engine,board,*,depth,multipv,root_moves=None):
    infos=engine.analyse(board,chess.engine.Limit(depth=depth),multipv=multipv,root_moves=root_moves,info=chess.engine.INFO_ALL)
    if isinstance(infos,dict):infos=[infos]
    return [_choice(x,board,k) for k,x in enumerate(infos,1)]

def _find_original_i9_moment(pgn:str,engine_path:str,ply:int):
    base=analyze_pgn(pgn,engine_path=engine_path,multipv=3,nodes=4000,
        engine_uci_options={"Use NNUE":False,"Threads":1,"Hash":16})
    return next((m for m in base["moments"] if m["ply"]==ply),None),base

def original_focused_verified_moment(board,played,pair,ply):
    facts=move_facts(board,played)
    atoms=heuristic_atoms(board,played,pair,facts)
    for i,a in enumerate(atoms):a["atom_id"]=f"p{ply}:focus:a{i}"
    errs=firewall(board,atoms)
    m={"ply":ply,"fen":board.fen(),"played_uci":played.uci(),
       "played_san":board.san(played),"atoms":atoms,"candidates":pair,
       "selection_reasons":["I10_PRESEALED_HISTORICAL_FOCUS"],
       "commentary_plan":{"categories":[],"atom_ids":[a["atom_id"] for a in atoms]},
       "firewall":{"pass":not errs,"errors":errs}}
    attach_graphs([m])
    attach_render_packets([m])
    attach_realizations([m],"advanced")
    attach_verification([m])
    return m

def run_case(engine_path,case):
    board,played,reply,ply=reconstruct_case(case)
    scout_engine=chess.engine.SimpleEngine.popen_uci(engine_path)
    try:
        scout_engine.configure({"Threads":1,"Hash":16,"Use NNUE":False})
        scout=_analysis(scout_engine,board,depth=9,multipv=3)
    finally:scout_engine.quit()
    rivals=[c for c in scout if c["uci"]!=played.uci()]
    if not rivals:raise ValueError("source scout has no distinct candidate")
    challenger=chess.Move.from_uci(rivals[0]["uci"])
    if challenger not in board.legal_moves:raise ValueError("scout rival illegal")
    pair_engine=chess.engine.SimpleEngine.popen_uci(engine_path)
    try:
        pair_engine.configure({"Threads":1,"Hash":16,"Use NNUE":False})
        paired=_analysis(pair_engine,board,depth=12,multipv=2,
                         root_moves=[played,challenger])
    finally:pair_engine.quit()
    if {x["uci"] for x in paired}!={played.uci(),challenger.uci()}:
        raise ValueError("native comparator did not return EXACT originally frozen pair")
    if any(x["depth"]!=12 for x in paired):
        raise ValueError("original native candidate comparator did not finish common depth 12")
    base,old=_find_original_i9_moment(case["pgn"],engine_path,ply)
    if base is None:raise ValueError("legacy I9 failed to select actual historic played move")
    m=original_focused_verified_moment(board,played,paired,ply)
    judgment=judge_moment(m)
    # MultiPV restricted to [actual, strongest independent scout alternative].
    # Decision abstention is a VALID negative outcome; never replace with an outcome-selected pair.
    for c in paired:
        p=verified_line_evidence(board,c)
        c["pv_legal_replay"]=bool(p and p.get("all_moves_legally_replayed") and p["steps"][0]["uci"]==c["uci"])
    if not all(x["pv_legal_replay"] for x in paired):
        raise ValueError("frozen source PV not legally verified")
    delta=candidate_delta(board,played,challenger)
    tactic=tactical_contrast(board,played,challenger)
    selected=paired[0]
    current=next(x for x in paired if x["uci"]==played.uci())
    alt=next(x for x in paired if x["uci"]==challenger.uci())
    comparable=(type(current["score_cp"]) is int and type(alt["score_cp"]) is int
                and not current["score_bound"] and not alt["score_bound"])
    score_baseline=(
        f"Original SF16 depth12 restricted pair: {current['san']} "
        f"{current['score_cp']}cp versus {alt['san']} {alt['score_cp']}cp; "
        "this is not the globally unrestricted best move."
        if comparable else "Exact ordinary centipawn comparator unavailable; no decisive score-only preference."
    )
    changed=delta.get("played_minus_alternative") or {}
    changed_txt=", ".join(f"{k}={v:+d}" for k,v in sorted(changed.items())) or "no selected board proxy difference"
    concept_proxy=(f"The played move {board.san(played)} versus {board.san(challenger)} "
        f"changes measured board-concept proxies: {changed_txt}. "
        f"Verified tactical-property contrast (played-only/alternative-only) is "
        f"{tactic.get('played_only_kinds',[])}/{tactic.get('alternative_only_kinds',[])}. "
        "These are descriptive concept and tactic proxies, not the independently executed Kim et al. CCC.")
    return {
        "case_id":case["id"],"nature":case["nature"],"original_game_source":case["source"],
        "development_only":True,"fen":board.fen(),"ply":ply,"played":played.uci(),
        "played_san":board.san(played),"recorded_actual_opponent_reply":reply.uci(),
        "scout_original_source":scout,
        "scout_winner_matches_played":scout[0]["uci"]==played.uci(),
        "scout_first_distinct_rival":challenger.uci(),
        "restricted_original_native_pair":paired,
        "i9_existing_actual": {
            "selected":True,"commentary":base["commentary"],
            "atom_types":[a.get("type") for a in base.get("atoms",[])],
            "firewall_pass":base.get("firewall",{}).get("pass"),
            "realization_verified":base.get("realization_verification",{}).get("pass"),
        },
        "strong_comparison": {
            "ENGINE_SCORE_ONLY":{"surface":score_baseline,"actual_native_source":True},
            "CONCEPT_AND_PV_DONOR_PROXY":{"surface":concept_proxy,
                "is_actual_kim_CCC_or_LLM":False,
                "source_board_proxy_delta":changed,
                "source_verified_tactical_difference":tactic},
            "C3X_I10_FOCUSED_EVIDENCE":{"surface":judgment.get("explanation_ko",judgment.get("explanation")),
                "decision":judgment["decision"],"abstention_reason":judgment.get("reason"),
                "atom_ids":judgment.get("evidence_atom_ids",[]),
                "causal_certificate_ids":judgment.get("local_causal_certificate_ids",[])},
        },
        "focused_original_verification":{
            "I9_atom_firewall":m["firewall"]["pass"],
            "I7_surface_verifier":m["realization_verification"]["pass"],
            "atoms":[{"atom_id":a.get("atom_id"),"type":a.get("type"),"authority":a.get("authority"),"provenance":a.get("provenance")} for a in m["atoms"]],
            "native_PV_legal":all(x["pv_legal_replay"] for x in paired)
        },
        "independent_human_outcome":None,
        "actual_Kim_CCC_model_run":False,
        "trained_Jev_or_Clef_run":False,
        "new_C3X_source_causal_information":False,
        "chess_value_proven":False,
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--engine",required=True)
    p.add_argument("--out",required=True)
    args=p.parse_args()
    results=[]
    for case in CASES:
        r=run_case(args.engine,case)
        results.append(r)
        print("C3X_I10_P1_CASE",json.dumps({
            "case":r["case_id"],"played":r["played_san"],"scout_first":r["scout_original_source"][0]["san"],
            "rival":r["scout_first_distinct_rival"],
            "pair":{x["san"]:x["score_cp"] for x in r["restricted_original_native_pair"]},
            "judgment":r["strong_comparison"]["C3X_I10_FOCUSED_EVIDENCE"]["decision"],
            "existing_i9_chars":len(r["i9_existing_actual"]["commentary"]),
            "C3X_causal_certificates":r["strong_comparison"]["C3X_I10_FOCUSED_EVIDENCE"]["causal_certificate_ids"],
        },ensure_ascii=False))
    artifact={"schema":"c3x-explain-i10-p1-real-historical-source-native-development-v1",
              "preseal_git":FREEZE,"official_stockfish_revision":SOURCE_REVISION,
              "context":"DEVELOPMENT_ONLY_TWO_PRESELECTED_PUBLIC_HISTORICAL_GAMES",
              "I10_P0_actual_smoke":{"run_id":38331884555,"unit_tests_passed":37,
                  "original_native_judgments":0,"native_abstentions":4},
              "human_benefit_claim":"HOLD_NO_PARTICIPANTS",
              "actual_CCC_or_LLM_comparator":"UNRUN_PROXIES_ONLY",
              "new_source_causal_certificates":"NONE_ATTACHED",
              "cases":results}
    Path(args.out).parent.mkdir(parents=True,exist_ok=True)
    Path(args.out).write_text(json.dumps(artifact,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")

if __name__=="__main__":
    main()
