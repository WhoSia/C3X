"""C3X 0.31/P2-B3: independent actual raw 1280 transcript audit.

Strictly derived: this performs NO NEW Stockfish searches and does not
retrain P1 or modify P2-B1/B2 events. Source checks physically executed
sham, both-off and futility-only arms in source stdout+stderr, followed
by independent Brier/AP computation from frozen pre-outcome predictions.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path
from zipfile import ZipFile
import re

EXPECTED_RAW_ZIP_SHA="6cf37ae5902131cd592b7dcb1893d8845eb24fbb154f3a35afcaf8d9bee4ae6c"
EXPECTED_B2_PRIVATE_SHA="be66a985016b4ceaae1379c64ee0f6347c3a2e8c4fd3660ceb394227ac237df1"
EXPECTED_B1_SHA="d364e6ca24599110fa19ac41e19164069a164c15aa396aac6b2833482e3818b1"
EXPECTED_SCORE_SHA="2fd97e80e04aaae039fe9ee5cf5e1c75d75406803af40c4d8c0a6ab7d1448420"
ARMS=("sham0","sham1","both_off0","both_off1","futility_only")


def require(ok,detail):
    if not ok:
        raise ValueError(detail)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def parse_event(line):
    parts=line.strip().split()
    out={}
    for field in parts[1:]:
        require("=" in field,"native log field lacks assignment")
        key,val=field.split("=",1)
        require(key not in out,"duplicate native key")
        out[key]=val
    return out


def raw_event(stderr, event_id):
    op,cl=[],[]
    for line in stderr.decode().splitlines():
        if line.startswith("C3X_R33_OPEN "):
            item=parse_event(line)
            if item.get("event")==event_id:
                op.append(item)
        if line.startswith("C3X_R33_CLOSE "):
            item=parse_event(line)
            if item.get("event")==event_id:
                cl.append(item)
    require(len(op)==len(cl)==1,"original physical source event absent or duplicated")
    return {"open":op[0],"close":cl[0]}


def raw_best(stdout):
    tokens=[x.split()[1] for x in stdout.decode().splitlines()
            if x.startswith("bestmove ")]
    require(len(tokens)==1,"raw original UCI has no unique final bestmove")
    return tokens[0]


def tied_ap(labels, scores):
    m=sum(labels)
    if m==0:return None
    groups={}
    for y,p in zip(labels,scores):
        n,k=groups.get(p,(0,0))
        groups[p]=(n+1,k+y)
    seen=got=0
    ap=0.
    for score in sorted(groups,reverse=True):
        n,k=groups[score]
        seen+=n
        got+=k
        ap+=(k/m)*(got/seen)
    return ap


def independent_scores(entries):
    require(len(entries)==126,"original model abstained on exactly two source targets")
    ys=[row["y"] for row in entries]
    out={}
    for key in ("m0","m1","m2"):
        ps=[row["predictions"][key] for row in entries]
        out[key]={
            "brier":sum((p-y)**2 for p,y in zip(ps,ys))/len(ys),
            "average_precision":tied_ap(ys,ps),
            "predicted_positive_at_0_5":sum(p>=.5 for p in ps),
            "true_positive_at_0_5":sum(y==1 and p>=.5 for y,p in zip(ys,ps)),
        }
    return out


def audit(source_b1_path, source_b2_path, native_logs, scored_path):
    b1raw=Path(source_b1_path).read_bytes()
    b2raw=Path(source_b2_path).read_bytes()
    score_raw=Path(scored_path).read_bytes()
    require(digest(b1raw)==EXPECTED_B1_SHA,"B1 original target forecasts changed")
    require(digest(b2raw)==EXPECTED_B2_PRIVATE_SHA,"B2 native treatment label/receipt drifted")
    require(digest(score_raw)==EXPECTED_SCORE_SHA,"original B2 independent court changed")
    b1=json.loads(b1raw)
    b2=json.loads(b2raw)
    score=json.loads(score_raw)
    root=Path(native_logs)
    archive=None
    if root.is_file():
        require(digest(root.read_bytes())==EXPECTED_RAW_ZIP_SHA,
                "original 640-process raw ZIP byte seal changed")
        archive=ZipFile(root)
        require(archive.testzip() is None,"raw source transcript ZIP CRC failure")
        names=archive.namelist()
        require(len(names)==1280 and len(set(names))==1280,
                "original 1280 transcript files incomplete")
    else:
        names=[str(p.relative_to(root)) for p in root.rglob("*.txt")]
        require(len(names)==1280 and len(set(names))==1280,
                "decompressed original transcript file census mismatch")
    def read(name):
        if archive:return archive.read(name)
        return (root/name).read_bytes()

    sources={r["id"]:r for r in b1["native_source_records"]}
    events=b2["source_event_results"]
    require(len(sources)==64 and len(events)==128,"original physical source denominator")
    counts={"sham":0,"both_off":0,"futility_only":0}
    exact_raw={"stderr_sha_matches":0,"source_events_equal":0,
               "raw_final_best_matches":0,"raw_sham_pair_equal":0,
               "raw_treatment_pair_equal":0}
    all_pred=[]
    changes=[]
    for row in events:
        case=sources[row["case_id"]]
        before=case["targets"][row["group"]]
        require(before["native_open_close"]["open"]==row["original_target"],
                "source pretreatment source event was reselected")
        require(case["original_untreated_bestmove"]==row["original_untreated_bestmove"],
                "source original move changed between B1 and B2")
        require(before.get("frozen_m0_m1_m2_forecasts")==row["predictions"],
                "actual B2 labels used a different P1-predicted probability")
        require(row["valid_primary"] and row["invalid_reason"] is None
                and row["y"] in (0,1),"original B2 physical source validity compromised")
        require(set(row["arms"])==set(ARMS),
                "genuine source arm missing")
        raw={}
        for arm in ARMS:
            path=row["id"]+"/"+arm
            stderr=read(path+"/stderr.txt")
            stdout=read(path+"/stdout.txt")
            arm_record=row["arms"][arm]
            require(digest(stderr)==arm_record["stderr_sha256"],
                    "raw original native stderr SHA != derived physical receipt")
            exact_raw["stderr_sha_matches"]+=1
            event=raw_event(stderr,row["original_target"]["event"])
            require(event==arm_record["target_event"],
                    "raw native original source OPEN/CLOSE differ from derived receipt")
            exact_raw["source_events_equal"]+=1
            uci=raw_best(stdout)
            require(uci==arm_record["bestmove"],
                    "raw original stdout UCI bestmove mismatch")
            exact_raw["raw_final_best_matches"]+=1
            flags=(arm.startswith("both_off"),arm.startswith("both_off"))
            if arm=="futility_only":flags=(True,False)
            require(event["close"]["skip_f"]==str(int(flags[0]))
                    and event["close"]["skip_n"]==str(int(flags[1]))
                    and event["close"]["stopped"]=="0",
                    "true physical source intervention missing or interrupted")
            raw[arm]=(stdout,stderr,uci)
            key=("sham" if arm.startswith("sham") else
                 "both_off" if arm.startswith("both_off") else "futility_only")
            counts[key]+=1
        # Cold source process pairs genuinely identical byte-for-byte
        # (even beyond the parsed proxy score/proof equality).
        require(raw["sham0"]==raw["sham1"],
                "raw repeated sham control differs")
        exact_raw["raw_sham_pair_equal"]+=1
        require(raw["both_off0"]==raw["both_off1"],
                "raw repeated source treatment differs")
        exact_raw["raw_treatment_pair_equal"]+=1
        require(raw["sham0"][2]==row["original_untreated_bestmove"],
                "source sham changed the original bestmove")
        recomputed_y=int(raw["both_off0"][2]!=raw["sham0"][2])
        require(recomputed_y==row["y"],"raw original physical flip label changed")
        if recomputed_y:changes.append(row["id"])
        if row["predictions"] is not None:
            all_pred.append(row)
    require(counts=={"sham":256,"both_off":256,"futility_only":128},
            "raw source experiment arm census not 640")
    require(len(changes)==14 and
            len({r.rsplit("-",1)[0] for r in changes})==13,
            "original 14 changes across 13 games not reproduced")
    computed=independent_scores(all_pred)
    for model in ("m0","m1","m2"):
        for field in ("brier","average_precision","predicted_positive_at_0_5"):
            require(abs(computed[model][field]-score["metrics"][model][field])<1e-12,
                    "independent original score calculation diverges: "+model+" "+field)
    require(score["verdict"]=="NO_CONFIRMED_PROSPECTIVE_SOURCE_STATE_GAIN"
            and score["actual_final_move_flips"]==14
            and score["valid_physical_event_contacts"]==128,
            "unapproved scientific gain promotion")
    if archive:archive.close()
    return {
        "schema":"C3X_031_P2_B3_ORIGINAL_RAW_SOURCE_TRANSCRIPT_AUDIT_V1",
        "scientific_classification":"DERIVED_VERIFICATION_NO_NEW_STOCKFISH_SEARCHES",
        "original_B1_preoutcome_sha256":EXPECTED_B1_SHA,
        "original_B2_native_result_sha256":EXPECTED_B2_PRIVATE_SHA,
        "original_B2_640_raw_logs_zip_sha256":EXPECTED_RAW_ZIP_SHA,
        "original_B2_metric_court_sha256":EXPECTED_SCORE_SHA,
        "source_games":64,"canonical_event_families":25,
        "original_native_searches_B1":192,"original_new_source_processes_B2":640,
        "actual_B2_source_arm_counts":counts,
        "raw_source_verifications":exact_raw,
        "original_final_move_change_events":14,
        "original_final_move_change_distinct_games":13,
        "source_1642_family_change_events":changes,
        "valid_original_predicted_events":len(all_pred),
        "original_noncp_abstention_events":2,
        "independently_recomputed_model_metrics":computed,
        "scientific_verdict":"NO_CONFIRMED_PROSPECTIVE_SOURCE_STATE_GAIN",
        "exact_TT_history_mediator_proved":False,
        "independent_chess_or_human_value_proved":False,
    }


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for k in ("b1_source","b2_original_results","native_original_logs",
              "b2_existing_metrics","out"):
        p.add_argument(k,type=Path)
    args=p.parse_args()
    result=audit(args.b1_source,args.b2_original_results,
                 args.native_original_logs,args.b2_existing_metrics)
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(result,sort_keys=True,indent=2)+"\n")
    print("P2_B3_1280_RAW_COURT",result["raw_source_verifications"],
          "14 real flips, independent scores verified",
          "sha256",digest(args.out.read_bytes()))


if __name__=="__main__":
    main()
