#!/usr/bin/env python3
from __future__ import annotations
import argparse,json
from collections import defaultdict,Counter
from pathlib import Path
import chess

GRAMMARS=("G0_LEGACY_PHYSICAL","G1_SAME_PIECE_COLLATERAL","G2_SAME_TYPE_SIDE_COLLATERAL","G3_SIDE_ROLE_COLLATERAL","G4_GLOBAL_COLLATERAL")
PIECE_NAME={chess.KNIGHT:"KNIGHT",chess.BISHOP:"BISHOP",chess.ROOK:"ROOK",chess.QUEEN:"QUEEN"}
ATOM_BASE=("A_FROM","A_TO","B_FROM","B_TO")

def load(p): return json.loads(Path(p).read_text())

def posid(r): return f"p14:{r['source_id']}:{r['trajectory_hash'][:12]}"

def canonical_fen(b):
    f=b.fen(en_passant="fen").split()
    return " ".join(f[:4])+" 0 1"

def cheb(a,b):
    return max(abs(chess.square_file(a)-chess.square_file(b)),abs(chess.square_rank(a)-chess.square_rank(b)))

def apply_edit(b,fr,to):
    q=b.copy(stack=False);pc=q.piece_at(fr)
    q.remove_piece_at(fr);q.set_piece_at(to,pc);q.halfmove_clock=0
    return q

def relvec(b,sq,endpoints):
    aa=b.attacks(sq)
    return [bool(aa & chess.BB_SQUARES[x]) for x in endpoints]

def atoms(before,after):
    out=[]
    for i,(x,y) in enumerate(zip(before,after)):
        if x==y:continue
        out.append(ATOM_BASE[i]+("_GAIN" if (not x and y) else "_LOSS"))
    return tuple(sorted(out))

def lexical_asym(a):
    return sum(x.startswith("A_") for x in a)!=sum(x.startswith("B_") for x in a)

def lbin(x):
    x=abs(int(x))
    return "LOW" if x<=2 else "MID" if x<=4 else "HIGH"

def abin(x):
    x=int(x)
    return "LOW" if x<=3 else "MID" if x<=6 else "HIGH"

def enumerate_edits(fen,A,B):
    b=chess.Board(fen)
    ma=chess.Move.from_uci(A);mb=chess.Move.from_uci(B)
    endpoints=[ma.from_square,ma.to_square,mb.from_square,mb.to_square]
    blocked=set(endpoints);moving={ma.from_square,mb.from_square}
    rows=[]
    for fr,piece in sorted(b.piece_map().items()):
        if fr in moving or piece.piece_type not in PIECE_NAME:continue
        if piece.piece_type==chess.ROOK and bool(b.castling_rights & chess.BB_SQUARES[fr]):continue
        for to in sorted(b.attacks(fr)):
            if to in blocked or b.piece_at(to) is not None:continue
            q=apply_edit(b,fr,to)
            if not q.is_valid() or q.is_game_over(claim_draw=False) or q.is_check():continue
            legal={m.uci() for m in q.legal_moves}
            if A not in legal or B not in legal:continue
            ld=q.legal_moves.count()-b.legal_moves.count()
            ad=len(set(b.attacks(fr)) ^ set(q.attacks(to)))
            if abs(ld)>6 or ad>10:continue
            before=relvec(b,fr,endpoints);after=relvec(q,to,endpoints);ats=atoms(before,after)
            rows.append({
              "edit_id":chess.square_name(fr)+chess.square_name(to),
              "from":chess.square_name(fr),"to":chess.square_name(to),
              "distance":cheb(fr,to),
              "piece_type":PIECE_NAME[piece.piece_type],
              "side_role":"OWN" if piece.color==b.turn else "OPPONENT",
              "atoms":ats,
              "legal_move_delta":ld,
              "attack_symdiff":ad,
              "legal_bin":lbin(ld),"attack_bin":abin(ad),
              "profile":f"{lbin(ld)}|{abin(ad)}",
              "fen":canonical_fen(q)
            })
    rows.sort(key=lambda z:(z["edit_id"],z["atoms"],z["legal_bin"],z["attack_bin"]))
    return rows

def match(g,t,c):
    if g=="G0_LEGACY_PHYSICAL":
        return t["from"]==c["from"] and t["distance"]==c["distance"]
    if g=="G1_SAME_PIECE_COLLATERAL":
        return t["from"]==c["from"] and t["profile"]==c["profile"]
    if g=="G2_SAME_TYPE_SIDE_COLLATERAL":
        return t["piece_type"]==c["piece_type"] and t["side_role"]==c["side_role"] and t["profile"]==c["profile"]
    if g=="G3_SIDE_ROLE_COLLATERAL":
        return t["side_role"]==c["side_role"] and t["profile"]==c["profile"]
    if g=="G4_GLOBAL_COLLATERAL":
        return t["profile"]==c["profile"]
    raise ValueError(g)

def collateral_key(x):
    return (abs(int(x["legal_move_delta"])),int(x["attack_symdiff"]),x["edit_id"])

def chains_for(rows,g):
    shams=[x for x in rows if not x["atoms"]]
    targets=[x for x in rows if x["atoms"] and lexical_asym(x["atoms"])]
    out=[]
    for t in targets:
        ts=set(t["atoms"])
        sham=[x for x in shams if x["edit_id"]!=t["edit_id"] and match(g,t,x)]
        if not sham:continue
        sham=sorted(sham,key=collateral_key)[0]
        if len(ts)==1:
            out.append({"type":"ATOMIC_CHAIN","target":t,"subset":sham,"sham":sham,
                        "deleted_atoms":1,"total_collateral":sum(collateral_key(x)[0]+collateral_key(x)[1] for x in (t,sham))})
            continue
        subs=[x for x in rows if x["edit_id"]!=t["edit_id"] and x["atoms"] and set(x["atoms"])<ts and match(g,t,x)]
        if not subs:continue
        subs.sort(key=lambda x:(0 if len(ts)-len(x["atoms"])==1 else 1,-len(x["atoms"]),*collateral_key(x)))
        s=subs[0]
        out.append({"type":"COMPOSITE_DELETION_CHAIN","target":t,"subset":s,"sham":sham,
                    "deleted_atoms":len(ts)-len(s["atoms"]),
                    "total_collateral":sum(abs(int(x["legal_move_delta"]))+int(x["attack_symdiff"]) for x in (t,s,sham))})
    out.sort(key=lambda z:(0 if z["type"]=="COMPOSITE_DELETION_CHAIN" else 1,z["deleted_atoms"],z["total_collateral"],
                           z["target"]["edit_id"],z["subset"]["edit_id"],z["sham"]["edit_id"]))
    return out

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--pair-freeze",required=True)
    ap.add_argument("--balanced-corpus",required=True)
    ap.add_argument("--out",required=True)
    a=ap.parse_args()
    pf=load(a.pair_freeze);corp=load(a.balanced_corpus)
    ctx={posid(r):r["cell"] for r in corp["positions"]}
    fen={}
    for c in pf["cases"]:
        fen.setdefault(c["position_id"],c["cell"]["fen"])
    admitted=[(pid,z) for pid,z in sorted(pf["positions"].items()) if z.get("admitted")]
    rows=[];summary={}
    for pid,z in admitted:
        if pid not in ctx or pid not in fen:raise SystemExit(f"P15_JOIN {pid}")
        A=z["pair"]["A"]["uci"];B=z["pair"]["B"]["uci"]
        edits=enumerate_edits(fen[pid],A,B)
        per={}
        for g in GRAMMARS:
            cc=chains_for(edits,g)
            per[g]={
              "chain_count":len(cc),
              "best_chain":None if not cc else {
                "type":cc[0]["type"],
                "target_edit":cc[0]["target"]["edit_id"],
                "subset_edit":cc[0]["subset"]["edit_id"],
                "sham_edit":cc[0]["sham"]["edit_id"],
                "target_atoms":list(cc[0]["target"]["atoms"]),
                "subset_atoms":list(cc[0]["subset"]["atoms"]),
                "piece_type":cc[0]["target"]["piece_type"],
                "side_role":cc[0]["target"]["side_role"],
                "profile":cc[0]["target"]["profile"],
                "total_collateral":cc[0]["total_collateral"],
                "target_fen":cc[0]["target"]["fen"],
                "subset_fen":cc[0]["subset"]["fen"],
                "sham_fen":cc[0]["sham"]["fen"]
              }
            }
        rows.append({"position_id":pid,"source_id":z["source_id"],"context":ctx[pid],"pair":z["pair"],
                     "eligible_edit_count":len(edits),"grammars":per})
    cells_total=sorted({"|".join((r["context"]["phase"],r["context"]["branching"],r["context"]["tactical_surface"])) for r in rows})
    for g in GRAMMARS:
        yes=[r for r in rows if r["grammars"][g]["chain_count"]>0]
        cells=sorted({"|".join((r["context"]["phase"],r["context"]["branching"],r["context"]["tactical_surface"])) for r in yes})
        phases=sorted({r["context"]["phase"] for r in yes});branches=sorted({r["context"]["branching"] for r in yes});tacts=sorted({r["context"]["tactical_surface"] for r in yes})
        summary[g]={
          "chain_positions":len(yes),"admitted_pair_positions":len(rows),
          "chain_fraction_of_pairs":len(yes)/len(rows) if rows else 0,
          "context_cells_with_chain_support":len(cells),"supported_cells":cells,
          "phase_levels":phases,"branching_levels":branches,"tactical_levels":tacts,
          "mean_eligible_edits":sum(r["eligible_edit_count"] for r in rows)/len(rows) if rows else 0
        }
        summary[g]["structural_gate_pass"]=(
          summary[g]["chain_fraction_of_pairs"]>=0.50 and len(cells)>=12 and len(phases)>=3 and len(branches)>=3 and len(tacts)>=2
        )
    selected=next((g for g in GRAMMARS if summary[g]["structural_gate_pass"]),None)
    verdict="PASS_MINIMAL_RELAXATION_STRUCTURAL_REALIZABILITY" if selected else "HOLD_NO_STRUCTURAL_GRAMMAR_RECOVERS_BALANCED_CHAIN_SUPPORT"
    allocation=[]
    if selected:
        for r in rows:
            b=r["grammars"][selected]["best_chain"]
            if b:
                allocation.append({"position_id":r["position_id"],"source_id":r["source_id"],"context":r["context"],"pair":r["pair"],"chain":b})
    out={
      "schema":"c3x-g10-p15-stage-a-v1","stage":"C3X 0.9.0-G10-P15",
      "status":"STRUCTURAL_ENGINE_FREE","verdict":verdict,
      "engine_execution":False,"intervention_outcomes_consulted":False,"defect_outcomes_consulted":False,
      "admitted_pair_positions":len(rows),"balanced_context_cells_in_pair_population":len(cells_total),
      "grammar_order":list(GRAMMARS),"grammar_summary":summary,"selected_grammar":selected,
      "stage_b_allocation":allocation,
      "position_rows":rows
    }
    Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print("G10_P15_STAGE_A",verdict,"SELECTED",selected)
    for g in GRAMMARS:
        z=summary[g];print("GRAMMAR",g,z["chain_positions"],z["chain_fraction_of_pairs"],z["context_cells_with_chain_support"],z["phase_levels"],z["branching_levels"],z["tactical_levels"],z["structural_gate_pass"])
    print("STAGE_B_ALLOC",len(allocation))
if __name__=="__main__":main()
