import json
from c3x_g10.invariant_lattice import adjudicate,counterexamples,build_evidence

MET={
 "metrology_0_3":{"canonical_repeatability_zero_positions_each_arm":34,"pair_sign_repeatability_1000ms":34,"nonzero_fixed_node_sign_transport_1000ms":165},
 "metrology_0_4":{"fixed_node_load_canonical_identity":170,"movetime_load_canonical_difference":170,"movetime_load_pair_sign_difference":17},
 "metrology_0_5":{"realized_node_pair_sign_reproduction":340,"search_state_reproduction_without_node_counter":336},
 "metrology_0_6":{"residual_states_exactly_reachable":4},
}
P12={"science":{"root_change_targets":42,"mediated_targets":24,"mediation_status_counts":{"EXACT_CUTOFF_BRIDGE":4,"EXACT_CUTOFF_INTERACTION_REDIRECT":4,"BASELINE_CUTOFF_SUFFICIENCY_ONLY":11,"COUNTERFACTUAL_CUTOFF_NECESSITY_ONLY":9,"CUTOFF_COLOCATION_ONLY":14},"replicated_mediated_transition_signatures":[]}}
P16={"result":{"minimal_full_bridge_records":1,"certificate_count":1,"replicated_exact_structural_signatures":[],"replicated_coarse_full_bridge_signatures":[]},"representative_minimal_bridge":{"pair_uci":"d6d5::e8g8","replication_status":"LOCAL_ONLY","subset_reproduced":False,"sham_reproduced":False}}

def test_counterexamples_cover_every_coarse_candidate():
    e=build_evidence(MET,P12,P16)
    c=counterexamples(e)
    assert {x["candidate"] for x in c}=={"CANONICAL_STATE","REGIME_TAGGED_PAIR_SIGN","CANDIDATE_FATE","INTERVENTION_RESPONSE"}

def test_two_level_architecture_passes_without_promoting_local_certificate():
    r=adjudicate(MET,P12,P16)
    assert r["verdict"]=="PASS_TWO_LEVEL_INVARIANT_ARCHITECTURE"
    assert r["adjudication"]["single_universal_quotient_rejected"] is True
    assert r["adjudication"]["causal_authority_object"]["representation"]=="LOCAL_CAUSAL_CERTIFICATE"
    assert "P16 remains LOCAL_ONLY." in r["authority_ceiling"]

def test_root_change_is_not_mediation():
    r=adjudicate(MET,P12,P16)
    d={x["candidate"]:x["failure"] for x in r["counterexamples"]}
    assert d["CANDIDATE_FATE"]=="ROOT_CHOICE_TRANSITION_DOES_NOT_IDENTIFY_CAUSAL_BRIDGE"

def test_intervention_response_without_falsifiers_is_insufficient():
    r=adjudicate(MET,P12,P16)
    d={x["candidate"]:x["failure"] for x in r["counterexamples"]}
    assert d["INTERVENTION_RESPONSE"]=="OMITS_MINIMALITY_AND_FALSIFIER_CONTRACT"
