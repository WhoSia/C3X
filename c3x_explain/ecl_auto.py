"""I10-P4 preoutcome-first automatic moment selection for real PGNs.

Preserves I9 auto-selection exactly (historical 0/3 negative). Uses only
*legally replayable game state and played move*, not engine MultiPV hindsight, to
rank a bounded set of moments, then calls existing original-source focus CLI
for each. Coverage measured over all eligible original game positions AND
attempts; invalid/abstaining source remains visible.
"""
from __future__ import annotations
import argparse, io, json
from pathlib import Path
import chess
import chess.pgn
from .ecl_focus import run_focussed_pgn
from .ecl_tiny_selector import select, QUESTIONS

SCHEMA="c3x-ecl-i10-p4-preoutcome-automatic-focus-v1"

def preselect(pgn:str,*,max_moments:int=3,min_ply:int=10)->dict:
    if not isinstance(max_moments,int) or not 1<=max_moments<=20:
        raise ValueError("INVALID_MAX_MOMENTS")
    if not isinstance(min_ply,int) or not 1<=min_ply<=1000:
        raise ValueError("INVALID_MIN_PLY")
    game=chess.pgn.read_game(io.StringIO(pgn))
    if game is None or game.errors:raise ValueError("UNREPLAYABLE_OR_EMPTY_PGN")
    board=game.board()
    eligible=[]
    excluded=[]
    for ply,m in enumerate(game.mainline_moves(),1):
        if not board.is_valid() or m not in board.legal_moves:
            raise ValueError("ILLEGAL_GAME_HISTORY")
        if ply<min_ply:
            excluded.append({"ply":ply,"reason":"PREDECLARED_EARLY_GAME_EXCLUSION"})
        elif board.is_game_over(claim_draw=False) or board.legal_moves.count()<2:
            excluded.append({"ply":ply,"reason":"NO_TWO_LEGAL_NONTERMINAL_CANDIDATES"})
        else:
            # Prior to any engine analysis. 'Played move' can be a mistake;
            # it must not be relabeled source bestmove by the model.
            score=(4 if board.gives_check(m) else 0)+(3 if board.is_capture(m) else 0)+(
                 3 if board.is_castling(m) else 0)+(3 if m.promotion else 0)
            legal_candidates=board.legal_moves.count()
            eligible.append({"ply":ply,"played_uci":m.uci(),"played_san":board.san(m),
                             "salience_score":score,"legal_move_count":legal_candidates,
                             "salience_basis":"BOARD_AND_PLAYED_MOVE_BEFORE_ENGINE_ONLY"})
        board.push(m)
    # Fixed deterministic tie break: higher board salience, earlier ply; no
    # cherry picking based on emit success or any engine signal.
    selected=sorted(eligible,key=lambda x:(-x["salience_score"],x["ply"]))[:max_moments]
    return {
       "schema":"c3x-ecl-i10-p4-preoutcome-ranking-v1",
       "original_total_plies":len(eligible)+len(excluded),
       "eligible_count":len(eligible),
       "excluded_count":len(excluded),
       "excluded":excluded,
       "ranking_rule":"BOARD_PREOUTCOME_CHECK_CAPTURE_CASTLE_PROMOTION_V1",
       "chosen_before_any_ENGINE_ANALYSIS":True,
       "max_moments":max_moments,
       "selected":selected,
       "not_attempted_eligible_count":len(eligible)-len(selected),
       "chosen_for_source_analysis_count":len(selected),
    }

def run_auto(pgn:str,engine_path:str,*,max_moments:int=3,
             min_ply:int=10,scout_depth:int=9,pair_depth:int=12,
             disable_nnue:bool=False,question:str="ENGINE_PREFERENCE",
             model:dict|None=None)->dict:
    if question not in QUESTIONS:raise ValueError("UNKNOWN_QUESTION")
    plan=preselect(pgn,max_moments=max_moments,min_ply=min_ply)
    outcomes=[]
    for z in plan["selected"]:
        try:
            receipt=run_focussed_pgn(pgn,engine_path,z["ply"],
                scout_depth=scout_depth,pair_depth=pair_depth,
                disable_nnue=disable_nnue)
            compiled=receipt["ecl"]
            selection=select(compiled,question,model=model)
            result={"ply":z["ply"],"preoutcome":z,"source_rival":receipt["source_selected_distinct_rival"],
                    "source_evidence":receipt["restricted_two_rival_source"],
                    "legacy_I9_firewall_pass":receipt["legacy_I9_firewall_pass"],
                    "ecl":compiled,"selection":selection,
                    "source_trial_status":"EXECUTED"}
        except ValueError as exc:
            # A data/source abstention is an observable failure, not a skipped row.
            result={"ply":z["ply"],"preoutcome":z,
                    "source_trial_status":"SOURCE_INPUT_ABSTAIN",
                    "source_error":str(exc),
                    "selection":{"decision":"ABSTAIN","selected_claim_ids":[],"source_causal_claim":False}}
        outcomes.append(result)
    emitted=sum(x["selection"]["decision"]=="EMIT_BOUNDED_CONVENTIONAL" for x in outcomes)
    return {"schema":SCHEMA,"preselection":plan,
            "source_engine_path":engine_path,"scout_depth":scout_depth,
            "restricted_pair_depth":pair_depth,"question":question,
            "selector_kind":"P4_TRAINED_PROXY" if model else "P3_FROZEN_BASELINE",
            "attempted":len(outcomes),"emitted":emitted,
            "abstained":len(outcomes)-emitted,
            "coverage_per_attempt":None if not outcomes else emitted/len(outcomes),
            "coverage_per_eligible_ply":None if not plan["eligible_count"] else emitted/plan["eligible_count"],
            "result_rows":outcomes,
            "original_I9_default_auto_history_modified":False,
            "selection_is_source_outcome_independent":True,
            "source_causal_authority_new":False,
            "human_utility":None,
            "heldout_generalization":None}

def main()->None:
    ap=argparse.ArgumentParser(description="Preoutcome-only PGN moment ranking and real bounded UCI source ECL")
    ap.add_argument("--pgn",required=True)
    ap.add_argument("--engine",required=True)
    ap.add_argument("--max-moments",type=int,default=3)
    ap.add_argument("--min-ply",type=int,default=10)
    ap.add_argument("--scout-depth",type=int,default=9)
    ap.add_argument("--pair-depth",type=int,default=12)
    ap.add_argument("--disable-nnue",action="store_true")
    ap.add_argument("--question",choices=QUESTIONS,default="ENGINE_PREFERENCE")
    ap.add_argument("--model-json")
    ap.add_argument("--out",required=True)
    a=ap.parse_args()
    model=json.loads(Path(a.model_json).read_text(encoding="utf-8")) if a.model_json else None
    x=run_auto(Path(a.pgn).read_text(encoding="utf-8"),a.engine,
               max_moments=a.max_moments,min_ply=a.min_ply,
               scout_depth=a.scout_depth,pair_depth=a.pair_depth,
               disable_nnue=a.disable_nnue,question=a.question,model=model)
    p=Path(a.out);p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("C3X_ECL_AUTO_P4",x["emitted"],x["attempted"],x["preselection"]["eligible_count"])

if __name__=="__main__":main()
