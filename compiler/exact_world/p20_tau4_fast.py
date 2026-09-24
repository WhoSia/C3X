#!/usr/bin/env python3
"""Exact-semantic accelerator for the P19/P20 depth-4 transposition witness.

This keeps the P19 tau4 contract unchanged for the pawnless, castling-free
P20 material worlds. It replaces repeated FEN construction at every internal
node with python-chess's fixed-version transposition tuple plus halfmove clock,
and stores only the four lexicographically smallest witness paths per endpoint.

It is not activated by p20_compile.py unless a later, separately sealed repair
explicitly opts into it after equivalence validation.
"""
import bisect
import hashlib
from collections import OrderedDict

def _h(x: bytes) -> str:
    return hashlib.sha256(x).hexdigest()

def _compact_key(board):
    # P20 is pinned to python-chess 1.11.2 and pawnless/castling-free worlds.
    # Board._transposition_key captures piece placement, side, castling and
    # legal EP state. P19 state_key additionally includes halfmove_clock.
    fn=getattr(board,"_transposition_key",None)
    if fn is None:
        raise RuntimeError("python-chess _transposition_key unavailable")
    return (fn(), int(board.halfmove_clock))

def _state_key(board):
    import chess
    ep="-" if board.ep_square is None else chess.square_name(board.ep_square)
    return " ".join([
        board.board_fen(),
        "w" if board.turn else "b",
        board.castling_xfen() or "-",
        ep,
        str(board.halfmove_clock),
    ])

def _insert_smallest4(a, value):
    bisect.insort(a,value)
    if len(a)>4:
        a.pop()

def tau4_fast(board,max_paths=350000):
    endpoints=OrderedDict()
    path_count=0
    excluded=0
    overflow=False
    root=_compact_key(board)

    def dfs(b,d,path,seen):
        nonlocal path_count,excluded,overflow
        if overflow:
            return
        if d==4:
            path_count+=1
            if path_count>max_paths:
                overflow=True
                return
            ck=_compact_key(b)
            rec=endpoints.get(ck)
            ps=" ".join(path)
            if rec is None:
                lh=_h(" ".join(sorted(m.uci() for m in b.legal_moves)).encode())
                rec={
                    "endpoint_state":_state_key(b),
                    "legal_move_set_sha256":lh,
                    "count":0,
                    "paths4":[],
                }
                endpoints[ck]=rec
            rec["count"]+=1
            _insert_smallest4(rec["paths4"],ps)
            return
        if b.is_game_over(claim_draw=False):
            return
        for mv in list(b.legal_moves):
            b.push(mv)
            ck=_compact_key(b)
            if ck in seen:
                excluded+=1
                b.pop()
                continue
            dfs(b,d+1,path+[mv.uci()],seen|{ck})
            b.pop()
            if overflow:
                return

    dfs(board.copy(stack=False),0,[],{root})
    if overflow:
        return {
            "tau4":None,
            "overflow":True,
            "enumerated_depth4_paths":path_count,
            "excluded_history_paths":excluded,
        }

    tau=0
    dup=0
    witnesses=[]
    for rec in endpoints.values():
        if rec["count"]>=2:
            dup+=1
            tau+=rec["count"]-1
            if len(witnesses)<3:
                witnesses.append({
                    "endpoint_state":rec["endpoint_state"],
                    "legal_move_set_sha256":rec["legal_move_set_sha256"],
                    "paths":list(rec["paths4"]),
                })
    return {
        "tau4":tau,
        "duplicate_endpoint_states":dup,
        "enumerated_depth4_paths":path_count,
        "excluded_history_paths":excluded,
        "overflow":False,
        "witnesses":witnesses,
    }
