from __future__ import annotations
from typing import Any

AXES=("structural","motif","tactic","position_judgment","semantic","contrastiveness","provenance")

def evaluation_packet(moments:list[dict[str,Any]],rating_band:str)->dict[str,Any]:
    atoms=[a for m in moments for a in m.get("atoms",[])]
    types={a.get("type") for a in atoms}
    axis={
      "structural":{"evidence":sum(a.get("type") in {"material_snapshot","concept_proxy_delta","move_fact"} for a in atoms)},
      "motif":{"evidence":sum(a.get("type") in {"tactical_fact","tactical_contrast","retrieval_reference"} for a in atoms)},
      "tactic":{"evidence":sum(a.get("type") in {"tactical_fact","tactical_contrast"} for a in atoms)},
      "position_judgment":{"evidence":sum(a.get("type")=="candidate_contrast" for a in atoms)},
      "semantic":{"evidence":sum(a.get("type") in {"concept_proxy_delta","retrieval_reference","causal_contrast"} for a in atoms)},
      "contrastiveness":{"evidence":sum(a.get("type") in {"candidate_contrast","tactical_contrast","concept_proxy_delta","causal_contrast"} for a in atoms)},
      "provenance":{"evidence":sum(bool(a.get("provenance") and a.get("authority")) for a in atoms)}
    }
    for k,v in axis.items():
        v["present"]=v["evidence"]>0
        v["human_score"]=None
    return {"schema":"c3x-commentary-evaluation-packet-v1","rating_band":rating_band,
            "axes":axis,"human_utility":{"correctness":None,"pedagogical_clarity":None,"trust_calibration":None,
            "preference_vs_baseline":None,"subsequent_move_understanding":None},
            "note":"Evidence coverage is not a human-utility score; human fields remain unset until adjudicated."}
