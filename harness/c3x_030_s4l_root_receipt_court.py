#!/usr/bin/env python3
"""S4-L: strict source-side root-score decision receipts, no false causal joins.

Each receipt is a completed root branch evaluation prior to RootMove update,
not evidence that a particular TT mask was responsible. Trial boundaries are
authentic UCI go epochs. Total root evaluations count past the 512 receipt cap.
"""
import re
from c3x_030_s4k_epoch_court import compare_by_go

BEGIN=re.compile(r"^C3X_S4K_GO_BEGIN epoch=(\d+) cap_per_go=8$")
END=re.compile(r"^C3X_S4K_GO_END epoch=(\d+) source_cutoff_total=(\d+) root_score_total=(\d+)$")
ROOT=re.compile(r"^C3X_S4L_ROOT_SCORE ordinal=(\d+) epoch=(\d+) root_move_raw=(\d+) "
                r"value=(-?\d+) old_best=(-?\d+) alpha=(-?\d+) beta=(-?\d+) "
                r"move_count=(\d+) will_update_best=([01]) will_update_root_pv=([01]) depth=(-?\d+)$")
TT=re.compile(r"^C3X_S4I_TT_CUTOFF ordinal=(\d+) epoch=(\d+) id=(\d+) parent=(\d+) "
              r"key=(\d+) ply=1 search_depth=(-?\d+) alpha=(-?\d+) beta=(-?\d+) "
              r"pv=([01]) cutnode=([01]) return_value=(-?\d+)$")

def parse(stderr,key):
    events={1:[],2:[]}
    roots={1:[],2:[]}
    totals={}
    active=None
    begins=[]
    ends=[]
    for line in stderr:
        if line.startswith("C3X_S4K_GO_BEGIN"):
            m=BEGIN.fullmatch(line)
            if m is None or active is not None:raise ValueError("S4L_BAD_BEGIN")
            epoch=int(m.group(1))
            if epoch not in (1,2) or len(begins)+1!=epoch:
                raise ValueError("S4L_NONSEQUENTIAL_EPOCH")
            active=epoch;begins.append(epoch)
        elif line.startswith("C3X_S4I_TT_CUTOFF"):
            m=TT.fullmatch(line)
            if m is None:raise ValueError("S4L_MALFORMED_TT")
            ordinal,epoch,ident,parent,ttkey,depth,alpha,beta,pv,cutnode,value=map(int,m.groups())
            if (active!=epoch or ordinal!=len(events[epoch]) or ordinal>=8 or
                ttkey!=int(key) or alpha>=beta or ident<=0):
                raise ValueError("S4L_INVALID_TT_PROVENANCE")
            events[epoch].append({"ordinal":ordinal,"invocation_id":str(ident),
                "parent_id":str(parent),"state":[ttkey,depth,alpha,beta,1,pv,cutnode],
                "return_value":value})
        elif line.startswith("C3X_S4L_ROOT_SCORE"):
            m=ROOT.fullmatch(line)
            if m is None:raise ValueError("S4L_BAD_ROOT_RECEIPT")
            ordinal,epoch,move,value,old,alpha,beta,count,updated,updatedpv,depth=map(int,m.groups())
            if (active!=epoch or ordinal!=len(roots[epoch]) or ordinal>=512
                or alpha>=beta or count<=0 or
                updated!=int(value>old) or updatedpv!=int(count==1 or value>alpha)):
                raise ValueError("S4L_FALSE_ROOT_UPDATE_FLAG")
            roots[epoch].append({"ordinal":ordinal,"epoch":epoch,"root_move_raw":move,
                "value":value,"old_best":old,"alpha":alpha,"beta":beta,
                "move_count":count,"will_update_best":bool(updated),
                "will_update_root_pv":bool(updatedpv),"depth":depth})
        elif line.startswith("C3X_S4K_GO_END"):
            m=END.fullmatch(line)
            if m is None or active!=int(m.group(1)):raise ValueError("S4L_BAD_GO_END")
            tt_total,root_total=map(int,m.groups()[1:])
            if (tt_total<len(events[active]) or len(events[active])!=min(tt_total,8)
                or root_total<len(roots[active]) or len(roots[active])!=min(root_total,512)):
                raise ValueError("S4L_SITE_TOTAL_RECEIPT_MISMATCH")
            totals[active]=(tt_total,root_total)
            ends.append(active);active=None
        elif line.startswith("C3X_S4L_") or line.startswith("C3X_S4K_"):
            raise ValueError("S4L_UNKNOWN_SOURCE_EVENT")
    if begins!=[1,2] or ends!=[1,2] or active is not None:
        raise ValueError("S4L_INCOMPLETE_EPOCH_CUSTODY")
    trials={}
    for epoch in (1,2):
        tt_total,root_total=totals[epoch]
        trials[str(epoch)]={"events":events[epoch],"observed":len(events[epoch]),
           "right_censored":tt_total>8,"coverage_complete":tt_total<=8,
           "actual_source_cutoffs_at_this_return_site":tt_total,
           "root_score_receipts":roots[epoch],
           "root_score_total_at_this_site":root_total,
           "root_score_right_censored":root_total>512,
           "root_candidate_update_site_covered":root_total<=512,
           "not_tied_to_specific_tt_invocation":True}
    return {"trials":trials,
        "all_cutoff_events_total":sum(x[0] for x in totals.values()),
        "logged_cutoff_events_total":sum(len(x) for x in events.values()),
        "all_root_score_events_total":sum(x[1] for x in totals.values()),
        "logged_root_score_events_total":sum(len(x) for x in roots.values()),
        "causal_mediation_proven":False}

def compare(sham,two):
    state=compare_by_go(sham,two)
    root={}
    for epoch in ("1","2"):
        a=sham["trials"][epoch];b=two["trials"][epoch]
        root[epoch]={"sham_root_scores":a["root_score_total_at_this_site"],
                     "two_root_scores":b["root_score_total_at_this_site"],
                     "sham_root_logged":len(a["root_score_receipts"]),
                     "two_root_logged":len(b["root_score_receipts"]),
                     "any_root_log_censored":a["root_score_right_censored"] or b["root_score_right_censored"],
                     "never_align_root_receipts_by_ordinal":True}
    return {"cutoff_candidate_alignment":state,"root_update_site_by_epoch":root,
       "root_value_counterfactual_mediation_proven":False}
