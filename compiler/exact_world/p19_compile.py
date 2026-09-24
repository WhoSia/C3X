#!/usr/bin/env python3
import argparse,hashlib,json,random,time,urllib.parse,urllib.request
from collections import Counter,defaultdict
from pathlib import Path
import chess

API="https://tablebase.lichess.ovh/standard"
VERSION="c3x-p19-stage-a-v2-fine-exact-split"
OFFSET=60000

VERTICES={
 "KQQvKQ":("HEAVY_HEAVY","00",[(chess.WHITE,chess.KING),(chess.WHITE,chess.QUEEN),(chess.WHITE,chess.QUEEN),(chess.BLACK,chess.KING),(chess.BLACK,chess.QUEEN)]),
 "KQRvKQ":("HEAVY_HEAVY","10",[(chess.WHITE,chess.KING),(chess.WHITE,chess.QUEEN),(chess.WHITE,chess.ROOK),(chess.BLACK,chess.KING),(chess.BLACK,chess.QUEEN)]),
 "KQQvKR":("HEAVY_HEAVY","01",[(chess.WHITE,chess.KING),(chess.WHITE,chess.QUEEN),(chess.WHITE,chess.QUEEN),(chess.BLACK,chess.KING),(chess.BLACK,chess.ROOK)]),
 "KQRvKR":("HEAVY_HEAVY","11",[(chess.WHITE,chess.KING),(chess.WHITE,chess.QUEEN),(chess.WHITE,chess.ROOK),(chess.BLACK,chess.KING),(chess.BLACK,chess.ROOK)]),
 "KRBvKB":("MINOR_MINOR","00",[(chess.WHITE,chess.KING),(chess.WHITE,chess.ROOK),(chess.WHITE,chess.BISHOP),(chess.BLACK,chess.KING),(chess.BLACK,chess.BISHOP)]),
 "KRNvKB":("MINOR_MINOR","10",[(chess.WHITE,chess.KING),(chess.WHITE,chess.ROOK),(chess.WHITE,chess.KNIGHT),(chess.BLACK,chess.KING),(chess.BLACK,chess.BISHOP)]),
 "KRBvKN":("MINOR_MINOR","01",[(chess.WHITE,chess.KING),(chess.WHITE,chess.ROOK),(chess.WHITE,chess.BISHOP),(chess.BLACK,chess.KING),(chess.BLACK,chess.KNIGHT)]),
 "KRNvKN":("MINOR_MINOR","11",[(chess.WHITE,chess.KING),(chess.WHITE,chess.ROOK),(chess.WHITE,chess.KNIGHT),(chess.BLACK,chess.KING),(chess.BLACK,chess.KNIGHT)])
}

def h(x): return hashlib.sha256(x).hexdigest()
def canon(o): return json.dumps(o,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()
def state_key(b):
    ep="-" if b.ep_square is None else chess.square_name(b.ep_square)
    return " ".join([b.board_fen(),"w" if b.turn else "b",b.castling_xfen() or "-",ep,str(b.halfmove_clock)])

def candidate(material,pieces,side,index):
    seed=f"{VERSION}|{material}|{'w' if side else 'b'}|{OFFSET+index}"
    rng=random.Random(int.from_bytes(hashlib.sha256(seed.encode()).digest()[:8],"big"))
    sq=list(chess.SQUARES); rng.shuffle(sq)
    b=chess.Board(None)
    for (color,pt),s in zip(pieces,sq): b.set_piece_at(s,chess.Piece(pt,color))
    b.turn=side; b.castling_rights=chess.BB_EMPTY; b.ep_square=None; b.halfmove_clock=0; b.fullmove_number=1
    if not b.is_valid() or b.is_game_over(claim_draw=False) or b.legal_moves.count()<2: return None
    return b

def query(fen,retries=5):
    url=API+"?"+urllib.parse.urlencode({"fen":fen}); last=None
    for i in range(retries):
        try:
            req=urllib.request.Request(url,headers={"User-Agent":"C3X-P19/1.0 mechanism-morphism"})
            with urllib.request.urlopen(req,timeout=30) as r: raw=r.read()
            return json.loads(raw),h(raw),url
        except Exception as e:
            last=e; time.sleep(.75*(i+1))
    raise RuntimeError(last)

def world(b):
    obj,raw,url=query(b.fen()); c={"win":2,"draw":0,"loss":-2}
    if obj.get("category") not in c: return None
    moves=[]
    for x in obj.get("moves",[]):
        cat=x.get("category"); pd=x.get("precise_dtz")
        if cat not in c or pd is None: return None
        moves.append({"uci":x["uci"],"mover_wdl":-c[cat],"successor_category":cat,
                      "successor_precise_dtz":int(pd),"mover_precise_dtz":-int(pd),
                      "zeroing":bool(x.get("zeroing",False))})
    if len(moves)<2: return None
    vals=[x["mover_wdl"] for x in moves]; best=max(vals)
    fine=Counter(f'{x["mover_wdl"]}:{x["mover_precise_dtz"]}' for x in moves)
    if len(fine)<2: return None
    cnt=Counter(vals)
    return {"provider":"lichess-syzygy-http","endpoint":API,"query_url":url,
            "root_category":obj.get("category"),"root_wdl":c[obj["category"]],
            "root_precise_dtz":obj.get("precise_dtz"),
            "moves":sorted(moves,key=lambda z:z["uci"]),
            "world_pattern":{str(k):cnt[k] for k in sorted(cnt)},
            "fine_value_pattern":dict(sorted(fine.items())),
            "fine_value_distinct_count":len(fine),
            "optimal_count":sum(v==best for v in vals),
            "strictly_worse_count":sum(v<best for v in vals),
            "raw_response_sha256":raw}

def tau4(board,max_paths=350000):
    endpoints=defaultdict(list); path_count=0; excluded=0; overflow=False; root=state_key(board)
    def dfs(b,d,path,seen):
        nonlocal path_count,excluded,overflow
        if overflow: return
        if d==4:
            path_count+=1
            if path_count>max_paths: overflow=True; return
            key=state_key(b); lh=h(" ".join(sorted(m.uci() for m in b.legal_moves)).encode())
            endpoints[(key,lh)].append(" ".join(path)); return
        if b.is_game_over(claim_draw=False): return
        for mv in list(b.legal_moves):
            b.push(mv); key=state_key(b)
            if key in seen:
                excluded+=1; b.pop(); continue
            dfs(b,d+1,path+[mv.uci()],seen|{key}); b.pop()
            if overflow:return
    dfs(board.copy(stack=False),0,[],{root})
    if overflow: return {"tau4":None,"overflow":True,"enumerated_depth4_paths":path_count,"excluded_history_paths":excluded}
    tau=0; dup=0; witnesses=[]
    for (key,lh),paths in endpoints.items():
        u=sorted(set(paths))
        if len(u)>=2:
            dup+=1; tau+=len(u)-1
            if len(witnesses)<3: witnesses.append({"endpoint_state":key,"legal_move_set_sha256":lh,"paths":u[:4]})
    return {"tau4":tau,"duplicate_endpoint_states":dup,"enumerated_depth4_paths":path_count,
            "excluded_history_paths":excluded,"overflow":False,"witnesses":witnesses}

def sig(b):
    out=[]
    for color,prefix in [(chess.WHITE,"W"),(chess.BLACK,"B")]:
        c=Counter(p.symbol().upper() for p in b.piece_map().values() if p.color==color)
        out.append(prefix+"".join(p*c[p] for p in "KQRBN" if c[p]))
    return "_".join(out)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--out",required=True)
    ap.add_argument("--target-per-vertex",type=int,default=36)
    ap.add_argument("--max-generated-per-vertex",type=int,default=520)
    ap.add_argument("--material",choices=tuple(VERTICES),help="Optional single-vertex material for parallel constitution")
    a=ap.parse_args()
    if a.target_per_vertex%2: raise SystemExit("target-per-vertex must be even")
    per_side=a.target_per_vertex//2; accepted=[]; audit={}
    items=VERTICES.items() if a.material is None else [(a.material,VERTICES[a.material])]
    for material,(square,vertex,pieces) in items:
        fam=[]; audited=0; world_pass=0; side_count={"WHITE":0,"BLACK":0}
        for i in range(a.max_generated_per_vertex):
            for side in (chess.WHITE,chess.BLACK):
                side_name="WHITE" if side else "BLACK"
                if side_count[side_name]>=per_side: continue
                b=candidate(material,pieces,side,i)
                if b is None: continue
                audited+=1
                try:w=world(b)
                except RuntimeError as e:
                    print("WORLD_QUERY_RETRY_EXHAUSTED",material,e,flush=True); continue
                time.sleep(.04)
                if w is None: continue
                world_pass+=1; t=tau4(b)
                if t["overflow"] or not t["tau4"]: continue
                x={"compiler_version":VERSION,"generation_index":OFFSET+i,"square":square,"vertex":vertex,
                   "material_seed_name":material,"material_signature":sig(b),"side_to_move":side_name,
                   "fen":b.fen(),"legal_move_count":b.legal_moves.count(),"world":w,"tau4":t}
                x["candidate_sha256"]=h(canon(x)); fam.append(x); accepted.append(x); side_count[side_name]+=1
                print(f"P19_ACCEPT square={square} vertex={vertex} material={material} n={len(fam)}/{a.target_per_vertex} side={side_name} side_n={side_count[side_name]}/{per_side} id={x['candidate_sha256'][:12]}",flush=True)
            if all(side_count[s]>=per_side for s in ("WHITE","BLACK")): break
        audit[material]={"square":square,"vertex":vertex,"audited":audited,"world_split_pass":world_pass,
                         "accepted":len(fam),"accepted_by_side":side_count}
        if len(fam)<a.target_per_vertex or any(side_count[s]<per_side for s in ("WHITE","BLACK")):
            raise SystemExit(f"P19-WORLD-AUTHORITY-FAIL {material} {len(fam)}/{a.target_per_vertex} side={side_count}")
    payload={"schema":"c3x-p19-stage-a-pool-v1","scientific_stage":"C3X 0.7.0-G9.4-P19",
             "compiler_version":VERSION,"stockfish_outcomes_consulted":False,
             "freshness":{"generation_index_offset":OFFSET,"historical_confirmatory_cells_reused":False},
             "constitution":{"legal_move_fine_exact_value_distinct_min":2,"split_definition":"distinct (mover_wdl,mover_precise_dtz) tuples; robust-WDL split alone is not required"},
             "squares":{"HEAVY_HEAVY":{"00":"KQQvKQ","10":"KQRvKQ","01":"KQQvKR","11":"KQRvKR"},
                        "MINOR_MINOR":{"00":"KRBvKB","10":"KRNvKB","01":"KRBvKN","11":"KRNvKN"}},
             "world_authority":{"provider":"Lichess public Syzygy tablebase API","endpoint":API,
                                "robust_categories_only":["win","draw","loss"],
                                "precise_dtz_required_for_every_move":True,"root_halfmove_clock":0,"pawnless":True},
             "audit_by_vertex":audit,"candidates":accepted}
    payload["pool_sha256"]=h(canon(payload))
    Path(a.out).parent.mkdir(parents=True,exist_ok=True)
    Path(a.out).write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n")
    print("P19_STAGE_A_PASS",len(accepted),payload["pool_sha256"])

if __name__=="__main__": main()
