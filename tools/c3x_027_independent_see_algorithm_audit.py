import json,sys,chess
from pathlib import Path
VALUES={None:0,chess.PAWN:126,chess.KNIGHT:781,chess.BISHOP:825,chess.ROOK:1276,chess.QUEEN:2538,chess.KING:0}
MASK=(1<<64)-1
def see_replay(board,move,threshold):
 if not board.is_castling(move) and not board.is_en_passant(move) and move.promotion is None:pass
 else:return 0>=threshold,{"special_move":True}
 origin=board.piece_at(move.from_square);victim=board.piece_at(move.to_square)
 assert origin
 swap=VALUES[victim.piece_type if victim else None]-threshold
 if swap<0:return False,{"first_gate":"capture_value_below_threshold","swap":swap}
 swap=VALUES[origin.piece_type]-swap
 if swap<=0:return True,{"first_gate":"capturing_piece_bound","swap":swap}
 occupied=board.occupied^(chess.BB_SQUARES[move.from_square]|chess.BB_SQUARES[move.to_square])
 stm=board.turn
 attackers=(board.attackers_mask(chess.WHITE,move.to_square,occupied)|board.attackers_mask(chess.BLACK,move.to_square,occupied))
 result=1;trace=[]
 for _ in range(32):
  stm=not stm
  attackers &=occupied
  candidates=attackers&board.occupied_co[stm]
  if not candidates:break
  # Stockfish original pinners and blockers are computed before the imagined exchange.
  # python-chess pin_mask represents pinned attackers in original chess state.
  filtered=0
  for sq in chess.scan_forward(candidates):
   if board.pin_mask(stm,sq)!=MASK:
    # Test whether the original pinner remains on the hypothetical board.
    king=board.king(stm)
    if king is not None:
     enemy_pinners=board.attackers_mask(not stm,king,board.occupied)
     if enemy_pinners&occupied:continue
   filtered|=chess.BB_SQUARES[sq]
  candidates=filtered
  if not candidates:break
  result^=1
  selected=None
  for pt in (chess.PAWN,chess.KNIGHT,chess.BISHOP,chess.ROOK,chess.QUEEN,chess.KING):
   bb=candidates&board.pieces_mask(pt,stm)
   if bb:
    selected=next(chess.scan_forward(bb))
    if pt==chess.KING:
     return bool(result^1 if attackers&~board.occupied_co[stm] else result),{"trace":trace,"terminal":"king"}
    occupied^=chess.BB_SQUARES[selected]
    swap=VALUES[pt]-swap
    trace.append([chess.square_name(selected),pt,swap,result])
    if swap<result:return bool(result),{"trace":trace,"terminal":"pruned"}
    attackers=(board.attackers_mask(chess.WHITE,move.to_square,occupied)|board.attackers_mask(chess.BLACK,move.to_square,occupied))
    break
  if selected is None:break
 return bool(result),{"trace":trace,"terminal":"attackers_exhausted"}
data=json.loads(Path(sys.argv[1]).read_text())
rows=[]
for r in data["records"]:
 b=chess.Board(r["fen"]);m=chess.Move.from_uci(r["move"])
 got,why=see_replay(b,m,r["threshold"])
 rows.append({"move":r["move"],"threshold":r["threshold"],"source_bool":r["original_see"],"replay_bool":got,"matched":got==bool(r["original_see"]),"detail":why})
Path(sys.argv[2]).write_text(json.dumps({"schema":"c3x027-independent-see-algorithm-audit-v1","source_semantics":"Stockfish16 PieceValueMG; independently reimplemented attacks, occupancy and approximate pin semantics","cases":rows},indent=2)+"\n")
print("C3X027_SOURCE_SEE_REPLAY",[(r["move"],r["source_bool"],r["replay_bool"]) for r in rows])
assert all(r["matched"] for r in rows),"SOURCE_SEE_INDEPENDENT_REPLAY_MISMATCH"
print("C3X027_SOURCE_SEE_REPLAY_PASS",len(rows))
