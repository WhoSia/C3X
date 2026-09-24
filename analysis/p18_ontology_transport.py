#!/usr/bin/env python3
import argparse,json
from pathlib import Path

TARGETS=("frozen_20260810","stockfish_19")
ANALOGS=(("KRBvKR","KRNvKR"),("KQvKRB","KQvKRN"),("KRvKQB","KRvKQN"))
ARMS=("10","01","11")

def parse_items(items):
    out={}
    for x in items:
        fam,p=x.split("=",1)
        out[fam]=json.loads(Path(p).read_text())
    return out

def phase_from_rows(rows,target):
    n=len(rows)
    m=sum(r["targets"][target]["arms"]["10"]["fine_changed"] for r in rows)
    q=sum(r["targets"][target]["arms"]["01"]["fine_changed"] for r in rows)
    mq=sum(r["targets"][target]["arms"]["11"]["fine_changed"] for r in rows)
    inter=mq/n-m/n-q/n
    vals={"MAIN":abs(m/n),"QSEARCH":abs(q/n),"INTERACTION":abs(inter)}
    ordered=sorted(vals.items(),key=lambda x:(-x[1],x[0]))
    floor=2/n; margin=1/n
    if ordered[0][1]<floor: phase="NULL"
    elif ordered[0][1]-ordered[1][1]<margin: phase="MIXED"
    else: phase=ordered[0][0]+"-DOMINANT"
    return {"phase":phase,"MAIN":m/n,"QSEARCH":q/n,"INTERACTION":inter,
            "counts":{"MAIN":m,"QSEARCH":q,"MAIN_QSEARCH":mq},"n":n}

def sign(x):
    return -1 if x<0 else 1 if x>0 else 0

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--ontology",required=True)
    ap.add_argument("--discovery",action="append",required=True)
    ap.add_argument("--heldout",action="append",required=True)
    ap.add_argument("--out",required=True)
    a=ap.parse_args()
    ontology=json.loads(Path(a.ontology).read_text())
    disc=parse_items(a.discovery); held=parse_items(a.heldout)
    out={"schema":"c3x-p18-ontology-transport-v1",
         "scientific_stage":"C3X 0.7.0-G9.4-P18",
         "ontology_schema":ontology["schema"],
         "ontology_secondary_rules_applied_without_postoutcome_regrouping":True,
         "targets":{}}
    for t in TARGETS:
        d={f:phase_from_rows(v["rows"],t) for f,v in disc.items()}
        h={f:phase_from_rows(v["rows"],t) for f,v in held.items()}
        pairs=[]
        for df,hf in ANALOGS:
            pairs.append({
                "discovery":df,"heldout":hf,
                "discovery_phase":d[df]["phase"],"heldout_phase":h[hf]["phase"],
                "phase_match":d[df]["phase"]==h[hf]["phase"],
                "discovery_interaction":d[df]["INTERACTION"],
                "heldout_interaction":h[hf]["INTERACTION"],
                "interaction_sign_match":sign(d[df]["INTERACTION"])==sign(h[hf]["INTERACTION"])
            })
        phase_matches=sum(p["phase_match"] for p in pairs)
        sign_matches=sum(p["interaction_sign_match"] for p in pairs)
        out["targets"][t]={
            "discovery":d,"heldout":h,"analog_pairs":pairs,
            "analog_phase_transport_pass":phase_matches>=2,
            "bishop_to_knight_interaction_sign_transport_pass":sign_matches>=2,
            "analog_phase_match_count":phase_matches,
            "interaction_sign_match_count":sign_matches,
            "far_extrapolation_KBBvKN":h["KBBvKN"]
        }
    out["cross_version_analog_phase_transport"]=all(out["targets"][t]["analog_phase_transport_pass"] for t in TARGETS)
    out["cross_version_interaction_sign_transport"]=all(out["targets"][t]["bishop_to_knight_interaction_sign_transport_pass"] for t in TARGETS)
    Path(a.out).parent.mkdir(parents=True,exist_ok=True)
    Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps(out,sort_keys=True))

if __name__=="__main__":
    main()
