#!/usr/bin/env python3
"""P21 seven-piece pawn-carrier exact-world constitution.

Each P20/P21 core material vertex receives one WHITE and one BLACK pawn.
The carrier is intentionally symmetric and keeps every root at seven pieces,
within Syzygy authority.  Unlike the pawnless core, this lane does not require
full-position tau4: the admitted Inanis PAWN_EVAL_CACHE keys pawn structure,
so its relevant dynamic reuse is established prospectively by SHAM engagement.
"""
import argparse,hashlib,json,random,time
from collections import Counter
from pathlib import Path
import chess
import p19_compile as base

VERSION="c3x-p21-pawn-carrier-v1"
OFFSET=180000

CORE={
 "KQQPvKQP":("HEAVY_HEAVY","00",[(chess.WHITE,chess.KING),(chess.WHITE,chess.QUEEN),(chess.WHITE,chess.QUEEN),(chess.WHITE,chess.PAWN),(chess.BLACK,chess.KING),(chess.BLACK,chess.QUEEN),(chess.BLACK,chess.PAWN)]),
 "KQRPvKQP":("HEAVY_HEAVY","10",[(chess.WHITE,chess.KING),(chess.WHITE,chess.QUEEN),(chess.WHITE,chess.ROOK),(chess.WHITE,chess.PAWN),(chess.BLACK,chess.KING),(chess.BLACK,chess.QUEEN),(chess.BLACK,chess.PAWN)]),
 "KQQPvKRP":("HEAVY_HEAVY","01",[(chess.WHITE,chess.KING),(chess.WHITE,chess.QUEEN),(chess.WHITE,chess.QUEEN),(chess.WHITE,chess.PAWN),(chess.BLACK,chess.KING),(chess.BLACK,chess.ROOK),(chess.BLACK,chess.PAWN)]),
 "KQRPvKRP":("HEAVY_HEAVY","11",[(chess.WHITE,chess.KING),(chess.WHITE,chess.QUEEN),(chess.WHITE,chess.ROOK),(chess.WHITE,chess.PAWN),(chess.BLACK,chess.KING),(chess.BLACK,chess.ROOK),(chess.BLACK,chess.PAWN)]),
 "KRBPvKBP":("MINOR_MINOR","00",[(chess.WHITE,chess.KING),(chess.WHITE,chess.ROOK),(chess.WHITE,chess.BISHOP),(chess.WHITE,chess.PAWN),(chess.BLACK,chess.KING),(chess.BLACK,chess.BISHOP),(chess.BLACK,chess.PAWN)]),
 "KRNPvKBP":("MINOR_MINOR","10",[(chess.WHITE,chess.KING),(chess.WHITE,chess.ROOK),(chess.WHITE,chess.KNIGHT),(chess.WHITE,chess.PAWN),(chess.BLACK,chess.KING),(chess.BLACK,chess.BISHOP),(chess.BLACK,chess.PAWN)]),
 "KRBPvKNP":("MINOR_MINOR","01",[(chess.WHITE,chess.KING),(chess.WHITE,chess.ROOK),(chess.WHITE,chess.BISHOP),(chess.WHITE,chess.PAWN),(chess.BLACK,chess.KING),(chess.BLACK,chess.KNIGHT),(chess.BLACK,chess.PAWN)]),
 "KRNPvKNP":("MINOR_MINOR","11",[(chess.WHITE,chess.KING),(chess.WHITE,chess.ROOK),(chess.WHITE,chess.KNIGHT),(chess.WHITE,chess.PAWN),(chess.BLACK,chess.KING),(chess.BLACK,chess.KNIGHT),(chess.BLACK,chess.PAWN)])
}

def h(x): return hashlib.sha256(x).hexdigest()
def canon(o): return json.dumps(o,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()

def candidate(material,pieces,side,index):
    seed=f"{VERSION}|{material}|{'w' if side else 'b'}|{OFFSET+index}"
    rng=random.Random(int.from_bytes(hashlib.sha256(seed.encode()).digest()[:8],"big"))
    sq=list(chess.SQUARES);rng.shuffle(sq)
    b=chess.Board(None)
    for (color,pt),s in zip(pieces,sq):
        b.set_piece_at(s,chess.Piece(pt,color))
    b.turn=side;b.castling_rights=chess.BB_EMPTY;b.ep_square=None;b.halfmove_clock=0;b.fullmove_number=1
    if not b.is_valid() or b.is_game_over(claim_draw=False) or b.legal_moves.count()<2:return None
    if len(b.pieces(chess.PAWN,chess.WHITE))!=1 or len(b.pieces(chess.PAWN,chess.BLACK))!=1:return None
    return b

def sig(b):
    out=[]
    for color,prefix in ((chess.WHITE,"W"),(chess.BLACK,"B")):
        c=Counter(p.symbol().upper() for p in b.piece_map().values() if p.color==color)
        out.append(prefix+"".join(p*c[p] for p in "KQRBNP" if c[p]))
    return "_".join(out)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--out",required=True)
    ap.add_argument("--target-per-vertex",type=int,default=48)
    ap.add_argument("--max-generated-per-vertex",type=int,default=1600)
    ap.add_argument("--material",choices=tuple(CORE),required=True)
    a=ap.parse_args()
    if a.target_per_vertex%2:raise SystemExit("target-per-vertex must be even")
    material=a.material;square,vertex,pieces=CORE[material]
    per_side=a.target_per_vertex//2
    accepted=[];audited=0;world_pass=0;side_count={"WHITE":0,"BLACK":0}
    for i in range(a.max_generated_per_vertex):
        for side in (chess.WHITE,chess.BLACK):
            sn="WHITE" if side else "BLACK"
            if side_count[sn]>=per_side:continue
            b=candidate(material,pieces,side,i)
            if b is None:continue
            audited+=1
            try:w=base.world(b)
            except RuntimeError as e:
                print("P21_CARRIER_WORLD_QUERY_RETRY_EXHAUSTED",material,e,flush=True);continue
            time.sleep(.04)
            if w is None:continue
            world_pass+=1
            x={
              "compiler_version":VERSION,
              "generation_index":OFFSET+i,
              "lane":"PAWN_CARRIER",
              "square":square,
              "vertex":vertex,
              "material_seed_name":material,
              "material_signature":sig(b),
              "side_to_move":sn,
              "fen":b.fen(),
              "legal_move_count":b.legal_moves.count(),
              "world":w,
              "carrier":{"white_pawns":1,"black_pawns":1,"total_pieces":len(b.piece_map())},
              "transposition_requirement":"DYNAMIC_CHANNEL_ENGAGEMENT_NOT_FULL_POSITION_TAU4"
            }
            x["candidate_sha256"]=h(canon(x));accepted.append(x);side_count[sn]+=1
            print(f"P21_CARRIER_ACCEPT material={material} n={len(accepted)}/{a.target_per_vertex} side={sn} id={x['candidate_sha256'][:12]}",flush=True)
        if all(side_count[s]>=per_side for s in ("WHITE","BLACK")):break
    if len(accepted)!=a.target_per_vertex:
        raise SystemExit(f"P21-CARRIER-WORLD-AUTHORITY-FAIL {material} {len(accepted)}/{a.target_per_vertex} {side_count}")
    out={
      "schema":"c3x-p21-pawn-carrier-part-v1",
      "scientific_stage":"C3X 0.7.0-G9.4-P21",
      "compiler_version":VERSION,
      "engine_outcomes_consulted":False,
      "freshness":{"generation_index_offset":OFFSET,"p20_cells_reused":False},
      "constitution":{
        "lane":"PAWN_CARRIER",
        "symmetric_carrier":"one WHITE pawn + one BLACK pawn",
        "piece_count":7,
        "legal_move_fine_exact_value_distinct_min":2,
        "full_position_tau4_required":False,
        "reason":"Inanis PAWN_EVAL_CACHE reuse is keyed by pawn structure; dynamic SHAM channel engagement is the prospectively relevant reuse gate."
      },
      "squares":{
        "HEAVY_HEAVY":{"00":"KQQPvKQP","10":"KQRPvKQP","01":"KQQPvKRP","11":"KQRPvKRP"},
        "MINOR_MINOR":{"00":"KRBPvKBP","10":"KRNPvKBP","01":"KRBPvKNP","11":"KRNPvKNP"}
      },
      "world_authority":{
        "provider":"Lichess public Syzygy tablebase API",
        "endpoint":base.API,
        "robust_categories_only":["win","draw","loss"],
        "precise_dtz_required_for_every_move":True,
        "root_halfmove_clock":0,
        "pawnless":False,
        "exact_piece_count":7
      },
      "audit_by_vertex":{material:{"square":square,"vertex":vertex,"audited":audited,"world_split_pass":world_pass,"accepted":len(accepted),"accepted_by_side":side_count}},
      "candidates":accepted
    }
    out["pool_sha256"]=h(canon(out))
    Path(a.out).parent.mkdir(parents=True,exist_ok=True)
    Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print("P21_CARRIER_PART_PASS",material,len(accepted),out["pool_sha256"])

if __name__=="__main__":main()
