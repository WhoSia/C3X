#!/usr/bin/env python3
"""P39/R1 exact chess-law certificate for forced checkmate by mover's second turn.

This is a diagnostic on 16 previously exposed P37 worlds, not a predictive
model, general chess-value oracle or independent cohort. No chess engine.
"""
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path
import chess

SOURCE_SHA = "77ebaa409e7c2099cc6cce3419c2f55ded295d925ab441dc2d13c16b67c2c361"
PRED_SHA = "da395f0eb16e7b294af2056dadd92b579770aa8f1ae288d1d358132685807051"
MAX_EXPANSIONS = 1000000

def need(ok, code):
    if not ok:
        raise ValueError("P39_R1_HOLD_" + code)

def digest(data):
    return hashlib.sha256(data).hexdigest()

def read_fixed(path, expected):
    data=Path(path).read_bytes()
    need(digest(data)==expected, "SOURCE_MEMBER_SHA")
    return json.loads(data)

def board_from_source(game):
    board=chess.Board()
    moves=game["full_game_uci"]
    need(game["fixed_ply"]==30 and len(moves)>=60,"SOURCE_PLY_OR_LENGTH")
    need(digest(" ".join(moves).encode("ascii"))==game["full_game_uci_sha256"],"FULL_GAME_SHA")
    for u in moves[:30]:
        m=chess.Move.from_uci(u)
        need(m in board.legal_moves,"ILLEGAL_SOURCE_HISTORY")
        board.push(m)
    need(board.fen(en_passant="fen")==game["frozen_fen"],"HISTORY_FEN")
    need(not board.is_game_over(claim_draw=False),"TERMINAL_SOURCE")
    return board

def calculate_q(board, root_uci, cap=MAX_EXPANSIONS):
    """TRUE iff root mates now, or every opponent move allows our mate in 1.

    Negative is certified by one opponent move and complete own legal response
    list. A cap reached results in HOLD, never a negative.
    """
    root=chess.Move.from_uci(root_uci)
    need(root in board.legal_moves,"ILLEGAL_ROOT")
    child=board.copy(stack=True)
    child.push(root)
    if child.is_checkmate():
        return {"verdict":"TRUE","kind":"IMMEDIATE_MATE",
                "opponent_reply_count":0,"all_reply_mating_witnesses":{},
                "counterexample":None,"expanded_legal_nodes":1}
    if child.is_game_over(claim_draw=False):
        return {"verdict":"FALSE","kind":"TERMINAL_NOT_MATE",
                "opponent_reply_count":0,"all_reply_mating_witnesses":{},
                "counterexample":{"type":"TERMINAL_AFTER_ROOT","fen":child.fen()},
                "expanded_legal_nodes":1}
    replies=sorted(m.uci() for m in child.legal_moves)
    need(len(replies)>0,"NO_OPPONENT_REPLIES_WITH_NONTERMINAL_STATE")
    witnesses={}
    expanded=1
    for response in replies:
        r=chess.Move.from_uci(response)
        after=child.copy(stack=True)
        after.push(r)
        expanded+=1
        need(expanded<=cap,"COMPUTE_CAP")
        replies_to_r=sorted(m.uci() for m in after.legal_moves)
        mating=None
        for own in replies_to_r:
            expanded+=1
            need(expanded<=cap,"COMPUTE_CAP")
            u=chess.Move.from_uci(own)
            if not after.gives_check(u):
                continue
            pos=after.copy(stack=True)
            pos.push(u)
            if pos.is_checkmate():
                mating=own
                break
        if mating is None:
            # Exact full legal set is included: independent replays can verify
            # absence of any mating own reply (including when reply is terminal).
            return {"verdict":"FALSE","kind":"OPPONENT_COUNTEREXAMPLE",
                    "opponent_reply_count":len(replies),
                    "all_reply_mating_witnesses":witnesses,
                    "counterexample":{"type":"LEGAL_RESPONSE",
                        "opponent_reply":response,
                        "all_own_legal_moves":replies_to_r},
                    "expanded_legal_nodes":expanded}
        witnesses[response]=mating
    need(set(witnesses)==set(replies),"REPLY_COVERAGE")
    return {"verdict":"TRUE","kind":"FORCED_MATE_ON_SECOND_TURN",
            "opponent_reply_count":len(replies),
            "all_reply_mating_witnesses":witnesses,
            "counterexample":None,"expanded_legal_nodes":expanded}

def verify_q_certificate(board, root_uci, record):
    """Independent full legal-replay verification of emitted proof/counterproof."""
    root=chess.Move.from_uci(root_uci)
    need(root in board.legal_moves,"CERT_ROOT_ILLEGAL")
    after_root=board.copy(stack=True);after_root.push(root)
    kind=record["kind"];v=record["verdict"]
    if kind=="IMMEDIATE_MATE":
        need(v=="TRUE" and after_root.is_checkmate(),"CERT_IMMEDIATE_NOT_MATE")
        return True
    if kind=="TERMINAL_NOT_MATE":
        need(v=="FALSE" and after_root.is_game_over(claim_draw=False)
             and not after_root.is_checkmate(),"CERT_TERMINAL_NOT_TERMINAL")
        return True
    need(not after_root.is_game_over(claim_draw=False),"CERT_INCORRECT_NONTERMINAL")
    all_replies=set(m.uci() for m in after_root.legal_moves)
    need(record["opponent_reply_count"]==len(all_replies),"CERT_OPP_REPLY_COUNT")
    if v=="TRUE":
        need(kind=="FORCED_MATE_ON_SECOND_TURN","CERT_TRUE_KIND")
        witnesses=record["all_reply_mating_witnesses"]
        need(set(witnesses)==all_replies,"CERT_MISSING_OPPONENT_REPLY")
        for r, u in witnesses.items():
            pos=after_root.copy(stack=True);pos.push_uci(r)
            move=chess.Move.from_uci(u)
            need(move in pos.legal_moves,"CERT_ILLEGAL_OWN_RESPONSE")
            pos.push(move)
            need(pos.is_checkmate(),"CERT_NOT_MATE")
        return True
    need(v=="FALSE" and kind=="OPPONENT_COUNTEREXAMPLE","CERT_NEG_KIND")
    counter=record["counterexample"]
    r=counter["opponent_reply"]
    need(r in all_replies,"CERT_ILLEGAL_OPPONENT_RESPONSE")
    pos=after_root.copy(stack=True);pos.push_uci(r)
    all_own=set(m.uci() for m in pos.legal_moves)
    need(set(counter["all_own_legal_moves"])==all_own,"CERT_INCOMPLETE_OWN_MOVES")
    for u in all_own:
        b=pos.copy(stack=True);b.push_uci(u)
        need(not b.is_checkmate(),"CERT_COUNTEREXAMPLE_HAS_MATE")
    return True

def audit(source, prediction):
    need(source["status"]=="EIGHT_EVENT_SOURCE_ONLY_FROZEN_HISTORY_LEDGER_GATE_PENDING","SOURCE_STATUS")
    need(prediction["status"]=="PRE_REFEREE_FROZEN_THREE_RIVAL_RESPONSE_FORECASTS","PRED_STATUS")
    need(len(source["sources"])==len(prediction["cases"])==8,"EIGHT_EVENTS")
    cases=[]
    for src,pred in zip(source["sources"],prediction["cases"]):
        game=src["selected"]
        need(src["source_id"]==pred["source_id"]==game["source_id"],"ID")
        need(game["case_id"]==pred["case_id"],"CASE_ID")
        need(pred["original_prefix_uci"]==game["full_game_uci"][:30],"PREFIX")
        need(pred["frozen_fen"]==game["frozen_fen"],"FEN")
        board=board_from_source(game)
        candidates=pred["candidate_pairs"]
        need(len(candidates)==2 and len({x["root_uci"] for x in candidates})==2,"CANDIDATES")
        worlds=[]
        for c in candidates:
            root=c["root_uci"]
            proof=calculate_q(board,root)
            need(verify_q_certificate(board,root,proof),"CERTIFICATE_VERIFICATION")
            worlds.append({"root_uci":root,**proof})
        cases.append({"case_id":game["case_id"],"source_id":src["source_id"],
                      "event_family":src["event_family"],"worlds":worlds})
    true_count=sum(w["verdict"]=="TRUE" for c in cases for w in c["worlds"])
    return {"status":"P39_R1_CHESS_LAW_COMPLETE_QM2_DIAGNOSTIC_NOT_HELDOUT",
            "outcome":"NO_POSITIVE_EXAMPLE" if true_count==0 else "POSITIVE_EXAMPLES_PRESENT",
            "source_games":8,"candidate_worlds":16,
            "q_true_worlds":true_count,"q_false_worlds":16-true_count,
            "definition":"immediate root checkmate OR forall legal opponent r exists legal own u causing immediate checkmate",
            "source_member_sha256":SOURCE_SHA,"pred_member_sha256":PRED_SHA,
            "scientific_limit":"Already-exposed P37 development; no explanatory predictor or independent chess value superiority.",
            "cases":cases}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source-member",type=Path,required=True)
    p.add_argument("--prediction-member",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    result=audit(read_fixed(a.source_member,SOURCE_SHA),read_fixed(a.prediction_member,PRED_SHA))
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n")
    print(result["status"],"true",result["q_true_worlds"],"false",result["q_false_worlds"])

if __name__=="__main__":
    main()
