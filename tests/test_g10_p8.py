import json
from c3x_g10.acquisition_policy import *

def eco():return json.load(open("c3x/data/g10-p7-development-ecology.json"))
def certs():return {c["id"]:c for c in eco()["certificates"]}

def test_nontrivial_orbits_only_are_target_prototypes():
    p=nontrivial_orbit_prototypes(eco())
    assert len(p)==2
    assert all(len(x["members"])==2 for x in p.values())

def test_unlicensed_gain_bound_generators_are_absent():
    assert GRAMMAR==("C","S","E")
    assert "G" not in GRAMMAR and "U" not in GRAMMAR

def test_candidate_relabel_is_trigger_gauge():
    c=certs()["P5_1664_ETHEREAL"]
    t=trigger_from_cert(c)
    x=transform_trigger(t,("C",))
    assert x["role"]==t["role"]
    assert x["delta_edges"]!=t["delta_edges"]

def test_side_role_is_substantive_but_admissible():
    c=certs()["P5_1664_ETHEREAL"];t=trigger_from_cert(c)
    x=transform_trigger(t,("S",))
    assert x["role"]!=t["role"]

def test_matching_distance_is_zero_for_equal_frozen_features():
    p={"engine_views":{"a":{"active":True},"b":{"active":True}},"source_ply":18,"pair":{"support_count":2,"median_gap_cp":7},"chain_candidates":[1,2]}
    assert distance(p,p)==0
