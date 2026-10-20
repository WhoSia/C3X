import chess

# Mirrors SF16 Position::slider_blockers() called by set_check_info().
# It computes pinners from original board occupancy, excluding ALL aligned
# slider snipers when determining the unique blocking piece.
def native_pin_masks(board):
 blockers={chess.WHITE:0,chess.BLACK:0}
 pinners={chess.WHITE:0,chess.BLACK:0}
 for victim in (chess.WHITE,chess.BLACK):
  king=board.king(victim)
  assert king is not None
  enemy=not victim
  snipers=0
  for sq in chess.scan_forward(board.occupied_co[enemy]):
   p=board.piece_at(sq)
   if not p or p.piece_type not in (chess.BISHOP,chess.ROOK,chess.QUEEN):continue
   on_rank=chess.square_rank(sq)==chess.square_rank(king)
   on_file=chess.square_file(sq)==chess.square_file(king)
   diagonal=abs(chess.square_rank(sq)-chess.square_rank(king))==abs(chess.square_file(sq)-chess.square_file(king))
   if (p.piece_type in (chess.ROOK,chess.QUEEN) and (on_rank or on_file)) or (p.piece_type in (chess.BISHOP,chess.QUEEN) and diagonal):
    snipers|=chess.BB_SQUARES[sq]
  without_snipers=board.occupied & ~snipers
  for sq in chess.scan_forward(snipers):
   between=chess.between(king,sq)&without_snipers
   if between and not (between & (between-1)):
    blockers[victim]|=between
    if between&board.occupied_co[victim]:
     pinners[enemy]|=chess.BB_SQUARES[sq]
 return blockers,pinners

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
 native_blockers,native_pinners=native_pin_masks(board)
 result=1;trace=[]
 for _ in range(32):
  stm=not stm
  attackers &=occupied
  candidates=attackers&board.occupied_co[stm]
  if not candidates:break
  # Stockfish original pinners and blockers are computed before the imagined exchange.
  # python-chess pin_mask represents pinned attackers in original chess state.
  if native_pinners[not stm] & occupied:
   candidates &= ~native_blockers[stm]
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
