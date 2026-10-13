"""C3X P5 305-parameter actual training: integrity and scientific anti-overclaim."""
import copy
import math
import pytest
from c3x_explain.ecl_test_fixture import base
from c3x_explain.evidence_compiler import compile_evidence
from c3x_explain.ecl_reply305 import FEATURES,PARAMETERS,SCHEMA,train,score,report,extract

def fixture(group="TRAIN_A",ply=1,label=1):
    features=[0.0]*len(FEATURES)
    features[0]=0.2 if label else 1.0
    features[1]=0.3 if label else -0.4
    features[3]=1.0 if label else 0.0
    return {"source_group":group,"original_ply":ply,
            "played_uci":"e2e4","engine_first_legal_predicted_reply":"e7e5",
            "features":features,
            "observed_reply_equals_engine_pv":label}

def trained():
    data=[fixture("TRAIN_A",i, i%2) for i in range(1,6)]+[
          fixture("TRAIN_B",i+6,i%2) for i in range(1,6)]
    return data,train(data)

def test_parameter_count_and_frozen_17_input_schema():
    d,m=trained()
    assert PARAMETERS==305
    assert m["trained_parameters"]==305
    assert m["feature_names"]==list(FEATURES)
    assert m["train_samples"]==10
    assert m["training_label"]=="ACTUAL_NEXT_OPPONENT_HUMAN_MOVE_VS_SOURCE_PV_FIRST_REPLY"
    assert m["calibrated"] is False and m["warrants_engine_search_cause"] is False

def test_actual_training_updates_weights_and_predicts_finite_uncalibrated_score():
    _,m=trained()
    res=score(m,[fixture("EVAL_C",55,1)],test_game_groups=["EVAL_C"])
    assert 0<=res[0]["reply_match_score_UNCALIBRATED"]<=1
    assert res[0]["calibrated_probability"] is None
    assert res[0]["no_new_chess_sentence_generated"]
    assert not res[0]["source_C3X_causal_concept_claim"]

def test_whole_game_split_strictly_fails_on_overlap():
    d,m=trained()
    with pytest.raises(ValueError,match="LEAKAGE"):
        score(m,[fixture("TRAIN_A",99,1)],test_game_groups=["TRAIN_A"])
    with pytest.raises(ValueError,match="OVERLAP"):
        report(d,[fixture("TRAIN_B",3,1)],m)

def test_hash_tamper_and_missing_dimensions_fail():
    _,m=trained()
    forged=copy.deepcopy(m)
    forged["W1"][0][0]+=1
    with pytest.raises(ValueError,match="SHA256_TAMPER"):
        score(forged,[fixture("EVAL_C",3,1)],test_game_groups=["EVAL_C"])
    forged=copy.deepcopy(m);forged["feature_names"]=["invented"]
    with pytest.raises(ValueError,match="SCHEMA_OR_DIMENSION"):
        score(forged,[fixture("EVAL_C",3,1)],test_game_groups=["EVAL_C"])

def test_actual_next_move_not_present_in_chess_features():
    b=base()
    p=compile_evidence(b)
    row={"source_game_id":"A","source_trial_status":"EXECUTED",
         "selection":{"decision":"EMIT_BOUNDED_CONVENTIONAL"},
         "source_fen":b["fen"],"ply":1,"ecl":p,
         "source_evidence":b["candidates"]}
    f=extract(row)
    assert f is not None
    assert len(f["features"])==17
    assert f["observed_reply_used_as_model_feature"] is False
    assert "observed_next_move" not in f
    assert f["engine_first_legal_predicted_reply"]=="e7e5"
    row["observed_next_human_reply_uci"]="e7e5"
    assert extract(row)["features"]==f["features"]

def test_original_legacy_abstention_never_becomes_learning_example():
    b=base();p=compile_evidence(b)
    p["verdict"]="ABSTAIN"
    row={"source_trial_status":"EXECUTED","selection":{"decision":"EMIT_BOUNDED_CONVENTIONAL"},
         "ecl":p,"source_fen":b["fen"],"source_evidence":b["candidates"],"ply":1}
    assert extract(row) is None

def test_actual_observed_next_move_is_label_not_best_reply_theorem():
    d,m=trained()
    test=[fixture("EVAL_C",i,i%2) for i in range(1,5)]
    x=report(d,test,m)
    assert x["test_rows"]==4
    assert x["new_source_causal_Chess_semantic_labels"]==0
    assert x["heldout_independent_human_pedagogic_gain"] is None
    assert x["whole_game_disjoint"]
    assert "brier_UNCALIBRATED" in x["trained_305_param"]

def test_single_game_training_is_rejected_even_with_many_plies():
    with pytest.raises(ValueError,match="TWO_SOURCE_TRAINING_GAMES"):
        train([fixture("ONLY",i,i%2) for i in range(1,11)])
