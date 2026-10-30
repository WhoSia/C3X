"""C3X restricted chess legality witness: KRK, one opposing king reply ply.

Independent no-engine verifier, NOT a general chess parser. The position has
white Kc6 Ra1, black Kh8, white to play; no pawns or castling rights.
"""
from itertools import product

FILES="abcdefgh"
def p(s): return FILES.index(s[0]),int(s[1])-1
def name(t): return FILES[t[0]]+str(t[1]+1)
def near(a,b): return max(abs(a[0]-b[0]),abs(a[1]-b[1]))==1
def rook_hit(r,t,block):
    if r==t or (r[0]!=t[0] and r[1]!=t[1]):return False
    dx=(t[0]>r[0])-(t[0]<r[0]);dy=(t[1]>r[1])-(t[1]<r[1])
    x,y=r[0]+dx,r[1]+dy
    while (x,y)!=t:
        if (x,y) in block:return False
        x+=dx;y+=dy
    return True
def legal_black_king(wk,wr,bk):
    r=[]
    for dx,dy in product((-1,0,1),repeat=2):
        if dx==dy==0:continue
        q=bk[0]+dx,bk[1]+dy
        if not all(0<=v<8 for v in q) or q==wk or near(q,wk):continue
        if q!=wr and rook_hit(wr,q,{wk}):continue
        # If q==wr, the rook is captured; no attack from that rook remains.
        r.append(name(q))
    return sorted(r)
def certificate():
    wk,rook,bk=p("c6"),p("a1"),p("h8")
    assert not near(wk,bk) and not rook_hit(rook,bk,{wk})
    a,b=p("a8"),p("b1")
    assert all(rook_hit(rook,x,{wk,bk}) and x not in (wk,bk) for x in (a,b))
    assert rook_hit(a,bk,{wk}) and not rook_hit(b,bk,{wk})
    ra,rb=legal_black_king(wk,a,bk),legal_black_king(wk,b,bk)
    assert ra==["g7","h7"] and rb==["g7","g8","h7"]
    assert all(x[1]!="8" for x in ra) and "g8" in rb
    return {"fen":"8/7k/2K5/8/8/8/8/R7 w - - 0 1",
      "A":"Ra8+","B":"Rb1","all_reply_A":ra,"all_reply_B":rb,
      "reason":"A forces black king off eighth rank for next reply; B allows Kg8",
      "refuter":"B Kg8","scope":"KRK one-ply legal reply set, NOT chess strength",
      "engine_calls":0}
if __name__=="__main__":
    import json
    print(json.dumps(certificate(),indent=2))
