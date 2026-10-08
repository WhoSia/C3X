#!/usr/bin/env python3
"""C3X 0.13 P1: verify archived pair-local attack atoms, not a causal concept."""
import argparse
import hashlib
import json
from pathlib import Path
import chess

def relation(board, piece_sq, pair):
    piece=board.piece_at(piece_sq)
    if piece is None or piece.piece_type!=chess.QUEEN:
        raise ValueError("PIECE_IDENTITY_MISMATCH")
    moves=[chess.Move.from_uci(pair[k]["uci"]) for k in ("A","B")]
    targets=[v for m in moves for v in (m.from_square,m.to_square)]
    attacked=board.attacks(piece_sq)
    return [{"square":chess.square_name(sq),"attacked":sq in attacked,
             "occupancy":"EMPTY" if board.piece_at(sq) is None else (
                 "OWN_OCCUPIED" if board.color_at(sq)==piece.color else "ENEMY_OCCUPIED")}
            for sq in targets]

def evaluate(cert):
    if cert.get("scientific_stage")!="C3X 0.7.0-G9.5-P16":
        raise ValueError("UNEXPECTED_HISTORICAL_SOURCE")
    boards=cert["counterfactual_boards"]
    chain=cert["chain"]
    if boards["SHAM"]["fen"]!=boards["SUBSET"]["fen"]:
        raise ValueError("SHAM_SUBSET_NOT_IDENTICAL")
    expected={
        "B0":chain["target_edit"]["relation_before"],
        "TARGET":chain["target_edit"]["relation_after"],
        "SHAM":chain["sham_edit"]["relation_after"]}
    vector={}
    all_legal=True
    for name in ("B0","TARGET","SHAM"):
        board=chess.Board(boards[name]["fen"])
        if not board.is_valid():
            raise ValueError("INVALID_BOARD_"+name)
        pair=cert["pair"]
        if any(chess.Move.from_uci(pair[k]["uci"]) not in board.legal_moves for k in ("A","B")):
            all_legal=False
            raise ValueError("PAIR_ILLEGAL_"+name)
        queen_square=("d8" if name=="B0" else chain[
            "target_edit" if name=="TARGET" else "sham_edit"]["to"])
        cells=relation(board,chess.parse_square(queen_square),pair)
        got=[z["attacked"] for z in cells]
        if got!=expected[name]:
            raise ValueError("ARCHIVE_VECTOR_NOT_REPRODUCED_"+name)
        vector[name]=cells
    own_king_contact=vector["B0"][2]
    if (own_king_contact["square"]!="e8" or
        own_king_contact["occupancy"]!="OWN_OCCUPIED" or
        not own_king_contact["attacked"]):
        raise ValueError("KING_OCCUPANCY_COUNTEREXAMPLE_MISSING")
    return {"schema":"c3x-013-p1-chess-semantic-grounding-v1",
        "historical_stage":cert["scientific_stage"],
        "development_only":True,
        "archived_pair":cert["pair"]["pair_id"],
        "all_three_legal":all_legal,
        "all_archived_attack_vectors_reproduced":True,
        "sham_is_exact_subset_world":True,
        "attack_relation_results":vector,
        "semantic_counterexample":{
            "claim":"A queen attack flag on candidate B source e8 proves hostile chess pressure",
            "verdict":"FALSIFIED",
            "reason":"e8 is BLACK KING occupied by the same side as the queen; pseudo-attack includes defended friendly squares",
            "observable_fact_only":True},
        "named_chess_concept_certified":False,
        "causal_mechanism_certified":False,
        "cross_engine_transport_certified":False,
        "human_understanding_improved":False}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--certificate",required=True)
    p.add_argument("--out",required=True)
    a=p.parse_args()
    path=Path(a.certificate)
    cert=json.loads(path.read_text())
    result=evaluate(cert)
    result["source_certificate_sha256"]=hashlib.sha256(path.read_bytes()).hexdigest()
    Path(a.out).parent.mkdir(parents=True,exist_ok=True)
    Path(a.out).write_text(json.dumps(result,indent=2)+"\n")
    print("C3X_013_P1_ARCHIVED_RELATION_VECTORS_PASS")
    print("C3X_013_P1_HOSTILE_PRESSURE_CONCEPT_REJECTED")
    print("C3X_013_P1_MECHANISM_CERTIFIED",False)

if __name__=="__main__":
    main()
