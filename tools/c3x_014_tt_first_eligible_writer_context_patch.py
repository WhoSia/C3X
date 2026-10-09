#!/usr/bin/env python3
"""SF16 original TT full-key last-writer context and first eligible-return triad.

Requires already-built C3X 0.14 ONE_MAIN + full-key slot sidecar. Adds passive
first-returnable event observation in OFF/ONE_MAIN/MAIN. Separates TT no-op
saves from actual move-only field writes. No native TTEntry layout changes.
"""
import argparse,hashlib,json
from pathlib import Path

def change(s,old,new,tag):
    n=s.count(old)
    if n!=1:raise RuntimeError("C3X014_ELIGIBLE_ANCHOR_"+tag+"_"+str(n))
    return s.replace(old,new,1)

def patch(root):
    root=Path(root)
    paths={z:root/"src"/z for z in ("tt.h","tt.cpp","search.cpp")}
    raw={k:v.read_bytes() for k,v in paths.items()}
    h=raw["tt.h"].decode();cpp=raw["tt.cpp"].decode();s=raw["search.cpp"].decode()
    if not all(q in s for q in ("producer_full_key","first_blocked_key","ONE_MAIN")) or "c3x014_tt_lookup_lineage" not in cpp:
        raise RuntimeError("REQUIRES_PREVIOUS_NATIVE_FULLKEY_PROVENANCE")
    if "first_eligible_key" in s:raise RuntimeError("MATCHED_EVENT_PATCH_ALREADY_APPLIED")
    h=change(h,
       "  int full_overwrites=0, slot_reuse_events=0, last_write_was_move_only=0;",
       "  int full_overwrites=0, slot_reuse_events=0, last_write_was_move_only=0;\n"
       "  int writer_ply=-1, writer_saved_depth=0, writer_saved_bound=0, writer_saved_tt_value=0;",
       "HEADER_WRITER_CONTEXT")
    h=change(h,
       "  std::uint64_t save_calls=0, full_field_writes=0, move_only_writes=0;",
       "  std::uint64_t save_calls=0, full_field_writes=0, move_only_writes=0, no_field_writes=0;",
       "HEADER_NOOP_CENSUS")
    h=change(h,
       "void c3x014_tt_save_labeled(TTEntry*, int producer_kind, Key, Value, bool, Bound, Depth, Move, Value);",
       "void c3x014_tt_save_labeled(TTEntry*, int producer_kind, int writer_ply, Key, Value, bool, Bound, Depth, Move, Value);",
       "HEADER_SIGNATURE")
    cpp=change(cpp,
       "  int tag=0, touch_tag=0, full_overwrites=0, reuse_events=0;",
       "  int tag=0, touch_tag=0, full_overwrites=0, reuse_events=0;\n"
       "  int writer_ply=-1, writer_saved_depth=0, writer_saved_bound=0, writer_saved_tt_value=0;",
       "CPP_CONTEXT_FIELDS")
    cpp=change(cpp,
       "static int c3x014_active_writer_label=0;",
       "static int c3x014_active_writer_label=0;\nstatic int c3x014_active_writer_ply=-1;",
       "CPP_WRITER_PLY")
    cpp=change(cpp,
       "  c3x014_active_writer_label=0;\n}",
       "  c3x014_active_writer_label=0;\n  c3x014_active_writer_ply=-1;\n}",
       "CPP_RESET_PLY")
    cpp=change(cpp,
       "void c3x014_record_saved_slot(const TTEntry* p, Key k, bool full) {",
       "void c3x014_record_saved_slot(const TTEntry* p, Key k, bool full, bool move_written, Value v, Bound b, Depth d) {",
       "CPP_RECORD_SIGNATURE")
    cpp=change(cpp,
       "    r.tag=c3x014_active_writer_label;\n    r.write_sequence=c3x014_tt_totals.save_calls;",
       "    r.tag=c3x014_active_writer_label;\n"
       "    r.writer_ply=c3x014_active_writer_ply;\n"
       "    r.writer_saved_depth=int(d);\n    r.writer_saved_bound=int(b);\n"
       "    r.writer_saved_tt_value=int(v);\n"
       "    r.write_sequence=c3x014_tt_totals.save_calls;",
       "CPP_RECORD_CONTEXT")
    cpp=change(cpp,
       "  } else {\n    ++c3x014_tt_totals.move_only_writes;\n  }\n}",
       "  } else if (move_written) {\n    ++c3x014_tt_totals.move_only_writes;\n"
       "  } else {\n    ++c3x014_tt_totals.no_field_writes;\n  }\n}",
       "CPP_NO_OP_DISPOSITION")
    cpp=change(cpp,
       "void c3x014_tt_save_labeled(TTEntry* e, int tag, Key k, Value v, bool pv, Bound b,\n"
       "                            Depth d, Move m, Value ev) {\n"
       "  const int old=c3x014_active_writer_label;\n"
       "  c3x014_active_writer_label=tag;\n"
       "  e->save(k,v,pv,b,d,m,ev);\n"
       "  c3x014_active_writer_label=old;\n}",
       "void c3x014_tt_save_labeled(TTEntry* e, int tag, int writer_ply, Key k, Value v, bool pv, Bound b,\n"
       "                            Depth d, Move m, Value ev) {\n"
       "  const int old=c3x014_active_writer_label;\n"
       "  const int old_ply=c3x014_active_writer_ply;\n"
       "  c3x014_active_writer_label=tag;\n"
       "  c3x014_active_writer_ply=writer_ply;\n"
       "  e->save(k,v,pv,b,d,m,ev);\n"
       "  c3x014_active_writer_label=old;\n"
       "  c3x014_active_writer_ply=old_ply;\n}",
       "CPP_LABEL_WRAPPER")
    cpp=change(cpp,
       "  x.last_write_was_move_only=int(r.last_move_only);\n",
       "  x.last_write_was_move_only=int(r.last_move_only);\n"
       "  x.writer_ply=r.writer_ply;\n"
       "  x.writer_saved_depth=r.writer_saved_depth;\n"
       "  x.writer_saved_bound=r.writer_saved_bound;\n"
       "  x.writer_saved_tt_value=r.writer_saved_tt_value;\n",
       "CPP_SNAPSHOT_FIELDS")
    cpp=change(cpp,
       "  if (m || (uint16_t)k != key16)\n      move16 = (uint16_t)m;",
       "  const bool c3x014_move_field_assigned=(m || (uint16_t)k != key16);\n"
       "  if (c3x014_move_field_assigned)\n      move16 = (uint16_t)m;",
       "CPP_MOVE_ONLY_ASSIGNMENT")
    cpp=change(cpp,
       "  c3x014_record_saved_slot(this,k,c3x014_full_field_write);",
       "  c3x014_record_saved_slot(this,k,c3x014_full_field_write,c3x014_move_field_assigned,v,b,d);",
       "CPP_SAVE_CLASSIFICATION")
    if s.count("c3x014_tt_save_labeled(tte, ")!=6:
        raise RuntimeError("SIX_SF16_TAGGED_TT_WRITERS_NOT_FOUND")
    # All six original SF16 saves have a source-local ss pointer, including qsearch.
    for kind in range(1,7):
        token="c3x014_tt_save_labeled(tte, "+str(kind)+", "
        s=change(s,token,"c3x014_tt_save_labeled(tte, "+str(kind)+", ss->ply, ","PASS_PLY_"+str(kind))
    s=change(s,
       '      int first_blocked_ply=-1, first_blocked_depth=-1;',
       '      int first_blocked_ply=-1, first_blocked_depth=-1;\n'
       '      std::uint64_t first_eligible_key=0, first_eligible_saved_fullkey=0;\n'
       '      int first_eligible_ply=-1,first_eligible_depth=-1,first_eligible_bound=-1;\n'
       '      int first_eligible_tt_value=0,first_eligible_beta=0,first_eligible_writer_tag=0;\n'
       '      int first_eligible_fullkey_match=0,first_eligible_writer_ply=-1;\n'
       '      int first_writer_ply=-1,first_writer_saved_depth=0,first_writer_saved_bound=0,first_writer_saved_tt_value=0;',
       "SEARCH_CONTEXT_STRUCT")
    s=change(s,
       '                    c3x014_trace.first_previous_writer_key=producer.previous_full_key;',
       '                    c3x014_trace.first_previous_writer_key=producer.previous_full_key;\n'
       '                    c3x014_trace.first_writer_ply=producer.writer_ply;\n'
       '                    c3x014_trace.first_writer_saved_depth=producer.writer_saved_depth;\n'
       '                    c3x014_trace.first_writer_saved_bound=producer.writer_saved_bound;\n'
       '                    c3x014_trace.first_writer_saved_tt_value=producer.writer_saved_tt_value;',
       "SEARCH_FIRST_BLOCK_WRITER_CONTEXT")
    enter="""            if ((c3x_ep9_mode & 1) || (c3x_ep9_mode == 4 && c3x_ep9_stats.main_cutoff_blocked == 0))"""
    replacement="""            if (c3x014_trace.first_eligible_ply < 0)
            {
                c3x014_trace.first_eligible_key=posKey;
                c3x014_trace.first_eligible_ply=ss->ply;
                c3x014_trace.first_eligible_depth=depth;
                c3x014_trace.first_eligible_bound=int(tte->bound());
                c3x014_trace.first_eligible_tt_value=int(ttValue);
                c3x014_trace.first_eligible_beta=int(beta);
                const auto writer=c3x014_tt_lookup_lineage(tte,posKey);
                c3x014_trace.first_eligible_saved_fullkey=writer.last_full_key;
                c3x014_trace.first_eligible_writer_tag=writer.producer_kind;
                c3x014_trace.first_eligible_fullkey_match=writer.full_key_exact;
                c3x014_trace.first_eligible_writer_ply=writer.writer_ply;
            }
"""+enter
    s=change(s,enter,replacement,"FIRST_ELIGIBLE_BEFORE_OFF_MAIN_DECISION")
    s=change(s,
       '      << " producer_previous_full_key=" << a.first_previous_writer_key',
       '      << " producer_previous_full_key=" << a.first_previous_writer_key\n'
       '      << " producer_writer_ply=" << a.first_writer_ply\n'
       '      << " producer_writer_saved_depth=" << a.first_writer_saved_depth\n'
       '      << " producer_writer_saved_bound=" << a.first_writer_saved_bound\n'
       '      << " producer_writer_saved_tt_value=" << a.first_writer_saved_tt_value\n'
       '      << " first_eligible_key=" << a.first_eligible_key\n'
       '      << " first_eligible_ply=" << a.first_eligible_ply\n'
       '      << " first_eligible_depth=" << a.first_eligible_depth\n'
       '      << " first_eligible_bound=" << a.first_eligible_bound\n'
       '      << " first_eligible_tt_value=" << a.first_eligible_tt_value\n'
       '      << " first_eligible_beta=" << a.first_eligible_beta\n'
       '      << " first_eligible_writer_tag=" << a.first_eligible_writer_tag\n'
       '      << " first_eligible_saved_fullkey=" << a.first_eligible_saved_fullkey\n'
       '      << " first_eligible_fullkey_match=" << a.first_eligible_fullkey_match\n'
       '      << " first_eligible_writer_ply=" << a.first_eligible_writer_ply',
       "TRACE_FIRST_ELIGIBLE_OUTPUT")
    s=change(s,
       '       << " move_only=" << t.move_only_writes',
       '       << " move_only=" << t.move_only_writes\n       << " no_op=" << t.no_field_writes',
       "TRACE_NOOP_OUTPUT")
    patched={"tt.h":h.encode(),"tt.cpp":cpp.encode(),"search.cpp":s.encode()}
    for k,v in patched.items():paths[k].write_bytes(v)
    return {"schema":"c3x-014-matched-first-eligible-and-source-writer-context-v1",
       "upstream_stockfish16":"sf_16 68e1e9b3811e16cad014b590d7443b9063b3eb52",
       "requires":["original EP9 TT paths","true native completedDepth","ONE_MAIN","full64 last physical slot writer sidecar"],
       "native_TTEntry_layout_changed":False,
       "added_fields":["first eligible actual TT return event prior to action across OFF/ONE_MAIN/MAIN",
                       "last successful TT saved writer ply/depth/bound/value",
                       "full field vs actual move-field vs no-field save calls"],
       "original_sha256":{k:hashlib.sha256(v).hexdigest() for k,v in raw.items()},
       "patched_sha256":{k:hashlib.sha256(v).hexdigest() for k,v in patched.items()},
       "science_limit":"Pre-return observations must compare equal across modes and exact previous UCI outcomes; writer/consumer provenance is not an identified independent LMR/history/NNUE causal mediator"}

def main():
    a=argparse.ArgumentParser()
    a.add_argument("--source",required=True);a.add_argument("--out-manifest",required=True)
    x=a.parse_args()
    r=patch(x.source);dest=Path(x.out_manifest);dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_text(json.dumps(r,indent=2)+"\n")
    print("C3X014_FIRST_ELIGIBLE_TRIAD_AND_WRITER_CONTEXT_PATCH_PASS",json.dumps(r["patched_sha256"]),flush=True)
if __name__=="__main__":main()
