#!/usr/bin/env python3
"""C3X021 P2: source-legal, response-contingent chess decision primitives.

No native chess engine or named motif detection. This is a SECOND chess
counterfactual axis: for the two formerly identified P1 root-choice pairs,
enumerate every legal opponent reply and every immediate subsequent legal
answer in both candidate continuations. Never identify it as a TT effect.
"""
import argparse,hashlib,json
from pathlib import Path
import chess
from c3x_021_P1_atomic_decision_transition_graph import sha

MARCH_SHA="d79e48633be2b683176f1a6d4650aeea1b7584f11c85c2349a5bddda113febee"
ATOMIC_SHA="c14711c0e31bde26c2c7fc6e77f1f2fdf0ac70180a517b91f71845f1fd78ed3f"
FIXED_PAIRS={4:("h8h4","g5h4"),9:("a6b7","f6h5")}

def profile_after_root(fen4,uci):
    b=chess.Board(fen4+" 0 1")
    m=chess.Move.from_uci(uci)
    if not b.is_valid() or m not in b.legal_moves:
        raise ValueError("P2_ILLEGAL_ROOT")
    b.push(m)
    out={}
    for response in sorted(list(b.legal_moves),key=lambda x:x.uci()):
        source=b.copy(stack=False)
        source.push(response)
        if not source.is_valid():
            raise ValueError("P2_ILLEGAL_RESPONSE_BOARD")
        legal=sorted(x.uci() for x in source.legal_moves)
        captures=sorted(x.uci() for x in source.legal_moves if source.is_capture(x))
        checks=sorted(x.uci() for x in source.legal_moves if source.gives_check(x))
        out[response.uci()]={
            "original_root_chess_move":uci,
            "opponent_response":response.uci(),
            "next_own_legal_count":len(legal),
            "next_own_legal_sha256":sha(legal),
            "next_own_captures":captures,
            "next_own_checks":checks,
            "own_king_in_check":source.is_check(),
            "next_turn_checkmate":source.is_checkmate(),
            "next_turn_stalemate":source.is_stalemate(),
        }
    return out

def pair_profile(fen4,f,v):
    fdata=profile_after_root(fen4,f)
    vdata=profile_after_root(fen4,v)
    common=sorted(set(fdata)&set(vdata))
    fonly=sorted(set(fdata)-set(vdata))
    vonly=sorted(set(vdata)-set(fdata))
    contrasts=[]
    for u in common:
        a,b=fdata[u],vdata[u]
        contrasts.append({
            "same_legal_opponent_reply":u,
            "F_next_own_legal_count":a["next_own_legal_count"],
            "V_next_own_legal_count":b["next_own_legal_count"],
            "same_next_own_legal_move_set":
                a["next_own_legal_sha256"]==b["next_own_legal_sha256"],
            "F_next_own_captures":a["next_own_captures"],
            "V_next_own_captures":b["next_own_captures"],
            "F_next_own_checks":a["next_own_checks"],
            "V_next_own_checks":b["next_own_checks"],
            "F_own_king_in_check":a["own_king_in_check"],
            "V_own_king_in_check":b["own_king_in_check"],
        })
    return {
        "F_move":f,"V_move":v,
        "F_legal_opponent_reply_count":len(fdata),
        "V_legal_opponent_reply_count":len(vdata),
        "F_opponent_reply_set_sha256":sha(sorted(fdata)),
        "V_opponent_reply_set_sha256":sha(sorted(vdata)),
        "common_legal_opponent_replies":len(common),
        "F_only_legal_opponent_replies":fonly,
        "V_only_legal_opponent_replies":vonly,
        "response_contingent_own_reply_comparisons":contrasts,
        "different_next_own_move_set_count":sum(
            not c["same_next_own_legal_move_set"] for c in contrasts),
        "different_next_own_move_count_count":sum(
            c["F_next_own_legal_count"]!=c["V_next_own_legal_count"]
            for c in contrasts),
        "scope":"Standard Chess fully legal 3-ply action-state comparison (root, opponent reply, own legal action); not a proof of engine valuation"
    }

def join(march,atomic):
    if len(march["selected"]) != 16 or len(atomic["positions"]) != 16:
        raise ValueError("P2_MARCH_SOURCE_DENOMINATOR")
    result={"schema":"c3x021-P2-legal-response-contingent-chess-decision-primitives-v1",
            "status":"ENGINE_FREE_RETROSPECTIVELY_SELECTED_P1_ROOT_CHOICE_CONTRAST",
            "frozen_source_sha256":MARCH_SHA,
            "frozen_p1_atomic_sha256":ATOMIC_SHA,
            "selected_cases":{}}
    for gid,(f,v) in FIXED_PAIRS.items():
        p=march["selected"][gid-1]
        atom=atomic["positions"][gid-1]
        if p["id"]!=gid or atom["id"]!=gid or p["source_game_sha256"]!=atom["game_sha256"]:
            raise ValueError("P2_SOURCE_JOIN_DRIFT")
        if not {f,v}.issubset({r["move"] for r in atom["profile"]["moves"]}):
            raise ValueError("P2_PAIR_NOT_FROZEN_LEGAL")
        got=pair_profile(p["fen4"],f,v)
        frozen_moves={m["move"]:m for m in atom["profile"]["moves"]}
        for key,action in (("F",f),("V",v)):
            observed=got[key+"_legal_opponent_reply_count"]
            reference=frozen_moves[action]["reply_legal_move_count"]
            if observed!=reference:
                raise ValueError("P2_REPLY_FAN_DRIFT_"+str(gid)+key)
            sig=got[key+"_opponent_reply_set_sha256"]
            if sig!=frozen_moves[action]["reply_legal_move_sha256"]:
                raise ValueError("P2_REPLY_LEGAL_SET_SHA_DRIFT_"+str(gid)+key)
        result["selected_cases"][str(gid)]={
            "source_game_sha256":p["source_game_sha256"],
            "fen4":p["fen4"],**got}
    return result

def checked(path,sha256):
    raw=Path(path).read_bytes()
    if hashlib.sha256(raw).hexdigest()!=sha256:
        raise ValueError("P2_FROZEN_SOURCE_HASH_ERROR")
    return json.loads(raw)

def main():
    ap=argparse.ArgumentParser()
    for k in ("march","atomic","out"):ap.add_argument("--"+k,required=True)
    args=ap.parse_args()
    d=join(checked(args.march,MARCH_SHA),checked(args.atomic,ATOMIC_SHA))
    out=Path(args.out);out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(d,indent=2,sort_keys=True,ensure_ascii=False)+"\n")
    for gid,c in d["selected_cases"].items():
        print("C3X021_P2_LEGAL_RESPONSE_MRI",gid,
              "F",c["F_move"],"V",c["V_move"],
              "shared_opponent_legal",c["common_legal_opponent_replies"],
              "different_next_own_move_sets",c["different_next_own_move_set_count"])
    print("C3X021_P2_CHESS_DECISION_PRIMITIVES_SOURCE_SHA",
          hashlib.sha256(out.read_bytes()).hexdigest())
if __name__=="__main__":main()
