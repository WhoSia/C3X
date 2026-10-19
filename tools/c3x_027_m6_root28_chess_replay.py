import chess,json
from pathlib import Path
fen="1r3rk1/4qpp1/4p3/6p1/1p2Q3/1P4P1/2P2P1P/R4RK1 w - - 1 22"
results=[]
for u in ("f1d1","a1a5"):
 b=chess.Board(fen);m=chess.Move.from_uci(u)
 assert b.is_valid() and m in b.legal_moves
 b.push(m);moves=list(b.legal_moves);captures=[x for x in moves if b.is_capture(x)]
 rows=[]
 for x in captures:
  b.push(x)
  replies=[v.uci() for v in b.legal_moves if b.is_capture(v) and v.to_square==x.to_square]
  b.pop()
  rows.append({"reply":x.uci(),"recaptures":replies})
 results.append({"root":u,"total_legal_replies":len(moves),"capture_replies":len(captures),"check_replies":sum(b.gives_check(x) for x in moves),"all_captures_immediately_recapturable":bool(rows) and all(r["recaptures"] for r in rows),"capture_reply_audit":rows})
out={"schema":"C3X-027-M6-ROOT28-EXPLORED-v1","fen":fen,"note":"post-outcome selected; properties exploratory, not preregistered predictors","results":results}
Path("C3X_027_M6_ROOT28_CHESS_RESULTS.json").write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n")
print("M6_ROOT28_CHESS_PASS",json.dumps(results))
