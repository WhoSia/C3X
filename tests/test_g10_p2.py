from c3x_g10.question_identity import adjudicate,compute_identity,hce_pair_equivalent,jaccard,mean_pairwise_jaccard,modal

def obs(*moves):return {"candidates":[{"uci":m} for m in moves]}
def pol():return {1200:{"e2e4":.25,"d2d4":.20,"c2c4":.18,"g1f3":.15},1800:{"e2e4":.22,"d2d4":.21,"c2c4":.17,"g1f3":.16},2400:{"e2e4":.20,"d2d4":.19,"c2c4":.18,"g1f3":.17}}
def base():
    f=[obs("e2e4","d2d4","g1f3") for _ in range(5)]
    return {"case_id":"x","phase":"opening","measurements":{"fresh_5k":f,"clean_5k":f,"history_5k":[obs("d2d4","e2e4","g1f3") for _ in range(5)],"budget_nonprimary":{"stockfish_2k":obs("e2e4","d2d4","g1f3"),"stockfish_10k":obs("d2d4","e2e4","g1f3"),"stockfish_40k":obs("e2e4","d2d4","c2c4")},"cross_engine_10k":{"berserk":obs("e2e4","d2d4","c2c4"),"ethereal":obs("c2c4","e2e4","d2d4")},"maia_policy":pol()}}

def test_primitives():
    assert modal([("a","b"),("a","b"),("b","c")])[1]==2/3
    assert jaccard({"a","b"},{"b","c"})==1/3
    assert mean_pairwise_jaccard([frozenset({"a","b"}),frozenset({"a","b"})])==1.0

def test_hce():
    x=hce_pair_equivalent(("e2e4","d2d4"),("e2e4","c2c4"),pol())
    assert x["equivalent"] is True
    assert x["authority"]=="PREDICTIVE_HUMAN_POLICY_EQUIVALENCE_ONLY"

def test_identity():
    x=compute_identity(base())
    assert x["stable"] is True
    assert x["fresh"]["u2_repeatability"]==1.0
    assert x["context"]["history_u2_agreement"]==1.0

def test_engine_conditional_is_allowed():
    c=base();c["measurements"]["cross_engine_10k"]={"berserk":obs("a2a3","h2h3","b2b3"),"ethereal":obs("a2a3","b2b3","h2h3")}
    c["identity"]=compute_identity(c)
    assert c["identity"]["stable"] is True
    assert c["identity"]["engine_scope"]["scope"]=="ENGINE_CONDITIONAL"

def test_court_passes_stable_bank_without_causality():
    rows=[]
    for i in range(60):
        c=base();c["case_id"]=f"c{i}";c["phase"]=["opening","middlegame","endgame"][i%3];c["identity"]=compute_identity(c);rows.append(c)
    out=adjudicate(rows,{"fresh_disjoint":True})
    assert out["stable_object_n"]==60
    assert out["fresh_local_certificate_induction_opened"] is False

def test_forbidden_field_fails():
    rows=[]
    for i in range(60):
        c=base();c["case_id"]=f"c{i}";c["phase"]="opening";c["certificate_yield"]=1;c["identity"]=compute_identity(c);rows.append(c)
    try:adjudicate(rows,{"fresh_disjoint":True})
    except ValueError as e:assert "forbidden causal fields" in str(e)
    else:raise AssertionError("leak should fail")
