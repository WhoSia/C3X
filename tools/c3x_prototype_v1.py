#!/usr/bin/env python3
from collections import Counter,defaultdict

STAGE="C3X 0.7.0-G9.5-P8"
SCHEMA="c3x-prototype-descriptor-v1"

CLASSES=("CUTOFF","MOVE_ORDER_SEED","EVAL_REUSE","TT_VALUE_AS_EVAL","PV_PROMOTION")

def ratio_bucket(num,den):
    if den<=0 or num<=0:return "ZERO"
    r=num/den
    if r<=0.05:return "LE05"
    if r<=0.15:return "LE15"
    if r<=0.30:return "LE30"
    if r<=0.50:return "LE50"
    return "GT50"

def gap_ratio_bucket(gap,n):
    if gap is None:return "NONE"
    r=gap/max(1,n)
    if r<=0.05:return "LE05"
    if r<=0.15:return "LE15"
    if r<=0.30:return "LE30"
    return "GT30"

def prefix_size_bucket(n):
    if n<=32:return "LE32"
    if n<=128:return "33_128"
    if n<=512:return "129_512"
    return "513_PLUS"

def ply_bucket(v):
    v=int(v)
    if v<=0:return "LE0"
    if v==1:return "1"
    if v==2:return "2"
    if v<=4:return "3_4"
    if v<=8:return "5_8"
    return "9_PLUS"

def depth_bucket(v):
    v=int(v)
    if v<=0:return "LE0"
    if v<=4:return "1_4"
    if v<=8:return "5_8"
    if v<=12:return "9_12"
    if v<=16:return "13_16"
    if v<=24:return "17_24"
    return "25_PLUS"

def bound_bucket(v):
    try:v=int(v)
    except Exception:return "OTHER"
    return {0:"NONE",1:"UPPER",2:"LOWER",3:"EXACT"}.get(v,"OTHER")

def payload_bucket(v):
    v=int(v)
    if v==0:return "ZERO"
    if v==1:return "ONE"
    if v==-1:return "NEG_ONE"
    return "POS_OTHER" if v>0 else "NEG_OTHER"

def window_relation(e):
    tv=int(e["tt_value"]);a=int(e["alpha"]);b=int(e["beta"])
    if tv<=a:return "LE_ALPHA"
    if tv>=b:return "GE_BETA"
    return "MID"

def board_atoms(fen):
    import chess
    b=chess.Board(fen)
    if not b.is_valid() or b.chess960:raise ValueError("P8 requires standard legal chess")
    vals={chess.PAWN:1,chess.KNIGHT:3,chess.BISHOP:3,chess.ROOK:5,chess.QUEEN:9}
    def mat(color):return sum(vals[p]*len(b.pieces(p,color)) for p in vals)
    nm=sum(vals[p]*(len(b.pieces(p,chess.WHITE))+len(b.pieces(p,chess.BLACK))) for p in (chess.KNIGHT,chess.BISHOP,chess.ROOK,chess.QUEEN))
    phase="OPEN" if nm>=44 else "MIDDLE" if nm>=20 else "END"
    diff=mat(b.turn)-mat(not b.turn)
    mb="STM_ADV_BIG" if diff>=4 else "STM_ADV_SMALL" if diff>=1 else "STM_BEHIND_BIG" if diff<=-4 else "STM_BEHIND_SMALL" if diff<=-1 else "EVEN"
    lm=b.legal_moves.count();legal="LE10" if lm<=10 else "11_20" if lm<=20 else "21_30" if lm<=30 else "31_45" if lm<=45 else "46_PLUS"
    us=bool(b.has_kingside_castling_rights(b.turn) or b.has_queenside_castling_rights(b.turn))
    them=bool(b.has_kingside_castling_rights(not b.turn) or b.has_queenside_castling_rights(not b.turn))
    castle="BOTH" if us and them else "STM_ONLY" if us else "OPP_ONLY" if them else "NONE"
    hm=b.halfmove_clock;hmb="ZERO" if hm==0 else "1_10" if hm<=10 else "11_30" if hm<=30 else "31_60" if hm<=60 else "61_PLUS"
    return {"side_to_move":"W" if b.turn else "B","in_check":str(bool(b.is_check())).lower(),"phase":phase,
      "legal_moves_bucket":legal,"material_balance_bucket":mb,"castling_bucket":castle,"halfmove_bucket":hmb}

def family(cls):
    if cls=="CUTOFF":return "CUTOFF"
    if cls=="MOVE_ORDER_SEED":return "MOVE"
    if cls in ("EVAL_REUSE","TT_VALUE_AS_EVAL"):return "EVAL"
    if cls=="PV_PROMOTION":return "PV"
    return "OTHER"

def dominant(xs,default="NONE"):
    if not xs:return default
    c=Counter(xs);m=max(c.values())
    return sorted(k for k,v in c.items() if v==m)[0]

def descriptor_for(fen,events,ordinal):
    i=int(ordinal)
    if i<0 or i>=len(events):raise ValueError("P8 event ordinal")
    prefix=events[:i+1];e=events[i];n=len(prefix)
    board=board_atoms(fen)
    cur={"scope":str(e["scope"]),"class":str(e["class"]),"ply_bucket":ply_bucket(e["ply"]),
      "depth_bucket":depth_bucket(e["depth"]),"bound_bucket":bound_bucket(e.get("bound",0)),
      "window_relation":window_relation(e),"move_presence":"PRESENT" if int(e.get("tt_move",0))!=0 else "NONE",
      "payload_bucket":payload_bucket(e.get("payload",0))}
    cc=Counter(str(z["class"]) for z in prefix)
    sc=Counter(str(z["scope"]) for z in prefix)
    keys=[str(z.get("key")) for z in prefix]
    kc=Counter(keys)
    repeated=[False]*n;seen=set()
    for j,k in enumerate(keys):
      repeated[j]=k in seen;seen.add(k)
    prev_key=next((j for j in range(i-1,-1,-1) if keys[j]==keys[i]),None)
    prev_cls=next((j for j in range(i-1,-1,-1) if str(events[j]["class"])==str(e["class"])),None)
    depths=[int(z["depth"]) for z in prefix];ply=int(e["ply"])
    prov={
      "cutoff_share":ratio_bucket(cc["CUTOFF"],n),
      "move_order_share":ratio_bucket(cc["MOVE_ORDER_SEED"],n),
      "eval_share":ratio_bucket(cc["EVAL_REUSE"]+cc["TT_VALUE_AS_EVAL"],n),
      "pv_share":ratio_bucket(cc["PV_PROMOTION"],n),
      "qsearch_share":ratio_bucket(sum(str(z["scope"])=="QSEARCH" for z in prefix),n),
      "current_scope_share":ratio_bucket(sc[str(e["scope"])],n),
      "current_class_share":ratio_bucket(cc[str(e["class"])],n),
      "unique_key_ratio":ratio_bucket(len(kc),n),
      "repeated_key_event_share":ratio_bucket(sum(repeated),n),
      "current_key_share":ratio_bucket(kc[keys[i]],n),
      "same_key_gap_ratio":gap_ratio_bucket(None if prev_key is None else i-prev_key,n),
      "same_class_gap_ratio":gap_ratio_bucket(None if prev_cls is None else i-prev_cls,n),
      "depth_percentile":ratio_bucket(sum(d<=int(e["depth"]) for d in depths),n),
      "same_ply_share":ratio_bucket(sum(int(z["ply"])==ply for z in prefix),n)
    }
    shape={}
    for q in range(4):
      lo=(q*n)//4;hi=((q+1)*n)//4
      seg=prefix[lo:hi]
      shape[f"q{q+1}_class"]=dominant([family(str(z["class"])) for z in seg])
      shape[f"q{q+1}_scope"]=dominant([str(z["scope"]) for z in seg])
      shape[f"q{q+1}_reuse"]=ratio_bucket(sum(repeated[lo:hi]),len(seg))
    scale={"prefix_size_bucket":prefix_size_bucket(n)}
    return {"board":board,"current_event":cur,"provenance_rates":prov,"temporal_shape":shape,"coarse_scale":scale}

def prepare_batch(fen,parent_trace,selected):
    byid={e["address_id"]:i for i,e in enumerate(parent_trace["events"])}
    rows=[]
    for s in selected:
      aid=s["event_id"]
      if aid not in byid:raise ValueError("P8_SELECTED_EVENT_NOT_IN_TRACE")
      rows.append({"event_id":aid,"sampling_stratum":s.get("sampling_stratum"),
        "descriptor":descriptor_for(fen,parent_trace["events"],byid[aid]),
        "target_fields_consulted":False,"counterfactual_information_consulted":False,
        "raw_tt_key_emitted":False,"p7_q_state_consulted":False})
    return {"schema":"c3x-prototype-descriptor-batch-p8-v1","scientific_stage":STAGE,"descriptor_schema":SCHEMA,
      "records":rows,"target_fields_consulted":False,"counterfactual_information_consulted":False,
      "raw_tt_key_emitted":False,"p7_q_state_consulted":False}
