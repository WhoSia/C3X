#!/usr/bin/env python3
"""C3X P38/R1 independent-engine referee on UNCHANGED P37 predictions.

P37 source/prediction sealed before this Ethereal-label experiment.
96k and 192k node-limited pinned Ethereal 12.75; zero model retuning.
No claim that Ethereal reply is objective chess truth or equal strength.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import zipfile
from pathlib import Path

import chess
import chess.engine

PRED_ZIP_SHA = "721471da43d0bd973e2b084fc47070f5a5826d0add38cbc39a2ccfbca6a427f6"
SOURCE_ZIP_SHA = "3f16f69c6cb01029c519aeb24654913303916ce79537c1a86497bb9c84b79191"
PRED_MEMBER = "P37_R2_THREE_RIVAL_PRE_REFERENCE_PREDICTIONS.json"
PRED_JSON_SHA = "da395f0eb16e7b294af2056dadd92b579770aa8f1ae288d1d358132685807051"
SOURCE_MEMBER = "P37_R1_8_EVENT_8_GAME_SOURCE_ONLY_MANIFEST.json"
SOURCE_JSON_SHA = "77ebaa409e7c2099cc6cce3419c2f55ded295d925ab441dc2d13c16b67c2c361"
ETHEREAL_COMMIT = "b55ed96881f163940569145fbcc4e222d7272338"
BUDGETS = (96000, 192000)
METHODS = ("stockfish_pv", "simple_json", "c3x_legal_plan")


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def need(ok: bool, code: str) -> None:
    if not ok:
        raise ValueError("P38_ETHEREAL_HOLD_" + code)


def authentic_archive(path: Path, zip_sha: str, member: str, member_sha: str) -> dict:
    data = path.read_bytes()
    need(sha(data) == zip_sha, "ARCHIVE_SHA_" + member)
    with zipfile.ZipFile(path) as z:
        need(member in z.namelist(), "MEMBER_ABSENT_" + member)
        raw = z.read(member)
    need(sha(raw) == member_sha, "MEMBER_SHA_" + member)
    return json.loads(raw)


def authentic_cases(prediction: dict, original_source: dict) -> list[dict]:
    need(prediction["status"] == "PRE_REFEREE_FROZEN_THREE_RIVAL_RESPONSE_FORECASTS",
         "FROZEN_FORECAST_STATUS")
    need(len(prediction["cases"]) == len(original_source["sources"]) == 8,
         "EIGHT_SOURCE_EVENTS")
    need(len({c["source_id"] for c in prediction["cases"]}) == 8,
         "DUPLICATE_EVENT")
    need(prediction.get("source_manifest_sha256") == SOURCE_JSON_SHA,
         "SOURCE_TO_FORECAST_SHA")
    original = {x["source_id"]: x["selected"] for x in original_source["sources"]}
    for row in prediction["cases"]:
        game = original.get(row["source_id"])
        need(game is not None, "UNKNOWN_SOURCE_ID")
        need(row["case_id"] == game["case_id"], "CASE_ID_CHANGED")
        need(row["original_game_sha256"] == game["full_game_uci_sha256"],
             "GAME_SHA_CHANGED")
        need(row["original_prefix_uci"] == game["full_game_uci"][:30],
             "GAME_PREFIX_CHANGED")
        need(len(row["candidate_pairs"]) == 2, "NOT_TWO_FROZEN_ROOTS")
        need(len({x["root_uci"] for x in row["candidate_pairs"]}) == 2,
             "DUPLICATE_FROZEN_ROOT")
        board = chess.Board()
        for u in row["original_prefix_uci"]:
            move = chess.Move.from_uci(u)
            need(move in board.legal_moves, "ILLEGAL_HISTORY")
            board.push(move)
        need(board.fen(en_passant="fen") == row["frozen_fen"],
             "FROZEN_FEN_DRIFT")
        for candidate in row["candidate_pairs"]:
            need(chess.Move.from_uci(candidate["root_uci"]) in board.legal_moves,
                 "ILLEGAL_FROZEN_ROOT")
            need(set(candidate["predictions"]) == set(METHODS),
                 "FROZEN_RIVALS_MISSING")
            for pred in candidate["predictions"].values():
                reply = pred["reply"]
                if reply is not None:
                    child = board.copy(stack=True)
                    child.push_uci(candidate["root_uci"])
                    need(chess.Move.from_uci(reply) in child.legal_moves,
                         "FORECAST_REPLY_ILLEGAL")
    return prediction["cases"]


def extract_reply(board: chess.Board, root_uci: str, info: dict) -> dict:
    pv = info.get("pv", [])
    root = chess.Move.from_uci(root_uci)
    if not pv:
        return {"status": "UNDEFINED_NO_PV", "reply": None, "pv": [],
                "nodes": info.get("nodes"), "depth": info.get("depth")}
    need(pv[0] == root, "ENGINE_CHANGED_ROOT")
    chess_board = board.copy(stack=True)
    for move in pv:
        need(move in chess_board.legal_moves, "REF_PV_ILLEGAL")
        chess_board.push(move)
    if len(pv) < 2:
        return {"status": "UNDEFINED_NO_OPPONENT_REPLY", "reply": None,
                "pv": [x.uci() for x in pv], "nodes": info.get("nodes"),
                "depth": info.get("depth")}
    return {
        "status": "VALID_NATIVE_REF_REPLY",
        "reply": pv[1].uci(),
        "pv": [x.uci() for x in pv],
        "nodes": info.get("nodes"),
        "depth": info.get("depth"),
        "score": str(info.get("score")),
    }


def evaluate_one(engine: str, history: list[str], root_uci: str, nodes: int) -> dict:
    board = chess.Board()
    for u in history:
        board.push_uci(u)
    root = chess.Move.from_uci(root_uci)
    need(root in board.legal_moves, "REF_ROOT_ILLEGAL")
    with chess.engine.SimpleEngine.popen_uci(engine, timeout=120) as process:
        need("Ethereal" in process.id.get("name", ""), "WRONG_ENGINE_FAMILY")
        need("Threads" in process.options and "Hash" in process.options,
             "MISSING_PERFORMANCE_OPTIONS")
        process.configure({"Threads": 1, "Hash": 16})
        result = process.analyse(board, chess.engine.Limit(nodes=nodes),
                                 root_moves=[root], info=chess.engine.INFO_ALL)
    parsed = extract_reply(board, root_uci, result)
    parsed["requested_nodes"] = nodes
    return parsed


def stable_label(low: dict, high: dict) -> dict:
    a,b = low.get("reply"), high.get("reply")
    if a is None or b is None:
        return {"status": "REFERENCE_UNDEFINED", "label": None,
                "reply_96k": a, "reply_192k": b}
    if a != b:
        return {"status": "REFERENCE_UNSTABLE", "label": None,
                "reply_96k": a, "reply_192k": b}
    return {"status": "REFERENCE_STABLE", "label": b,
            "reply_96k": a, "reply_192k": b}


def compare_fixed_predictions(cases: list[dict], engine: str) -> dict:
    totals = {m: {"correct": 0, "wrong": 0} for m in METHODS}
    all96 = {m: {"correct":0,"wrong":0} for m in METHODS}
    pairs = {"both_correct":0,"pv_only_correct":0,"c3x_only_correct":0,
             "both_wrong":0}
    status = {"REFERENCE_STABLE":0,"REFERENCE_UNSTABLE":0,"REFERENCE_UNDEFINED":0}
    results = []
    for case in cases:
        entries = []
        for item in case["candidate_pairs"]:
            root=item["root_uci"]
            observations={str(n):evaluate_one(engine,case["original_prefix_uci"],root,n)
                          for n in BUDGETS}
            ref=stable_label(observations["96000"],observations["192000"])
            status[ref["status"]]+=1
            forecasts={m:item["predictions"][m]["reply"] for m in METHODS}
            if observations["96000"]["reply"] is not None:
                for method in METHODS:
                    key="correct" if forecasts[method] == observations["96000"]["reply"] else "wrong"
                    all96[method][key]+=1
            hits={}
            if ref["label"] is not None:
                for method in METHODS:
                    success=forecasts[method] == ref["label"]
                    hits[method]=success
                    totals[method]["correct" if success else "wrong"]+=1
                p=hits["stockfish_pv"]
                c=hits["c3x_legal_plan"]
                pairs["both_correct" if p and c else
                      "pv_only_correct" if p else
                      "c3x_only_correct" if c else "both_wrong"]+=1
            entries.append({"root_uci":root,"reference":ref,
                            "original_predictions":forecasts,
                            "hits_only_if_stable":hits,
                            "native_output_by_budget":observations})
            print("P38_ETHEREAL",case["source_id"],root,ref["status"],
                  ref["reply_96k"],ref["reply_192k"],flush=True)
        results.append({"case_id":case["case_id"],"event_family":case["event_family"],
                        "source_id":case["source_id"],"candidate_results":entries})
    need(sum(status.values())==16, "SIXTEEN_TRIALS")
    return {
        "status":"P38_CROSS_ENGINE_REPLY_LABEL_TRANSPORT_OBSERVED_NOT_CHESS_TRUTH",
        "engine_family":"Ethereal classical independent source",
        "engine_source_commit":ETHEREAL_COMMIT,
        "stable_eligible":status["REFERENCE_STABLE"],
        "unstable":status["REFERENCE_UNSTABLE"],
        "undefined":status["REFERENCE_UNDEFINED"],
        "referee_label_status":status,
        "stable_label_exact_matches":totals,
        "all_defined_96k_only_secondary":all96,
        "paired_pv_vs_c3x_only_stable":pairs,
        "all_cases":results,
        "claim_ceiling":"Same presealed forecast vs different older engine's finite-node move preference, not objective chess value, cost equality, or full model generalization",
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--prediction-zip",type=Path,required=True)
    p.add_argument("--source-zip",type=Path,required=True)
    p.add_argument("--ethereal",required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    forecast=authentic_archive(a.prediction_zip,PRED_ZIP_SHA,PRED_MEMBER,PRED_JSON_SHA)
    source=authentic_archive(a.source_zip,SOURCE_ZIP_SHA,SOURCE_MEMBER,SOURCE_JSON_SHA)
    cases=authentic_cases(forecast,source)
    report=compare_fixed_predictions(cases,a.ethereal)
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
    print("P38_CROSS_ENGINE_COURT_COMPLETED",report["referee_label_status"],flush=True)


if __name__=="__main__":
    main()
