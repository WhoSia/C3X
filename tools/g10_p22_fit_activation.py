#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,math
from pathlib import Path
from collections import defaultdict
import numpy as np
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder,StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.tree import DecisionTreeClassifier,export_text
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import confusion_matrix

RIVALS={
 "R0_BOUNDARY_ONLY":{
   "num":["base_target_gap_cp","base_subset_gap_cp","base_sham_gap_cp","base_max_gap_cp","base_min_slack_to_50cp"],
   "cat":["base_support_pattern","family"]
 },
 "R1_BOUNDARY_PLUS_LOAD":{
   "num":["base_target_gap_cp","base_subset_gap_cp","base_sham_gap_cp","base_max_gap_cp","base_min_slack_to_50cp",
          "family_event_count_total","family_event_count_target","family_event_count_subset","family_event_count_sham",
          "event_ply_median","event_depth_median","event_scope_balance","candidate_side_event_imbalance"],
   "cat":["base_support_pattern","base_activity_bucket","base_qshare_bucket","family"]
 },
 "R2_CONTEXT_GATED":{
   "num":["base_target_gap_cp","base_subset_gap_cp","base_sham_gap_cp","base_max_gap_cp","base_min_slack_to_50cp",
          "family_event_count_total","family_event_count_target","family_event_count_subset","family_event_count_sham",
          "event_ply_median","event_depth_median","event_scope_balance","candidate_side_event_imbalance","material_imbalance"],
   "cat":["base_support_pattern","base_activity_bucket","base_qshare_bucket","family","phase","legal_branching","tactical_surface",
          "in_check","candidate_tactical_mode","relation_atom_family","chain_type"]
 },
 "R3_ENGINE_CONDITIONAL":{
   "num":["base_target_gap_cp","base_subset_gap_cp","base_sham_gap_cp","base_max_gap_cp","base_min_slack_to_50cp",
          "family_event_count_total","family_event_count_target","family_event_count_subset","family_event_count_sham",
          "event_ply_median","event_depth_median","event_scope_balance","candidate_side_event_imbalance","material_imbalance"],
   "cat":["base_support_pattern","base_activity_bucket","base_qshare_bucket","family","phase","legal_branching","tactical_surface",
          "in_check","candidate_tactical_mode","relation_atom_family","chain_type","engine","family_x_engine"]
 }
}
ORDER=list(RIVALS)
def load(p):return json.loads(Path(p).read_text())
def matrix(rows,cols):
    return [[r.get(c) for c in cols] for r in rows]
def fold_metric(y,p):
    y=np.asarray(y);p=np.asarray(p);classes=set(y.tolist())
    tp=int(((y==1)&(p==1)).sum());fn=int(((y==1)&(p==0)).sum());tn=int(((y==0)&(p==0)).sum());fp=int(((y==0)&(p==1)).sum())
    tpr=tp/(tp+fn) if tp+fn else None;tnr=tn/(tn+fp) if tn+fp else None
    if tpr is not None and tnr is not None:score=(tpr+tnr)/2
    elif tpr is not None:score=tpr
    else:score=tnr
    return {"score":score,"positive_recall":tpr,"negative_specificity":tnr,"tp":tp,"fn":fn,"tn":tn,"fp":fp}
def pipe(spec,kind):
    num=spec["num"];cat=spec["cat"]
    tr=ColumnTransformer([("num",StandardScaler() if kind=="logistic" else "passthrough",num),
                          ("cat",OneHotEncoder(handle_unknown="ignore",sparse_output=False),cat)],remainder="drop")
    if kind=="tree":m=DecisionTreeClassifier(max_depth=3,min_samples_leaf=4,class_weight="balanced",random_state=0)
    else:m=LogisticRegression(C=1.0,class_weight="balanced",max_iter=5000,solver="liblinear",random_state=0)
    return Pipeline([("prep",tr),("model",m)]),num+cat
def loeo(rows,spec,kind):
    ec=sorted({r["source_id"] for r in rows});folds=[]
    for hold in ec:
        train=[r for r in rows if r["source_id"]!=hold];test=[r for r in rows if r["source_id"]==hold]
        cols=spec["num"]+spec["cat"];Xtr=matrix(train,cols);ytr=[r["activation"] for r in train];Xte=matrix(test,cols);yte=[r["activation"] for r in test]
        model,_=pipe(spec,kind);model.fit(Xtr,ytr);pred=model.predict(Xte)
        m=fold_metric(yte,pred);m.update({"ecology":hold,"n":len(test),"positives":sum(yte)});folds.append(m)
    score=sum(x["score"] for x in folds)/len(folds)
    positive_ecologies=[x for x in folds if x["positives"]>0]
    pos_nonzero=sum((x["positive_recall"] or 0)>0 for x in positive_ecologies)
    return {"score":score,"folds":folds,"positive_ecologies_with_nonzero_recall":pos_nonzero}
def main():
    ap=argparse.ArgumentParser();ap.add_argument("--dataset",required=True);ap.add_argument("--out",required=True);a=ap.parse_args()
    D=load(a.dataset);rows=D["rows"]
    results={}
    for rid in ORDER:
        tree=loeo(rows,RIVALS[rid],"tree");log=loeo(rows,RIVALS[rid],"logistic")
        results[rid]={"tree":tree,"logistic_secondary":log}
    selected=ORDER[0]
    for rid in ORDER[1:]:
        max_simpler=max(results[x]["tree"]["score"] for x in ORDER[:ORDER.index(rid)])
        if results[rid]["tree"]["score"]>=max_simpler+0.10 and results[rid]["tree"]["positive_ecologies_with_nonzero_recall"]>=2:
            selected=rid
            break
    spec=RIVALS[selected];cols=spec["num"]+spec["cat"];X=matrix(rows,cols);y=[r["activation"] for r in rows]
    model,_=pipe(spec,"tree");model.fit(X,y)
    prep=model.named_steps["prep"];names=list(prep.get_feature_names_out());tree=model.named_steps["model"]
    rules=export_text(tree,feature_names=names,max_depth=3)
    importances=sorted([{"feature":n,"importance":float(v)} for n,v in zip(names,tree.feature_importances_) if v>0],key=lambda z:-z["importance"])
    positive_sources=sorted({r["source_id"] for r in rows if r["activation"]})
    out={"schema":"c3x-g10-p22-development-activation-field-v1","stage":"C3X 0.10.0-G10-P22",
         "dataset_verdict":D["verdict"],"rows":len(rows),"positives":sum(y),"rivals":results,"selected_rival":selected,
         "selection_rule":"simplest rival with >=0.10 LOEO improvement over every simpler rival and nonzero positive recall in >=2 positive ecologies; otherwise retain simpler rival",
         "tree_rules":rules,"tree_nonzero_importances":importances,
         "authority":"DEVELOPMENT_ONLY","source_identity_used_as_feature":False,
         "heldout_transport_authority":False}
    Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps({k:out[k] for k in ("rows","positives","selected_rival","rivals","tree_nonzero_importances")},indent=2,sort_keys=True))
if __name__=="__main__":main()
