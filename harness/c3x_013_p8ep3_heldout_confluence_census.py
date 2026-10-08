#!/usr/bin/env python3
"""P8-EP3: fresh 32-source two-root exact chess legal confluence census."""
import argparse,hashlib,io,json,re,subprocess
from pathlib import Path
import chess,chess.pgn
from harness.c3x_013_p6r1_birth_rival_support import births
from harness.c3x_013_p7r1_tactical_support import hazard
from harness.c3x_013_p5_source_partition import SRC,H

PLY=(16,32,48,64)
PREFIX_16="7f9e865ced89aa47ed06aac5fa0d40ff02481f8ff4e696f12769fdcffbc9fa1b"
PREFIX_32="e5ca78464ef6bb2e95271c12428c47e8f9535efca9674d1048aed029ef1584c0"
PREFIX_P8="c5a18fdb71f752d37ceae740990937499d95c5dc6bf7981e7c672fdfeef659de"

def select(path):
    if H(Path(path).read_bytes())!=SRC:raise ValueError("SOURCE_ARCHIVE_SHA_DRIFT")
    raw=subprocess.check_output(["zstd","-dc",str(path)])
    starts=[m.start() for m in re.finditer(rb'(?m)^\[Event "',raw)]
    groups={}
    for i,start in enumerate(starts):
        seg=raw[start:starts[i+1] if i+1<len(starts) else len(raw)].strip()
        head=seg.split(b"\n\n",1)[0]
        tags={m.group(1).decode():m.group(2).decode("utf-8","replace")
              for m in re.finditer(rb'(?m)^\[([^]]+) "([^"]*)"\]',head)}
        group,url=tags.get("BroadcastName"),tags.get("GameURL","")
        if (not tags.get("Date","").startswith("2026.09.") or
            tags.get("Variant")!="Standard" or not group or
            not url.startswith("https://lichess.org/broadcast/")):continue
        if group not in groups or url<groups[group]["game_url"]:
            groups[group]={"broadcast":group,"game_url":url,
                           "event_header":tags.get("Event"),"sha":H(seg),"raw":seg}
    xs=sorted(groups.values(),key=lambda x:(H(x["broadcast"].encode()),x["game_url"]))
    digest=lambda rows:H(("\n".join(z["sha"] for z in rows)+"\n").encode())
    if (len(starts)!=28638 or len(xs)!=299 or
        digest(xs[:16])!=PREFIX_16 or digest(xs[16:48])!=PREFIX_32 or
        digest(xs[48:80])!=PREFIX_P8):
        raise ValueError("P5_P7_P8_PREVIOUS_SOURCE_PREFIX_DRIFT")
    new=xs[80:112]
    assert len(new)==32
    return xs[:80],new,digest(new)

def read_boards(item):
    game=chess.pgn.read_game(io.StringIO(item["raw"].decode("utf-8","replace")))
    if game is None or game.errors:
        return {"source_status":"HOLD_PGN_OR_VARIANT","worlds":{}}
    moves=list(game.mainline_moves())
    board0=game.board()
    out={}
    for ply in PLY:
        if len(moves)<ply:
            out[str(ply)]={"status":"HOLD_SHORT_GAME"}
            continue
        b=board0.copy(stack=False);legal=True
        for m in moves[:ply]:
            if m not in b.legal_moves:legal=False;break
            b.push(m)
        if not legal or not b.is_valid() or b.is_game_over():
            out[str(ply)]={"status":"HOLD_ILLEGAL_TERMINAL"}
            continue
        f=b.fen(en_passant="fen")
        out[str(ply)]={"status":"LEGAL_PLY","fen":f,
                       "fen4_sha256":H(" ".join(f.split()[:4]).encode())}
    return {"source_status":"PARSED_SOURCE","worlds":out}

def captured_piece_square(b,reply):
    if not b.is_capture(reply):return None
    return reply.to_square+(-8 if b.turn==chess.WHITE else 8) if b.is_en_passant(reply) else reply.to_square

def legal_captures_of_moved_pawn(board,root):
    moved=board.piece_at(root.from_square)
    assert moved and moved.piece_type==chess.PAWN and root in board.legal_moves
    successor=board.copy(stack=False);successor.push(root)
    captures={}
    for r in successor.legal_moves:
        if captured_piece_square(successor,r)!=root.to_square:continue
        aggressor=successor.piece_at(r.from_square)
        if not aggressor:continue
        q=successor.copy(stack=False);q.push(r)
        fen=q.fen(en_passant="fen")
        captures.setdefault(fen,[]).append({
            "reply":r.uci(),
            "kind":"EN_PASSANT" if successor.is_en_passant(r) else "NORMAL_CAPTURE",
            "attacker":chess.piece_name(aggressor.piece_type)})
    return captures

def candidates(board):
    froms={}
    for m in board.legal_moves:
        p=board.piece_at(m.from_square)
        if not p or p.piece_type!=chess.PAWN or board.is_capture(m) or m.promotion:
            continue
        steps=abs(chess.square_rank(m.to_square)-chess.square_rank(m.from_square))
        if m.from_square not in froms:froms[m.from_square]={}
        if steps in (1,2):froms[m.from_square][steps]=m
    allpairs=[]
    for square,m in sorted(froms.items()):
        if 1 in m and 2 in m:
            allpairs.append((m[1],m[2]))
    return allpairs

def proof(board):
    legal_pairs=candidates(board)
    found=[]
    for single,double in legal_pairs:
        capt1=legal_captures_of_moved_pawn(board,single)
        capt2=legal_captures_of_moved_pawn(board,double)
        shared=sorted(set(capt1).intersection(capt2))
        hazard_equal=hazard(board,single)["recapture_types"]==hazard(board,double)["recapture_types"]
        born1,born2=births(board,single),births(board,double)
        for fen in shared:
            for a in capt1[fen]:
                for b in capt2[fen]:
                    found.append({
                        "single":single.uci(),"double":double.uci(),
                        "reply_after_single":a,
                        "reply_after_double":b,
                        "same_opponent_reply_uci":a["reply"]==b["reply"],
                        "normal_vs_en_passant":set([a["kind"],b["kind"]])==set(["NORMAL_CAPTURE","EN_PASSANT"]),
                        "exact_common_full_fen":fen,
                        "root_capture_hazard_equal":hazard_equal,
                        "passed_birth_single":born1,"passed_birth_double":born2,
                        "passed_birth_toggled":bool(born1)!=bool(born2)})
    return {"legal_one_vs_two_push_pairs":len(legal_pairs),
            "exact_legal_reply_confluence_count":len(found),
            "strict_same_uci_normal_vs_ep_confluences":sum(
                z["same_opponent_reply_uci"] and z["normal_vs_en_passant"] for z in found),
            "strict_genesis_toggled_confluences":sum(
                z["same_opponent_reply_uci"] and z["normal_vs_en_passant"]
                and z["passed_birth_toggled"] and z["root_capture_hazard_equal"] for z in found),
            "witnesses":found}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--source",required=True);ap.add_argument("--out",required=True)
    args=ap.parse_args()
    earlier,new,digest=select(args.source)
    prior_fens=set()
    for x in earlier:
        for world in read_boards(x)["worlds"].values():
            if world.get("status")=="LEGAL_PLY":prior_fens.add(world["fen4_sha256"])
    rows=[];seen=set()
    for rank,item in enumerate(new,81):
        r={"source_rank":rank,"broadcast":item["broadcast"],"game_url":item["game_url"],
           "source_game_sha256":item["sha"],"event_header":item["event_header"],
           "worlds":{}}
        source=read_boards(item)
        r["source_status"]=source["source_status"]
        for ply in PLY:
            w=source["worlds"].get(str(ply),{"status":"HOLD_SOURCE"})
            if w["status"]!="LEGAL_PLY":
                r["worlds"][str(ply)]={"status":w["status"]}
                continue
            if w["fen4_sha256"] in prior_fens or w["fen4_sha256"] in seen:
                r["worlds"][str(ply)]={"status":"HOLD_DUPLICATE_FEN4"}
                continue
            seen.add(w["fen4_sha256"])
            q=proof(chess.Board(w["fen"]))
            r["worlds"][str(ply)]={"status":"LEGAL_SOURCE_SUPPORT",
                "fen":w["fen"],"fen4_sha256":w["fen4_sha256"],"census":q}
        rows.append(r)
    summary={}
    for ply in PLY:
        valid=[r["worlds"][str(ply)] for r in rows
               if r["worlds"][str(ply)]["status"]=="LEGAL_SOURCE_SUPPORT"]
        summary[str(ply)]={
            "legal_worlds":len(valid),
            "legal_one_vs_two_root_pairs":sum(x["census"]["legal_one_vs_two_push_pairs"] for x in valid),
            "exact_two_move_FEN_confluences":sum(x["census"]["exact_legal_reply_confluence_count"] for x in valid),
            "same_reply_normal_vs_ep_confluences":sum(x["census"]["strict_same_uci_normal_vs_ep_confluences"] for x in valid),
            "pawn_birth_toggling_tactical_confluences":sum(x["census"]["strict_genesis_toggled_confluences"] for x in valid)}
    out={"schema":"c3x-013-p8-ep3-heldout-chess-legal-confluence-census-v1",
         "stage":"C3X 0.13 P8-EP3","source_sha256":SRC,
         "prior_broadcast_groups":80,"frozen_heldout_groups":32,
         "frozen_new_segment_list_sha256":digest,
         "source_denominator":32,"landmark_halfmoves":list(PLY),
         "summary":summary,"records":rows,
         "source_same_provider_and_overlap_caution":True,
         "engine_scores_opened":False,"causal_concept_certificates":[],
         "C3X_014":"CANDIDATE_ONLY_NO_NAME"}
    Path(args.out).parent.mkdir(parents=True,exist_ok=True)
    Path(args.out).write_text(json.dumps(out,indent=2,ensure_ascii=False)+"\n")
    print("P8_EP3_NEW32_COHORT_DIGEST",digest)
    print("P8_EP3_LEGAL_TWO_MOVE_CONFLUENCE",summary)
    assert len(rows)==32 and not out["causal_concept_certificates"]
if __name__=="__main__":main()
