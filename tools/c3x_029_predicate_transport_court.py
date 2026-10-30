"""C3X 0.29 P1: explicit off-support legal-position falsifier for chess explanation.

Limited to white Kc6 Rb1 vs lone black king, black to move.
This is not full chess legality, native engine play or human understanding.
"""
from itertools import product
FILES="abcdefgh"
WK=(2,5)
WR=(1,0)

def name(square):
    return FILES[square[0]]+str(square[1]+1)

def adjacent(a,b):
    return max(abs(a[0]-b[0]),abs(a[1]-b[1]))<=1

def rook_attacks(rook,target,blockers):
    if rook==target or (rook[0]!=target[0] and rook[1]!=target[1]):
        return False
    dx=(target[0]>rook[0])-(target[0]<rook[0])
    dy=(target[1]>rook[1])-(target[1]<rook[1])
    pos=(rook[0]+dx,rook[1]+dy)
    while pos!=target:
        if pos in blockers:
            return False
        pos=(pos[0]+dx,pos[1]+dy)
    return True

def legal_krk_black_to_move(king):
    return (king not in (WK,WR) and not adjacent(king,WK)
            and not rook_attacks(WR,king,{WK}))

def pred_rank7(king):
    return king[1]==6

def pred_not_g8(king):
    return king!=(6,7)

def court():
    external=[s for s in product(range(8),repeat=2)
              if legal_krk_black_to_move(s)]
    disagreements=[s for s in external
                   if pred_rank7(s)!=pred_not_g8(s)]
    witness=(0,7)
    assert witness in disagreements
    assert pred_rank7(witness) is False and pred_not_g8(witness) is True
    assert len(external)==43 and len(disagreements)==37
    return {
        "white_king":"c6",
        "white_rook":"b1",
        "legal_black_king_states":len(external),
        "predicate_disagreement_legal_states":len(disagreements),
        "first_disagreement_square":"a8",
        "example_fen":"k7/8/2K5/8/8/8/8/1R6 b - - 0 1",
        "rank7_value":False,
        "not_g8_value":True,
        "full_chess_rules_verified":False,
        "original_KRK1_reply_reachability_claim":False,
        "native_stockfish_calls":0
    }

if __name__=="__main__":
    import json
    print(json.dumps(court(),indent=2,sort_keys=True))
