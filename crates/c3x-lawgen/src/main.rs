use serde::{Deserialize, Serialize};
use serde_json::{json, Map, Value};
use sha2::{Digest, Sha256};
use std::collections::{BTreeMap, BTreeSet};
use std::env;
use std::fs;
use std::path::Path;

#[derive(Debug, Deserialize)]
struct Spec {
    schema: String,
    scientific_stage: String,
    title: String,
    parent_authority: Value,
    fresh_worlds: FreshWorlds,
    search_budget_axis: BudgetAxis,
    engines: Vec<Engine>,
    descriptor_authority: DescriptorAuthority,
    atlas: Value,
    intervention_algebra: Value,
    prospective_claims: Vec<Value>,
    claim_ceiling: Vec<String>,
}

#[derive(Debug, Deserialize)]
struct FreshWorlds {
    lane: String,
    generation_index_offset: u64,
    families: Vec<String>,
    worlds_per_family: usize,
    worlds_per_side_per_family: usize,
    engine_outcomes_consulted: bool,
}

#[derive(Debug, Deserialize)]
struct BudgetAxis {
    sham_nodes: Vec<u64>,
    canonical_atlas_nodes: u64,
    selective_intervention_nodes: u64,
    atlas_levels: Vec<usize>,
    stability_metrics: Vec<String>,
    selection_rule: String,
}

#[derive(Debug, Deserialize, Clone)]
struct Engine {
    id: String,
    instrument_protocol: String,
    instrument_binary_sha256: String,
    descriptor: BTreeMap<String, Value>,
}

#[derive(Debug, Deserialize)]
struct DescriptorAuthority {
    freeze_time: String,
    candidate_coordinates: Vec<String>,
    shared_coordinates_not_eligible_to_explain_between_engine_variation: Vec<String>,
    minimality_rule: String,
    identification_ceiling: String,
}

#[derive(Debug, Serialize)]
struct MatrixRow {
    ordinal: usize,
    phase: String,
    family: Option<String>,
    budget_nodes: Option<u64>,
    authority: String,
}

fn canonical(v: &Value) -> Value {
    match v {
        Value::Object(m) => {
            let mut keys: Vec<_> = m.keys().cloned().collect();
            keys.sort();
            let mut out = Map::new();
            for k in keys {
                out.insert(k.clone(), canonical(&m[&k]));
            }
            Value::Object(out)
        }
        Value::Array(a) => Value::Array(a.iter().map(canonical).collect()),
        _ => v.clone(),
    }
}

fn sha_value(v: &Value) -> String {
    let bytes = serde_json::to_vec(&canonical(v)).expect("canonical json");
    let mut h = Sha256::new();
    h.update(bytes);
    format!("{:x}", h.finalize())
}

fn validate(spec: &Spec) {
    assert_eq!(spec.schema, "c3x-lawgen-spec-v1", "schema");
    assert_eq!(spec.scientific_stage, "C3X 0.7.0-G9.4-P25", "stage");
    assert!(!spec.fresh_worlds.engine_outcomes_consulted, "fresh world constitution must be outcome blind");
    assert_eq!(spec.fresh_worlds.families.len(), 8, "eight material families");
    assert_eq!(spec.fresh_worlds.worlds_per_family, 48, "48 worlds/family");
    assert_eq!(spec.fresh_worlds.worlds_per_side_per_family * 2, spec.fresh_worlds.worlds_per_family, "balanced sides");
    assert!(spec.fresh_worlds.generation_index_offset > 520000, "freshness must exceed P24 offset");

    let mut budgets = spec.search_budget_axis.sham_nodes.clone();
    let original = budgets.clone();
    budgets.sort_unstable();
    budgets.dedup();
    assert_eq!(budgets, original, "budgets must be unique and increasing");
    assert!(budgets.contains(&spec.search_budget_axis.canonical_atlas_nodes), "canonical budget frozen in budget axis");
    assert!(budgets.contains(&spec.search_budget_axis.selective_intervention_nodes), "intervention budget must also be censused");
    assert_eq!(spec.search_budget_axis.atlas_levels, vec![1, 2, 4, 8], "nested atlas levels");

    let ids: BTreeSet<_> = spec.engines.iter().map(|e| e.id.as_str()).collect();
    assert_eq!(ids.len(), spec.engines.len(), "unique engine ids");
    assert_eq!(ids, BTreeSet::from(["berserk", "ethereal", "stockfish_19"]), "frozen P24 engine set");
    for e in &spec.engines {
        assert!(matches!(e.instrument_protocol.as_str(), "env" | "stockfish_uci"), "known instrument protocol");
        assert_eq!(e.instrument_binary_sha256.len(), 64, "binary sha256");
        for c in &spec.descriptor_authority.candidate_coordinates {
            assert!(e.descriptor.contains_key(c), "engine {} missing candidate descriptor {}", e.id, c);
        }
    }
    assert_eq!(spec.descriptor_authority.freeze_time, "pre_selective_outcome", "descriptor freeze authority");
    assert!(!spec.descriptor_authority.candidate_coordinates.is_empty(), "candidate descriptor set");
}

fn matrix(spec: &Spec) -> Vec<MatrixRow> {
    let mut rows = Vec::new();
    let mut n = 0usize;
    let mut push = |phase: &str, family: Option<String>, budget_nodes: Option<u64>, authority: &str| {
        n += 1;
        rows.push(MatrixRow { ordinal: n, phase: phase.to_string(), family, budget_nodes, authority: authority.to_string() });
    };
    for f in &spec.fresh_worlds.families {
        push("world_compile", Some(f.clone()), None, "outcome_blind");
    }
    push("world_merge", None, None, "outcome_blind");
    for &b in &spec.search_budget_axis.sham_nodes {
        for f in &spec.fresh_worlds.families {
            push("sham_census", Some(f.clone()), Some(b), "outcome_blind");
        }
        push("atlas_build", None, Some(b), "outcome_blind");
    }
    push("budget_stability", None, None, "outcome_blind");
    push("precommit", None, None, "outcome_blind");
    for f in &spec.fresh_worlds.families {
        push("selective_intervention", Some(f.clone()), Some(spec.search_budget_axis.selective_intervention_nodes), "post_precommit");
    }
    push("law_adjudication", None, Some(spec.search_budget_axis.selective_intervention_nodes), "post_precommit");
    push("independent_verification", None, None, "post_adjudication");
    rows
}

fn descriptor_subsets(coords: &[String]) -> Vec<Vec<String>> {
    let n = coords.len();
    let mut out = Vec::new();
    for k in 1..=n {
        for mask in 1usize..(1usize << n) {
            if mask.count_ones() as usize != k { continue; }
            out.push((0..n).filter(|i| mask & (1usize << i) != 0).map(|i| coords[i].clone()).collect());
        }
    }
    out
}

fn main() {
    let args: Vec<String> = env::args().collect();
    if args.len() != 3 {
        eprintln!("usage: c3x-lawgen <spec.json> <out-dir>");
        std::process::exit(2);
    }
    let raw = fs::read_to_string(&args[1]).expect("read spec");
    let raw_value: Value = serde_json::from_str(&raw).expect("parse spec json");
    let spec: Spec = serde_json::from_value(raw_value.clone()).expect("typed spec");
    validate(&spec);

    let out = Path::new(&args[2]);
    fs::create_dir_all(out).expect("create out dir");
    let spec_sha256 = sha_value(&raw_value);
    let rows = matrix(&spec);

    let constitution = json!({
        "schema": "c3x-lawgen-constitution-v1",
        "scientific_stage": spec.scientific_stage,
        "title": spec.title,
        "spec_sha256": spec_sha256,
        "parent_authority": spec.parent_authority,
        "fresh_worlds": {
            "lane": spec.fresh_worlds.lane,
            "generation_index_offset": spec.fresh_worlds.generation_index_offset,
            "families": spec.fresh_worlds.families,
            "worlds_per_family": spec.fresh_worlds.worlds_per_family,
            "engine_outcomes_consulted": false
        },
        "budget_axis": {
            "sham_nodes": spec.search_budget_axis.sham_nodes,
            "canonical_atlas_nodes": spec.search_budget_axis.canonical_atlas_nodes,
            "selective_intervention_nodes": spec.search_budget_axis.selective_intervention_nodes,
            "atlas_levels": spec.search_budget_axis.atlas_levels,
            "stability_metrics": spec.search_budget_axis.stability_metrics,
            "selection_rule": spec.search_budget_axis.selection_rule
        },
        "atlas": spec.atlas,
        "intervention_algebra": spec.intervention_algebra,
        "engines": spec.engines.iter().map(|e| json!({"id":e.id,"protocol":e.instrument_protocol,"binary_sha256":e.instrument_binary_sha256,"descriptor":e.descriptor})).collect::<Vec<_>>(),
        "descriptor_authority": {
            "freeze_time": spec.descriptor_authority.freeze_time,
            "candidate_coordinates": spec.descriptor_authority.candidate_coordinates,
            "shared_coordinates_not_eligible_to_explain_between_engine_variation": spec.descriptor_authority.shared_coordinates_not_eligible_to_explain_between_engine_variation,
            "minimality_rule": spec.descriptor_authority.minimality_rule,
            "identification_ceiling": spec.descriptor_authority.identification_ceiling,
            "candidate_subsets_in_test_order": descriptor_subsets(&spec.descriptor_authority.candidate_coordinates)
        },
        "prospective_claims": spec.prospective_claims,
        "claim_ceiling": spec.claim_ceiling,
        "execution_matrix_rows": rows.len(),
        "selective_outcomes_consulted": false
    });
    let constitution_sha256 = sha_value(&constitution);
    let sealed = json!({
        "constitution": constitution,
        "constitution_sha256": constitution_sha256
    });
    fs::write(out.join("constitution.json"), serde_json::to_string_pretty(&sealed).unwrap() + "\n").expect("write constitution");

    let mut tsv = String::from("ordinal\tphase\tfamily\tbudget_nodes\tauthority\n");
    for r in &rows {
        tsv.push_str(&format!("{}\t{}\t{}\t{}\t{}\n", r.ordinal, r.phase, r.family.as_deref().unwrap_or(""), r.budget_nodes.map(|x| x.to_string()).unwrap_or_default(), r.authority));
    }
    fs::write(out.join("execution-matrix.tsv"), tsv).expect("write matrix");

    let lattice = json!({
        "schema": "c3x-lawgen-claim-lattice-v1",
        "scientific_stage": "C3X 0.7.0-G9.4-P25",
        "constitution_sha256": constitution_sha256,
        "nodes": [
            {"id":"W","requires":[],"meaning":"fresh exact-world constitution"},
            {"id":"A","requires":["W"],"meaning":"multi-budget outcome-blind atlas family"},
            {"id":"B","requires":["A"],"meaning":"budget-stability readout"},
            {"id":"R","requires":["A"],"meaning":"fresh architecture-index replication"},
            {"id":"C","requires":["R"],"meaning":"frozen descriptor compression"},
            {"id":"M","requires":["C"],"meaning":"minimal frozen descriptor coordinate set"}
        ],
        "non_implications": [
            "B does not imply untested-budget invariance",
            "R does not imply architecture identity is fundamental",
            "C does not imply population-level causal identification",
            "M does not license post-outcome descriptor invention"
        ]
    });
    fs::write(out.join("claim-lattice.json"), serde_json::to_string_pretty(&lattice).unwrap() + "\n").expect("write lattice");
    println!("P25_LAWGEN_PASS spec_sha256={} constitution_sha256={} matrix_rows={}", spec_sha256, constitution_sha256, rows.len());
}

#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn subsets_are_cardinality_ordered() {
        let c = vec!["a".into(), "b".into(), "c".into()];
        let s = descriptor_subsets(&c);
        assert_eq!(s.len(), 7);
        assert!(s.windows(2).all(|w| w[0].len() <= w[1].len()));
    }
    #[test]
    fn canonical_hash_ignores_object_key_order() {
        let a: Value = serde_json::from_str(r#"{"b":2,"a":1}"#).unwrap();
        let b: Value = serde_json::from_str(r#"{"a":1,"b":2}"#).unwrap();
        assert_eq!(sha_value(&a), sha_value(&b));
    }
}
