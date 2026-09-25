use std::cmp::Ordering;
use std::collections::{BTreeMap, HashMap};
use std::env;
use std::fs;
use std::io::{self, Write};

#[derive(Clone, Debug)]
struct Row {
    sha: String,
    family: String,
    side: String,
    square: String,
    main: [f64; 3],
    q: [f64; 3],
    qshare: [f64; 3],
}

#[derive(Clone, Debug, Default)]
struct Atlas {
    c_total: f64,
    c_q: f64,
    d_total: f64,
    d_q: f64,
    d_joint: f64,
    state2: String,
    state4: String,
    state8: String,
}

fn parse_f64(s: &str, name: &str) -> f64 {
    let v: f64 = s.parse().unwrap_or_else(|_| panic!("invalid {name}: {s}"));
    assert!(v.is_finite(), "non-finite {name}");
    v
}

fn median3(mut x: [f64; 3]) -> f64 {
    x.sort_by(|a, b| a.partial_cmp(b).unwrap_or(Ordering::Equal));
    x[1]
}

fn spread3(x: [f64; 3]) -> f64 {
    let lo = x.iter().copied().fold(f64::INFINITY, f64::min);
    let hi = x.iter().copied().fold(f64::NEG_INFINITY, f64::max);
    hi - lo
}

/// Average-tie empirical ranks in (0,1), using (midrank + 0.5) / n.
fn midranks(values: &[(usize, f64)]) -> HashMap<usize, f64> {
    let mut v = values.to_vec();
    v.sort_by(|a, b| a.1.partial_cmp(&b.1).unwrap_or(Ordering::Equal).then(a.0.cmp(&b.0)));
    let n = v.len() as f64;
    let mut out = HashMap::new();
    let mut i = 0usize;
    while i < v.len() {
        let mut j = i + 1;
        while j < v.len() && v[j].1 == v[i].1 { j += 1; }
        let mid_zero_based = (i as f64 + (j - 1) as f64) / 2.0;
        let r = (mid_zero_based + 0.5) / n;
        for k in i..j { out.insert(v[k].0, r); }
        i = j;
    }
    out
}

fn header_map(header: &str) -> HashMap<&str, usize> {
    header.split('\t').enumerate().map(|(i, x)| (x, i)).collect()
}

fn read_rows(path: &str) -> Vec<Row> {
    let text = fs::read_to_string(path).expect("read census TSV");
    let mut lines = text.lines();
    let header = lines.next().expect("header");
    let h = header_map(header);
    let need = [
        "sha","family","side","square",
        "sf_main","sf_q","sf_qshare",
        "berserk_main","berserk_q","berserk_qshare",
        "ethereal_main","ethereal_q","ethereal_qshare",
    ];
    for k in need { assert!(h.contains_key(k), "missing column {k}"); }
    let mut rows = Vec::new();
    for (line_no, line) in lines.enumerate() {
        if line.trim().is_empty() { continue; }
        let c: Vec<&str> = line.split('\t').collect();
        let get = |k: &str| -> &str { c[*h.get(k).unwrap()] };
        rows.push(Row {
            sha: get("sha").to_string(),
            family: get("family").to_string(),
            side: get("side").to_string(),
            square: get("square").to_string(),
            main: [parse_f64(get("sf_main"), "sf_main"), parse_f64(get("berserk_main"), "berserk_main"), parse_f64(get("ethereal_main"), "ethereal_main")],
            q: [parse_f64(get("sf_q"), "sf_q"), parse_f64(get("berserk_q"), "berserk_q"), parse_f64(get("ethereal_q"), "ethereal_q")],
            qshare: [parse_f64(get("sf_qshare"), "sf_qshare"), parse_f64(get("berserk_qshare"), "berserk_qshare"), parse_f64(get("ethereal_qshare"), "ethereal_qshare")],
        });
        assert!(c.len() >= h.len(), "short row {}", line_no + 2);
    }
    rows
}

fn assign_half<F: Fn(usize) -> f64>(idxs: &[usize], atlas: &mut [Atlas], rows: &[Row], value: F, prefix: &str, field: usize) -> (Vec<usize>, Vec<usize>) {
    assert!(idxs.len() % 2 == 0, "balanced split requires even support");
    let mut v = idxs.to_vec();
    v.sort_by(|&a, &b| value(a).partial_cmp(&value(b)).unwrap_or(Ordering::Equal).then(rows[a].sha.cmp(&rows[b].sha)));
    let mid = v.len()/2;
    let lo = v[..mid].to_vec();
    let hi = v[mid..].to_vec();
    for &i in &lo {
        match field { 2 => atlas[i].state2 = format!("{prefix}0"), 4 => atlas[i].state4 = format!("{prefix}0"), 8 => atlas[i].state8 = format!("{prefix}0"), _ => unreachable!() }
    }
    for &i in &hi {
        match field { 2 => atlas[i].state2 = format!("{prefix}1"), 4 => atlas[i].state4 = format!("{prefix}1"), 8 => atlas[i].state8 = format!("{prefix}1"), _ => unreachable!() }
    }
    (lo, hi)
}

fn build(rows: &[Row]) -> Vec<Atlas> {
    assert_eq!(rows.len(), 384, "P24 requires exactly 384 fresh cells");
    let mut groups: BTreeMap<(String,String), Vec<usize>> = BTreeMap::new();
    for (i, r) in rows.iter().enumerate() { groups.entry((r.family.clone(), r.side.clone())).or_default().push(i); }
    assert_eq!(groups.len(), 16, "expected 8 families x 2 sides");
    assert!(groups.values().all(|v| v.len()==24), "every family-side stratum must contain 24 cells");
    let mut atlas = vec![Atlas::default(); rows.len()];

    for ((_family,_side), idxs) in groups.iter() {
        let mut rt: [HashMap<usize,f64>;3] = std::array::from_fn(|_| HashMap::new());
        let mut rq: [HashMap<usize,f64>;3] = std::array::from_fn(|_| HashMap::new());
        for e in 0..3 {
            let totals: Vec<(usize,f64)> = idxs.iter().map(|&i| (i, rows[i].main[e] + rows[i].q[e])).collect();
            let shares: Vec<(usize,f64)> = idxs.iter().map(|&i| (i, rows[i].qshare[e])).collect();
            rt[e] = midranks(&totals);
            rq[e] = midranks(&shares);
        }
        for &i in idxs {
            let t = [rt[0][&i],rt[1][&i],rt[2][&i]];
            let q = [rq[0][&i],rq[1][&i],rq[2][&i]];
            atlas[i].c_total = median3(t);
            atlas[i].c_q = median3(q);
            atlas[i].d_total = spread3(t);
            atlas[i].d_q = spread3(q);
            atlas[i].d_joint = (atlas[i].d_total + atlas[i].d_q)/2.0;
        }

        // K2: Q-share consensus. Exactly 12/12.
        let (q0,q1) = assign_half(idxs, &mut atlas, rows, |i| atlas[i].c_q, "Q", 2);
        let halves = [("Q0_T",q0),("Q1_T",q1)];
        let mut state4_groups: Vec<(String,Vec<usize>)> = Vec::new();
        for (prefix, block) in halves {
            let (lo,hi) = assign_half(&block, &mut atlas, rows, |i| atlas[i].c_total, prefix, 4);
            state4_groups.push((format!("{}0_D",prefix),lo));
            state4_groups.push((format!("{}1_D",prefix),hi));
        }
        // K8: cross-architecture disagreement. Exactly 3/3 within each K4 block.
        for (prefix, block) in state4_groups {
            let _ = assign_half(&block, &mut atlas, rows, |i| atlas[i].d_joint, &prefix, 8);
        }
    }

    for a in &atlas {
        assert!(!a.state2.is_empty() && !a.state4.is_empty() && !a.state8.is_empty(), "unassigned atlas state");
    }
    atlas
}

fn validate(rows: &[Row], atlas: &[Atlas]) -> BTreeMap<String, usize> {
    let mut counts = BTreeMap::new();
    for (r,a) in rows.iter().zip(atlas.iter()) {
        *counts.entry(format!("{}|{}|K2|{}",r.family,r.side,a.state2)).or_insert(0) += 1;
        *counts.entry(format!("{}|{}|K4|{}",r.family,r.side,a.state4)).or_insert(0) += 1;
        *counts.entry(format!("{}|{}|K8|{}",r.family,r.side,a.state8)).or_insert(0) += 1;
    }
    for (k,v) in &counts {
        let expected = if k.contains("|K2|") {12} else if k.contains("|K4|") {6} else {3};
        assert_eq!(*v, expected, "quota failure {k}");
    }
    counts
}

fn write_atlas(path: &str, rows: &[Row], atlas: &[Atlas]) -> io::Result<()> {
    let mut f = fs::File::create(path)?;
    writeln!(f,"sha\tfamily\tside\tsquare\tstate2\tstate4\tstate8\tc_total\tc_q\td_total\td_q\td_joint")?;
    let mut order: Vec<usize> = (0..rows.len()).collect();
    order.sort_by(|&a,&b| rows[a].sha.cmp(&rows[b].sha));
    for i in order {
        let r=&rows[i]; let a=&atlas[i];
        writeln!(f,"{}\t{}\t{}\t{}\t{}\t{}\t{}\t{:.17}\t{:.17}\t{:.17}\t{:.17}\t{:.17}",r.sha,r.family,r.side,r.square,a.state2,a.state4,a.state8,a.c_total,a.c_q,a.d_total,a.d_q,a.d_joint)?;
    }
    Ok(())
}

fn json_escape(s: &str) -> String { s.replace('\\',"\\\\").replace('"',"\\\"") }

fn write_receipt(path: &str, counts: &BTreeMap<String,usize>) -> io::Result<()> {
    let mut f=fs::File::create(path)?;
    writeln!(f,"{{")?;
    writeln!(f,"  \"schema\": \"c3x-p24-atlas-v1\",")?;
    writeln!(f,"  \"scientific_stage\": \"C3X 0.7.0-G9.4-P24\",")?;
    writeln!(f,"  \"outcomes_consulted\": false,")?;
    writeln!(f,"  \"alignment\": \"within-stratum average-tie empirical-copula ranks; engine-symmetric median plus rank spread\",")?;
    writeln!(f,"  \"refinement\": [1,2,4,8],")?;
    writeln!(f,"  \"cells\": 384,")?;
    writeln!(f,"  \"quota_certificate\": {{")?;
    for (n,(k,v)) in counts.iter().enumerate() {
        let comma=if n+1==counts.len(){""}else{","};
        writeln!(f,"    \"{}\": {}{}",json_escape(k),v,comma)?;
    }
    writeln!(f,"  }}")?;
    writeln!(f,"}}")?;
    Ok(())
}

fn main() {
    let args: Vec<String> = env::args().collect();
    if args.len()!=4 { eprintln!("usage: c3x-atlas <census.tsv> <atlas.tsv> <receipt.json>"); std::process::exit(2); }
    let rows=read_rows(&args[1]);
    let atlas=build(&rows);
    let counts=validate(&rows,&atlas);
    write_atlas(&args[2],&rows,&atlas).expect("write atlas");
    write_receipt(&args[3],&counts).expect("write receipt");
    println!("P24_ATLAS_PASS cells={} quota_entries={} K=1,2,4,8",rows.len(),counts.len());
}

#[cfg(test)]
mod tests {
    use super::*;
    #[test] fn median_is_middle(){ assert_eq!(median3([3.0,1.0,2.0]),2.0); }
    #[test] fn ties_get_same_midrank(){
        let r=midranks(&[(0,1.0),(1,1.0),(2,3.0),(3,4.0)]);
        assert_eq!(r[&0],r[&1]);
        assert!(r[&0] < r[&2] && r[&2] < r[&3]);
    }
}
