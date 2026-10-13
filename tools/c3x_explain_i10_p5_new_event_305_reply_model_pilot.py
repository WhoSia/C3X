"""I10-P5: real newly presealed Olympiad 8-game, original SF16 reply-observation ML study.

Train FIRST 4 previously unanalysed 2026 Olympiad games, eval LAST 4
games, frozen by original provider BEFORE source-engine. The observed actual
next human move is ONLY a label, never a feature. No chess understanding,
objective best-reply, language model, human pedagogy or causal event claimed.
"""
from __future__ import annotations
import argparse
import hashlib
import io
import json
from pathlib import Path
import chess.pgn
from c3x_explain.ecl_auto import run_auto
from c3x_explain.ecl_reply305 import extract,train,report,PARAMETERS
from tools.c3x_explain_i10_p5_olympiad_source_targets import SOURCE_SHA,GAME_SHA

def main():
    a=argparse.ArgumentParser()
    a.add_argument("--input",required=True)
    a.add_argument("--raw-source",required=True)
    a.add_argument("--engine",required=True)
    a.add_argument("--out",required=True)
    a.add_argument("--moments",type=int,default=8)
    args=a.parse_args()
    if hashlib.sha256(Path(args.raw_source).read_bytes()).hexdigest()!=SOURCE_SHA:
        raise ValueError("ORIGINAL_OLYMPIAD_SOURCE_SHA_NOT_PRESEALED")
    out=Path(args.out);out.mkdir(parents=True,exist_ok=True)
    groups={"TRAIN":[],"EVAL":[]}
    stats=[]
    records=[]
    for i,gid in enumerate(GAME_SHA):
        pgn=Path(args.input,"game-"+gid+".pgn").read_text(encoding="utf-8")
        game=chess.pgn.read_game(io.StringIO(pgn))
        if game is None or game.errors:raise ValueError("NEW_OLYMPIAD_GAME_UNREPLAYABLE")
        moves=list(game.mainline_moves())
        split="TRAIN" if i<4 else "EVAL"
        output=run_auto(pgn,args.engine,max_moments=args.moments,
                        min_ply=12,scout_depth=9,pair_depth=12,disable_nnue=True)
        output["source_game_group"]=gid
        (out/("native-evidence-"+gid+".json")).write_text(json.dumps(output,ensure_ascii=False,indent=2)+"\n")
        allowed=0;replies=0
        for x in output["result_rows"]:
            x["source_game_id"]=gid
            f=extract(x)
            if f is None:continue
            allowed+=1
            ply=x["ply"]
            if ply>=len(moves):continue # no recorded next reply in source PGN
            observed_next=moves[ply].uci()
            f["observed_reply_equals_engine_pv"]=int(f["engine_first_legal_predicted_reply"]==observed_next)
            f["observed_next_human_reply_uci_AUDIT_LABEL_ONLY"]=observed_next
            f["source_chess_original_fen"]=x["source_fen"]
            f["split"]=split
            groups[split].append(f)
            records.append(f)
            replies+=1
        stats.append({"game_id":gid,"split":split,"original_total_plies":output["preselection"]["original_total_plies"],
                      "eligible":output["preselection"]["eligible_count"],
                      "source_attempts":output["attempted"],"ECL_emitted":output["emitted"],
                      "ECL_abstained":output["abstained"],"feature_rows_qualified":allowed,
                      "historical_next_reply_observations":replies})
        print("C3X_P5_NEW_GAME_NATIVE_SOURCE_REPLY_DATA",gid,split,
              "attempted",output["attempted"],"emitted",output["emitted"],"reply_records",replies,flush=True)
    # Only position-identity FEN, not labels or predictions, determines any
    # cross-split duplicate-exclusion. Game-level split stays unchanged.
    train_fens={z["source_chess_original_fen"] for z in groups["TRAIN"]}
    exact_duplicate_eval=[z for z in groups["EVAL"] if z["source_chess_original_fen"] in train_fens]
    test=[z for z in groups["EVAL"] if z["source_chess_original_fen"] not in train_fens]
    train_rows=groups["TRAIN"]
    if len(train_rows)<6 or len(test)<4:
        raise ValueError("INSUFFICIENT_NEW_FRESH_GAMES_SOURCE_OBSERVATIONS")
    # Training features exclude observed actual replies. No eval game
    # scores or labels are consulted by train().
    model=train(train_rows)
    evaluation=report(train_rows,test,model)
    train_data_label={
        "source_raw_pgn_sha256":SOURCE_SHA,
        "source_game_id_split":{"train":GAME_SHA[:4],"test":GAME_SHA[4:]},
        "all_eight_games_new_to_I10_P4":True,
        "all_source_attempts_included_in_stats":True,
        "features_cannot_read_actual_opponent_move":True,
        "real_source_evaluation":"official original Stockfish 16 NNUE off depth9 scout depth12 restricted played/rival",
        "trained_model_params":PARAMETERS,
        "weak_question_proxy_model_is_separate":"legacy I10-P4 9-parameter router frozen, no replacement",
        "excluded_exact_fen_duplicate_eval_positions":len(exact_duplicate_eval),
        "game_summary":stats,
        "total_eligible_moves":sum(s["eligible"] for s in stats),
        "total_attempts":sum(s["source_attempts"] for s in stats),
        "total_ECL_emits":sum(s["ECL_emitted"] for s in stats),
        "total_ECL_abstains":sum(s["ECL_abstained"] for s in stats),
        "train_observations":len(train_rows),
        "heldout_eval_observations":len(test),
        "original_Queen_Cui_CCC_rival_models_called":False,
        "human_semantic_chess_causal_training_labels":False,
        "independent_human_pedagogic_result":None,
        "actual_human_opponent_response_is_not_objectively_best":True,
        "all_first4_vs_last4_presealed_before_engine":True,
    }
    evaluation.update(train_data_label)
    (out/"new-olympiad-P5-305-model-params.json").write_text(json.dumps(model,ensure_ascii=False,indent=2)+"\n")
    (out/"new-olympiad-P5-305-model-game-disjoint-eval.json").write_text(json.dumps(evaluation,ensure_ascii=False,indent=2)+"\n")
    (out/"new-olympiad-P5-training-actual-next-move-observations.json").write_text(json.dumps(
        [{"source_game_group":r["source_group"],"ply":r["original_ply"],
          "label_only_observed_opponent_reply":r["observed_next_human_reply_uci_AUDIT_LABEL_ONLY"],
          "source_original_pv_opponent_reply":r["engine_first_legal_predicted_reply"],
          "observed_match":r["observed_reply_equals_engine_pv"]} for r in train_rows],
        ensure_ascii=False,indent=2)+"\n")
    print("C3X_P5_ACTUAL_305_PARAM_TRAIN_NEW_GAMES",len(train_rows),
          "positive",model["train_positive_reply_matches"],
          "test",len(test),"eval_positive",evaluation["test_positive_count"],
          "305_BRIER",evaluation["trained_305_param"]["brier_UNCALIBRATED"],
          "BASE_TRAIN_PREVALENCE_BRIER",evaluation["baselines"]["TRAIN_PREVALENCE_CONSTANT"]["brier"],flush=True)
    print("C3X_P5_NEW_SOURCE_ECL_COVERAGE",evaluation["total_ECL_emits"],
          evaluation["total_attempts"],evaluation["total_eligible_moves"],flush=True)

if __name__=="__main__":main()
