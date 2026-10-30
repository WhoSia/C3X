"""Finite C3X 0.29 explanation equivalence and active distinguishing suite.

Abstract king-square predicate domain; NOT chess legality, engine faithfulness
or human concept transfer. Predeclared predicate vocabulary and candidate tests.
"""
from itertools import combinations

def predicates():
    return {
        "rank_7":lambda x:x[1]=="7",
        "not_g8":lambda x:x!="g8",
        "file_not_g":lambda x:x[0]!="g",
        "rank_below_8":lambda x:x[1]!="8",
    }

def partition(domain, hypotheses):
    result={}
    for label, predicate in hypotheses.items():
        signature=tuple(bool(predicate(x)) for x in domain)
        result.setdefault(signature,[]).append(label)
    return tuple(tuple(sorted(v)) for v in result.values())

def distinct_pairs(domain,hypotheses):
    labels=tuple(hypotheses)
    return frozenset((a,b) for i,a in enumerate(labels) for b in labels[i+1:]
        if any(hypotheses[a](x)!=hypotheses[b](x) for x in domain))

def minimum_suite(domain,hypotheses):
    pairs=distinct_pairs(domain,hypotheses)
    for size in range(len(domain)+1):
        solutions=[]
        for subset in combinations(domain,size):
            if distinct_pairs(subset,hypotheses)==pairs:
                solutions.append(subset)
        if solutions:
            return tuple(solutions), pairs
    raise AssertionError("finite exhaustive failure")

def court():
    h=predicates()
    original=("g7","h7","g8")
    base=partition(original,h)
    assert ("not_g8","rank_7","rank_below_8") in base
    candidates=("a8","g8","g7","h7","f8","a7","b8")
    suites,pairs=minimum_suite(candidates,h)
    # Independent subset-mask oracle: verify no shorter candidate suite exists.
    acceptable=[]
    for mask in range(1<<len(candidates)):
        subset=tuple(x for i,x in enumerate(candidates) if mask&(1<<i))
        if distinct_pairs(subset,h)==pairs:
            acceptable.append(subset)
    minimum=min(map(len,acceptable))
    assert set(suites)=={s for s in acceptable if len(s)==minimum}
    assert minimum==2 and len(suites)==3 and len(pairs)==5
    return {"candidate_contexts":list(candidates),"predicate_names":list(h),
        "original_equivalence_classes":base,"distinct_pairs":len(pairs),
        "minimum_suite_size":minimum,"minimum_suites":suites,
        "independently_checked_subsets":1<<len(candidates),
        "hypothesis_class_is_predeclared":True,
        "chess_legality_verified":False,"native_engine_calls":0}

if __name__=="__main__":
    import json
    print(json.dumps(court(),indent=2,sort_keys=True))
