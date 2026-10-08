#!/usr/bin/env python3
"""P8-R1 preselected fresh 32 broadcast groups: chess-only support at ply32/64/80."""
import argparse,hashlib,io,json,re,subprocess
from pathlib import Path

import chess
import chess.pgn
from harness.c3x_013_p7r1_tactical_support import hazard,census
from harness.c3x_013_p6r1_birth_rival_support import births
from harness.c3x_013_p5_source_partition import SRC,H

PLIES=(32,64,80)
OLD_P5="7f9e865ced89aa47ed06aac5fa0d40ff02481f8ff4e696f12769fdcffbc9fa1b"
OLD_P7="e5ca78464ef6bb2e95271c12428c47e8f9535efca9674d1048aed029ef1584c0"

def select(path):
    if H(Path(path).read_bytes())!=SRC:raise ValueError("ORIGINAL_SOURCE_SHA_DRIFT")
    raw=subprocess.check_output(["zstd","-dc",str(path)])
    starts=[m.start() for m in re.finditer(rb'(?m)^\[Event "',raw)]
    groups={}
    for i,start in enumerate(starts):
        item=raw[start:starts[i+1] if i+1<len(starts) else len(raw)].strip()
        head=item.split(b"\n\n",1)[0]
        tags={m.group(1).decode():m.group(2).decode("utf-8","replace")
              for m in re.finditer(rb'(?m)^\[([^]]+) "([^"]*)"\]',head)}
        group,url=tags.get("BroadcastName"),tags.get("GameURL","")
        if (not tags.get("Date","").startswith("2026.09.")
            or tags.get("Variant")!="Standard" or not group
            or not url.startswith("https://lichess.org/broadcast/")):
            continue
        if group not in groups or url<groups[group]["game_url"]:
            groups[group]={"broadcast":group,"game_url":url,"sha":H(item),
                           "event_header":tags.get("Event"),"raw":item}
    chosen=sorted(groups.values(),key=lambda z:(H(z["broadcast"].encode()),z["game_url"]))
    digest=lambda rows:H(("\n".join(z["sha"] for z in rows)+"\n").encode())
    if (len(starts)!=28638 or len(chosen)!=299 or
        digest(chosen[:16])!=OLD_P5 or digest(chosen[16:48])!=OLD_P7):
        raise ValueError("P5_P7_SOURCE_PREFIX_DRIFT")
    return chosen[:48],chosen[48:80],digest(chosen[48:80])

def boards(entry):
    game=chess.pgn.read_game(io.StringIO(entry["raw"].decode("utf-8","replace")))
    if game is None or game.errors:return {"status":"HOLD_PGN_OR_VARIANT","worlds":{}}
    board=game.board()
    mainline=list(game.mainline_moves())
    at={}
    for ply in PLIES:
        if len(mainline)<ply:
            at[str(ply)]={"status":"HOLD_SHORTER_THAN_LANDMARK"}
            continue
        b=board.copy(stack=False)
        for m in mainline[:ply]:
            if m not in b.legal_moves:
                at[str(ply)]={"status":"HOLD_ILLEGAL_MOVE"}
                break
            b.push(m)
        else:
            if not b.is_valid() or b.is_game_over():
                at[str(ply)]={"status":"HOLD_BOARD_INVALID_OR_TERMINAL"}
            else:
                fen=b.fen(en_passant="fen")
                four=" ".join(fen.split()[:4])
                at[str(ply)]={"status":"VALID_WORLD","fen":fen,
                              "fen4_sha256":H(four.encode())}
    return {"status":"PARSED_COMPLETE_SOURCE","worlds":at,"game_mainline_ply":len(mainline)}

def sample_birth_contrasts(board,limit=4):
    moves=sorted(board.legal_moves,key=lambda m:m.uci())
    signatures={m.uci():hazard(board,m) for m in moves}
    status={m.uci():bool(births(board,m)) for m in moves}
    grouping={}
    for m in moves:
        meta=signatures[m.uci()]
        k=(meta["mover"],meta["captured"],meta["gives_check"],
           meta["promotion"],meta["castling"],tuple(meta["recapture_types"]))
        grouping.setdefault(k,[[],[]])[int(status[m.uci()])].append(m.uci())
    out=[]
    for k,(negative,positive) in sorted(grouping.items(),key=lambda z:str(z[0])):
        for a in negative:
            for b in positive:
                out.append({"birth_false_root":a,"birth_true_root":b,
                            "same_from_square":a[:2]==b[:2],
                            "tactical_signature":{"mover":k[0],"capture":k[1],
                                                 "check":k[2],"promotion":k[3],
                                                 "castling":k[4],"recapture_types":k[5]}})
                if len(out)>=limit:return out
    return out

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source",required=True)
    p.add_argument("--out",required=True)
    args=p.parse_args()
    prior,current,digest=select(args.source)
    old_fen=set()
    for item in prior:
        for world in boards(item)["worlds"].values():
            if world.get("status")=="VALID_WORLD":
                old_fen.add(world["fen4_sha256"])
    rows=[]; seen=set()
    for index,item in enumerate(current,49):
        prior_status=boards(item)
        row={"source_rank":index,"broadcast":item["broadcast"],
             "game_url":item["game_url"],"event_header":item["event_header"],
             "source_game_sha256":item["sha"],
             "game_source_status":prior_status["status"],"worlds":{}}
        for ply in PLIES:
            world=prior_status["worlds"].get(str(ply),{"status":"HOLD_SOURCE"})
            if world.get("status")!="VALID_WORLD":
                row["worlds"][str(ply)]={"status":world["status"]}
                continue
            fid=world["fen4_sha256"]
            if fid in old_fen or fid in seen:
                row["worlds"][str(ply)]={"status":"HOLD_DUPLICATE_EARLIER_FEN4"}
                continue
            seen.add(fid)
            board=chess.Board(world["fen"])
            c=census(board)
            row["worlds"][str(ply)]={
                "status":"CHESS_RULE_PAIR_SUPPORT_ONLY",
                "fen":world["fen"],"fen4_sha256":fid,
                "legal_root_count":c["legal_root_count"],
                "gate_counts":c["counts"],
                "pre_engine_birth_pair_examples":sample_birth_contrasts(board)}
        rows.append(row)
    total={}
    for ply in PLIES:
        accepted=[x["worlds"][str(ply)] for x in rows
                  if x["worlds"][str(ply)]["status"]=="CHESS_RULE_PAIR_SUPPORT_ONLY"]
        ckeys=("all_legal_pairs","matched_legal_immediate_recapture",
               "matched_and_same_origin","passed_birth_toggling_in_matched",
               "passed_birth_toggling_in_strict")
        total[str(ply)]={"legal_worlds":len(accepted),
            "groups_with_born_matched":sum(x["gate_counts"]["passed_birth_toggling_in_matched"]>0 for x in accepted),
            "groups_with_born_strict":sum(x["gate_counts"]["passed_birth_toggling_in_strict"]>0 for x in accepted)}
        total[str(ply)].update({k:sum(x["gate_counts"][k] for x in accepted) for k in ckeys})
    paired=[x for x in rows
            if x["worlds"]["80"]["status"]=="CHESS_RULE_PAIR_SUPPORT_ONLY"]
    within={str(ply):{"denominator_ply80_survivors":len(paired),
        "observed":sum(x["worlds"][str(ply)]["status"]=="CHESS_RULE_PAIR_SUPPORT_ONLY" for x in paired),
        "matched_birth_groups":sum(x["worlds"][str(ply)].get("gate_counts",{}).get("passed_birth_toggling_in_matched",0)>0 for x in paired)}
        for ply in PLIES}
    out={"schema":"c3x-013-p8-r1-source-only-phase-positivity-v1",
         "status":"PREOUTCOME_NEW32_SOURCE_TACTICAL_CONCEPT_SUPPORT_ONLY",
         "source_sha256":SRC,"prior_P5_P7_groups":48,
         "fresh_frozen_group_count":32,"new_group_digest":digest,
         "new_group_url_digest":H(("\n".join(z["game_url"] for z in current)+"\n").encode()),
         "source_group_denominator":32,"landmarks":total,
         "survivor_matched_landmarks":within,
         "records":rows,
         "same_provider_not_independent_ecology":True,
         "experimental_engine_evaluation":None,
         "causal_explanation_claim":False,
         "C3X_014":"CANDIDATE_ONLY_NO_FORMAL_NAME"}
    Path(args.out).parent.mkdir(parents=True,exist_ok=True)
    Path(args.out).write_text(json.dumps(out,indent=2,ensure_ascii=False)+"\n")
    print("P8R1_SOURCE_DIGEST",digest)
    print("P8R1_LANDMARK_SUPPORT",total)
    print("P8R1_DURATION_MATCHED",within)
    assert len(rows)==32 and not out["causal_explanation_claim"]
if __name__=="__main__":main()
