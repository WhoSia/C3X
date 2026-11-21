"""C3X 0.31 P2: independent P1-only final model freeze verifier.

The pre-outcome model was sealed before any new native intervention outcomes.
Do not refit on TWIC1670 or use 0.31/P2 outcomes in this program.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
from pathlib import Path
from c3x_031_p1_forecast import PUBLIC, SOURCE, load_rows, value, sigmoid, RIDGE, ITER, STEP

TSV_SHA="6e5cd1215ab13ac3dba3c93447b577f305c06fad1fd00c2b4a5338c71e7a63ba"
MODEL_SHA="f27a89fd15efa3f35738ba8cf2a6d1243c8336268e4661c653bbd1e6c0bfee23"


def require(ok, reason):
    if not ok:
        raise ValueError(reason)


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def fit(rows, features):
    means=[sum(value(r,k) for r in rows)/len(rows) for k in features]
    scales=[]
    for j,key in enumerate(features):
        variance=sum((value(r,key)-means[j])**2 for r in rows)/len(rows)
        scales.append(math.sqrt(variance) if variance>1e-12 else 1.0)
    design=[[1.0]+[(value(r,k)-means[j])/scales[j]
                   for j,k in enumerate(features)] for r in rows]
    positives=sum(r["y"] for r in rows)
    weights=[0.0]*len(design[0])
    weights[0]=math.log((positives+0.5)/(len(rows)-positives+0.5))
    for _ in range(ITER):
        grad=[0.0]*len(weights)
        for sample,features_row in zip(rows,design):
            err=sigmoid(sum(a*b for a,b in zip(weights,features_row)))-sample["y"]
            for j in range(len(weights)):
                grad[j]+=err*features_row[j]/len(rows)
        for j in range(1,len(weights)):
            grad[j]+=RIDGE*weights[j]
        weights=[w-STEP*g for w,g in zip(weights,grad)]
    return {"features":list(features),"means":means,
            "scales":scales,"coefficients":weights}


def verify(frozen_path, source_path):
    actual=Path(frozen_path).read_bytes()
    require(digest(actual)==MODEL_SHA,"preoutcome model bytes unexpectedly changed")
    require(digest(Path(source_path).read_bytes())==TSV_SHA,
            "original P1 training source changed")
    model=json.loads(actual)
    rows=load_rows(source_path)
    require(model["schema"]=="C3X_031_P2_FIXED_MODEL_PRE_OUTCOME_V1"
            and model["used_p2_test_outcomes"] is False
            and model["training_source"]=="R33_exposed_64games_128targets",
            "model source preoutcome authority false")
    require(model["source_p1_tsv_sha256"]==TSV_SHA
            and model["optimizer"]=={
                "iterations":900,"regularization_ridge":.02,"step":.1},
            "optimizer or source not frozen")
    require(len(rows)==128 and sum(r["y"] for r in rows)==11,
            "P1 fit denominator mismatch")
    require(model["label_positives"]==11 and
            abs(model["m0"]["prevalence"] - 11.5/129)<1e-14,
            "M0 prior changed")
    for name,features in (("m1",PUBLIC),("m2",PUBLIC+SOURCE)):
        independently_fit=fit(rows,features)
        for key in ("means","scales","coefficients"):
            require(len(independently_fit[key])==len(model[name][key]),
                    "wrong model dimensionality")
            require(all(abs(a-b)<1e-12 for a,b in zip(
                independently_fit[key],model[name][key])),
                "model is not the frozen full P1 fit: "+name+" "+key)
        require(independently_fit["features"]==model[name]["features"],
                "feature order changed")
    return {"status":"P2_MODEL_FIT_FROZEN_PRE_NEW_TREATMENT",
            "P1_label_source_only":True,"P2_treatments_seen":0,
            "P1_rows":128,"P1_positive":11,"fullfit_models":["m0","m1","m2"],
            "model_sha256":MODEL_SHA,"training_tsv_sha256":TSV_SHA}


def predict(model,row,name):
    if name=="m0":return model["m0"]["prevalence"]
    table=model[name]
    transformed=[]
    for key,mu,scale in zip(table["features"],table["means"],table["scales"]):
        if key not in row:
            raise ValueError("Missing pre-treatment feature "+key)
        transformed.append((value(row,key)-mu)/scale)
    return sigmoid(sum(w*x for w,x in zip(table["coefficients"],[1.0]+transformed)))


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("model",type=Path)
    ap.add_argument("p1_source",type=Path)
    ap.add_argument("out",type=Path)
    args=ap.parse_args()
    verdict=verify(args.model,args.p1_source)
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(verdict,indent=2,sort_keys=True)+"\n")
    print(json.dumps(verdict,sort_keys=True))


if __name__=="__main__":
    main()
