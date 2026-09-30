from __future__ import annotations
import io,json,math
from dataclasses import dataclass,asdict
from typing import Any,Iterable
import chess,chess.pgn,chess.engine
from .concepts import candidate_delta

CAUSAL="C3X_CAUSAL_CONTRAST"
HEURISTIC="CONVENTIONAL_HEURISTIC_COMMENTARY"
RATING_THRESHOLDS={"beginner":80,"intermediate":50,"advanced":25,"expert":15}

def score_cp(score: chess.engine.PovScore, turn: chess.Color)->int|None:
    s=score.pov(turn).score(mate_score=100000)
    return None if s is None else int(s)

def material(board: chess.Board)->dict[str,int]:
    vals={chess.PAWN:1,chess.KNIGHT:3,chess.BISHOP:3,chess.ROOK:5,chess.QUEEN:9}
    out={"white":0,"black":0}
    for p in board.piece_map().values():
        if p.piece_type in vals:out["white" if p.color else "black"]+=vals[p.piece_type]
    out["balance_white"]=out["white"]-out["black"]
    return out

def move_facts(board: chess.Board,move: chess.Move)->list[dict[str,Any]]:
    san=board.san(move);facts=[]
    if board.is_capture(move):facts.append({"kind":"capture","text":f"{san} is a capture."})
    if board.gives_check(move):facts.append({"kind":"check","text":f"{san} gives check."})
    if board.is_castling(move):facts.append({"kind":"castling","text":f"{san} castles."})
    if move.promotion:facts.append({"kind":"promotion","text":f"{san} promotes a pawn."})
    return facts

def candidate_packet(engine: chess.engine.SimpleEngine,board: chess.Board,multipv:int,nodes:int)->list[dict[str,Any]]:
    infos=engine.analyse(board,chess.engine.Limit(nodes=nodes),multipv=multipv)
    if isinstance(infos,dict):infos=[infos]
    out=[]
    for i,info in enumerate(infos,1):
        pv=info.get("pv",[])
        if not pv:continue
        out.append({"rank":i,"uci":pv[0].uci(),"san":board.san(pv[0]),"score_cp":score_cp(info["score"],board.turn),
                    "depth":info.get("depth"),"nodes":info.get("nodes"),"pv_uci":[m.uci() for m in pv[:8]]})
    return out

def cert_index(certs:Iterable[dict[str,Any]])->dict[str,list[dict[str,Any]]]:
    idx={}
    for c in certs:
        fen=c.get("position_fen") or c.get("fen") or c.get("original_fen")
        if fen:idx.setdefault(" ".join(str(fen).split()[:4]),[]).append(c)
    return idx

def choose_moment(board:chess.Board,played:chess.Move,cands:list[dict[str,Any]],facts:list[dict[str,Any]],certs:list[dict[str,Any]],threshold_cp:int)->tuple[bool,list[str]]:
    reasons=[]
    if facts:reasons.append("forcing_or_irreversible_move")
    rank=next((c["rank"] for c in cands if c["uci"]==played.uci()),None)
    top=cands[0] if cands else None
    played_c=next((c for c in cands if c["uci"]==played.uci()),None)
    if top and played_c and top["score_cp"] is not None and played_c["score_cp"] is not None:
        if top["uci"]!=played.uci() and top["score_cp"]-played_c["score_cp"]>=threshold_cp:reasons.append("meaningful_candidate_gap")
    elif top and top["uci"]!=played.uci():reasons.append("played_move_outside_multipv_or_not_top")
    if certs:reasons.append("c3x_certificate_available")
    return bool(reasons),reasons

def causal_atoms(board:chess.Board,certs:list[dict[str,Any]])->list[dict[str,Any]]:
    atoms=[]
    for c in certs:
        pair=c.get("pair") or c.get("pair_id")
        bound=c.get("bound")
        fam=c.get("family") or c.get("engine_relative_atoms")
        atoms.append({"type":"causal_contrast","provenance":CAUSAL,"authority":"engine_preference_causality",
                      "claim":{"pair":pair,"bound":bound,"family":fam,"collapse_to":c.get("collapse_to"),
                               "certificate_id":c.get("certificate_id") or c.get("receipt_sha256")},
                      "text":"A C3X intervention certificate is available for this position; causal wording is limited to the engine preference contrast recorded by that certificate."})
    return atoms

def heuristic_atoms(board:chess.Board,played:chess.Move,cands:list[dict[str,Any]],facts:list[dict[str,Any]])->list[dict[str,Any]]:
    atoms=[]
    for f in facts:atoms.append({"type":"move_fact","provenance":HEURISTIC,"authority":"verified_board_fact","claim":f,"text":f["text"]})
    if cands:
        top=cands[0];played_c=next((c for c in cands if c["uci"]==played.uci()),None)
        claim={"played_uci":played.uci(),"top_uci":top["uci"],"top_san":top["san"],"top_score_cp":top["score_cp"],
               "played_rank":None if played_c is None else played_c["rank"],"played_score_cp":None if played_c is None else played_c["score_cp"],
               "top_pv_uci":top["pv_uci"]}
        atoms.append({"type":"candidate_contrast","provenance":HEURISTIC,"authority":"engine_analysis","claim":claim,
                      "text":candidate_sentence(board,played,claim)})
        if top["uci"]!=played.uci():
            alt=chess.Move.from_uci(top["uci"])
            delta=candidate_delta(board,played,alt)
            if delta["played_minus_alternative"]:
                pairs=", ".join(f"{k} {v:+d}" for k,v in sorted(delta["played_minus_alternative"].items()))
                atoms.append({"type":"concept_proxy_delta","provenance":HEURISTIC,"authority":"verified_board_proxy",
                              "claim":delta,
                              "text":f"Compared with {top['san']}, {board.san(played)} changes these measured board proxies: {pairs}."})
    atoms.append({"type":"material_snapshot","provenance":HEURISTIC,"authority":"verified_board_fact","claim":material(board),"text":""})
    return atoms

def candidate_sentence(board:chess.Board,played:chess.Move,c:dict[str,Any])->str:
    psan=board.san(played)
    if c["played_uci"]==c["top_uci"]:return f"{psan} is the engine's first candidate in this analysis."
    if c["played_score_cp"] is not None and c["top_score_cp"] is not None:
        gap=c["top_score_cp"]-c["played_score_cp"]
        return f"Against {psan}, the engine prefers {c['top_san']} by about {abs(gap)} centipawns in this bounded analysis."
    return f"The engine prefers {c['top_san']} to {psan} in this bounded MultiPV analysis."

def firewall(board:chess.Board,atoms:list[dict[str,Any]])->list[str]:
    errs=[]
    legal={m.uci() for m in board.legal_moves}
    for a in atoms:
        if a.get("provenance") not in (CAUSAL,HEURISTIC):errs.append("missing_or_invalid_provenance")
        if a.get("type")=="candidate_contrast":
            c=a["claim"]
            for k in ("played_uci","top_uci"):
                if c.get(k) not in legal:errs.append(f"illegal_{k}:{c.get(k)}")
        txt=(a.get("text") or "").lower()
        if any(w in txt for w in ("causes the engine","causally","because the search")) and a.get("provenance")!=CAUSAL:
            errs.append("causal_wording_without_certificate")
    return errs

def analyze_pgn(pgn_text:str,engine_path:str|None=None,multipv:int=3,nodes:int=20000,certificates:Iterable[dict[str,Any]]=(),threshold_cp:int|None=None,rating_band:str="advanced")->dict[str,Any]:
    game=chess.pgn.read_game(io.StringIO(pgn_text))
    if game is None:raise ValueError("No PGN game found")
    if rating_band not in RATING_THRESHOLDS:raise ValueError(f"Unknown rating band: {rating_band}")
    effective_threshold=RATING_THRESHOLDS[rating_band] if threshold_cp is None else int(threshold_cp)
    board=game.board();certs=cert_index(certificates);moments=[];eng=None
    if engine_path:eng=chess.engine.SimpleEngine.popen_uci(engine_path)
    try:
        for ply,move in enumerate(game.mainline_moves(),1):
            fen=board.fen();key=" ".join(fen.split()[:4]);local_certs=certs.get(key,[])
            facts=move_facts(board,move);cands=candidate_packet(eng,board,multipv,nodes) if eng else []
            selected,reasons=choose_moment(board,move,cands,facts,local_certs,effective_threshold)
            if selected:
                atoms=heuristic_atoms(board,move,cands,facts)+causal_atoms(board,local_certs)
                errs=firewall(board,atoms)
                moments.append({"ply":ply,"fen":fen,"played_uci":move.uci(),"played_san":board.san(move),
                                "selection_reasons":reasons,"candidates":cands,"atoms":atoms,
                                "firewall":{"pass":not errs,"errors":errs},
                                "commentary":" ".join(a["text"] for a in atoms if a.get("text") and not errs)})
            board.push(move)
    finally:
        if eng:eng.quit()
    return {"schema":"c3x-explanation-graph-v1","provenance_classes":[CAUSAL,HEURISTIC],
            "rating_band":rating_band,"candidate_gap_threshold_cp":effective_threshold,
            "headers":dict(game.headers),"moment_count":len(moments),"moments":moments,
            "authority_note":"Useful commentary is not automatically causal. Causal wording requires a C3X certificate."}

def load_certificates(paths:list[str])->list[dict[str,Any]]:
    out=[]
    for p in paths:
        x=json.load(open(p))
        if isinstance(x,list):out+=x
        elif "causal_explanation_certificates" in x:out+=x["causal_explanation_certificates"]
        else:out.append(x)
    return out
