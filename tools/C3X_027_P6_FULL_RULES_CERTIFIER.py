import chess,json
from pathlib import Path
P=[
("KRK_M1","8/8/8/8/8/1R6/8/k1K5 w - - 0 1","b3a3"),
("KRK_H3","8/8/8/8/2R5/k7/8/1K6 w - - 0 1","b1c2"),
("2","2rrk3/pp2n1p1/2nbpp2/P2p3p/3P3P/1NPBB1P1/1P3P2/R4RK1 w - - 0 21","f1e1,g1g2"),
("31","2r5/3k1ppp/qprBp3/PR1pP3/Q7/2n5/P4PPK/R7 w - - 1 30","a4f4,a4h4"),
("42","r3r1k1/pbq2pp1/1p1bp2p/4P3/P7/2PB3P/3BQPP1/R3R1K1 b - - 0 17","d6c5,d6f8"),
("43","r7/1p4pk/2p2p1p/p2q4/Pn1PrB1P/6Q1/1P3PP1/2R2RK1 b - - 2 27","a8e8,d5f5"),
("47","r5k1/ppb4p/2p2qp1/3pR3/2P5/3B2Pb/PP1N1P1P/R2Q2K1 b - - 0 21","c7e5,f6e5"),
("52","r1b1qrk1/ppp4p/3p1nnb/3P1p2/2P1p3/2N3BP/PPQNBPP1/1K1R3R w - - 0 18","d2b3,g3h2"),
("56","r1q2rk1/p1p1nnbp/1p1p4/3Pppp1/1PP2P2/2N1P1P1/PB1QN1KP/R4R2 w - - 0 17","a2a4,b4b5"),
("79","2kr3r/pppbq3/2n1pp2/3pP2p/3P3R/2NBQ1P1/PPP2P2/2K4R w - - 0 22","c3e2,f2f4"),
("99","2r3k1/1p3p2/2q1b1p1/3p3p/1R1Q3P/1P2PBP1/2rR1P1K/8 w - - 0 28","d2c2,h2g2")]
LIMIT=150000
def run_mate(board,root,H):
    m=chess.Move.from_uci(root)
    assert m in board.legal_moves
    b=board.copy();who=b.turn;b.push(m);nodes=[1]
    def v(remaining):
        if b.is_checkmate():return b.turn!=who,{"mate":True}
        if b.is_stalemate() or b.is_insufficient_material():return False,{"terminal":"draw"}
        if remaining==0:return False,{"terminal":"horizon"}
        items=[]
        for m in list(b.legal_moves):
            nodes[0]+=1
            if nodes[0]>LIMIT:raise OverflowError
            b.push(m);ok,p=v(remaining-1);b.pop()
            items.append((m.uci(),ok,p))
            if b.turn==who and ok:return True,{"choose":m.uci(),"child":p}
            if b.turn!=who and not ok:return False,{"refute":m.uci(),"child":p}
        if b.turn==who:return False,{"all_own_fail":[[m,p] for m,_,p in items]}
        return True,{"all_opponent":[[m,p] for m,_,p in items]}
    try:
        ok,proof=v(H-1)
        return {"status":"TRUE" if ok else "FALSE","visited_edges":nodes[0],"certificate_bytes":len(json.dumps(proof,separators=(',',':')).encode()),"certificate":proof}
    except OverflowError:return {"status":"UNKNOWN_BUDGET","visited_edges":nodes[0]}
def recapture(b,root):
    m=chess.Move.from_uci(root);bb=b.copy();bb.push(m)
    allr=list(bb.legal_moves);cr=[r for r in allr if bb.is_capture(r)];rows=[]
    for r in cr:
        bb.push(r)
        target=bb.piece_at(r.to_square)
        moves=[t.uci() for t in bb.legal_moves if t.to_square==r.to_square and bb.is_capture(t) and target and target.color!=bb.turn]
        bb.pop();rows.append({"reply":r.uci(),"witness":min(moves) if moves else None})
    failures=[x for x in rows if x["witness"] is None]
    proof={"complete_eligible_reply_list":rows if not failures else None,"counterexample":failures[0] if failures else None,"eligible":len(cr),"legal_opponent":len(allr)}
    return {"status":"EMPTY_CONDITION" if not cr else ("FALSE" if failures else "TRUE"),"certificate_bytes":len(json.dumps(proof).encode()),"proof":proof}
output=[]
for ident,fen,roots in P:
    b=chess.Board(fen)
    assert b.is_valid(),(ident,b.status())
    for root in roots.split(","):
        entry={"id":ident,"fen":fen,"root":root,"group":"CONSTRUCTED_KRK" if ident.startswith("KRK") else "P11_PRESELECTED_NOT_HELDOUT","mate_within_H":{str(h):run_mate(b,root,h) for h in (1,2,3)}}
        if not ident.startswith("KRK"):entry["conditional_recapture"]=recapture(b,root)
        output.append(entry)
assert len(output)==20
assert [output[0]["mate_within_H"][str(h)]["status"] for h in (1,2,3)]==["TRUE"]*3
assert [output[1]["mate_within_H"][str(h)]["status"] for h in (1,2,3)]==["FALSE","FALSE","TRUE"]
Path("C3X_027_P6_FULL_RULES_RESULTS.json").write_text(json.dumps({"status":"P6_FULL_RULES_PASS","library":chess.__version__,"cases":output},indent=2)+"\n")
print("P6_FULL_RULES_PASS",len(output))
for r in output:print("RESULT",r["id"],r["root"],[(h,x["status"],x["visited_edges"],x.get("certificate_bytes")) for h,x in r["mate_within_H"].items()])
