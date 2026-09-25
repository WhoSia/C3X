#!/usr/bin/env python3
import argparse,json,shutil,subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
LOCKS={
 "stockfish_19":"edb0d9db6731067ec50ce619ff372b463bc4dd5d",
 "berserk":"32628515050b83805bab4afa1026dd2bcaa93f55",
 "ethereal":"0e47e9b67f345c75eb965d9fb3e2493b6a11d09a",
}

def one(t,a,b,label):
 n=t.count(a)
 if n!=1: raise SystemExit(f"{label}_ANCHOR_{n}")
 return t.replace(a,b,1)

def get_head(root):
 return subprocess.check_output(["git","-C",str(root),"rev-parse","HEAD"],text=True).strip()

def install_inc(root,name):
 dst=root/"src"/"c3x_p29_trace.inc"
 shutil.copyfile(ROOT/"tools"/name,dst)
 return str(dst.relative_to(root))

def stockfish(root,policy):
 inc=install_inc(root,"p29_trace_stockfish.inc")
 p=root/"src"/"tt.cpp";t=p.read_text()
 t=one(t,'#include <vector>\n','#include <vector>\n#include <cstdio>\n#include <unordered_map>\n',"SF_HEADERS")
 anchor='''    RelaxedAtomic<i16>  eval16;
};
'''
 t=one(t,anchor,anchor+'\n#include "c3x_p29_trace.inc"\n',"SF_INCLUDE")

 old='''    // Overwrite less valuable entries (cheapest checks first)
    if (b == BOUND_EXACT || u16(k) != key16 || d - DEPTH_NONE + 2 * pv > depth8 - 4
        || relative_age(curr_generation))
    {'''
 new='''    // Overwrite less valuable entries (cheapest checks first)
    const bool c3xOverwrite =
      b == BOUND_EXACT || u16(k) != key16 || d - DEPTH_NONE + 2 * pv > depth8 - 4
      || relative_age(curr_generation);
    c3x_store(this,k,c3xOverwrite);
    if (c3xOverwrite)
    {'''
 t=one(t,old,new,"SF_STORE")

 t=one(t,'            depth8 = std::max(int(depth8) - 1, 0);',
       '            { depth8 = std::max(int(depth8) - 1, 0); if (!depth8) c3x_vacate(this); }',"SF_VACATE_SAVE")
 t=one(t,'    entry->depth8 = std::max(int(entry->depth8) - penalty, 0);',
       '    entry->depth8 = std::max(int(entry->depth8) - penalty, 0);\n    if (!entry->depth8) c3x_vacate(entry);',"SF_VACATE_PEN")
 t=one(t,'    for (usize i = 0; i < threadCount; ++i)\n        threads.wait_on_thread(i);',
       '    for (usize i = 0; i < threadCount; ++i)\n        threads.wait_on_thread(i);\n\n    c3x_trace_reset();',"SF_CLEAR")
 t=one(t,'void TranspositionTable::new_search() {\n    ++generation8;',
       'void TranspositionTable::new_search() {\n    c3x_begin_search();\n    ++generation8;',"SF_SEQ")

 if policy=="ON":
  old='''    TTEntry* const tte   = first_entry(key);
    const u16      key16 = u16(key);  // Use the low 16 bits as key inside the cluster

    for (int i = 0; i < ClusterSize; ++i)
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
        }'''
  new='''    const usize c3xBucket = mul_hi64(key, clusterCount);
    TTEntry* const tte   = first_entry(key);
    const u16      key16 = u16(key);  // Use the low 16 bits as key inside the cluster
    c3x_probe_start();

    for (int i = 0; i < ClusterSize; ++i)
        if (tte[i].key16 == key16)
        {
            c3x_loc(&tte[i],c3xBucket,i);
            // C3X P27: force age-on-hit ON while preserving bound/PV bits.
            const bool occupied = tte[i].is_occupied();
            c3x_probe_result(&tte[i],key,occupied);
            if (occupied)
            {
                const u8 c3xOld=u8(tte[i].genBound8);
                const u8 c3xNew=u8((c3xOld & u8(~GENERATION_MASK)) | generation8);
                tte[i].genBound8=c3xNew;
                c3x_age(&tte[i],key,c3xOld,c3xNew);
            }
            // This gap is the main place for read races.
            // After `read()` completes that copy is final, but may be self-inconsistent.
            return {occupied, tte[i].read(), TTWriter(&tte[i])};
        }'''
 else:
  old='''    TTEntry* const tte   = first_entry(key);
    const u16      key16 = u16(key);  // Use the low 16 bits as key inside the cluster

    for (int i = 0; i < ClusterSize; ++i)
        if (tte[i].key16 == key16)
            // This gap is the main place for read races.
            // After `read()` completes that copy is final, but may be self-inconsistent.
            return {tte[i].is_occupied(), tte[i].read(), TTWriter(&tte[i])};'''
  new='''    const usize c3xBucket = mul_hi64(key, clusterCount);
    TTEntry* const tte   = first_entry(key);
    const u16      key16 = u16(key);  // Use the low 16 bits as key inside the cluster
    c3x_probe_start();

    for (int i = 0; i < ClusterSize; ++i)
        if (tte[i].key16 == key16)
        {
            c3x_loc(&tte[i],c3xBucket,i);
            const bool occupied=tte[i].is_occupied();
            c3x_probe_result(&tte[i],key,occupied);
            // This gap is the main place for read races.
            // After `read()` completes that copy is final, but may be self-inconsistent.
            return {occupied, tte[i].read(), TTWriter(&tte[i])};
        }'''
 t=one(t,old,new,"SF_PROBE")
 t=one(t,'    return {false, TTData{Move::none(), VALUE_NONE, VALUE_NONE, DEPTH_NONE, BOUND_NONE, false},\n            TTWriter(replace)};',
       '    c3x_loc(replace,c3xBucket,int(replace-tte));\n    return {false, TTData{Move::none(), VALUE_NONE, VALUE_NONE, DEPTH_NONE, BOUND_NONE, false},\n            TTWriter(replace)};',"SF_MISS")
 p.write_text(t)
 return {"include":inc,"files":["src/tt.cpp"],"shadow":"pointer-indexed full-key map"}

def berserk(root,policy):
 inc=install_inc(root,"p29_trace_berserk.inc")
 h=root/"src"/"transposition.h";t=h.read_text()
 proto='''extern TTTable TT;

void c3x_tt_trace_probe_start(uint64_t hash);
void c3x_tt_trace_probe_result(uint64_t hash, TTEntry* e, int hit);
void c3x_tt_trace_store(TTEntry* e, uint64_t hash, int commit);
void c3x_tt_trace_age(TTEntry* e, uint64_t requested, uint8_t oldv, uint8_t newv);
'''
 t=one(t,'extern TTTable TT;\n',proto,"BE_PROTO")
 t=one(t,'  const uint16_t shortHash = (uint16_t) hash;\n\n  for (int i = 0; i < BUCKET_SIZE; i++) {',
       '  const uint16_t shortHash = (uint16_t) hash;\n  c3x_tt_trace_probe_start(hash);\n\n  for (int i = 0; i < BUCKET_SIZE; i++) {',"BE_START")
 t=one(t,'      *hit = !!bucket[i].depth;\n\n      if (*hit) {',
       '      *hit = !!bucket[i].depth;\n      c3x_tt_trace_probe_result(hash,&bucket[i],*hit);\n\n      if (*hit) {',"BE_RESULT")
 t=one(t,'  return replace;\n}\n\nINLINE void TTPut',
       '  c3x_tt_trace_probe_result(hash,replace,0);\n  return replace;\n}\n\nINLINE void TTPut',"BE_MISS")
 old='''  if ((bound == BOUND_EXACT) || shortHash != tt->hash || depth + 4 > TTDepth(tt) || TTAge(tt)) {
    tt->hash       = shortHash;'''
 new='''  int c3xWrite = (bound == BOUND_EXACT) || shortHash != tt->hash || depth + 4 > TTDepth(tt) || TTAge(tt);
  c3x_tt_trace_store(tt,hash,c3xWrite);
  if (c3xWrite) {
    tt->hash       = shortHash;'''
 t=one(t,old,new,"BE_STORE")
 if policy=="ON":
  old='''        bucket[i].agePvBound =
          (uint8_t) (TT.age | (bucket[i].agePvBound & (PV_MASK | BOUND_MASK)));
        *hashMove = TTMove(&bucket[i]);'''
  new='''        {
          uint8_t c3xOld=bucket[i].agePvBound;
          uint8_t c3xNew=(uint8_t) (TT.age | (bucket[i].agePvBound & (PV_MASK | BOUND_MASK)));
          bucket[i].agePvBound=c3xNew;
          c3x_tt_trace_age(&bucket[i],hash,c3xOld,c3xNew);
        }
        *hashMove = TTMove(&bucket[i]);'''
  t=one(t,old,new,"BE_AGE")
 h.write_text(t)

 c=root/"src"/"transposition.c";u=c.read_text()
 u=one(u,'TTTable TT = {0};\n','TTTable TT = {0};\n#include "c3x_p29_trace.inc"\n',"BE_INCLUDE")
 u=one(u,'  TT.count   = size / sizeof(TTBucket);\n\n  TTClear();',
       '  TT.count   = size / sizeof(TTBucket);\n  c3x_trace_alloc(TT.count * BUCKET_SIZE);\n\n  TTClear();',"BE_ALLOC")
 u=one(u,'  for (int i = 0; i < Threads.count; i++)\n    ThreadWaitUntilSleep(Threads.threads[i]);\n}',
       '  for (int i = 0; i < Threads.count; i++)\n    ThreadWaitUntilSleep(Threads.threads[i]);\n  c3x_trace_reset_common(TT.count * BUCKET_SIZE);\n}',"BE_CLEAR")
 u=one(u,'inline void TTUpdate() {\n  TT.age += AGE_INC;\n}',
       'inline void TTUpdate() {\n  c3x_trace_begin_search();\n  TT.age += AGE_INC;\n}',"BE_SEQ")
 c.write_text(u)
 return {"include":inc,"files":["src/transposition.h","src/transposition.c"],"shadow":"parallel full-key/store-seq arrays"}

def ethereal(root,policy):
 inc=install_inc(root,"p29_trace_ethereal.inc")
 p=root/"src"/"transposition.c";t=p.read_text()
 t=one(t,'#include <pthread.h>\n','#include <pthread.h>\n#include <stdio.h>\n',"ET_STDIO")
 t=one(t,'TTable Table; // Global Transposition Table\n','TTable Table; // Global Transposition Table\n#include "c3x_p29_trace.inc"\n',"ET_INCLUDE")
 t=one(t,'void tt_update() { Table.generation += TT_MASK_BOUND + 1; }',
       'void tt_update() { c3x_trace_begin_search(); Table.generation += TT_MASK_BOUND + 1; }',"ET_SEQ")
 t=one(t,'    Table.hashMask = (1ull << keySize) - 1u;\n\n    // Clear the table',
       '    Table.hashMask = (1ull << keySize) - 1u;\n    c3x_trace_alloc((Table.hashMask + 1) * TT_BUCKET_NB);\n\n    // Clear the table',"ET_ALLOC")
 t=one(t,'    TTEntry *slots = Table.buckets[hash & Table.hashMask].slots;\n\n    for (int i = 0; i < TT_BUCKET_NB; i++) {',
       '    TTEntry *slots = Table.buckets[hash & Table.hashMask].slots;\n    c3x_et_probe_start();\n\n    for (int i = 0; i < TT_BUCKET_NB; i++) {',"ET_PROBE_START")
 if policy=="ON":
  old='''        if (slots[i].hash16 == hash16) {

            slots[i].generation = Table.generation | (slots[i].generation & TT_MASK_BOUND);

            *move  = slots[i].move;'''
  new='''        if (slots[i].hash16 == hash16) {

            const int c3xOccupied=(slots[i].generation & TT_MASK_BOUND) != BOUND_NONE;
            c3x_et_probe_result(hash,&slots[i],1,c3xOccupied);
            {
                uint8_t c3xOld=slots[i].generation;
                uint8_t c3xNew=Table.generation | (slots[i].generation & TT_MASK_BOUND);
                slots[i].generation=c3xNew;
                c3x_et_age(&slots[i],hash,c3xOld,c3xNew);
            }

            *move  = slots[i].move;'''
 else:
  old='''        if (slots[i].hash16 == hash16) {

            // C3X P27: force age-on-hit OFF; all read semantics remain unchanged.

            *move  = slots[i].move;'''
  new='''        if (slots[i].hash16 == hash16) {

            // C3X P27: force age-on-hit OFF; all read semantics remain unchanged.
            const int c3xOccupied=(slots[i].generation & TT_MASK_BOUND) != BOUND_NONE;
            c3x_et_probe_result(hash,&slots[i],1,c3xOccupied);

            *move  = slots[i].move;'''
 t=one(t,old,new,"ET_PROBE")
 old='''    if (   bound != BOUND_EXACT
        && hash16 == replace->hash16
        && depth < replace->depth - 2)
        return;

    // Don't overwrite a move'''
 new='''    int c3xWrite = !(bound != BOUND_EXACT
        && hash16 == replace->hash16
        && depth < replace->depth - 2);
    c3x_et_store(replace,hash,c3xWrite);
    if (!c3xWrite)
        return;

    // Don't overwrite a move'''
 t=one(t,old,new,"ET_STORE")
 t=one(t,'    for (int i = 1; i < nworkers; i++)\n        pthread_join(pthreads[i], NULL);\n}',
       '    for (int i = 1; i < nworkers; i++)\n        pthread_join(pthreads[i], NULL);\n    c3x_trace_reset_common((Table.hashMask + 1) * TT_BUCKET_NB);\n}',"ET_CLEAR")
 p.write_text(t)
 return {"include":inc,"files":["src/transposition.c"],"shadow":"parallel full-key/store-seq arrays"}

def main():
 ap=argparse.ArgumentParser()
 ap.add_argument("--root",required=True)
 ap.add_argument("--engine",choices=LOCKS,required=True)
 ap.add_argument("--policy",choices=["OFF","ON"],required=True)
 ap.add_argument("--manifest",required=True)
 a=ap.parse_args();r=Path(a.root)
 h=get_head(r)
 if h!=LOCKS[a.engine]:raise SystemExit(f"SOURCE_LOCK {h}")
 edit={"stockfish_19":stockfish,"berserk":berserk,"ethereal":ethereal}[a.engine](r,a.policy)
 subprocess.check_call(["git","diff","--check"],cwd=r)
 m={"schema":"c3x-p29-tttrace-variant-v1","scientific_stage":"C3X 0.7.0-G9.4-P29",
    "engine":a.engine,"source_commit":h,"age_policy":a.policy,
    "trace_semantics":"full-key shadow + search-sequence provenance + exact replacement/signature-collision/age-write events",
    "graph_seq_env":"C3X_TT_GRAPH_SEQ","semantic_intervention":False,"edit":edit}
 Path(a.manifest).parent.mkdir(parents=True,exist_ok=True)
 Path(a.manifest).write_text(json.dumps(m,indent=2,sort_keys=True)+"\n")
 print(json.dumps(m,sort_keys=True))

if __name__=="__main__":main()
