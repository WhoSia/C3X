#!/usr/bin/env python3
import argparse,json,subprocess
from pathlib import Path

LOCKS={
 "stockfish_19":"edb0d9db6731067ec50ce619ff372b463bc4dd5d",
 "berserk":"32628515050b83805bab4afa1026dd2bcaa93f55",
 "ethereal":"0e47e9b67f345c75eb965d9fb3e2493b6a11d09a",
}
NATIVE={"stockfish_19":"OFF","berserk":"OFF","ethereal":"ON"}

def one(t,a,b,label):
 n=t.count(a)
 if n!=1: raise SystemExit(f"{label}_ANCHOR_{n}")
 return t.replace(a,b,1)

def head(root):
 return subprocess.check_output(["git","-C",str(root),"rev-parse","HEAD"],text=True).strip()

def patch_stockfish(root,policy):
 p=root/"src/tt.cpp";t=p.read_text()
 anchor="""    for (int i = 0; i < ClusterSize; ++i)
        if (tte[i].key16 == key16)
            // This gap is the main place for read races.
            // After `read()` completes that copy is final, but may be self-inconsistent.
            return {tte[i].is_occupied(), tte[i].read(), TTWriter(&tte[i])};
"""
 if policy=="ON":
  repl="""    for (int i = 0; i < ClusterSize; ++i)
        if (tte[i].key16 == key16)
        {
            // C3X P27: force age-on-hit ON while preserving bound/PV bits.
            const bool occupied = tte[i].is_occupied();
            if (occupied)
                tte[i].genBound8 =
                  u8((u8(tte[i].genBound8) & u8(~GENERATION_MASK)) | generation8);
            // This gap is the main place for read races.
            // After `read()` completes that copy is final, but may be self-inconsistent.
            return {occupied, tte[i].read(), TTWriter(&tte[i])};
        }
"""
  t=one(t,anchor,repl,"STOCKFISH")
 else:
  if t.count(anchor)!=1: raise SystemExit("STOCKFISH_NATIVE_ANCHOR")
 p.write_text(t)
 return {"file":"src/tt.cpp","edit":"force_refresh_on_hit" if policy=="ON" else "native_no_refresh"}

def patch_berserk(root,policy):
 p=root/"src/transposition.h";t=p.read_text()
 anchor="""      *hit = !!bucket[i].depth;

      if (*hit) {
        *hashMove = TTMove(&bucket[i]);
"""
 if policy=="ON":
  repl="""      *hit = !!bucket[i].depth;

      if (*hit) {
        // C3X P27: force age-on-hit ON, preserving PV and bound bits.
        bucket[i].agePvBound =
          (uint8_t) (TT.age | (bucket[i].agePvBound & (PV_MASK | BOUND_MASK)));
        *hashMove = TTMove(&bucket[i]);
"""
  t=one(t,anchor,repl,"BERSERK")
 else:
  if t.count(anchor)!=1: raise SystemExit("BERSERK_NATIVE_ANCHOR")
 p.write_text(t)
 return {"file":"src/transposition.h","edit":"force_refresh_on_hit" if policy=="ON" else "native_no_refresh"}

def patch_ethereal(root,policy):
 p=root/"src/transposition.c";t=p.read_text()
 anchor="""            slots[i].generation = Table.generation | (slots[i].generation & TT_MASK_BOUND);

            *move  = slots[i].move;
"""
 if policy=="OFF":
  repl="""            // C3X P27: force age-on-hit OFF; all read semantics remain unchanged.

            *move  = slots[i].move;
"""
  t=one(t,anchor,repl,"ETHEREAL")
 else:
  if t.count(anchor)!=1: raise SystemExit("ETHEREAL_NATIVE_ANCHOR")
 p.write_text(t)
 return {"file":"src/transposition.c","edit":"force_no_refresh_on_hit" if policy=="OFF" else "native_refresh"}

def main():
 ap=argparse.ArgumentParser()
 ap.add_argument("--root",required=True)
 ap.add_argument("--engine",choices=LOCKS,required=True)
 ap.add_argument("--policy",choices=["OFF","ON"],required=True)
 ap.add_argument("--manifest",required=True)
 a=ap.parse_args();r=Path(a.root)
 h=head(r)
 if h!=LOCKS[a.engine]:raise SystemExit(f"SOURCE_LOCK {h}")
 edit={"stockfish_19":patch_stockfish,"berserk":patch_berserk,"ethereal":patch_ethereal}[a.engine](r,a.policy)
 subprocess.check_call(["git","diff","--check"],cwd=r)
 m={
  "schema":"c3x-p27-age-policy-variant-v1",
  "scientific_stage":"C3X 0.7.0-G9.4-P27",
  "engine":a.engine,
  "source_commit":h,
  "coordinate":"probe_refreshes_age_on_hit",
  "policy":a.policy,
  "native_policy":NATIVE[a.engine],
  "native_equivalent":a.policy==NATIVE[a.engine],
  "preserved_semantics":["key","depth","move","value","evaluation","bound","pv"],
  "edit":edit
 }
 Path(a.manifest).parent.mkdir(parents=True,exist_ok=True)
 Path(a.manifest).write_text(json.dumps(m,indent=2,sort_keys=True)+"\n")
 print(json.dumps(m,sort_keys=True))

if __name__=="__main__":main()
