from __future__ import annotations
import hashlib,itertools,json,math
from collections import Counter
from typing import Any

STAGE_TITLE="C3X 0.8.0-G10-P2 — Prospective Explanation-Question Identity Constitution, Search-Context Repeatability, Independent-Instance Reconstitution, Budget↔Engine Perturbation Decomposition, Human-Salience-Preserving Contrast Equivalence, Fresh-Disjoint Real-PGN Replication, Measurement-Error Localization & Stable Research-Admission Object Court"
ELO_BANDS=(1200,1800,2400)
FRESH_REPEATS=5
CLEAN_REPEATS=5
HISTORY_REPEATS=5
BUDGETS=(2000,5000,10000,40000)
PRIMARY_BUDGET=5000
CROSS_ENGINE_BUDGET=10000
P2_POLICY={
  "schema": "c3x-g10-p2-policy-v1",
  "position_target": 60,
  "phase_quota": {
    "opening": 20,
    "middlegame": 20,
    "endgame": 20
  },
  "max_positions_per_game": 2,
  "fresh_repeats": 5,
  "clean_repeats": 5,
  "history_repeats": 5,
  "fresh_u2_repeatability_min": 0.8,
  "fresh_n3_pairwise_jaccard_min": 0.8,
  "clean_u2_agreement_min": 0.8,
  "history_u2_agreement_min": 0.6,
  "budget_direct_support_min": 2,
  "hce_band_min": 2,
  "hce_rank_max": 5,
  "hce_probability_min": 0.01,
  "hce_pair_mass_delta_max": 0.15,
  "stable_bank_min": 24,
  "fail_bank_max": 5,
  "engine_universal_support_min": 2,
  "uses_certificate_yield": False,
  "uses_p1_survivors": False
}
FORBIDDEN_KEYS={"certificate_id","certificate_yield","intervention_outcome","causal_family","structural_signature","replication_status","decision_cells","falsifiers"}

def stable_hash(value:Any)->str:
    raw=json.dumps(value,sort_keys=True,separators=(",",":"),ensure_ascii=False)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()

def board_key(fen:str)->str:
    p=str(fen).split()
    if len(p)<4: raise ValueError("invalid FEN")
    return " ".join(p[:4])

def phase_from_board(board)->str:
    import chess
    values={chess.KNIGHT:3,chess.BISHOP:3,chess.ROOK:5,chess.QUEEN:9}
    nonpawn=sum(v*(len(board.pieces(pt,chess.WHITE))+len(board.pieces(pt,chess.BLACK))) for pt,v in values.items())
    if board.fullmove_number<=15 and nonpawn>=42:return "opening"
    if nonpawn<=18:return "endgame"
    return "middlegame"

def top_moves(obs,k):
    return tuple(str(x["uci"]) for x in (obs.get("candidates") or [])[:k] if x.get("uci"))
def o2(obs):return top_moves(obs,2)
def u2(obs):return tuple(sorted(o2(obs)))
def n3(obs):return frozenset(top_moves(obs,3))

def modal(values):
    if not values:return None,0.0
    c=Counter(values);b=max(c.values())
    w=sorted((k for k,v in c.items() if v==b),key=lambda x:str(x))
    return w[0],b/len(values)

def jaccard(a,b):
    a,b=set(a),set(b);u=a|b
    return 1.0 if not u else len(a&b)/len(u)

def mean_pairwise_jaccard(sets):
    if len(sets)<2:return None
    xs=[jaccard(a,b) for a,b in itertools.combinations(sets,2)]
    return sum(xs)/len(xs)

def mode_agreement(observations,modal_u2):
    if not observations or modal_u2 is None:return 0.0
    return sum(u2(x)==modal_u2 for x in observations)/len(observations)

def maia_ranked(policy):
    return [m for m,_ in sorted(((str(m),float(p)) for m,p in policy.items()),key=lambda kv:(-kv[1],kv[0]))]

def hce_pair_equivalent(base_pair,alt_pair,policy_by_elo):
    a=tuple(sorted(str(x) for x in base_pair));b=tuple(sorted(str(x) for x in alt_pair))
    if len(a)!=2 or len(b)!=2:return {"equivalent":False,"supported_bands":0,"bands":{}}
    if a==b:return {"equivalent":True,"supported_bands":len(ELO_BANDS),"bands":{str(e):{"exact_pair":True} for e in ELO_BANDS},"authority":"PREDICTIVE_HUMAN_POLICY_EQUIVALENCE_ONLY"}
    details={};supported=0
    for elo in ELO_BANDS:
        probs={str(k):float(v) for k,v in (policy_by_elo.get(elo) or policy_by_elo.get(str(elo)) or {}).items()}
        ranked=maia_ranked(probs)
        ranks={m:(ranked.index(m)+1 if m in ranked else None) for m in set(a)|set(b)}
        all_close=all(probs.get(m,0.0)>=P2_POLICY["hce_probability_min"] and ranks.get(m) is not None and ranks[m]<=P2_POLICY["hce_rank_max"] for m in set(a)|set(b))
        ma=sum(probs.get(m,0.0) for m in a);mb=sum(probs.get(m,0.0) for m in b)
        ok=bool(all_close and abs(ma-mb)<=P2_POLICY["hce_pair_mass_delta_max"])
        supported+=int(ok)
        details[str(elo)]={"supported":ok,"pair_a_mass":ma,"pair_b_mass":mb,"mass_delta":abs(ma-mb),"ranks":ranks}
    return {"equivalent":supported>=P2_POLICY["hce_band_min"],"supported_bands":supported,"bands":details,"authority":"PREDICTIVE_HUMAN_POLICY_EQUIVALENCE_ONLY"}

def budget_transport(modal_pair,budget_obs,policy_by_elo):
    direct=hce=0;worlds={}
    for key,obs in sorted(budget_obs.items()):
        pair=u2(obs);exact=bool(modal_pair and pair==modal_pair)
        eq=hce_pair_equivalent(modal_pair or (),pair,policy_by_elo) if modal_pair else {"equivalent":False}
        direct+=int(exact);hce+=int(bool(eq.get("equivalent")))
        worlds[key]={"u2":list(pair),"direct":exact,"hce":eq}
    return {"worlds":worlds,"direct_support":direct,"hce_support":hce,"passes":direct>=P2_POLICY["budget_direct_support_min"] or hce>=P2_POLICY["budget_direct_support_min"]}

def engine_scope(stockfish_pair,engine_obs,policy_by_elo):
    support=0;worlds={}
    for name,obs in sorted(engine_obs.items()):
        pair=u2(obs);exact=bool(stockfish_pair and pair==stockfish_pair)
        eq=hce_pair_equivalent(stockfish_pair or (),pair,policy_by_elo) if stockfish_pair else {"equivalent":False}
        transported=bool(exact or eq.get("equivalent"));support+=int(transported)
        worlds[name]={"u2":list(pair),"exact":exact,"hce":eq,"transported":transported}
    return {"scope":"MULTI_ENGINE" if support>=P2_POLICY["engine_universal_support_min"] else "ENGINE_CONDITIONAL","support":support,"worlds":worlds}

def compute_identity(case):
    m=case["measurements"];fresh=m["fresh_5k"];clean=m["clean_5k"];history=m["history_5k"]
    fo=[o2(x) for x in fresh];fu=[u2(x) for x in fresh];fn=[n3(x) for x in fresh]
    mo,os=modal(fo);mu,us=modal(fu);mn,ne=modal([tuple(sorted(x)) for x in fn]);nj=mean_pairwise_jaccard(fn)
    ca=mode_agreement(clean,mu);ha=mode_agreement(history,mu);pol=m["maia_policy"]
    bt=budget_transport(mu,m["budget_nonprimary"],pol);es=engine_scope(mu,m["cross_engine_10k"],pol)
    stable=bool(us>=P2_POLICY["fresh_u2_repeatability_min"] and nj is not None and nj>=P2_POLICY["fresh_n3_pairwise_jaccard_min"] and ca>=P2_POLICY["clean_u2_agreement_min"] and ha>=P2_POLICY["history_u2_agreement_min"] and bt["passes"])
    return {"schema":"c3x-g10-p2-question-identity-v1","fresh":{"modal_o2":list(mo or()),"o2_repeatability":os,"modal_u2":list(mu or()),"u2_repeatability":us,"modal_n3":list(mn or()),"n3_exact_share":ne,"n3_mean_pairwise_jaccard":nj},"context":{"clean_u2_agreement":ca,"history_u2_agreement":ha,"clean_minus_history":ca-ha},"budget_transport":bt,"engine_scope":es,"stable":stable,"authority":"MEASUREMENT_STABLE_RESEARCH_QUESTION_ONLY" if stable else "NONADMITTED_MEASUREMENT_OBJECT"}

def localize_measurement_error(records):
    n=len(records)
    if not n:return {"n":0}
    vs=[x["identity"] for x in records]
    vals={
      "WITHIN_FRESH_REPEATABILITY":sum(v["fresh"]["u2_repeatability"]<P2_POLICY["fresh_u2_repeatability_min"] for v in vs),
      "CLEAN_CONTEXT_TRANSPORT":sum(v["context"]["clean_u2_agreement"]<P2_POLICY["clean_u2_agreement_min"] for v in vs),
      "HISTORY_CONTEXT_SENSITIVITY":sum(v["context"]["history_u2_agreement"]<P2_POLICY["history_u2_agreement_min"] for v in vs),
      "BUDGET_TRANSPORT":sum(not v["budget_transport"]["passes"] for v in vs),
      "ENGINE_SCOPE":sum(v["engine_scope"]["scope"]=="ENGINE_CONDITIONAL" for v in vs),
    }
    dom=max(vals.items(),key=lambda x:x[1])
    return {"n":n,**{k.lower()+"_n":v for k,v in vals.items()},"dominant_observed_limitation":dom[0],"dominant_count":dom[1],"causal_mechanism_claimed":False}

def recursive_forbidden(value):
    found=set()
    if isinstance(value,dict):
        for k,v in value.items():
            if k in FORBIDDEN_KEYS:found.add(k)
            found|=recursive_forbidden(v)
    elif isinstance(value,list):
        for x in value:found|=recursive_forbidden(x)
    return found

def adjudicate(records,bank_meta):
    leaked=sorted(recursive_forbidden(records))
    if leaked:raise ValueError(f"forbidden causal fields leaked: {leaked}")
    stable=[x for x in records if x["identity"]["stable"]];phases=sorted({x["phase"] for x in stable})
    scopes=Counter(x["identity"]["engine_scope"]["scope"] for x in stable);n=len(stable)
    if len(records)!=P2_POLICY["position_target"] or bank_meta.get("fresh_disjoint") is not True:verdict="HOLD_FRESH_DISJOINT_SOURCE_SUPPORT_INSUFFICIENT"
    elif n<=P2_POLICY["fail_bank_max"]:verdict="FAIL_NO_STABLE_QUESTION_OBJECT"
    elif n<P2_POLICY["stable_bank_min"] or len(phases)<2:verdict="HOLD_SEARCH_CONTEXT_REPEATABILITY_UNRESOLVED"
    elif scopes.get("MULTI_ENGINE",0)>=math.ceil(n/2):verdict="PASS_STABLE_QUESTION_OBJECT_BANK_FROZEN"
    else:verdict="PASS_ENGINE_CONDITIONAL_QUESTION_OBJECT_BANK_FROZEN"
    return {"schema":"c3x-g10-p2-court-v1","stage":STAGE_TITLE,"verdict":verdict,"position_bank_n":len(records),"stable_object_n":n,"stable_object_fraction":None if not records else n/len(records),"stable_phases":phases,"scope_counts":dict(scopes),"measurement_error_localization":localize_measurement_error(records),"stable_case_ids":[x["case_id"] for x in stable],"stable_bank_sha256":stable_hash([x["case_id"] for x in stable]),"fresh_local_certificate_induction_opened":False,"certificate_yield_visible":False,"uses_p1_survivors":False,"authority":"STABLE_RESEARCH_QUESTION_OBJECT_ONLY"}
