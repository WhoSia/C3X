#!/usr/bin/env python3
"""P37/R2 two-job blind forecast and later 96k SF16 reference court.

A = Stockfish24k PV reply, B = one-ply foil-aware JSON reply heuristic,
C = C3X-inspired legal response/recapture finite plan (NOT a trained model).
Every competitor receives the identical 24k shared engine PV information.
96k reference runs ONLY in separate, downstream referee CI job.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path

import chess
import chess.engine

SOURCE_MANIFEST_SHA = "77ebaa409e7c2099cc6cce3419c2f55ded295d925ab441dc2d13c16b67c2c361"
ENGINE_COMMIT = "68e1e9b3811e16cad014b590d7443b9063b3eb52"
NET_SHA = "5af11540bbfefcb54e38c5dd000cab4b469dfa7599a1d55be5d2722c20a8929b"
PRED_NODES = 24000
REF_NODES = 96000
SOURCE_IDS = ("sahel-open-a", "kazchess-masters", "chinese-league",
              "clutch-champions", "freiburger-open", "magdeburg-open",
              "cerrado-garcia-palacios", "greg-hjorth-open")
PIECE_CP = {chess.PAWN:100, chess.KNIGHT:320, chess.BISHOP:330,
            chess.ROOK:500, chess.QUEEN:900, chess.KING:0}


def need(ok, issue):
    if not ok:
        raise ValueError("P37_FORECAST_HOLD_" + issue)


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def reconstruct(case: dict) -> chess.Board:
    b = chess.Board()
    moves = case["original_prefix_uci"]
    need(case["fixed_ply"] == len(moves) == 30, "PLY_OR_PREFIX")
    for uci in moves:
        m = chess.Move.from_uci(uci)
        need(m in b.legal_moves, "ILLEGAL_PREFIX_" + uci)
        b.push(m)
    need(b.fen(en_passant="fen") == case["frozen_fen"], "ROOT_FEN_NOT_IDENTICAL")
    need(not b.is_game_over(claim_draw=False), "TERMINAL_SOURCE_BOARD")
    return b


def material(board: chess.Board, original_color: bool) -> int:
    value = sum(PIECE_CP[k] * (len(board.pieces(k, original_color)) -
                                   len(board.pieces(k, not original_color)))
                for k in PIECE_CP)
    return value


def next_reply_pv(board: chess.Board, root: chess.Move, pv) -> str | None:
    if not pv or pv[0] != root or len(pv) < 2:
        return None
    x = board.copy(stack=True)
    x.push(root)
    return pv[1].uci() if pv[1] in x.legal_moves else None


def predict_json_reply(after_root: chess.Board, original: bool) -> dict:
    before = material(after_root, original)
    rows = []
    for reply in after_root.legal_moves:
        check = after_root.gives_check(reply)
        after_root.push(reply)
        opp_gain = before - material(after_root, original)
        after_root.pop()
        rows.append((-opp_gain, -int(check), reply.uci()))
    need(bool(rows), "NO_LEGAL_OPPONENT_REPLIES")
    rows.sort()
    return {"reply": rows[0][2], "legal_opponent_replies_considered": len(rows),
            "own_continuations_enumerated": 0}


def predict_c3x_plan_reply(after_root: chess.Board, original: bool) -> dict:
    rows = []
    own_expansions = 0
    for reply in after_root.legal_moves:
        gives_check = after_root.gives_check(reply)
        after_root.push(reply)
        if after_root.is_checkmate():
            best_own_material = -100000
        elif after_root.is_stalemate():
            best_own_material = 0
        else:
            continuation_scores = []
            for own_reply in after_root.legal_moves:
                after_root.push(own_reply)
                continuation_scores.append(material(after_root, original))
                own_expansions += 1
                after_root.pop()
            need(bool(continuation_scores), "EMPTY_CONTINUATION")
            best_own_material = max(continuation_scores)
        after_root.pop()
        rows.append((best_own_material, -int(gives_check), reply.uci()))
    need(bool(rows), "NO_LEGAL_OPPONENT_REPLIES")
    rows.sort()
    return {"reply": rows[0][2], "legal_opponent_replies_considered": len(rows),
            "own_continuations_enumerated": own_expansions}


def sanitized_source(source_archive_manifest: Path) -> dict:
    raw = source_archive_manifest.read_bytes()
    need(sha(raw) == SOURCE_MANIFEST_SHA, "SOURCE_FREEZE_MANIFEST_SHA")
    data = json.loads(raw)
    need(data["selected_game_count"] == 8 and len(data["sources"]) == 8,
         "SOURCE_COUNT")
    need(tuple(s["source_id"] for s in data["sources"]) == SOURCE_IDS,
         "FROZEN_EIGHT_SOURCE_IDS")
    cases = []
    for row in data["sources"]:
        selected = row["selected"]
        prefix = selected["full_game_uci"][:30]
        need(len(prefix)==30 and selected["fixed_ply"]==30,"SOURCE_PLY")
        original_sha=sha(" ".join(selected["full_game_uci"]).encode("ascii"))
        need(original_sha==selected["full_game_uci_sha256"],"FULL_HISTORY_SHA")
        case = {
            "case_id":selected["case_id"],"source_id":row["source_id"],
            "event_family":row["event_family"],"event_date":selected["headers"]["Date"],
            "pgn_source_sha256":row["raw_sha256"],
            "original_game_sha256":original_sha,
            "fixed_ply":30,"frozen_fen":selected["frozen_fen"],
            "original_prefix_uci":prefix,
        }
        reconstruct(case)
        cases.append(case)
    return {"status":"SOURCE_PREFIX_ONLY_NO_FUTURE_GAME_MOVES",
            "original_full_manifest_sha256":SOURCE_MANIFEST_SHA,
            "reference_oracle_available_in_this_file":False,
            "event_count":8,"cases":cases}


def native(engine_path: str, board: chess.Board, budget: int, *,
           two_pv: bool = False, root: chess.Move | None = None):
    with chess.engine.SimpleEngine.popen_uci(engine_path,timeout=90) as engine:
        need("Stockfish 16" in engine.id.get("name",""),"WRONG_ENGINE")
        need("Use NNUE" in engine.options,"MISSING_NNUE_OPTION")
        engine.configure({"Threads":1,"Hash":16,"Use NNUE":True})
        kw={"multipv":2} if two_pv else {}
        if root is not None:
            kw["root_moves"]=[root]
        return engine.analyse(board,chess.engine.Limit(nodes=budget),
                              info=chess.engine.INFO_ALL,**kw)


def response_from_analysis(board:chess.Board, info:dict):
    pv = info.get("pv") or []
    need(bool(pv) and pv[0] in board.legal_moves, "EMPTY_OR_ILLEGAL_ROOT")
    return {
        "root_uci":pv[0].uci(),
        "pv_uci":[m.uci() for m in pv],
        "root_side_cp":info["score"].pov(board.turn).score(),
        "root_side_mate":info["score"].pov(board.turn).mate(),
        "reported_nodes":info.get("nodes"),
        "depth":info.get("depth"),
        "lowerbound":bool(info.get("lowerbound",False)),
        "upperbound":bool(info.get("upperbound",False)),
    }


def signed_margin(ordered: list[dict]):
    a,b=ordered
    ac,bc=a["root_side_cp"],b["root_side_cp"]
    if ac is None or bc is None:
        return {"signed_cp":None,"absolute_cp":None,"stratum":"mate_or_unscored"}
    delta=ac-bc
    return {"signed_cp":delta,"absolute_cp":abs(delta),
            "stratum":"rank_unresolved" if delta<0 else
                     "near" if delta<20 else "intermediate" if delta<100 else "wide"}


def forecast(prefix_only:dict, engine_path:str) -> dict:
    need(prefix_only["status"]=="SOURCE_PREFIX_ONLY_NO_FUTURE_GAME_MOVES","PREDICTOR_LEAKAGE")
    out=[]
    for case in prefix_only["cases"]:
        board=reconstruct(case)
        infos=native(engine_path,board,PRED_NODES,two_pv=True)
        need(len(infos)==2,"MULTIPV_NOT_TWO")
        analyses=[response_from_analysis(board,x) for x in infos]
        need(len({a["root_uci"] for a in analyses})==2,"DUPLICATE_TWO_CANDIDATES")
        pairs=[]
        for a in analyses:
            root=chess.Move.from_uci(a["root_uci"])
            child=board.copy(stack=True)
            child.push(root)
            pv=[chess.Move.from_uci(m) for m in a["pv_uci"]]
            sf=next_reply_pv(board,root,pv)
            if child.is_game_over(claim_draw=False):
                json_reply={"reply":None,"legal_opponent_replies_considered":0,
                            "own_continuations_enumerated":0}
                c3x_reply=dict(json_reply)
            else:
                json_reply=predict_json_reply(child,board.turn)
                c3x_reply=predict_c3x_plan_reply(child,board.turn)
            pairs.append({
                "root_uci":a["root_uci"],"original_joint24k_info":a,
                "predictions":{
                    "stockfish_pv":{"reply":sf,"extra_engine_nodes":0},
                    "simple_json":{"extra_engine_nodes":0,**json_reply},
                    "c3x_legal_plan":{"extra_engine_nodes":0,**c3x_reply},
                },
            })
        out.append({**case,"signed_root_margin":signed_margin(analyses),
                    "candidate_pairs":pairs})
        print("P37_PREDICTION_SEALED",case["source_id"],
              [x["root_uci"] for x in pairs],flush=True)
    return {
        "status":"PRE_REFEREE_FROZEN_THREE_RIVAL_RESPONSE_FORECASTS",
        "source_manifest_sha256":SOURCE_MANIFEST_SHA,
        "engine_git":ENGINE_COMMIT,"network_sha":NET_SHA,
        "shared_engine_nodes_per_case":PRED_NODES,
        "forecast_cardinality_per_candidate":1,
        "both_baselines_and_c3x_have_exact_same_native_engine_inputs":True,
        "cpu_computation_equated":False,
        "c3x_is_existing_NNUE_mechanistic_model":False,
        "no_future_game_moves_in_predictor_input":True,
        "cases":out,
    }


def judge(predictions:dict, engine_path:str) -> dict:
    need(predictions["status"]=="PRE_REFEREE_FROZEN_THREE_RIVAL_RESPONSE_FORECASTS",
         "PREDICTION_STATUS")
    need(predictions["source_manifest_sha256"]==SOURCE_MANIFEST_SHA,"SOURCE_DRIFT")
    need(len(predictions["cases"])==8,"EIGHT_CASES")
    observations=[]
    for case in predictions["cases"]:
        board=reconstruct(case)
        choices=[x["root_uci"] for x in case["candidate_pairs"]]
        need(len(choices)==2 and len(set(choices))==2,"BAD_CANDIDATES")
        ref={}
        for root_uci in choices:
            info=native(engine_path,board,REF_NODES,
                        root=chess.Move.from_uci(root_uci))
            d=response_from_analysis(board,info)
            need(d["root_uci"]==root_uci,"FORCED_REF_ROOT_DRIFT")
            pv=[chess.Move.from_uci(x) for x in d["pv_uci"]]
            ref[root_uci]={"answer":next_reply_pv(board,chess.Move.from_uci(root_uci),pv),
                           "reference":d}
        competitions={}
        for budget in (48000,96000):
            raw=native(engine_path,board,budget,two_pv=True)
            infos=[response_from_analysis(board,x) for x in raw]
            competitors=[x["root_uci"] for x in infos]
            competitions[str(budget)]={"roots":competitors,
                                       "margin":signed_margin(infos),
                                       "same_two_root_set_as_24k":set(competitors)==set(choices),
                                       "same_root_order_as_24k":competitors==choices}
        scored=[]
        for p in case["candidate_pairs"]:
            answer=ref[p["root_uci"]]["answer"]
            forecasts={}
            for method,v in p["predictions"].items():
                predicted=v["reply"]
                forecasts[method]={"prediction":predicted,"reference":answer,
                                   "abstain":predicted is None,
                                   "exact_match":predicted is not None and predicted==answer}
            scored.append({"root_uci":p["root_uci"],"reference_96k":ref[p["root_uci"]],
                           "method_verdicts":forecasts})
        near=case["signed_root_margin"]["stratum"]=="near"
        stable=near and all(competitions[str(n)]["same_two_root_set_as_24k"]
                            and competitions[str(n)]["margin"]["stratum"]=="near"
                            for n in (48000,96000))
        observations.append({
            "source_id":case["source_id"],"case_id":case["case_id"],
            "event_family":case["event_family"],
            "initial_24k_margin":case["signed_root_margin"],
            "candidate_roots_24k":choices,
            "competitions":competitions,
            "stable_near_across_24_48_96k":bool(stable),
            "scored_candidate_predictions":scored,
        })
        print("P37_REFEREE",case["source_id"],"near_stable",bool(stable),flush=True)
    methods=("stockfish_pv","simple_json","c3x_legal_plan")
    summary={}
    for method in methods:
        v=[x["method_verdicts"][method] for o in observations
           for x in o["scored_candidate_predictions"]]
        summary[method]={
            "correct":sum(x["exact_match"] for x in v),
            "abstain":sum(x["abstain"] for x in v),
            "wrong_nonabstain":sum(not x["exact_match"] and not x["abstain"] for x in v),
            "total":len(v),
        }
    return {
        "status":"EIGHT_EVENT_P37_EXPLORATORY_RESPONSE_FORECAST_SCORED_NOT_CONFIRMED_SUPERIORITY",
        "target":"one 96k forced-root SF16 PV opponent reply, not chess ground truth",
        "source_manifest_sha256":SOURCE_MANIFEST_SHA,
        "predictor_engine_nodes_per_game":PRED_NODES,
        "reference_nodes_per_forced_candidate":REF_NODES,
        "native_engine_compute_equated_across_forecasters":True,
        "cpu_legal_move_cost_equated":False,
        "all_prior_game_event_ledger_complete":False,
        "stable_near_count":sum(x["stable_near_across_24_48_96k"] for x in observations),
        "case_count":len(observations),"candidate_response_trials":16,
        "summary":summary,
        "cases":observations,
        "claim_ceiling":"Exploratory finite-budget same-engine reference reply forecast; no chess truth or NNUE causal mediation or human advantage.",
    }


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--mode",choices=("sanitize","forecast","judge"),required=True)
    parser.add_argument("--source-manifest",type=Path)
    parser.add_argument("--input",type=Path)
    parser.add_argument("--engine")
    parser.add_argument("--out",type=Path,required=True)
    args=parser.parse_args()
    if args.mode=="sanitize":
        need(args.source_manifest is not None,"MISSING_SOURCE_MANIFEST")
        out=sanitized_source(args.source_manifest)
    else:
        need(args.input is not None and args.engine,"MISSING_INPUT_OR_ENGINE")
        data=read_json(args.input)
        out=forecast(data,args.engine) if args.mode=="forecast" else judge(data,args.engine)
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("P37_"+args.mode.upper()+"_SUCCESS",len(out.get("cases",[])),flush=True)


if __name__=="__main__":
    main()
