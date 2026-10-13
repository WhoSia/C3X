"""I10-P5 compact **305-parameter** trained PGN reply-observation selector.

17 chess/engine *pre-reply* features -> 16 tanh hidden units -> sigmoid
reply-match propensity. Real training target: whether the first legal original
engine PV reply for the ACTUAL played move coincides with the recorded next
human move in the historical PGN. Not chess strength, opponent determinism,
human explanation quality or engine search-event causal identification.

Output 'scores' are UNCALIBRATED, and can only choose whether to *show an
already verified optional original-engine PV reply*. It cannot generate a new
move, certify a strategic concept, grant causal authority or label truth.
"""
from __future__ import annotations
import hashlib, json, math
from typing import Any
import chess
import numpy as np

SCHEMA="c3x-i10-p5-305-param-reply-observation-micro-MLP-v1"
FEATURES=(
    "clipped_source_score_gap_cp_200",
    "clipped_played_source_score_cp_500",
    "clipped_leader_source_cp_500",
    "actual_played_source_rank_one",
    "ply_frac_120",
    "original_fullmove_frac_60",
    "original_legal_count_frac_64",
    "original_material_count_frac_32",
    "actual_played_is_capture",
    "actual_played_gives_check",
    "actual_played_is_castle",
    "resulting_opponent_legal_replies_frac_64",
    "actual_played_first_pv_line_len_frac_12",
    "original_source_pair_depth_frac_16",
    "first_pv_reply_is_capture",
    "first_pv_reply_gives_check",
    "original_legal_center_attack_frac_4",
)
D=len(FEATURES)
H=16
PARAMETERS=D*H+H+H+1
assert PARAMETERS==305
SEED=20261013
EPOCHS=160
LEARNING_RATE=0.03
WEIGHT_DECAY=0.035

def _clip(v:float,k:float=3.)->float:
    return float(max(-k,min(k,v)))

def extract(row:dict[str,Any])->dict[str,Any]|None:
    if row.get("source_trial_status")!="EXECUTED":return None
    selection=row.get("selection",{})
    if selection.get("decision")!="EMIT_BOUNDED_CONVENTIONAL":return None
    e=row.get("ecl",{})
    if e.get("source_causal_claim") is not False or e.get("verdict")!="EMIT_BOUNDED_CONVENTIONAL":
        return None
    try:
        board=chess.Board(row["source_fen"])
        u=chess.Move.from_uci(e["played_uci"])
        if not board.is_valid() or u not in board.legal_moves:
            return None
        candidates=row["source_evidence"]
        if len(candidates)!=2 or any(c.get("score_bound") for c in candidates):
            return None
        actual=next(c for c in candidates if c["uci"]==u.uci())
        ranks=[c["rank"] for c in candidates]
        if ranks!=[1,2]:return None
        if any(type(c.get("score_cp")) is not int or type(c.get("depth")) is not int for c in candidates):
            return None
        if candidates[0]["depth"]!=candidates[1]["depth"]:
            return None
        pv=actual.get("pv_uci") or []
        if len(pv)<2 or pv[0]!=u.uci():
            return None
        board_post=board.copy()
        capture=board.is_capture(u); check=board.gives_check(u); castle=board.is_castling(u)
        center=[chess.D4,chess.E4,chess.D5,chess.E5]
        center_attacks=sum(board.is_attacked_by(board.turn,s) for s in center)
        board_post.push(u)
        next_engine=chess.Move.from_uci(pv[1])
        if next_engine not in board_post.legal_moves:
            return None
        reply_capture=board_post.is_capture(next_engine)
        reply_check=board_post.gives_check(next_engine)
        material=sum(len(board.pieces(t,c)) for c in chess.COLORS for t in chess.PIECE_TYPES)
        gap=candidates[0]["score_cp"]-candidates[1]["score_cp"]
        f=[
            _clip(gap/200),_clip(actual["score_cp"]/500),_clip(candidates[0]["score_cp"]/500),
            float(actual["rank"]==1),_clip(row["ply"]/120,1),
            _clip(board.fullmove_number/60,1),
            _clip(board.legal_moves.count()/64,1),
            _clip(material/32,1),
            float(capture),float(check),float(castle),
            _clip(board_post.legal_moves.count()/64,1),
            _clip(len(pv)/12,1),
            _clip(candidates[0]["depth"]/16,2),
            float(reply_capture),float(reply_check),float(center_attacks/4)
        ]
        if len(f)!=D or not all(math.isfinite(x) for x in f):return None
        return {
            "schema":"c3x-i10-p5-before-opponent-reply-features-v1",
            "source_group":row["source_game_id"],
            "original_ply":row["ply"],
            "played_uci":u.uci(),
            "engine_first_legal_predicted_reply":next_engine.uci(),
            "source_candidate_pair":[c["uci"] for c in candidates],
            "features":f,
            "feature_names":list(FEATURES),
            "observed_reply_used_as_model_feature":False,
            "fixed_label_contract":"PGN_NEXT_ACTUAL_HUMAN_REPLY_EXACT_UCI_EQUALS_SOURCE_PV_REPLY",
            "source_causal_warrant_added":False
        }
    except (KeyError,ValueError,TypeError,StopIteration):
        return None

def _weights(raw:dict[str,Any])->tuple[np.ndarray,np.ndarray,np.ndarray,float]:
    if raw.get("schema")!=SCHEMA or raw.get("trained_parameters")!=PARAMETERS or raw.get("feature_names")!=list(FEATURES):
        raise ValueError("MICRO_MLP_MODEL_SCHEMA_OR_DIMENSION_INVALID")
    w=np.asarray(raw["W1"],dtype=np.float64)
    b=np.asarray(raw["b1"],dtype=np.float64)
    v=np.asarray(raw["w2"],dtype=np.float64)
    intercept=float(raw["b2"])
    if w.shape!=(D,H) or b.shape!=(H,) or v.shape!=(H,):
        raise ValueError("MICRO_MLP_WEIGHT_DIMENSIONS_WRONG")
    if not all(np.isfinite(x).all() for x in (w,b,v)) or not math.isfinite(intercept):
        raise ValueError("NONFINITE_TRAINED_WEIGHTS")
    if raw.get("requires_causal_certification") is not False or raw.get("calibrated") is not False:
        raise ValueError("MODEL_SCOPE_INCONSISTENT")
    digest=raw.get("sha256_canonical")
    if digest is not None:
        obj={k:v for k,v in raw.items() if k!="sha256_canonical"}
        canonical=hashlib.sha256(json.dumps(obj,sort_keys=True,separators=(",",":")).encode()).hexdigest()
        if canonical!=digest:raise ValueError("MICRO_MLP_MODEL_SHA256_TAMPER")
    return w,b,v,intercept

def _sigmoid(x:np.ndarray)->np.ndarray:
    return 1/(1+np.exp(-np.clip(x,-40,40)))

def train(rows:list[dict[str,Any]])->dict[str,Any]:
    if len(rows)<6 or len(rows)>10000:
        raise ValueError("INSUFFICIENT_OBSERVED_CHESS_REPLY_TRAINING_ROWS")
    X=np.asarray([r["features"] for r in rows],dtype=np.float64)
    y=np.asarray([r["observed_reply_equals_engine_pv"] for r in rows],dtype=np.float64)
    if X.shape!=(len(rows),D) or not np.isfinite(X).all() or not np.isin(y,[0,1]).all():
        raise ValueError("INVALID_OR_LEAKED_TRAINING_LABELS")
    games=sorted({r["source_group"] for r in rows})
    if len(games)<2:raise ValueError("NEEDS_AT_LEAST_TWO_SOURCE_TRAINING_GAMES")
    rng=np.random.default_rng(SEED)
    w=rng.standard_normal((D,H))*0.08
    b=np.zeros(H)
    v=rng.standard_normal(H)*0.08
    p0=float(np.clip(y.mean(),0.05,0.95))
    b2=float(math.log(p0/(1-p0)))
    for _ in range(EPOCHS):
        a=X@w+b
        h=np.tanh(a)
        p=_sigmoid(h@v+b2)
        diff=(p-y)/len(y)
        gv=h.T@diff + WEIGHT_DECAY*v
        gb2=float(diff.sum())
        ga=(diff[:,None]*v[None,:])*(1-h*h)
        gw=X.T@ga+WEIGHT_DECAY*w
        gb=ga.sum(axis=0)
        w-=LEARNING_RATE*gw;b-=LEARNING_RATE*gb;v-=LEARNING_RATE*gv;b2-=LEARNING_RATE*gb2
    obj={
       "schema":SCHEMA,
       "W1":np.round(w,10).tolist(),"b1":np.round(b,10).tolist(),
       "w2":np.round(v,10).tolist(),"b2":round(b2,10),
       "feature_names":list(FEATURES),"trained_parameters":PARAMETERS,
       "model_class":"TWO_LAYER_17x16x1_REPLY_MATCH_PROPENSITY_NOT_CHESS_RANKER",
       "training_game_groups":games,"train_samples":len(rows),
       "train_positive_reply_matches":int(y.sum()),
       "train_negative_reply_matches":int(len(y)-y.sum()),
       "training_label":"ACTUAL_NEXT_OPPONENT_HUMAN_MOVE_VS_SOURCE_PV_FIRST_REPLY",
       "observed_reply_in_features":False,"calibrated":False,
       "requires_causal_certification":False,
       "warrants_engine_search_cause":False,
       "independent_human_education":None,
       "train_settings":{"seed":SEED,"epochs":EPOCHS,"rate":LEARNING_RATE,"weight_decay":WEIGHT_DECAY}
    }
    obj["sha256_canonical"]=hashlib.sha256(json.dumps(obj,sort_keys=True,separators=(",",":")).encode()).hexdigest()
    _weights(obj)
    return obj

def score(model:dict[str,Any],rows:list[dict[str,Any]],*,test_game_groups:list[str])->list[dict[str,Any]]:
    w,b,v,b2=_weights(model)
    if set(test_game_groups)&set(model["training_game_groups"]):
        raise ValueError("GAME_GROUP_LEAKAGE_IN_EVALUATION")
    X=np.asarray([r["features"] for r in rows],dtype=np.float64).reshape(-1,D)
    if not np.isfinite(X).all():raise ValueError("INPUT_NAN_OR_INF")
    probs=_sigmoid(np.tanh(X@w+b)@v+b2)
    return [{
      "source_group":r["source_group"],"ply":r["original_ply"],
      "actual_played_uci":r["played_uci"],
      "engine_legally_replayed_reply_uci":r["engine_first_legal_predicted_reply"],
      "reply_match_score_UNCALIBRATED":float(p),
      "fixed_threshold_selected_to_show_PV":bool(p>=0.5),
      "source_C3X_causal_concept_claim":False,
      "true_chess_reply_guarantee":None,
      "calibrated_probability":None,
      "no_new_chess_sentence_generated":True,
    } for r,p in zip(rows,probs)]

def report(train_rows:list[dict[str,Any]],eval_rows:list[dict[str,Any]],model:dict[str,Any])->dict:
    train_groups={r["source_group"] for r in train_rows}
    test_groups={r["source_group"] for r in eval_rows}
    if not test_groups or train_groups&test_groups:
        raise ValueError("TRAIN_TEST_GAME_GROUP_OVERLAP")
    scores=score(model,eval_rows,test_game_groups=sorted(test_groups))
    actual=np.asarray([r["observed_reply_equals_engine_pv"] for r in eval_rows],dtype=np.float64)
    if not len(actual):raise ValueError("NO_INDEPENDENT_GAME_TEST_TARGETS")
    prediction=np.asarray([x["reply_match_score_UNCALIBRATED"] for x in scores])
    prevalence=float(np.mean([r["observed_reply_equals_engine_pv"] for r in train_rows]))
    # Distinguish two baselines: constant train prevalence, and always show
    # existing legal PV. Both see same source packets as 305-param model.
    brier=lambda x:float(np.mean((x-actual)**2))
    binary=(prediction>=0.5).astype(float)
    coverage=float(np.mean(prediction>=0.5))
    rows=[dict(x,observed_next_reply_matched_source_pv=bool(r["observed_reply_equals_engine_pv"]))
          for x,r in zip(scores,eval_rows)]
    return {
      "schema":"c3x-i10-p5-original-new-event-heldout-reply-predictor-v1",
      "original_game_train_groups":sorted(train_groups),
      "original_game_test_groups":sorted(test_groups),
      "whole_game_disjoint":True,
      "same_tournament_not_event_disjoint":True,
      "training_rows":len(train_rows),"test_rows":len(eval_rows),
      "train_positive_count":int(sum(r["observed_reply_equals_engine_pv"] for r in train_rows)),
      "test_positive_count":int(actual.sum()),
      "baselines":{
          "TRAIN_PREVALENCE_CONSTANT":{"brier":brier(prevalence),"train_prevalence":prevalence},
          "ALWAYS_SHOW_SOURCE_PV":{"exact_next_reply_match_rate":float(actual.mean())},
      },
      "trained_305_param":{
          "brier_UNCALIBRATED":brier(prediction),
          "raw_binary_accuracy_at_PREDECLARED_0_5":float(np.mean(binary==actual)),
          "show_pv_coverage_at_PREDECLARED_0_5":coverage,
          "observed_match_rate_on_shown":None if not int(binary.sum()) else float(actual[binary==1].mean()),
          "raw_score_not_calibrated_probability":True,
      },
      "per_position_observed_label_and_score":rows,
      "real_Queen_Cui_CCC_responders_compared":False,
      "new_source_causal_Chess_semantic_labels":0,
      "heldout_independent_human_pedagogic_gain":None,
      "scope":"PGN next actual human reply observational match only, not objective best response"
    }
