#!/usr/bin/env python3
"""P37/R5: retrospective actual human continuation audit, not optimal chess play.

Use exactly the sealed R1 source and pre-referee R2 predictions.
Counterfactual root branches have no observed human reply label.
"""
from __future__ import annotations
import argparse, hashlib, json, re, zipfile
from pathlib import Path

SOURCE_ZIP_SHA256="3f16f69c6cb01029c519aeb24654913303916ce79537c1a86497bb9c84b79191"
SOURCE_JSON_SHA256="77ebaa409e7c2099cc6cce3419c2f55ded295d925ab441dc2d13c16b67c2c361"
PRED_ZIP_SHA256="721471da43d0bd973e2b084fc47070f5a5826d0add38cbc39a2ccfbca6a427f6"
PRED_JSON_SHA256="da395f0eb16e7b294af2056dadd92b579770aa8f1ae288d1d358132685807051"
SOURCE_MEMBER="P37_R1_8_EVENT_8_GAME_SOURCE_ONLY_MANIFEST.json"
PRED_MEMBER="P37_R2_THREE_RIVAL_PRE_REFERENCE_PREDICTIONS.json"
METHODS=("stockfish_pv","simple_json","c3x_legal_plan")
UCI=re.compile(r"^[a-h][1-8][a-h][1-8][qrbn]?$")

def sha(data):
    return hashlib.sha256(data).hexdigest()

def need(ok,code):
    if not ok:raise ValueError("P37_R5_HOLD_"+code)

def load(original,outer_hash,member,inner_hash):
    raw=Path(original).read_bytes()
    need(sha(raw)==outer_hash,"ZIP_HASH_"+member)
    with zipfile.ZipFile(original) as z:
        body=z.read(member)
    need(sha(body)==inner_hash,"MEMBER_HASH_"+member)
    return json.loads(body)

def audit(src,pred):
    need(src["status"]=="EIGHT_EVENT_SOURCE_ONLY_FROZEN_HISTORY_LEDGER_GATE_PENDING","SOURCE_STATUS")
    need(pred["status"]=="PRE_REFEREE_FROZEN_THREE_RIVAL_RESPONSE_FORECASTS","PRED_STATUS")
    ss=src["sources"];pp=pred["cases"]
    need(len(ss)==len(pp)==8,"EIGHT_CASES")
    need(len(set(s["event_family"] for s in ss))==8,"EVENT_DUPLICATE")
    observed=[];censored=[];counts={m:0 for m in METHODS}
    pair={"pv_only_vs_c3x":0,"c3x_only_vs_pv":0,"both_pv_c3x":0,"neither_pv_c3x":0}
    for i,(s,p) in enumerate(zip(ss,pp)):
        c=s["selected"];history=c["full_game_uci"];ply=c["fixed_ply"]
        need(s["source_id"]==p["source_id"]==c["source_id"],"SOURCE_ID")
        need(c["case_id"]==p["case_id"],"CASE_ID")
        need(len(history)>=60 and ply==p["fixed_ply"]==30,"GAME_LENGTH_AND_PLY")
        need(sha(" ".join(history).encode("ascii"))==c["full_game_uci_sha256"]==p["original_game_sha256"],"GAME_HISTORY_SHA")
        need(history[:ply]==p["original_prefix_uci"],"PREFIX")
        need(c["frozen_fen"]==p["frozen_fen"],"FEN")
        played,human_reply=history[ply],history[ply+1]
        need(bool(UCI.fullmatch(played)) and bool(UCI.fullmatch(human_reply)),"HUMAN_UCI")
        candidates=p["candidate_pairs"]
        need(len(candidates)==2 and len({v["root_uci"] for v in candidates})==2,"TWO_ROOTS")
        matched=next((v for v in candidates if v["root_uci"]==played),None)
        if matched is None:
            censored.append({"case_id":c["case_id"],"source_id":s["source_id"],"played_root":played,
                "engine_roots":[v["root_uci"] for v in candidates],
                "label_state":"COUNTERFACTUAL_HUMAN_REPLY_UNOBSERVED"})
            continue
        predictions={m:matched["predictions"][m]["reply"] for m in METHODS}
        outcomes={m:(predictions[m] is not None and predictions[m]==human_reply) for m in METHODS}
        for m in METHODS:
            if predictions[m] is not None:need(bool(UCI.fullmatch(predictions[m])),"PRED_FORMAT")
            counts[m]+=int(outcomes[m])
        a,b=outcomes["stockfish_pv"],outcomes["c3x_legal_plan"]
        if a and b:pair["both_pv_c3x"]+=1
        elif a:pair["pv_only_vs_c3x"]+=1
        elif b:pair["c3x_only_vs_pv"]+=1
        else:pair["neither_pv_c3x"]+=1
        observed.append({"case_id":c["case_id"],"source_id":s["source_id"],
            "played_root":played,"observed_human_reply":human_reply,
            "predictions":predictions,"correct":outcomes})
    need(len(observed)+len(censored)==8,"COMPLETE_DENOMINATOR")
    return {"status":"P37_R5_POSTHOC_HUMAN_CONTINUATION_AUDIT_NOT_CHESS_VALUE_CERTIFICATION",
       "source_events":8,"observed_human_reply_labels":len(observed),
       "counterfactual_unobserved":len(censored),"hits":counts,"paired_pv_c3x":pair,
       "observed":observed,"unobserved":censored,
       "limits":["retrospective secondary test after source selection",
       "human move is behavior, not unique correct minimax reply",
       "only actual played root can have observed human reply",
       "full historical event/game overlap still HOLD",
       "C3X model is finite material 3-ply heuristic, not full mechanistic C3X"]}

def main():
    p=argparse.ArgumentParser()
    for n in ("source-zip","predictions-zip","out"):p.add_argument("--"+n,required=True)
    a=p.parse_args()
    result=audit(
      load(a.source_zip,SOURCE_ZIP_SHA256,SOURCE_MEMBER,SOURCE_JSON_SHA256),
      load(a.predictions_zip,PRED_ZIP_SHA256,PRED_MEMBER,PRED_JSON_SHA256))
    Path(a.out).write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n")
    print("P37_R5_HUMAN_CONTINUATION",result["observed_human_reply_labels"],result["hits"])

if __name__=="__main__":main()
