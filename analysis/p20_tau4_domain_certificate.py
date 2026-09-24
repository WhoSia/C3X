#!/usr/bin/env python3
"""Domain certificate for the P20 tau4 exact-semantic accelerator.

The certificate is outcome-blind.  It checks the actual P20 candidate domain
and a bounded depth-2 closure for representation collisions in both directions:
frozen P19 state_key <-> accelerated compact key.  It also enforces the domain
facts that make the representation equivalence valid (pawnless, castling-free,
no en-passant state, no promoted markers).
"""
import json
import sys
from collections import deque
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"compiler"/"exact_world"))

import chess
import p19_compile as old
from p20_tau4_fast import _compact_key

ROOTS_PER_SIDE=6
MAX_STATES_PER_ROOT=6000
DEPTH=2

def domain_guard(b):
    if b.pawns:
        raise AssertionError("P20_TAU4_DOMAIN_PAWN")
    if b.castling_rights:
        raise AssertionError("P20_TAU4_DOMAIN_CASTLING")
    if b.ep_square is not None:
        raise AssertionError("P20_TAU4_DOMAIN_EP")
    if getattr(b,"promoted",0):
        raise AssertionError("P20_TAU4_DOMAIN_PROMOTED")

def inspect_root(root):
    q=deque([(root.copy(stack=False),0)])
    c2s={}
    s2c={}
    states=0
    while q:
        b,d=q.popleft()
        domain_guard(b)
        ck=repr(_compact_key(b))
        sk=old.state_key(b)
        prior=c2s.setdefault(ck,sk)
        if prior!=sk:
            raise AssertionError("P20_TAU4_COMPACT_COLLISION")
        prior2=s2c.setdefault(sk,ck)
        if prior2!=ck:
            raise AssertionError("P20_TAU4_STATE_COLLISION")
        states+=1
        if states>=MAX_STATES_PER_ROOT or d>=DEPTH or b.is_game_over(claim_draw=False):
            continue
        for mv in list(b.legal_moves):
            z=b.copy(stack=False)
            z.push(mv)
            q.append((z,d+1))
    return states,len(c2s),len(s2c)

rows=[]
for material,(_,_,pieces) in old.VERTICES.items():
    for side in (chess.WHITE,chess.BLACK):
        found=0
        for i in range(96):
            b=old.candidate(material,pieces,side,i)
            if b is None:
                continue
            states,nc,ns=inspect_root(b)
            rows.append({
                "material":material,
                "side":"WHITE" if side else "BLACK",
                "index":i,
                "states_checked":states,
                "compact_keys":nc,
                "state_keys":ns
            })
            found+=1
            if found>=ROOTS_PER_SIDE:
                break
        if found<ROOTS_PER_SIDE:
            raise SystemExit(f"P20_TAU4_DOMAIN_ROOT_SHORTFALL {material} {side} {found}")

out={
    "schema":"c3x-p20-tau4-domain-certificate-v1",
    "scientific_stage":"C3X 0.7.0-G9.4-P20-R2",
    "python_chess":chess.__version__,
    "depth":DEPTH,
    "roots_per_side_per_material":ROOTS_PER_SIDE,
    "rows":rows,
    "total_roots":len(rows),
    "total_states_checked":sum(r["states_checked"] for r in rows),
    "engine_outcomes_consulted":False,
    "verdict":"PASS"
}
print(json.dumps(out,indent=2,sort_keys=True))
