"""P21 original 12 source moves: independent bounded chess geometry and self-check audit.

This verifier supports non-special moves only, not castling, en passant, promotion,
game history, adjudication or complete move generation.
"""
def board_from_fen(fen):
    fields=fen.split()
    if len(fields)!=4: raise ValueError("FOUR_FIELD_ONLY")
    rows=fields[0].split("/")
    if len(rows)!=8 or fields[1] not in ("w","b"):raise ValueError("BAD_FEN")
    b={}
    for yi,row in enumerate(rows):
        x=0
        for c in row:
            if c in "12345678":x+=int(c)
            elif c in "prnbqkPRNBQK" and x<8:b[(x,7-yi)]=c;x+=1
            else:raise ValueError("BAD_FEN_PIECE")
        if x!=8:raise ValueError("BAD_FEN_RANK")
    return b,fields[1]

def square(s):
    if len(s)!=2 or s[0] not in "abcdefgh" or s[1] not in "12345678":raise ValueError("BAD_SQUARE")
    return (ord(s[0])-97,int(s[1])-1)

def attacked(board,tgt,by_white):
    tx,ty=tgt
    for (x,y),piece in board.items():
        if piece.isupper()!=by_white:continue
        dx,dy=tx-x,ty-y;p=piece.lower()
        if p=="p":
            if abs(dx)==1 and dy==(1 if by_white else -1):return True
        elif p=="n":
            if (abs(dx),abs(dy)) in ((1,2),(2,1)):return True
        elif p=="k":
            if max(abs(dx),abs(dy))==1:return True
        elif (p=="b" and abs(dx)==abs(dy) and dx!=0) or (p=="r" and (dx==0)!=(dy==0)) or (p=="q" and ((abs(dx)==abs(dy) and dx!=0) or (dx==0)!=(dy==0))):
            sx=(dx>0)-(dx<0);sy=(dy>0)-(dy<0);xx,yy=x+sx,y+sy
            while (xx,yy)!=(tx,ty):
                if (xx,yy) in board:break
                xx+=sx;yy+=sy
            else:return True
    return False

def inspect(fen,uci):
    try:
        board,turn=board_from_fen(fen)
        if len(uci)!=4:return "HOLD_SPECIAL_OR_MALFORMED_MOVE"
        origin,dest=square(uci[:2]),square(uci[2:])
    except ValueError:return "HOLD_UNPARSEABLE"
    piece=board.get(origin);victim=board.get(dest)
    if piece is None:return "FAIL_NO_SOURCE_PIECE"
    white=turn=="w"
    if piece.isupper()!=white:return "FAIL_WRONG_SIDE"
    if victim and victim.isupper()==white:return "FAIL_FRIENDLY_CAPTURE"
    if victim and victim.lower()=="k":return "FAIL_KING_CAPTURE"
    dx,dy=dest[0]-origin[0],dest[1]-origin[1];p=piece.lower()
    if p=="n":ok=(abs(dx),abs(dy)) in ((1,2),(2,1))
    elif p=="k":ok=max(abs(dx),abs(dy))==1
    elif p=="p":ok=(dx==0 and dy==(1 if white else -1) and not victim) or (abs(dx)==1 and dy==(1 if white else -1) and bool(victim))
    elif p=="b":ok=abs(dx)==abs(dy) and dx!=0
    elif p=="r":ok=(dx==0)!=(dy==0)
    elif p=="q":ok=(abs(dx)==abs(dy) and dx!=0) or ((dx==0)!=(dy==0))
    else:return "HOLD_PIECE"
    if not ok:return "FAIL_BAD_GEOMETRY"
    if p=="p" and dest[1] in (0,7):return "HOLD_PROMOTION"
    if p in "brq":
        sx=(dx>0)-(dx<0);sy=(dy>0)-(dy<0);x,y=origin[0]+sx,origin[1]+sy
        while (x,y)!=dest:
            if (x,y) in board:return "FAIL_BLOCKED"
            x+=sx;y+=sy
    after=dict(board);after.pop(origin);after[dest]=piece
    kings=[s for s,v in after.items() if v==("K" if white else "k")]
    if len(kings)!=1:return "HOLD_KING_COUNT"
    if attacked(after,kings[0],not white):return "FAIL_SELF_CHECK"
    return "PASS_BOUNDED_NON_SPECIAL_MOVE_ONLY"
