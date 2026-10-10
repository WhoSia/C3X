#!/usr/bin/env python3
"""C3X021-P1: engine-blind, move-level atomic chess transition graph.

Not a taxonomy of motifs. Captures exact primitive deltas for EVERY legal root
move before observing any March native root-choice result. Chess geometric
attacks (including pinned pseudo-attacks) and legal responses are separate.
"""
import argparse
import hashlib
import json
from pathlib import Path
import chess

SOURCE_SHA="d79e48633be2b683176f1a6d4650aeea1b7584f11c85c2349a5bddda113febee"
P0_SHA="99afa9aec2bb53d29ca45e4aafb9f57b411dae77b5ddfbc0372a79ee1c127d81"
SCHEMA="c3x021-p1-atomic-move-affordance-state-transitions-v1"

def canon(x):
    return json.dumps(x,sort_keys=True,separators=(",",":"),ensure_ascii=False)

def sha(x):
    return hashlib.sha256(canon(x).encode("utf8")).hexdigest()

def piece_map(board):
    return {chess.square_name(sq):piece.symbol()
            for sq,piece in board.piece_map().items()}

def attack_edges(board):
    """Pseudo-legal geometric attacks, NOT legal capture or evaluation."""
    edges=set()
    for frm,p in board.piece_map().items():
        for sq in board.attacks(frm):
            edges.add((p.symbol(),chess.square_name(frm),chess.square_name(sq)))
    return edges

def pins(board):
    result=set()
    for sq,p in board.piece_map().items():
        if p.piece_type != chess.KING and board.is_pinned(p.color,sq):
            result.add((p.symbol(),chess.square_name(sq)))
    return result

def occupied_attack_balance(board):
    """Signed defender/attacker piece->target edges, target identity retained."""
    result={}
    for sq,p in board.piece_map().items():
        label=chess.square_name(sq)
        result[label]={
            "piece":p.symbol(),
            "same_side_geometric_attackers":len(board.attackers(p.color,sq)),
            "opposing_geometric_attackers":len(board.attackers(not p.color,sq)),
        }
    return result

def safe_response_list(board):
    if not board.is_valid():
        raise ValueError("INVALID_POST_MOVE_BOARD")
    legal=list(board.legal_moves)
    return (
        sorted(m.uci() for m in legal),
        sorted(m.uci() for m in legal if board.is_capture(m)),
        sorted(m.uci() for m in legal if board.gives_check(m)),
    )

def diffs(before,after):
    return {
        "lost":sorted(before-after),
        "gained":sorted(after-before),
    }

def transition(board,move,baseline_edges=None,baseline_pins=None,
               baseline_balance=None,baseline_piece_map=None):
    if move not in board.legal_moves:
        raise ValueError("UNLEGAL_ROOT_MOVE")
    baseline_edges=attack_edges(board) if baseline_edges is None else baseline_edges
    baseline_pins=pins(board) if baseline_pins is None else baseline_pins
    baseline_balance=(occupied_attack_balance(board) if baseline_balance is None
                      else baseline_balance)
    baseline_piece_map=piece_map(board) if baseline_piece_map is None else baseline_piece_map
    origin=chess.square_name(move.from_square)
    destination=chess.square_name(move.to_square)
    capture=board.is_capture(move)
    en_passant=board.is_en_passant(move)
    castle=board.is_castling(move)
    mover=board.piece_at(move.from_square).symbol()
    next_board=board.copy(stack=False)
    next_board.push(move)
    now_map=piece_map(next_board)
    now_edges=attack_edges(next_board)
    now_pins=pins(next_board)
    now_balance=occupied_attack_balance(next_board)
    replies,captures,checks=safe_response_list(next_board)
    occupancy=[{"square":sq,"before":baseline_piece_map.get(sq),
                "after":now_map.get(sq)}
               for sq in sorted(set(baseline_piece_map)|set(now_map))
               if baseline_piece_map.get(sq)!=now_map.get(sq)]
    changed_balances=[{"square":sq,"before":baseline_balance.get(sq),
                       "after":now_balance.get(sq)}
                      for sq in sorted(set(baseline_balance)|set(now_balance))
                      if baseline_balance.get(sq)!=now_balance.get(sq)]
    attack_delta=diffs(baseline_edges,now_edges)
    pin_delta=diffs(baseline_pins,now_pins)
    # Check if the opponent has an actual legal response that captures the
    # newly occupied destination. This is NOT a SEE exchange proof.
    legal_dest_capture=sorted(
        x for x in captures
        if chess.Move.from_uci(x).to_square==move.to_square
    )
    event={
        "move":move.uci(),
        "native_move":move.from_square*64+move.to_square,
        "piece":mover,"from":origin,"to":destination,
        "root_capture":capture,"root_en_passant":en_passant,"root_castle":castle,
        "promotion":chess.piece_name(move.promotion) if move.promotion else None,
        "occupancy_delta":occupancy,
        "attack_edge_removed":[list(x) for x in attack_delta["lost"]],
        "attack_edge_added":[list(x) for x in attack_delta["gained"]],
        "pin_removed":[list(x) for x in pin_delta["lost"]],
        "pin_added":[list(x) for x in pin_delta["gained"]],
        "occupied_target_attack_balance_delta":changed_balances,
        "reply_legal_move_count":len(replies),
        "reply_legal_move_sha256":sha(replies),
        "reply_capture_count":len(captures),
        "reply_check_count":len(checks),
        "reply_captures_destination":legal_dest_capture,
        "after_root_opponent_in_check":next_board.is_check(),
        "after_root_checkmate":next_board.is_checkmate(),
        "after_root_stalemate":next_board.is_stalemate(),
    }
    return event

def profile(board):
    if not board.is_valid():
        raise ValueError("INVALID_SOURCE_BOARD")
    moves=sorted(list(board.legal_moves),key=lambda m:m.uci())
    edges=attack_edges(board)
    pin_set=pins(board)
    bal=occupied_attack_balance(board)
    pieces=piece_map(board)
    return {
        "fen4":" ".join(board.fen(en_passant="fen").split()[:4]),
        "legal_root_move_count":len(moves),
        "geometric_attack_edge_count":len(edges),
        "baseline_pin_vertices":[list(x) for x in sorted(pin_set)],
        "moves":[transition(board,m,edges,pin_set,bal,pieces) for m in moves],
    }

def prepare(source,p0):
    selected=source["selected"]
    old=p0["positions"]
    if len(selected)!=len(old) or len(selected)!=16:
        raise ValueError("MARCH_16_SOURCE_AND_P0_DENOMINATORS")
    out=[]
    for i,(row,p0row) in enumerate(zip(selected,old),1):
        if not (row["id"]==p0row["id"]==i and
                row["source_game_sha256"]==p0row["source_game_sha256"] and
                row["fen4"]==p0row["features"]["fen4"]):
            raise ValueError("SOURCE_P0_IDENTITY_MISMATCH")
        board=chess.Board(row["fen4"]+" 0 1")
        x=profile(board)
        if x["legal_root_move_count"]!=row["source_root_legal_count"]:
            raise ValueError("FROZEN_LEGAL_ROOT_COUNT_DRIFT")
        if not any(m["move"]==row["played_legal_move_uci"] for m in x["moves"]):
            raise ValueError("SOURCE_MAINLINE_MOVE_ABSENT")
        out.append({
            "id":i,"game_sha256":row["source_game_sha256"],
            "source_mainline_root_move":row["played_legal_move_uci"],
            "profile":x,
        })
    return {
        "schema":SCHEMA,
        "phase":"ENGINE_BLIND_CHESS_ATOMIC_MOVE_STRUCTURE_SEALED",
        "frozen_source_sha256":SOURCE_SHA,
        "frozen_p0_sha256":P0_SHA,
        "interpretation":"Primitive per-move state transitions; no causal Stockfish motif labels or bestmove observations.",
        "positions":out,
    }

def main():
    ap=argparse.ArgumentParser()
    for field in ("march","p0","out"):ap.add_argument("--"+field,required=True)
    a=ap.parse_args()
    def read(path,expected):
        raw=Path(path).read_bytes()
        if hashlib.sha256(raw).hexdigest()!=expected:
            raise ValueError("INPUT_SHA_DRIFT_"+Path(path).name)
        return json.loads(raw)
    report=prepare(read(a.march,SOURCE_SHA),read(a.p0,P0_SHA))
    out=Path(a.out)
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(report,sort_keys=True,indent=2,ensure_ascii=False)+"\n")
    print("C3X021_P1_ATOMIC_CHESS_TRANSITIONS_SOURCE_FROZEN",
          len(report["positions"]),
          sum(len(r["profile"]["moves"]) for r in report["positions"]),
          hashlib.sha256(out.read_bytes()).hexdigest(),flush=True)
if __name__=="__main__":main()
