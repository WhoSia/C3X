#!/usr/bin/env python3
import argparse,json
from pathlib import Path

TARGETS=("frozen_20260810","stockfish_19")
ANALOGS=(("KRBvKR","KRNvKR"),("KQvKRB","KQvKRN"),("KRvKQB","KRvKQN"))
ORIENTATION_PAIRS=(("KQvKRB","KRvKQB"),("KQvKRN","KRvKQN"))

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

def relation(a,b):
    return [a,b]

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--ontology",required=True)
    ap.add_argument("--discovery",action="append",required=True)
    ap.add_argument("--heldout",action="append",required=True)
    ap.add_argument("--out",required=True)
    a=ap.parse_args()
    ontology=json.loads(Path(a.ontology).read_text())
    disc=parse_items(a.discovery); held=parse_items(a.heldout)
    out={"schema":"c3x-p18-ontology-transport-v2",
         "scientific_stage":"C3X 0.7.0-G9.4-P18",
         "ontology_schema":ontology["schema"],
         "ontology_secondary_rules_applied_without_postoutcome_regrouping":True,
         "targets":{}}
    for t in TARGETS:
        d={f:phase_from_rows(v["rows"],t) for f,v in disc.items()}
        h={f:phase_from_rows(v["rows"],t) for f,v in held.items()}
        allfam={**d,**h}
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

        orientation=[]
        for a0,b0 in ORIENTATION_PAIRS:
            orientation.append({
                "pair":[a0,b0],
                "phase_match":allfam[a0]["phase"]==allfam[b0]["phase"],
                "interaction_sign_match":sign(allfam[a0]["INTERACTION"])==sign(allfam[b0]["INTERACTION"]),
                "phase_relation":[allfam[a0]["phase"],allfam[b0]["phase"]],
                "interaction_sign_relation":[sign(allfam[a0]["INTERACTION"]),sign(allfam[b0]["INTERACTION"])]
            })
        orientation_pass=all(x["phase_match"] and x["interaction_sign_match"] for x in orientation)

        top=(d["KQvKRB"],h["KQvKRN"])
        bottom=(d["KRvKQB"],h["KRvKQN"])
        top_phase_change=relation(top[0]["phase"],top[1]["phase"])
        bottom_phase_change=relation(bottom[0]["phase"],bottom[1]["phase"])
        top_sign_change=relation(sign(top[0]["INTERACTION"]),sign(top[1]["INTERACTION"]))
        bottom_sign_change=relation(sign(bottom[0]["INTERACTION"]),sign(bottom[1]["INTERACTION"]))
        commutative={
            "top_substitution_phase_change":top_phase_change,
            "bottom_substitution_phase_change":bottom_phase_change,
            "top_substitution_interaction_sign_change":top_sign_change,
            "bottom_substitution_interaction_sign_change":bottom_sign_change,
            "phase_change_commutes":top_phase_change==bottom_phase_change,
            "interaction_sign_change_commutes":top_sign_change==bottom_sign_change
        }
        commutative["pass"]=commutative["phase_change_commutes"] and commutative["interaction_sign_change_commutes"]

        out["targets"][t]={
            "discovery":d,"heldout":h,"analog_pairs":pairs,
            "analog_phase_transport_pass":phase_matches>=2,
            "bishop_to_knight_interaction_sign_transport_pass":sign_matches>=2,
            "analog_phase_match_count":phase_matches,
            "interaction_sign_match_count":sign_matches,
            "orientation_duality_pairs":orientation,
            "orientation_duality_pass":orientation_pass,
            "commutative_square":commutative,
            "far_extrapolation_KBBvKN":h["KBBvKN"]
        }
    out["cross_version_analog_phase_transport"]=all(out["targets"][t]["analog_phase_transport_pass"] for t in TARGETS)
    out["cross_version_interaction_sign_transport"]=all(out["targets"][t]["bishop_to_knight_interaction_sign_transport_pass"] for t in TARGETS)
    out["cross_version_orientation_duality"]=all(out["targets"][t]["orientation_duality_pass"] for t in TARGETS)
    out["cross_version_commutative_square"]=all(out["targets"][t]["commutative_square"]["pass"] for t in TARGETS)
    Path(a.out).parent.mkdir(parents=True,exist_ok=True)
    Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps(out,sort_keys=True))

if __name__=="__main__":
    main()
