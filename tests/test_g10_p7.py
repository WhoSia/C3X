import json
from c3x_g10.morphism_grammar import *

def eco():return json.load(open("c3x/data/g10-p7-development-ecology.json"))
def certs():return {c["id"]:c for c in eco()["certificates"]}

def test_side_role_only_development_witness():
    c=certs();w=morphism_witness(c["P5_1663_ETHEREAL"],c["HOLDOUT_f05f7fbd9afcec6d80016f8b"])
    assert w["isomorphic"] is True
    assert w["minimal_generators"]==["S"]

def test_candidate_endpoint_side_witness():
    c=certs();w=morphism_witness(c["P5_1664_ETHEREAL"],c["HOLDOUT_c64ae837e530ff9822621fc3"])
    assert w["isomorphic"] is True
    assert w["minimal_generators"]==["C","E","S"]

def test_p6_same_trigger_different_response_stays_distinct():
    c=certs();w=morphism_witness(c["P5_1663_BERSERK"],c["P5_1663_ETHEREAL"])
    assert w["isomorphic"] is False

def test_p6_same_response_different_trigger_stays_distinct_without_gainloss():
    c=certs();w=morphism_witness(c["P5_1664_ETHEREAL"],c["P5_1663_BERSERK"])
    assert w["isomorphic"] is False

def test_gainloss_and_bound_are_not_admissible_generators():
    assert "G" not in ADMISSIBLE_GRAMMAR
    assert "U" not in ADMISSIBLE_GRAMMAR

def test_development_grammar_is_nondegenerate():
    r=development_adjudication(eco())
    assert r["verdict"]=="PASS_MORPHISM_GRAMMAR_PRESEALED"
    assert r["nondegenerate"] is True
    assert r["largest_orbit"] < r["certificate_count"]
