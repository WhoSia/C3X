from __future__ import annotations
import io,json,math
from dataclasses import dataclass,asdict
from typing import Any,Iterable
import chess,chess.pgn,chess.engine
from .concepts import candidate_delta
from .tactics import verified_move_evidence,tactical_contrast
from .retrieval import retrieve,retrieval_atoms,audit_retrieval_corpus
from .graph import attach_graphs
from .evaluation import evaluation_packet
from .certificates import certificate_claim
from .planning import verified_line_evidence,line_sentence
from .renderer import attach_render_packets,renderer_benchmark
from .realization import attach_realizations,realization_benchmark
from .verification import attach_verification,verification_benchmark
from .susceptibility import susceptibility_index,atoms_for_fen
from .authority_support import authority_index,atoms_for_fen as authority_atoms_for_fen,route_for_fen
from .p8_ep8 import observation_index,observation_atoms_for_board
from .p8_ep10 import mechanism_index,mechanism_atoms_for_board

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

def tactical_text(e:dict[str,Any])->str:
    kind=e.get("kind");san=e.get("san","the move")
    if kind=="checkmate":return f"{san} is checkmate."
    if kind=="multi_attack":
        xs=", ".join(f"{z['piece']['piece_type']} on {z['square']}" for z in e.get("attacked",[]))
        return f"After {san}, the moved piece attacks multiple valuable enemy pieces: {xs}."
    if kind=="absolute_pin_created":
        xs=", ".join(f"{z['piece']['piece_type']} on {z['square']}" for z in e.get("pinned",[]))
        return f"After {san}, the following enemy piece is absolutely pinned to its king: {xs}."
    return ""

def route_categories(atoms:list[dict[str,Any]])->list[str]:
    cats=[]
    types={a.get("type") for a in atoms}
    if "causal_contrast" in types:cats.append("causal_contrast")
    if "tactical_fact" in types or "tactical_contrast" in types or "move_fact" in types:cats.append("tactics")
    if "candidate_contrast" in types:cats.append("comparison")
    if "concept_proxy_delta" in types:cats.append("positional_proxy")
    if "material_snapshot" in types:cats.append("material_context")
    if "retrieval_reference" in types:cats.append("retrieval_context")
    if "verified_line_evidence" in types:cats.append("verified_line")
    if "intervention_admissibility" in types:cats.append("intervention_admissibility")
    if "mechanism_authority_route" in types:cats.append("mechanism_authority")
    if "opponent_reply_observation" in types:cats.append("opponent_reply_observation")
    if "engine_path_sensitivity_observation" in types:cats.append("engine_path_sensitivity_observation")
    return cats

def graph_audit(moments:list[dict[str,Any]])->dict[str,Any]:
    atoms=[a for m in moments for a in m.get("atoms",[])]
    categories={}
    for m in moments:
        for c in m.get("commentary_plan",{}).get("categories",[]):categories[c]=categories.get(c,0)+1
    causal=sum(a.get("provenance")==CAUSAL for a in atoms)
    heuristic=sum(a.get("provenance")==HEURISTIC for a in atoms)
    with_ids=sum(bool(a.get("atom_id")) for a in atoms)
    return {"moment_count":len(moments),"atom_count":len(atoms),"causal_atom_count":causal,
            "heuristic_atom_count":heuristic,"atoms_with_ids":with_ids,
            "provenance_coverage":0 if not atoms else (causal+heuristic)/len(atoms),
            "traceability_coverage":0 if not atoms else with_ids/len(atoms),
            "firewall_failed_moments":sum(not m.get("firewall",{}).get("pass",False) for m in moments),
            "category_moment_counts":dict(sorted(categories.items()))}

def _san_from_fen(fen:str,uci:str|None)->str|None:
    if not uci:return None
    try:
        b=chess.Board(fen);m=chess.Move.from_uci(uci)
        return b.san(m) if m in b.legal_moves else uci
    except Exception:
        return uci

def _causal_certificate_text(board:chess.Board,claim:dict[str,Any])->str:
    consequence=claim.get("chess_native_consequence")
    if not isinstance(consequence,dict):
        return "A C3X intervention certificate supports a causal statement only about the recorded engine-preference contrast; it does not establish objective chess truth."
    baseline=consequence.get("baseline") or {}
    board_transition=consequence.get("board_preference_transition") or {}
    search_transition=consequence.get("search_mediation_transition") or {}
    intervention=consequence.get("structural_intervention") or {}
    bfen=str(baseline.get("fen") or board.fen())
    tfen=intervention.get("target_fen")
    before=_san_from_fen(bfen,board_transition.get("before"))
    after=_san_from_fen(str(tfen),board_transition.get("after")) if tfen else board_transition.get("after")
    suppressed=_san_from_fen(bfen,search_transition.get("event_suppressed"))
    clauses=[]
    if board_transition.get("changed") and before and after:
        clauses.append(f"the recorded board intervention changed the engine's root choice from {before} to {after}")
    if search_transition.get("changed") and before and suppressed:
        clauses.append(f"suppressing the recorded search event on the baseline changed the root choice from {before} to {suppressed}")
    if not clauses:
        return "A C3X local causal certificate is attached, but no additional chess-native transition is surfaceable from the bounded packet."
    return ("For this exact certified engine world, " + "; ".join(clauses) +
            ". This is local engine-preference causal evidence, not objective chess truth or a human strategic-intent claim.")

def causal_atoms(board:chess.Board,certs:list[dict[str,Any]])->list[dict[str,Any]]:
    atoms=[]
    for c in certs:
        claim=certificate_claim(c,board.fen())
        atoms.append({"type":"causal_contrast","provenance":CAUSAL,"authority":"engine_preference_causality",
                      "claim":claim,"text":_causal_certificate_text(board,claim)})
    return atoms

def heuristic_atoms(board:chess.Board,played:chess.Move,cands:list[dict[str,Any]],facts:list[dict[str,Any]])->list[dict[str,Any]]:
    atoms=[]
    for f in facts:atoms.append({"type":"move_fact","provenance":HEURISTIC,"authority":"verified_board_fact","claim":f,"text":f["text"]})
    for e in verified_move_evidence(board,played):
        if e["kind"] in ("checkmate","multi_attack","absolute_pin_created"):
            atoms.append({"type":"tactical_fact","provenance":HEURISTIC,"authority":"verified_board_tactic",
                          "claim":e,"text":tactical_text(e)})
    if cands:
        top=cands[0];played_c=next((c for c in cands if c["uci"]==played.uci()),None)
        claim={"played_uci":played.uci(),"top_uci":top["uci"],"top_san":top["san"],"top_score_cp":top["score_cp"],
               "played_rank":None if played_c is None else played_c["rank"],"played_score_cp":None if played_c is None else played_c["score_cp"],
               "top_pv_uci":top["pv_uci"]}
        atoms.append({"type":"candidate_contrast","provenance":HEURISTIC,"authority":"engine_analysis","claim":claim,
                      "text":candidate_sentence(board,played,claim)})
        line=verified_line_evidence(board,top)
        if line:
            atoms.append({"type":"verified_line_evidence","provenance":HEURISTIC,"authority":"verified_engine_pv_line",
                          "claim":line,"text":line_sentence(line)})
        if top["uci"]!=played.uci():
            alt=chess.Move.from_uci(top["uci"])
            delta=candidate_delta(board,played,alt)
            if delta["played_minus_alternative"]:
                pairs=", ".join(f"{k} {v:+d}" for k,v in sorted(delta["played_minus_alternative"].items()))
                atoms.append({"type":"concept_proxy_delta","provenance":HEURISTIC,"authority":"verified_board_proxy",
                              "claim":delta,
                              "text":f"Compared with {top['san']}, {board.san(played)} changes these measured board proxies: {pairs}."})
            tc=tactical_contrast(board,played,alt)
            if tc["played_only_kinds"] or tc["alternative_only_kinds"]:
                text=(f"Compared with {top['san']}, the verified tactical-property differences are "
                      f"played-only={','.join(tc['played_only_kinds']) or 'none'}; "
                      f"alternative-only={','.join(tc['alternative_only_kinds']) or 'none'}.")
                atoms.append({"type":"tactical_contrast","provenance":HEURISTIC,"authority":"verified_board_tactic",
                              "claim":tc,"text":text})
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

def _retrieval_query_tags(atoms:list[dict[str,Any]])->list[str]:
    tags=set()
    for a in atoms:
        t=a.get("type")
        if t:tags.add(str(t))
        c=a.get("claim") or {}
        k=c.get("kind")
        if k:tags.add(str(k))
        if t=="concept_proxy_delta":
            tags.update(str(x) for x in (c.get("played_minus_alternative") or {}).keys())
        if t=="tactical_contrast":
            tags.update(str(x) for x in c.get("played_only_kinds",[]))
            tags.update(str(x) for x in c.get("alternative_only_kinds",[]))
    return sorted(tags)

def analyze_pgn(pgn_text:str,engine_path:str|None=None,multipv:int=3,nodes:int=20000,certificates:Iterable[dict[str,Any]]=(),threshold_cp:int|None=None,rating_band:str="advanced",retrieval_records:Iterable[dict[str,Any]]=(),retrieval_top_k:int=3,susceptibility_packets:Iterable[dict[str,Any]]=(),authority_packets:Iterable[dict[str,Any]]=(),ep8_observation_packets:Iterable[dict[str,Any]]=(),ep10_observation_packets:Iterable[dict[str,Any]]=())->dict[str,Any]:
    game=chess.pgn.read_game(io.StringIO(pgn_text))
    if game is None:raise ValueError("No PGN game found")
    if rating_band not in RATING_THRESHOLDS:raise ValueError(f"Unknown rating band: {rating_band}")
    effective_threshold=RATING_THRESHOLDS[rating_band] if threshold_cp is None else int(threshold_cp)
    board=game.board();certs=cert_index(certificates);sidx=susceptibility_index(susceptibility_packets);aidx=authority_index(authority_packets);oidx=observation_index(ep8_observation_packets);midx=mechanism_index(ep10_observation_packets);moments=[];eng=None
    if engine_path:eng=chess.engine.SimpleEngine.popen_uci(engine_path)
    try:
        for ply,move in enumerate(game.mainline_moves(),1):
            fen=board.fen();key=" ".join(fen.split()[:4]);local_certs=certs.get(key,[])
            facts=move_facts(board,move);cands=candidate_packet(eng,board,multipv,nodes) if eng else []
            local_sus=sidx.get(key,[]);local_auth=authority_atoms_for_fen(aidx,fen);aroute=route_for_fen(aidx,fen)
            local_ep8=observation_atoms_for_board(oidx,board,move.uci())
            local_ep10=mechanism_atoms_for_board(midx,board,move.uci())
            selected,reasons=choose_moment(board,move,cands,facts,local_certs,effective_threshold)
            if local_sus:
                selected=True
                reasons=list(reasons)+["transparent_intervention_admissibility_packet"]
            if local_auth:
                selected=True
                reasons=list(reasons)+["precausal_authority_route"]
            if local_ep8:
                selected=True
                reasons=list(reasons)+["source_frozen_developmental_engine_observation"]
            if local_ep10:
                selected=True
                reasons=list(reasons)+["exploratory_source_local_search_path_observation"]
            if selected:
                atoms=heuristic_atoms(board,move,cands,facts)+atoms_for_fen(sidx,fen)+local_auth+local_ep8+local_ep10
                if aroute["allow_causal"]:
                    atoms+=causal_atoms(board,local_certs)
                rpacket=retrieve(_retrieval_query_tags(atoms),retrieval_records,retrieval_top_k)
                atoms+=retrieval_atoms(rpacket)
                for idx,atom in enumerate(atoms):
                    atom["atom_id"]=f"p{ply}:a{idx}"
                errs=firewall(board,atoms)
                moments.append({"ply":ply,"fen":fen,"played_uci":move.uci(),"played_san":board.san(move),
                                "selection_reasons":reasons,"candidates":cands,"atoms":atoms,
                                "commentary_plan":{"categories":route_categories(atoms),"atom_ids":[a["atom_id"] for a in atoms]},
                                "retrieval_packet":rpacket,
                                "firewall":{"pass":not errs,"errors":errs},
                                "commentary":" ".join(a["text"] for a in atoms if a.get("text") and not errs)})
            board.push(move)
    finally:
        if eng:eng.quit()
    attach_graphs(moments)
    attach_render_packets(moments)
    attach_realizations(moments,rating_band)
    attach_verification(moments)
    return {"schema":"c3x-explanation-graph-v1","provenance_classes":[CAUSAL,HEURISTIC],
            "rating_band":rating_band,"candidate_gap_threshold_cp":effective_threshold,
            "headers":dict(game.headers),"moment_count":len(moments),"moments":moments,
            "evaluation_packet":graph_audit(moments),
            "commentary_evaluation":evaluation_packet(moments,rating_band),
            "renderer_benchmark":renderer_benchmark(moments),
            "realization_benchmark":realization_benchmark(moments),
            "verification_benchmark":verification_benchmark(moments),
            "retrieval_corpus_audit":audit_retrieval_corpus(retrieval_records),
            "susceptibility_packet_count":sum(len(v) for v in sidx.values()),
            "authority_packet_count":sum(len(v) for v in aidx.values()),
            "ep8_observation_atom_count":sum(a.get("type")=="opponent_reply_observation" for m in moments for a in m.get("atoms",[])),
            "causal_authority_blocked_moments":sum(1 for m in moments if any(a.get("type")=="mechanism_authority_route" and a.get("claim",{}).get("state")!="SUPPORTED" for a in m.get("atoms",[]))),
            "authority_note":"Useful commentary is not automatically causal. Causal wording requires both a C3X certificate and any applicable precausal authority route to permit it."}

def load_certificates(paths:list[str])->list[dict[str,Any]]:
    out=[]
    for p in paths:
        x=json.load(open(p))
        if isinstance(x,list):out+=x
        elif "causal_explanation_certificates" in x:out+=x["causal_explanation_certificates"]
        else:out.append(x)
    return out
