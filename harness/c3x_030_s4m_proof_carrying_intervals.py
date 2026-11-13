#!/usr/bin/env python3
"""C3X 0.30/S4-M: proof-carrying, partial-coverage endgame intervals.

Research lineage: Herbeck & Barth (1996), ICCA Journal 19(2), 75–82.
Original C3X contribution: enforce a TYPE boundary between a proved
terminal/inductively backed-up WDL interval and an observed Stockfish
search-site trace (which never by itself certifies a WDL lower bound).

Bounds are for the player to MOVE, in ordered -1(loss),0(draw),+1(win).
Unknown legal moves count as [-1,+1]; no synthetic exactness. A winning
witness can prove [+1,+1] with INCOMPLETE branch coverage; proving that a
position is no better than a draw requires universal upper-bound coverage.
No NNUE score is converted to a mathematically certified outcome.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Mapping
import chess

WDL=(-1,0,1)
SCHEMA="c3x030-s4m-proof-carrying-interval-v1"

@dataclass(frozen=True)
class ProofInterval:
    lower:int
    upper:int
    lower_tags:tuple[str,...]=()
    upper_tags:tuple[str,...]=()
    certificate:str="unknown"
    verified:bool=False
    def __post_init__(self):
        if type(self.lower) is not int or type(self.upper) is not int or self.lower not in WDL or self.upper not in WDL or self.lower>self.upper:
            raise ValueError("S4M_BAD_WDL_INTERVAL")
        if self.verified and self.certificate not in ("legal_terminal","partial_sound_negamax_backup"):
            raise ValueError("S4M_UNTRUSTED_PROOF_KIND")
        if not self.verified and (self.lower,self.upper)!=(-1,1):
            raise ValueError("S4M_UNVERIFIED_SOURCE_CANNOT_TIGHTEN_WDL")
    def as_dict(self):
        return {"lower":self.lower,"upper":self.upper,"lower_tags":list(self.lower_tags),
          "upper_tags":list(self.upper_tags),"certificate":self.certificate,
          "verified":self.verified}

def unknown()->ProofInterval:
    return ProofInterval(-1,1)

def terminal(board:chess.Board)->ProofInterval:
    """Legal terminal only. History-sensitive threefold/fifty move claims excluded."""
    if not board.is_valid():
        raise ValueError("S4M_INVALID_BOARD")
    if board.is_checkmate():
        value=-1
        reason="mate"
    elif board.is_stalemate():
        value=0
        reason="stalemate"
    elif board.is_insufficient_material():
        value=0
        reason="insufficient_material"
    else:
        raise ValueError("S4M_NOT_A_CERTIFIABLE_TERMINAL")
    tag=f"TERMINAL:{reason}:{board.fen()}"
    return ProofInterval(value,value,(tag,),(tag,),"legal_terminal",True)

def terminal_child(board:chess.Board,move_uci:str)->ProofInterval:
    """Certify the resulting position, not an arbitrary engine/Q-score label."""
    if not board.is_valid():
        raise ValueError("S4M_INVALID_BOARD")
    try:
        move=chess.Move.from_uci(move_uci)
    except ValueError as e:
        raise ValueError("S4M_BAD_UCI") from e
    if move not in board.legal_moves:
        raise ValueError("S4M_ILLEGAL_MOVE")
    child=board.copy(stack=False)
    child.push(move)
    return terminal(child)

def backup(board:chess.Board,children:Mapping[str,ProofInterval])->dict:
    """Sound one-ply negamax WDL aggregation with conservative unknown edges.

    Child intervals use child side-to-move perspective. Inverted parent move
    interval is [-child.upper, -child.lower]. Strict upper-bound proof requires
    every legal move to be accounted for; unproven legal moves remain [-1,+1].
    Full exact results can nevertheless follow from ONE winning witness.
    """
    if not board.is_valid():
        raise ValueError("S4M_INVALID_BOARD")
    if board.is_game_over(claim_draw=False) and (board.is_checkmate() or board.is_stalemate() or board.is_insufficient_material()):
        if children:
            raise ValueError("S4M_TERMINAL_WITH_CHILDREN")
        value=terminal(board)
        return {"schema":SCHEMA,"board_fen":board.fen(),"interval":value.as_dict(),
          "complete_legal_branch_coverage":True,"unknown_legal_moves":[],
          "legal_move_count":0,"witness_moves":[],"universal_upper_covered":True,
          "explanation_strength":"TERMINAL_RULE_PROVEN","stockfish_mediation_proven":False}
    legal={move.uci() for move in board.legal_moves}
    if set(children)-legal:
        raise ValueError("S4M_FORGED_OR_ILLEGAL_CHILD_MOVE")
    for uci, claimed in children.items():
        if not isinstance(claimed,ProofInterval) or not claimed.verified:
            raise ValueError("S4M_UNVERIFIED_CHILD_PROOF")
        # NEVER trust a caller-supplied 'verified' flag or an arbitrary
        # Stockfish numerical score: recompute terminal chess legality AND
        # the exact certified WDL from the supplied parent and move.
        independently_verified=terminal_child(board,uci)
        if claimed != independently_verified:
            raise ValueError("S4M_FORGED_TERMINAL_CERTIFICATE")
    if not legal:
        raise ValueError("S4M_TERMINAL_NOT_HANDLED")
    evaluated={}
    for move in sorted(legal):
        child=children.get(move,unknown())
        evaluated[move]=(-child.upper,-child.lower,child)
    best_lower=max(x[0] for x in evaluated.values())
    best_upper=max(x[1] for x in evaluated.values())
    witnesses=[m for m,(lo,hi,b) in evaluated.items() if lo==best_lower and b.verified]
    unknown_moves=[m for m in sorted(legal) if m not in children]
    all_upper_proved=not unknown_moves and all(evaluated[m][2].verified for m in legal)
    lower_tags=tuple(f"MOVE:{m}/NEGATED_UPPER:"+t for m in witnesses for t in evaluated[m][2].upper_tags)
    if best_lower==-1 and not lower_tags:
        lower_tags=() # universal trivial lower bound, not a winning witness
    upper_tags=tuple(f"MOVE:{m}/NEGATED_LOWER:"+t
                   for m,(lo,hi,b) in sorted(evaluated.items())
                   for t in b.lower_tags) if all_upper_proved else ()
    # A global WDL maximum <= 1 is a trivial upper bound even with missing moves.
    upper_universal=best_upper==1 or all_upper_proved
    cert=ProofInterval(best_lower,best_upper,lower_tags,upper_tags,
             "partial_sound_negamax_backup",True)
    exact=best_lower==best_upper
    return {"schema":SCHEMA,"board_fen":board.fen(),"interval":cert.as_dict(),
      "complete_legal_branch_coverage":all_upper_proved,
      "unknown_legal_moves":unknown_moves,"legal_move_count":len(legal),
      "witness_moves":witnesses,"universal_upper_covered":upper_universal,
      "explanation_strength":"EXACT_WDL_PROVED" if exact else "SOUND_BOUNDS_ONLY",
      "stockfish_mediation_proven":False}

def observational_engine_event(event:dict)->ProofInterval:
    """TT/root logging may carry source information but NEVER WDL proof."""
    if not isinstance(event,dict) or event.get("source_kind") not in (
         "native_tt_mask","native_root_score","native_tt_cutoff"):
        raise ValueError("S4M_UNKNOWN_ENGINE_OBSERVATION")
    return unknown()
