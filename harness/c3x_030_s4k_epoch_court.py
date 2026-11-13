#!/usr/bin/env python3
"""C3X 0.30 S4-K source-only trial-boundary and TT-cutoff receipt court.

Logs distinguish true UCI go epochs 1 and 2, preserve all source cutoff
receipts (max 8 per epoch), and separately report *total* source cutoff count.
The data can establish coverage of that ONE return site, not whole search-tree
or counterfactual causal mediation. No invocation-ID joining across runs.
"""
import re
from c3x_030_s4j_state_alignment import compare as compare_states

BEGIN=re.compile(r"^C3X_S4K_GO_BEGIN epoch=(\d+) cap_per_go=8$")
END=re.compile(r"^C3X_S4K_GO_END epoch=(\d+) source_cutoff_total=(\d+)$")
EVENT=re.compile(r"^C3X_S4I_TT_CUTOFF ordinal=(\d+) epoch=(\d+) id=(\d+) parent=(\d+) "
                 r"key=(\d+) ply=1 search_depth=(-?\d+) alpha=(-?\d+) beta=(-?\d+) "
                 r"pv=([01]) cutnode=([01]) return_value=(-?\d+)$")
TRIALS=(1,2)

def parse(stderr, frozen_key):
    events={n:[] for n in TRIALS}
    counters={}
    started=[]
    finished=[]
    active=None
    for line in stderr:
        if line.startswith("C3X_S4K_GO_BEGIN"):
            m=BEGIN.fullmatch(line)
            if not m or active is not None:
                raise ValueError("S4K_GO_BEGIN_MALFORMED_OR_NESTED")
            epoch=int(m.group(1))
            if epoch not in TRIALS or epoch in started or len(started)+1!=epoch:
                raise ValueError("S4K_GO_BEGIN_NOT_SEQUENTIAL")
            started.append(epoch);active=epoch
        elif line.startswith("C3X_S4I_TT_CUTOFF"):
            m=EVENT.fullmatch(line)
            if not m:raise ValueError("S4K_TT_EVENT_MALFORMED")
            ordinal,epoch,ident,parent,key,depth,alpha,beta,pv,cutnode,value=map(int,m.groups())
            if (active!=epoch or key!=int(frozen_key) or ordinal!=len(events[epoch])
                or ordinal>=8 or ident<=0 or parent<0 or alpha>=beta):
                raise ValueError("S4K_TT_EVENT_IDENTITY_OR_WINDOW")
            events[epoch].append({"ordinal":ordinal,"invocation_id":str(ident),
                "parent_id":str(parent),
                "state":[key,depth,alpha,beta,1,pv,cutnode],
                "return_value":value})
        elif line.startswith("C3X_S4K_GO_END"):
            m=END.fullmatch(line)
            if not m or active is None or int(m.group(1))!=active:
                raise ValueError("S4K_GO_END_MALFORMED_OR_UNPAIRED")
            total=int(m.group(2))
            if total < len(events[active]) or len(events[active])!=min(total,8):
                raise ValueError("S4K_TT_LOG_TOTAL_DISAGREES")
            counters[active]=total
            finished.append(active);active=None
        elif line.startswith("C3X_S4K_"):
            raise ValueError("S4K_UNKNOWN_SOURCE_EVENT")
    if started!=list(TRIALS) or finished!=list(TRIALS) or active is not None:
        raise ValueError("S4K_MISSING_GO_BOUNDARY")
    return {
      "trials":{str(n):{"events":events[n],"observed":len(events[n]),
          "actual_source_cutoffs_at_this_return_site":counters[n],
          "right_censored":counters[n]>8,
          "coverage_complete":counters[n]<=8,
          "site_scope_only":True} for n in TRIALS},
      "all_cutoff_events_total":sum(counters.values()),
      "logged_cutoff_events_total":sum(len(v) for v in events.values()),
      "full_search_tree_mediation_proven":False}

def compare_by_go(sham, treated):
    trials={}
    for epoch in TRIALS:
        key=str(epoch)
        if key not in sham["trials"] or key not in treated["trials"]:
            raise ValueError("S4K_EPOCH_MISMATCH")
        trials[key]=compare_states(sham["trials"][key],treated["trials"][key])
    return {"per_epoch":trials,
        "shared_states_total":sum(v["shared_candidate_state_count"] for v in trials.values()),
        "unambiguous_candidates_total":sum(len(v["unique_candidate_states"]) for v in trials.values()),
        "unambiguous_changed_values_total":sum(sum(z["value_diff"]!=0 for z in v["unique_candidate_states"]) for v in trials.values()),
        "ambiguous_candidates_total":sum(len(v["ambiguous_repeated_states"]) for v in trials.values()),
        "any_site_log_censored":any(v["any_right_censoring"] for v in trials.values()),
        "cross_process_invocation_identity_proven":False,
        "full_tt_to_root_causal_mediation_proven":False}
