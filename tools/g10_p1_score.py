from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import chess
import chess.engine

from c3x_explain.core import candidate_packet
from c3x_g10.demand_validity import (
    ELO_BANDS,
    SF_BUDGETS,
    decision_pressure_features,
    engine_stability_features,
    maia_policy_features,
    refined_gate,
)
from c3x_g10.loop import demand_from_candidate_packet


def configure_engine(engine: chess.engine.SimpleEngine) -> None:
    opts={}
    if "Threads" in engine.options: opts["Threads"]=1
    if "Hash" in engine.options: opts["Hash"]=16
    if opts: engine.configure(opts)


def set_maia_position(maia,case:dict[str,Any]) -> None:
    initial=case.get("initial_fen") or chess.STARTING_FEN
    moves=" ".join(case.get("moves_before_uci") or [])
    if initial==chess.STARTING_FEN:
        cmd="position startpos"
    else:
        cmd=f"position fen {initial}"
    if moves:
        cmd += f" moves {moves}"
    maia.cmd_position(cmd)


def maia_policies(maia,case:dict[str,Any]) -> dict[int,dict[str,float]]:
    out={}
    for elo in ELO_BANDS:
        maia.self_elo=int(elo);maia.oppo_elo=int(elo)
        set_maia_position(maia,case)
        _chosen,top=maia.score_moves()
        out[int(elo)]={x["move"].uci():float(x["policy"]) for x in top}
    return out


def obs(engine:chess.engine.SimpleEngine,board:chess.Board,nodes:int) -> dict[str,Any]:
    return {"nodes_limit":nodes,"candidates":candidate_packet(engine,board,3,nodes)}


def score_case(case,engines,maia):
    row=json.loads(json.dumps(case))
    board=chess.Board(row["position_fen"])

    observations={}
    sf=engines["stockfish_19"]
    for n in SF_BUDGETS:
        observations[f"stockfish_19@{n}"]=obs(sf,board,int(n))
    observations["berserk@10000"]=obs(engines["berserk"],board,10000)
    observations["ethereal@10000"]=obs(engines["ethereal"],board,10000)

    p0c=observations["stockfish_19@5000"]["candidates"]
    q=demand_from_candidate_packet(
        position_fen=board.fen(),
        played_uci=row["played_uci"],
        candidates=p0c,
        source_id=row["source_id"],
        game_id=row["game_id"],
        ply=int(row["ply"]),
    )
    frozen=row.get("p0")
    if frozen is not None:
        row["p0_replay_match"]=(
            bool(frozen.get("admitted"))==bool(q.get("admitted"))
            and frozen.get("candidate_pair")==q.get("candidate_pair")
        )
        if not row["p0_replay_match"]:
            row["p0_replay_detail"]={
                "frozen_pair":frozen.get("candidate_pair"),
                "replay_pair":q.get("candidate_pair"),
                "frozen_admitted":frozen.get("admitted"),
                "replay_admitted":q.get("admitted"),
            }
        pair=(frozen.get("candidate_pair") or q.get("candidate_pair") or "").split("::")
    else:
        row["p0"]=q
        row["p0_replay_match"]=True
        pair=(q.get("candidate_pair") or "").split("::")

    if len(pair)!=2:
        row["score_error"]="P0_PAIR_UNAVAILABLE"
        return row

    policies=maia_policies(maia,row)
    human=maia_policy_features(policies,played_uci=row["played_uci"],candidate_pair=pair)
    stability=engine_stability_features(observations,candidate_pair=pair)
    pressure=decision_pressure_features(
        board_fen=row["position_fen"],
        p0_candidates=p0c,
        clock_after_move_seconds=row.get("clock_after_move_seconds"),
    )
    row["observations"]=observations
    row["validity"]={
        "human_salience":human,
        "engine_stability":stability,
        "decision_pressure":pressure,
    }
    row["refined_gate"]=refined_gate(row)
    row["fresh_local_certificate_induction_opened"]=False
    row["certificate_yield_visible"]=False
    return row


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--base-bank",required=True)
    ap.add_argument("--control-bank",required=True)
    ap.add_argument("--stockfish",required=True)
    ap.add_argument("--berserk",required=True)
    ap.add_argument("--ethereal",required=True)
    ap.add_argument("--maia-checkpoint",required=True)
    ap.add_argument("--out",required=True)
    args=ap.parse_args()

    from maia3.uci import Maia3UCIEngine, parse_args as maia_parse_args

    base=json.load(open(args.base_bank,encoding="utf-8"))["cases"]
    control=json.load(open(args.control_bank,encoding="utf-8"))
    cases=[]
    for x in base:
        y=dict(x);y["case_kind"]="base";cases.append(y)
    for x in control["positive_cases"]+control["negative_cases"]:
        y=dict(x);y["case_kind"]="annotation_control";cases.append(y)
    cases.sort(key=lambda x:x["case_id"])

    engines={
        "stockfish_19":chess.engine.SimpleEngine.popen_uci(args.stockfish),
        "berserk":chess.engine.SimpleEngine.popen_uci(args.berserk),
        "ethereal":chess.engine.SimpleEngine.popen_uci(args.ethereal),
    }
    for e in engines.values(): configure_engine(e)

    cfg=maia_parse_args([
        "--model","maia3-5m",
        "--checkpoint-path",args.maia_checkpoint,
        "--device","cpu",
        "--no-use-amp",
        "--use-uci-history",
        "--multipv","20",
        "--temperature","0",
    ])
    maia=Maia3UCIEngine(cfg)
    maia.ensure_model_loaded()

    out=[]
    try:
        for i,case in enumerate(cases,1):
            row=score_case(case,engines,maia)
            out.append(row)
            print("G10_P1_SCORE",i,len(cases),case["case_id"],row.get("refined_gate",{}).get("admitted"),flush=True)
    finally:
        for e in engines.values():
            e.quit()

    Path(args.out).write_text(json.dumps({
        "schema":"c3x-g10-p1-score-shard-v1",
        "case_count":len(out),
        "cases":out,
        "fresh_local_certificate_induction_opened":False,
    },indent=2,sort_keys=True)+"\n",encoding="utf-8")


if __name__=="__main__":
    main()
