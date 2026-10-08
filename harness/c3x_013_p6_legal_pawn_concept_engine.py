#!/usr/bin/env python3
"""Real UCI for two FROZEN synthetic legal-root concept toggles; NO mediator claim."""
import argparse
import hashlib
import json
from pathlib import Path
import chess
import chess.engine
from c3x_explain.concepts import snapshot

FIXTURES=[
 {"id":"PASSED_BOUNDARY","fen":"4k3/8/p7/2p5/P2P4/8/8/4K3 w - - 0 1",
  "treated":"d4d5","control":"a4a5","concept":"own_passed_pawn_count"},
 {"id":"ISOLATION_CAPTURE","fen":"4k3/8/8/1p2p3/2PP1P2/8/8/4K3 w - - 0 1",
  "treated":"c4b5","control":"d4e5","concept":"own_isolated_pawn_count"}
]
DEPTHS=[8,12,16]

def cp_pair(engine,b,roots,depth):
    with chess.engine.SimpleEngine.popen_uci(engine,timeout=30) as e:
        e.configure({"Threads":1,"Hash":16})
        rows=e.analyse(b,chess.engine.Limit(depth=depth),multipv=2,root_moves=roots)
    result={}
    for item in rows:
        pv=item.get("pv")
        score=item.get("score")
        if not pv or score is None:continue
        value=score.pov(b.turn).score(mate_score=None)
        if value is None:continue
        result[pv[0].uci()]={"cp":value,"depth":item.get("depth"),
                            "nodes":item.get("nodes"),"pv":[m.uci() for m in pv[:8]]}
    if len(result)!=2 or any(z.uci() not in result for z in roots):
        return {"status":"HOLD_MATE_OR_INCOMPLETE","raw":result}
    a,c=(result[m.uci()] for m in roots)
    if a["depth"] is None or a["depth"]!=c["depth"] or a["depth"]<depth:
        return {"status":"HOLD_UNEQUAL_OR_INCOMPLETE_DEPTH","raw":result}
    return {"status":"RAW_COMPARABLE_CP","depth":depth,
            "treated_cp":a["cp"],"control_cp":c["cp"],
            "treated_minus_control_cp":a["cp"]-c["cp"],"raw":result}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--engine",default="/usr/games/stockfish")
    p.add_argument("--output",required=True)
    a=p.parse_args()
    answer={"schema":"c3x-013-p6-legal-pawn-concept-toggles-v1",
            "status":"SYNTHETIC_CHESS_FIXTURE_ENGINE_OBSERVATION_ONLY",
            "engine_sha256":hashlib.sha256(Path(a.engine).read_bytes()).hexdigest(),
            "depths":DEPTHS,"independent_engine_restarts":2,
            "fixture_natural_games":0,"causal_mediator_identified":False,
            "source_independent_replication":False,"results":[]}
    for f in FIXTURES:
        b=chess.Board(f["fen"])
        assert b.is_valid() and not b.is_game_over()
        moves=[chess.Move.from_uci(f[k]) for k in ("treated","control")]
        assert all(m in b.legal_moves for m in moves)
        facts={}
        for name,move in zip(("treated","control"),moves):
            after=b.copy(stack=False)
            before=snapshot(b,b.turn)
            after.push(move)
            aft=snapshot(after,b.turn)
            facts[name]={"before":before[f["concept"]],"after":aft[f["concept"]],
                         "delta":aft[f["concept"]]-before[f["concept"]],
                         "full_descriptive_feature_deltas":{k:a-before[k] for k,a in aft.items()
                                                            if a!=before[k]}}
        assert facts["treated"]["delta"]!=facts["control"]["delta"]
        record={"id":f["id"],"fen":f["fen"],"fen_sha256":hashlib.sha256(f["fen"].encode()).hexdigest(),
                "root_uci":[m.uci() for m in moves],"concept":f["concept"],
                "concept_rule_facts":facts,"measurements":{}}
        for d in DEPTHS:
            trials=[cp_pair(a.engine,b,moves,d) for _ in range(2)]
            comparable=all(x["status"]=="RAW_COMPARABLE_CP" for x in trials)
            repeated=comparable and (trials[0]["treated_minus_control_cp"]==
                                     trials[1]["treated_minus_control_cp"])
            record["measurements"][str(d)]={"trials":trials,"same_cp_repeated":repeated,
                                             "status":"DEVELOPMENT_RAW_RANK_ONLY" if repeated else "HOLD_REPEAT_OR_SCORE"}
        answer["results"].append(record)
    answer["claim_ceiling"]="LEGAL_ROOT_CHESS_RULE_AND_ENGINE_RANK_NOT_CONCEPT_MEDIATION"
    Path(a.output).parent.mkdir(parents=True,exist_ok=True)
    Path(a.output).write_text(json.dumps(answer,indent=2)+"\n")
    print("P6_PAWN_ENGINE_FROZEN_RANKS",[(x["id"],{d:r["trials"][0].get("treated_minus_control_cp")
        for d,r in x["measurements"].items()}) for x in answer["results"]])
    print("P6_CAUSAL_MECHANISM_ADMISSION",False)
if __name__=="__main__":
    main()
