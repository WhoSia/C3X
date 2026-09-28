#!/usr/bin/env python3


SCHEMA="c3x-cseg-input-v1"

def bucket(v,cuts,labels):
 for c,l in zip(cuts,labels):
  if v<=c:return l
 return labels[-1]

def board_atoms(fen):
 import chess
 b=chess.Board(fen)
 vals={chess.PAWN:1,chess.KNIGHT:3,chess.BISHOP:3,chess.ROOK:5,chess.QUEEN:9}
 def mat(color):
  return sum(vals[p]*len(b.pieces(p,color)) for p in vals)
 def nonpawn():
  return sum(vals[p]*(len(b.pieces(p,chess.WHITE))+len(b.pieces(p,chess.BLACK))) for p in (chess.KNIGHT,chess.BISHOP,chess.ROOK,chess.QUEEN))
 nm=nonpawn()
 phase="OPEN" if nm>=44 else "MIDDLE" if nm>=20 else "END"
 stm=b.turn
 diff=mat(stm)-mat(not stm)
 if diff>=4:mb="STM_ADV_BIG"
 elif diff>=1:mb="STM_ADV_SMALL"
 elif diff<=-4:mb="STM_BEHIND_BIG"
 elif diff<=-1:mb="STM_BEHIND_SMALL"
 else:mb="EVEN"
 lm=b.legal_moves.count()
 legal=bucket(lm,[10,20,30,45],["LE10","11_20","21_30","31_45","46_PLUS"])
 us=bool(b.has_kingside_castling_rights(stm) or b.has_queenside_castling_rights(stm))
 them=bool(b.has_kingside_castling_rights(not stm) or b.has_queenside_castling_rights(not stm))
 castle="BOTH" if us and them else "STM_ONLY" if us else "OPP_ONLY" if them else "NONE"
 hm=bucket(b.halfmove_clock,[0,10,30,60],["ZERO","1_10","11_30","31_60","61_PLUS"])
 return {
  "side_to_move":"W" if stm else "B",
  "in_check":bool(b.is_check()),
  "phase":phase,
  "legal_moves_bucket":legal,
  "material_balance_bucket":mb,
  "castling_bucket":castle,
  "halfmove_bucket":hm
 }

def prepare_batch(fen,parent_trace,selected):
 byid={e["address_id"]:i for i,e in enumerate(parent_trace["events"])}
 sels=[]
 for s in selected:
  aid=s["event_id"]
  if aid not in byid:raise ValueError("CSEG_SELECTED_EVENT_NOT_IN_TRACE")
  sels.append({"event_id":aid,"ordinal":byid[aid],"sampling_stratum":s.get("sampling_stratum")})
 ev=[]
 for e in parent_trace["events"]:
  ev.append({
   "scope":e["scope"],"class":e["class"],"key":str(e["key"]),"ply":int(e["ply"]),"depth":int(e["depth"]),
   "alpha":int(e["alpha"]),"beta":int(e["beta"]),"tt_value":int(e["tt_value"]),"bound":int(e["bound"]),
   "tt_move":int(e["tt_move"]),"payload":int(e["payload"]),"address_id":e["address_id"]
  })
 return {"schema":SCHEMA,"board_atoms":board_atoms(fen),"events":ev,"selected":sels,
  "target_fields_consulted":False,"counterfactual_trace_consulted":False,"fiber_id_consulted":False}

def root_move_phenotype(fen,baseline_uci,counterfactual_uci):
 import chess
 b=chess.Board(fen)
 def atom(uci):
  if not uci:return None
  m=chess.Move.from_uci(uci)
  if m not in b.legal_moves:return {"uci":uci,"legal":False}
  piece=b.piece_at(m.from_square)
  cap=b.is_capture(m)
  promo=chess.piece_name(m.promotion) if m.promotion else None
  b2=b.copy();b2.push(m)
  return {"uci":uci,"legal":True,"piece":None if piece is None else chess.piece_name(piece.piece_type),
    "capture":cap,"check":b2.is_check(),"promotion":promo}
 return {"baseline":atom(baseline_uci),"counterfactual":atom(counterfactual_uci)}
