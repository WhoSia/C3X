#!/usr/bin/env python3
import argparse,json,subprocess
from pathlib import Path

LOCK="7ef903e8f86f7dcaf4fd04aeecb22711190d2a6d"
VARIANTS=("instrument","removal_tt_main","removal_pawn_main","removal_pawn_q")

def one(text,old,new,label):
    n=text.count(old)
    if n!=1:
        raise SystemExit(f"{label}_ANCHOR_COUNT {n}")
    return text.replace(old,new,1)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--root",required=True)
    ap.add_argument("--variant",choices=VARIANTS,required=True)
    ap.add_argument("--manifest",required=True)
    a=ap.parse_args()
    root=Path(a.root)
    head=subprocess.check_output(["git","-C",str(root),"rev-parse","HEAD"],text=True).strip()
    if head!=LOCK:
        raise SystemExit("SOURCE_LOCK_FAIL")

    fixed={
        "instrument":None,
        "removal_tt_main":"MASK_TT_MAIN",
        "removal_pawn_main":"MASK_PAWN_MAIN",
        "removal_pawn_q":"MASK_PAWN_Q",
    }[a.variant]

    lib=root/"src/lib.rs"
    t=lib.read_text()
    if "pub mod c3x;" in t:
        raise SystemExit("C3X_MODULE_ALREADY_PRESENT")
    t=one(t,"pub mod cache;","pub mod c3x;\npub mod cache;","LIB_MODULE")
    lib.write_text(t)

    c3x=root/"src/c3x.rs"
    mode_fn=(
        f'fn mode() -> &\'static str {{ "{fixed}" }}'
        if fixed is not None else
        '''fn mode() -> &'static str {
    MODE.get_or_init(|| std::env::var("C3X_P21_MODE").unwrap_or_else(|_| "NATIVE".to_string())).as_str()
}'''
    )
    c3x.write_text(f'''use crate::cache::search::TTableResult;
use std::cell::Cell;
use std::sync::atomic::{{AtomicU64,Ordering}};
use std::sync::OnceLock;

pub const PHASE_NONE:u8=0;
pub const PHASE_MAIN:u8=1;
pub const PHASE_QSEARCH:u8=2;

thread_local! {{
    static PHASE: Cell<u8> = Cell::new(PHASE_NONE);
}}

static MODE:OnceLock<String>=OnceLock::new();
static TT_MAIN_PROBES:AtomicU64=AtomicU64::new(0);
static TT_MAIN_HITS:AtomicU64=AtomicU64::new(0);
static TT_MAIN_MASKS:AtomicU64=AtomicU64::new(0);
static PAWN_MAIN_PROBES:AtomicU64=AtomicU64::new(0);
static PAWN_MAIN_HITS:AtomicU64=AtomicU64::new(0);
static PAWN_MAIN_MASKS:AtomicU64=AtomicU64::new(0);
static PAWN_Q_PROBES:AtomicU64=AtomicU64::new(0);
static PAWN_Q_HITS:AtomicU64=AtomicU64::new(0);
static PAWN_Q_MASKS:AtomicU64=AtomicU64::new(0);
static PAWN_OTHER_PROBES:AtomicU64=AtomicU64::new(0);

{mode_fn}

fn mask_tt_main() -> bool {{
    matches!(mode(),"MASK_TT_MAIN"|"MASK_TT_AND_PAWN_Q"|"MASK_ALL")
}}
fn mask_pawn_main() -> bool {{
    matches!(mode(),"MASK_PAWN_MAIN"|"MASK_PAWN_ALL"|"MASK_ALL")
}}
fn mask_pawn_q() -> bool {{
    matches!(mode(),"MASK_PAWN_Q"|"MASK_PAWN_ALL"|"MASK_TT_AND_PAWN_Q"|"MASK_ALL")
}}

pub fn with_phase<T,F:FnOnce()->T>(phase:u8,f:F)->T {{
    let prev=PHASE.with(|p|{{let z=p.get();p.set(phase);z}});
    let out=f();
    PHASE.with(|p|p.set(prev));
    out
}}

pub fn tt_main_read(raw:Option<TTableResult>)->Option<TTableResult> {{
    TT_MAIN_PROBES.fetch_add(1,Ordering::Relaxed);
    let hit=raw.is_some();
    if hit {{ TT_MAIN_HITS.fetch_add(1,Ordering::Relaxed); }}
    if hit && mask_tt_main() {{
        TT_MAIN_MASKS.fetch_add(1,Ordering::Relaxed);
        None
    }} else {{
        raw
    }}
}}

pub fn pawn_read_should_mask(hit:bool)->bool {{
    let phase=PHASE.with(|p|p.get());
    match phase {{
        PHASE_MAIN => {{
            PAWN_MAIN_PROBES.fetch_add(1,Ordering::Relaxed);
            if hit {{ PAWN_MAIN_HITS.fetch_add(1,Ordering::Relaxed); }}
            let m=hit && mask_pawn_main();
            if m {{ PAWN_MAIN_MASKS.fetch_add(1,Ordering::Relaxed); }}
            m
        }},
        PHASE_QSEARCH => {{
            PAWN_Q_PROBES.fetch_add(1,Ordering::Relaxed);
            if hit {{ PAWN_Q_HITS.fetch_add(1,Ordering::Relaxed); }}
            let m=hit && mask_pawn_q();
            if m {{ PAWN_Q_MASKS.fetch_add(1,Ordering::Relaxed); }}
            m
        }},
        _ => {{
            PAWN_OTHER_PROBES.fetch_add(1,Ordering::Relaxed);
            false
        }}
    }}
}}

pub fn reset() {{
    for x in [&TT_MAIN_PROBES,&TT_MAIN_HITS,&TT_MAIN_MASKS,
              &PAWN_MAIN_PROBES,&PAWN_MAIN_HITS,&PAWN_MAIN_MASKS,
              &PAWN_Q_PROBES,&PAWN_Q_HITS,&PAWN_Q_MASKS,&PAWN_OTHER_PROBES] {{
        x.store(0,Ordering::Relaxed);
    }}
}}

pub fn report() {{
    println!(
        "info string c3x_p21_inanis_v1 mode={{}} tt_main_probes={{}} tt_main_hits={{}} tt_main_masks={{}} pawn_main_probes={{}} pawn_main_hits={{}} pawn_main_masks={{}} pawn_q_probes={{}} pawn_q_hits={{}} pawn_q_masks={{}} pawn_other_probes={{}}",
        mode(),
        TT_MAIN_PROBES.load(Ordering::Relaxed),
        TT_MAIN_HITS.load(Ordering::Relaxed),
        TT_MAIN_MASKS.load(Ordering::Relaxed),
        PAWN_MAIN_PROBES.load(Ordering::Relaxed),
        PAWN_MAIN_HITS.load(Ordering::Relaxed),
        PAWN_MAIN_MASKS.load(Ordering::Relaxed),
        PAWN_Q_PROBES.load(Ordering::Relaxed),
        PAWN_Q_HITS.load(Ordering::Relaxed),
        PAWN_Q_MASKS.load(Ordering::Relaxed),
        PAWN_OTHER_PROBES.load(Ordering::Relaxed)
    );
}}
''')

    p=root/"src/engine/search/runner.rs"
    t=p.read_text()
    ttold="match context.ttable.get(context.board.state.hash, ply) {"
    t=one(t,ttold,"match crate::c3x::tt_main_read(context.ttable.get(context.board.state.hash, ply)) {","TT_MAIN")
    ev="context.board.evaluate_fast(context.board.stm, &context.phtable, &mut context.stats)"
    nev=t.count(ev)
    if nev!=3:
        raise SystemExit(f"MAIN_EVAL_ANCHOR_COUNT {nev}")
    t=t.replace(ev,f"crate::c3x::with_phase(crate::c3x::PHASE_MAIN, || {ev})")
    p.write_text(t)

    p=root/"src/engine/qsearch/runner.rs"
    t=p.read_text()
    qev="context.board.evaluate(context.board.stm, &context.phtable, &mut context.stats)"
    t=one(t,qev,f"crate::c3x::with_phase(crate::c3x::PHASE_QSEARCH, || {qev})","Q_EVAL")
    p.write_text(t)

    p=root/"src/evaluation/pawns.rs"
    t=p.read_text()
    old="    match phtable.get(board.state.pawn_hash) {"
    new='''    let c3x_raw = phtable.get(board.state.pawn_hash);
    let c3x_mask = crate::c3x::pawn_read_should_mask(c3x_raw.is_some());
    match if c3x_mask { None } else { c3x_raw } {'''
    t=one(t,old,new,"PAWN_READ")
    p.write_text(t)

    p=root/"src/interface/uci.rs"
    t=p.read_text()
    t=one(t,
          "        let mut best_move = Move::default();",
          "        crate::c3x::reset();\n\n        let mut best_move = Move::default();",
          "UCI_RESET")
    t=one(t,
          "        if ponder && ponder_move.is_some() {",
          "        crate::c3x::report();\n\n        if ponder && ponder_move.is_some() {",
          "UCI_REPORT")
    p.write_text(t)

    manifest={
      "schema":"c3x-p21-inanis-native-adapter-v1",
      "scientific_stage":"C3X 0.7.0-G9.4-P21",
      "source_commit":LOCK,
      "language":"Rust",
      "variant":a.variant,
      "fixed_mode":fixed,
      "source_census":{
        "MAIN×SEARCH_TT":{"direct_semantic_read_sites":1,"instrumented":1},
        "QSEARCH×SEARCH_TT":{"direct_semantic_read_sites":0,"structural_zero":True},
        "PAWN_EVAL_CACHE":{"direct_semantic_read_sites":1,"instrumented":1},
        "MAIN evaluation phase wrappers":3,
        "QSEARCH evaluation phase wrappers":1
      },
      "occupied_cells":["MAIN×SEARCH_TT","MAIN×PAWN_EVAL_CACHE","QSEARCH×PAWN_EVAL_CACHE"],
      "complete_scoped_mediation":True,
      "native_rust":True,
      "forced_phase_homology":False
    }
    Path(a.manifest).parent.mkdir(parents=True,exist_ok=True)
    Path(a.manifest).write_text(json.dumps(manifest,indent=2,sort_keys=True)+"\n")
    print("P21_INANIS_PATCH_PASS",a.variant,head)

if __name__=="__main__":
    main()
