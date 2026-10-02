import json
from c3x_g10.mechanism_identity import *

def eco():
    return json.load(open("c3x/data/g10-p6-development-ecology.json"))

def byid():
    return {c["id"]:c for c in eco()["certificates"]}

def test_exact_signature_is_not_constitutive_identity():
    c=byid();x=classify_pair(c["P5_1663_BERSERK"],c["P5_1663_ETHEREAL"])
    assert x["same_exact_signature"] is True
    assert x["same_relation_delta"] is True
    assert x["same_response_topology"] is False
    assert x["class"]=="SAME_BOARD_TRIGGER_DIFFERENT_SEARCH_MANIFESTATION"

def test_response_topology_alone_is_not_board_causal_identity():
    c=byid();x=classify_pair(c["P5_1664_ETHEREAL"],c["P5_1663_BERSERK"])
    assert x["same_response_topology"] is True
    assert x["same_relation_delta"] is False
    assert x["class"]=="SAME_SEARCH_RESPONSE_DIFFERENT_BOARD_TRIGGER"

def test_minimal_empirical_witness_is_conjunction():
    r=development_adjudication(eco())
    assert r["verdict"]=="PASS_CONJUNCTIVE_CONSTITUTIVE_CORE_PRESEALED"
    assert ["relation_delta","response_topology"] in r["minimal_witness_sets"]
    assert ["relation_delta"] not in r["minimal_witness_sets"]
    assert ["response_topology"] not in r["minimal_witness_sets"]

def test_physical_context_is_not_built_into_core():
    c=byid()
    assert constitutive_core(c["P5_1664_ETHEREAL"])==constitutive_core(c["P5_1663_BERSERK"]) is False

def test_composition_requires_independent_provenance():
    c=byid()
    x=classify_pair(c["P5_1663_BERSERK"],c["P5_1663_ETHEREAL"])
    assert x["independent_provenance"] is False
