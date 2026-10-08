#!/usr/bin/env python3
"""C3X 0.13 P2: chess attack-map semantics with explicit abstention."""
import argparse
import hashlib
import json
from pathlib import Path
import chess
from c3x_013_p1_concept_grounding import evaluate

def classify(cell):
    if not cell["attacked"]:
        return "NO_ATTACK_MAP_CONTACT"
    if cell["occupancy"]=="OWN_OCCUPIED":
        return "OWN_OCCUPIED_COVERAGE"
    if cell["occupancy"]=="ENEMY_OCCUPIED":
        return "ENEMY_OCCUPIED_CONTACT"
    if cell["occupancy"]=="EMPTY":
        return "EMPTY_SQUARE_ATTACK"
    raise ValueError("UNKNOWN_OCCUPANCY")

def admit_claim(claim,cell,independent_worlds=1):
    kind=claim.get("claim_kind")
    if kind=="BOARD_FACT":
        expected=classify(cell)
        if claim.get("predicate")!=expected:
            raise ValueError("BOARD_FACT_MISMATCH")
        return {"authority":"OBSERVABLE_PSEUDO_ATTACK_FACT","admitted":True}
    if kind=="INDEPENDENT_REPLICATION":
        if independent_worlds<2:
            raise ValueError("DUPLICATED_SAME_FEN_NOT_INDEPENDENT")
        return {"authority":"SOURCE_INDEPENDENCE_NOT_PROVEN","admitted":False}
    if kind in ("HOSTILE_PRESSURE","STRATEGIC_CONCEPT","CAUSAL_MECHANISM",
                "CROSS_ENGINE_TRANSPORT","HUMAN_LEARNING_BENEFIT"):
        raise ValueError("UNLICENSED_SEMANTIC_OR_CAUSAL_PROMOTION")
    raise ValueError("UNKNOWN_CLAIM_KIND")

def produce(cert):
    original=evaluate(cert)
    cells=original["attack_relation_results"]
    out={"schema":"c3x-013-p2-occupancy-relative-semantic-firewall-v1",
         "status":"DEVELOPMENT_ONLY",
         "source_science_stage":"C3X 0.7.0-G9.5-P16",
         "candidate_pair":original["archived_pair"],
         "worlds":{},
         "negative_control_results":{},
         "historical_sham_subset_independent_n":1,
         "concept_label_authorized":False,
         "causal_explanation_authorized":False,
         "human_understanding_claim_authorized":False}
    for name in ("B0","TARGET","SHAM"):
        out["worlds"][name]=[
            {**cell,"predicate":classify(cell)}
            for cell in cells[name]]
    original_king=out["worlds"]["B0"][2]
    out["negative_control_results"]["friendly_king_square_not_hostile_pressure"]=(
        original_king["square"]=="e8"
        and original_king["occupancy"]=="OWN_OCCUPIED"
        and original_king["predicate"]=="OWN_OCCUPIED_COVERAGE")
    out["negative_control_results"]["sham_subset_no_independent_replication"]=(
        cert["counterfactual_boards"]["SHAM"]["fen"]==
        cert["counterfactual_boards"]["SUBSET"]["fen"])
    out["negative_control_results"]["target_change_is_descriptive_only"]=(
        out["worlds"]["B0"][2]["predicate"]=="OWN_OCCUPIED_COVERAGE"
        and out["worlds"]["TARGET"][2]["predicate"]=="NO_ATTACK_MAP_CONTACT")
    if not all(out["negative_control_results"].values()):
        raise ValueError("HISTORICAL_SEMANTIC_NEGATIVE_CONTROL_FAILED")
    out["released_fact_text"]="The queen's pseudo-attack coverage of the black king's e8 square changes under a legal board edit."
    out["withheld_text"]="This proves pressure on the opposing king, strategic advantage, causal move preference, or human understanding."
    return out

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--certificate",required=True)
    p.add_argument("--out",required=True)
    args=p.parse_args()
    cert_path=Path(args.certificate)
    o=produce(json.loads(cert_path.read_text()))
    o["certificate_sha256"]=hashlib.sha256(cert_path.read_bytes()).hexdigest()
    Path(args.out).parent.mkdir(parents=True,exist_ok=True)
    Path(args.out).write_text(json.dumps(o,indent=2)+"\n")
    print("C3X_013_P2_NEGATIVE_CONTROLS_PASS",o["negative_control_results"])
    print("C3X_013_P2_CAUSAL_AUTHORITY",False)

if __name__=="__main__":
    main()
