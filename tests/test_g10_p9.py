import json
from pathlib import Path
from c3x_g10.graded_recoverability import cayley_distance, development_geometry, chain_score
from c3x_g10.acquisition_policy import transform_trigger

ECO = json.loads(Path("c3x/data/g10-p7-development-ecology.json").read_text())

def trig(role="OWN", endpoint="A_FROM", sign="GAIN"):
    return {"role": role, "delta_edges": ((endpoint, sign),)}

def test_cayley_metric_basic():
    a = trig()
    assert cayley_distance(a, a) == 0
    assert cayley_distance(a, transform_trigger(a, ("C",))) == 1
    assert cayley_distance(a, transform_trigger(a, ("C","S"))) == 2
    assert cayley_distance(a, trig(sign="LOSS")) == 99

def test_development_geometry_separates_nontrivial_and_singletons():
    fam, non = development_geometry(ECO)
    assert len(fam) == 2
    assert all(len(v["members"]) == 2 for v in fam.values())
    assert {x["id"] for x in non} == {"P16_BASE","P5_1663_BERSERK"}

def test_chain_score_is_preoutcome_only_shape():
    fam, non = development_geometry(ECO)
    ch = {
        "chain_id":"x",
        "target":{
            "fen":"8/8/8/8/8/8/8/8 w - - 0 1",
            "piece_color":"WHITE",
            "relation_before":[False,True,False,False],
            "relation_after":[True,True,False,False],
        },
    }
    s = chain_score(ch, fam, non)
    assert 0 <= s["family_distance"] <= 3
    assert "response_topology" not in s
    assert "certificate" not in s
