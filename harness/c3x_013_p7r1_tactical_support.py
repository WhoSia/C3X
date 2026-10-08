#!/usr/bin/env python3
"""P7-R1: tactical-equivalence support across pre-frozen next 32 broadcasts.

Zero engine outcome, zero claim of causal concept explanation or 0.14 opening.
"""
from __future__ import annotations
import argparse, hashlib, io, itertools, json, re, subprocess
from pathlib import Path
import chess, chess.pgn
from harness.c3x_013_p5_source_partition import H, SRC, OLD, court
from harness.c3x_013_p6r1_birth_rival_support import births

SOURCE_SEGMENT_DIGEST="e5ca78464ef6bb2e95271c12428c47e8f9535efca9674d1048aed029ef1584c0"
URL_DIGEST="fb80bb78b31727f7b485a36687fe302829ecca22fbf97a1ba505bc486ad8d10d"
ORIGINAL_P5_DIGEST="7f9e865ced89aa47ed06aac5fa0d40ff02481f8ff4e696f12769fdcffbc9fa1b"

def freeze_source(path):
    p=Path(path)
    if H(p.read_bytes())!=SRC:raise ValueError("SOURCE_BYTES_CHANGED")
    raw=subprocess.check_output(["zstd","-dc",str(p)])
    starts=[m.start() for m in re.finditer(rb'(?m)^\[Event "',raw)]
    groups={}
    for i,start in enumerate(starts):
        seg=raw[start:starts[i+1] if i+1<len(starts) else len(raw)].strip()
        head=seg.split(b"\n\n",1)[0]
        tags={m.group(1).decode():m.group(2).decode("utf-8","replace")
              for m in re.finditer(rb'(?m)^\[([^]]+) "([^"]*)"\]',head)}
        group,url=tags.get("BroadcastName"),tags.get("GameURL","")
        if not(tags.get("Date","").startswith("2026.09.") and
               tags.get("Variant")=="Standard" and group and
               url.startswith("https://lichess.org/broadcast/")):continue
        if group not in groups or url<groups[group]["game_url"]:
            groups[group]={"broadcast":group,"game_url":url,"sha":H(seg),
                           "date":tags.get("Date"),"raw":seg}
    order=sorted(groups.values(),key=lambda x:(H(x["broadcast"].encode()),x["game_url"]))
    first=order[:16]
    selected=order[16:48]
    digest=lambda xs:H(("\n".join(x["sha"] for x in xs)+"\n").encode())
    uhash=H(("\n".join(x["game_url"] for x in selected)+"\n").encode())
    if (len(starts)!=28638 or len(groups)!=299 or len(selected)!=32 or
        digest(first)!=ORIGINAL_P5_DIGEST or
        digest(selected)!=SOURCE_SEGMENT_DIGEST or uhash!=URL_DIGEST):
        raise ValueError("P7_PREOUTCOME_GROUP_SELECTION_DRIFT")
    return first,selected

def hazard(board,move):
    """Immediate legal opponent capture of the moved piece, including en passant victim square."""
    if move not in board.legal_moves:raise ValueError("ILLEGAL_MOVE")
    mover=board.piece_at(move.from_square)
    if not mover:raise ValueError("MISSING_MOVER")
    victim_sq=move.to_square
    if board.is_en_passant(move):
        victim_sq+=(-8 if board.turn else 8)
    victim=board.piece_at(victim_sq) if board.is_capture(move) else None
    after=board.copy(stack=False)
    after.push(move)
    occupant=after.piece_at(move.to_square)
    recapture=[]
    if occupant:
        for reply in after.legal_moves:
            if not after.is_capture(reply):
                continue
            captured_square=reply.to_square
            if after.is_en_passant(reply):
                # En passant captures the pawn on its FINAL SQUARE, not the
                # en passant capturing pawn's landing square.
                captured_square += -8 if after.turn==chess.WHITE else 8
            if captured_square==move.to_square:
                attacker=after.piece_at(reply.from_square)
                if attacker:
                    recapture.append(chess.piece_name(attacker.piece_type))
    signature={
        "mover":chess.piece_name(mover.piece_type),
        "captured":chess.piece_name(victim.piece_type) if victim else "NONE",
        "gives_check":after.is_check(),
        "promotion":chess.piece_name(move.promotion) if move.promotion else "NONE",
        "castling":board.is_castling(move),
        "recapture_types":sorted(recapture)
    }
    return signature

def census(board):
    moves=sorted(board.legal_moves,key=lambda m:m.uci())
    entries={m.uci():hazard(board,m) for m in moves}
    born={m.uci():bool(births(board,m)) for m in moves}
    counts={"all_legal_pairs":0,"same_class_capture_check_promotion":0,
            "matched_legal_immediate_recapture":0,
            "matched_and_same_origin":0,
            "passed_birth_toggling_in_matched":0,
            "passed_birth_toggling_in_strict":0}
    strict_examples=[]
    matched_examples=[]
    for a,b in itertools.combinations(moves,2):
        counts["all_legal_pairs"]+=1
        aa,bb=entries[a.uci()],entries[b.uci()]
        cls=("mover","captured","gives_check","promotion","castling")
        if any(aa[k]!=bb[k] for k in cls):continue
        counts["same_class_capture_check_promotion"]+=1
        if aa["recapture_types"]!=bb["recapture_types"]:continue
        counts["matched_legal_immediate_recapture"]+=1
        toggles=born[a.uci()]!=born[b.uci()]
        if toggles:
            counts["passed_birth_toggling_in_matched"]+=1
        if len(matched_examples)<3:matched_examples.append([a.uci(),b.uci()])
        if a.from_square==b.from_square:
            counts["matched_and_same_origin"]+=1
            if toggles:
                counts["passed_birth_toggling_in_strict"]+=1
                if len(strict_examples)<3:strict_examples.append([a.uci(),b.uci()])
    assert counts["all_legal_pairs"]==len(moves)*(len(moves)-1)//2
    assert counts["passed_birth_toggling_in_strict"]<=counts["matched_and_same_origin"]
    return {"legal_root_count":len(moves),"counts":counts,
            "same_origin_birth_pair_examples":strict_examples,
            "matched_pairs_first3":matched_examples}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source",required=True);p.add_argument("--output",required=True)
    a=p.parse_args()
    first,selected=freeze_source(a.source)
    earlier=set()
    for item in first:
        x=court(item)
        if x.get("status")=="BOARD_FACT_ONLY":earlier.add(x["fen4_sha256"])
    seen=set()
    rows=[]
    for idx,item in enumerate(selected,17):
        row={"selection_rank":idx,"broadcast":item["broadcast"],"game_url":item["game_url"],
             "date":item["date"],"raw_game_segment_sha256":item["sha"]}
        x=court(item)
        row["source_status"]=x["status"]
        if x["status"]!="BOARD_FACT_ONLY":
            row["status"]="SOURCE_HOLD_"+x["status"];rows.append(row);continue
        ident=x["fen4_sha256"]
        if ident in seen or ident in earlier or ident in OLD:
            row["status"]="HOLD_PRIOR_OR_DUPLICATE_POSITION";rows.append(row);continue
        seen.add(ident)
        board=chess.Board(x["fen"])
        if not board.is_valid() or board.is_game_over():
            row["status"]="HOLD_BOARD_NOT_ELIGIBLE";rows.append(row);continue
        row["status"]="TACTICAL_RULE_SUPPORT_MEASURED"
        row["fen"]=x["fen"];row["fen4_sha256"]=ident
        row["tactical"]=census(board)
        rows.append(row)
    result={"schema":"c3x-013-p7-r1-disjoint-tactical-support-census-v1",
            "original_labeled_provider":"Lichess CC BY-SA 4.0",
            "original_source_sha256":SRC,
            "prior_p5_group_count":16,"new_frozen_broadcast_groups":32,
            "frozen_segment_digest":SOURCE_SEGMENT_DIGEST,
            "frozen_url_digest":URL_DIGEST,
            "source_independence_limit":"P5-disjoint BroadcastName labels only; source provider and competition/player clusters are not independently established",
            "records":rows,"counts":{s:sum(x["status"]==s for x in rows)
                                     for s in sorted({x["status"] for x in rows})},
            "totals":{key:sum(x["tactical"]["counts"][key] for x in rows
                              if x["status"]=="TACTICAL_RULE_SUPPORT_MEASURED")
                      for key in ("all_legal_pairs","same_class_capture_check_promotion",
                        "matched_legal_immediate_recapture","matched_and_same_origin",
                        "passed_birth_toggling_in_matched","passed_birth_toggling_in_strict")},
            "engine_scores_opened":False,
            "scientific_concept_causality_authorized":False,
            "P7_0_14_bridge":"CANDIDATE_ONLY_NOT_OPENED"}
    Path(a.output).parent.mkdir(parents=True,exist_ok=True)
    Path(a.output).write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n")
    print("P7_R1_DISJOINT_SOURCE_COUNTS",result["counts"])
    print("P7_R1_TACTICAL_SUPPORT_NESTED",result["totals"])
    assert len(rows)==32 and sum(result["counts"].values())==32
    assert not result["scientific_concept_causality_authorized"]
if __name__=="__main__":main()
