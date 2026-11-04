"""Sharp binary-overlap bounds from archived aggregate native receipts.

No inference that semantic plan Q changed, or about Stockfish internal causal
mediators. Counts are from an EXPOSED development cohort, not heldout.
"""
import json
from pathlib import Path


def overlap_bounds(n, count_a, count_b):
    if not all(type(x) is int for x in (n,count_a,count_b)) or n < 1 or not 0 <= count_a <= n or not 0 <= count_b <= n:
        raise ValueError("invalid counts")
    return {'lower':max(0,count_a+count_b-n),'upper':min(count_a,count_b)}


def same_choice_trace_bounds(receipt):
    if not isinstance(receipt,dict) or 'observed_summary' not in receipt:
        raise ValueError("receipt missing aggregate summary")
    s=receipt['observed_summary']
    n=receipt.get('unique_input_positions')
    changed=s.get('categorical_bestmove_changed')
    if type(n) is not int or type(changed) is not int or n<=0 or changed<0 or changed>n:
        raise ValueError("invalid base counts")
    same=n-changed
    out={'cohort_size':n,'bestmove_unchanged':same,'bestmove_changed':changed,
         'claim_scope':'archived-development aggregate overlap bounds only'}
    for name,key in [('pv','PV_changed'),('nodes','nodes_changed'),('score_or_bound','score_or_bound_changed')]:
        value=s.get(key)
        out[name+'_changed_given_same_bestmove_bounds']=overlap_bounds(n,same,value)
    return out


def from_repo(root=None):
    root=Path(root) if root is not None else Path(__file__).resolve().parents[1]
    p=root/'c3x/receipts/c3x-017-opening-12-independent-Lichess-root-order-72native-P4-legacy-id-20261009.json'
    return same_choice_trace_bounds(json.loads(p.read_text(encoding='utf-8')))


if __name__=='__main__':
    print(json.dumps(from_repo(),sort_keys=True,indent=2))
