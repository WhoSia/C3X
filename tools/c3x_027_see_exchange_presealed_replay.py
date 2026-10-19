import ast,json,hashlib
from pathlib import Path
import chess
src=Path("tools/C3X_027_P6_FULL_RULES_CERTIFIER.py").read_text()
tree=ast.parse(src)
P=next(ast.literal_eval(n.value) for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=="P" for t in n.targets))
VALUE={chess.PAWN:1,chess.KNIGHT:3,chess.BISHOP:3,chess.ROOK:5,chess.QUEEN:9}
def val(board,move):
    if board.is_en_passant(move):return 1
    x=board.piece_at(move.to_square)
    return VALUE.get(x.piece_type,0) if x else 0
def inspect(k,fen,root):
    b=chess.Board(fen);m=chess.Move.from_uci(root)
    assert b.is_valid() and m in b.legal_moves
    initial=val(b,m)
    b.push(m)
    all_replies=list(b.legal_moves)
    rows=[]
    for reply in all_replies:
        if not b.is_capture(reply):continue
        loss=val(b,reply)
        b.push(reply)
        options=[(v.uci(),val(b,v)) for v in b.legal_moves if b.is_capture(v) and v.to_square==reply.to_square]
        b.pop()
        best=max((x[1] for x in options),default=None)
        rows.append(dict(reply=reply.uci(),opponent_capture_loss=loss,white_immediate_recaptures=options,best_recapture_gain=best,net_material_if_best_reply=(initial-loss+best if best is not None else None)))
    if not rows:status="EMPTY_CONDITION";worst=None
    elif any(r["best_recapture_gain"] is None for r in rows):status="UNRECOVERABLE_CAPTURE";worst=None
    else:status="FULL_COVERAGE";worst=min(r["net_material_if_best_reply"] for r in rows)
    return dict(game_index=k,root=root,all_reply_count=len(all_replies),capture_reply_count=len(rows),root_material_gain=initial,status=status,worst_guaranteed_recapture_material_delta=worst,rows=rows)
cases=[]
for k,fen,roots in P:
    if str(k).startswith("KRK"):continue
    for root in roots.split(","):cases.append(inspect(k,fen,root))
assert len(cases)==18
for x in cases:
    if x["game_index"] in ("42","43","47","99"):print("SEE_EXCHANGE",x["game_index"],x["root"],x["status"],x["worst_guaranteed_recapture_material_delta"])
report={"schema":"c3x027-see-exchange-presealed-replay-v1","source_preseal":"f6d1baff6de0d90c115f6ef5d050ef52e9b4858a","library":chess.__version__,"cases":cases}
data=json.dumps(report,indent=2).encode()
Path("C3X_027_SEE_EXCHANGE_RESULTS.json").write_bytes(data)
print("SEE_EXCHANGE_REPLAY_PASS",len(cases),hashlib.sha256(data).hexdigest())
