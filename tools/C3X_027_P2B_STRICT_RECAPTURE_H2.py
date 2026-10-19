#!/usr/bin/env python3
"""C3X 0.27 P2-B: exhaustive legal strict immediate recapture at H=2."""
import argparse, collections, hashlib, json
from pathlib import Path
import chess
P11_SHA = '18c2f25551a5a929e7cd95ec7c207837a79ea7f5c3df75e96109884ed168b9d2'
def continuation(board, reply):
    if reply not in board.legal_moves: raise ValueError(('illegal reply',reply.uci()))
    moved_before=board.piece_at(reply.from_square)
    castle=board.is_castling(reply)
    ep=board.is_en_passant(reply)
    b=board.copy(stack=True);b.push(reply)
    moved=b.piece_at(reply.to_square)
    assert moved and moved_before and moved.piece_type==moved_before.piece_type
    recaptures=[]
    if not castle:
        for t in b.legal_moves:
            if t.to_square==reply.to_square and b.is_capture(t):
                captured=b.piece_at(t.to_square)
                if captured and captured.color==moved.color and captured.piece_type==moved.piece_type:
                    recaptures.append(t.uci())
    return {'reply':reply.uci(),'recaptures':sorted(recaptures),
            'strict_recapture_exists':bool(recaptures),'reply_castling':castle,
            'reply_en_passant':ep,'reply_gives_check':board.gives_check(reply)}
def main(source):
    raw=source.read_bytes()
    if hashlib.sha256(raw).hexdigest()!=P11_SHA: raise ValueError('P11 source hash mismatch')
    rows=[json.loads(x) for x in raw.splitlines() if x.strip()]
    if len(rows)!=144:raise ValueError('P11 row count')
    grouped=collections.defaultdict(list)
    for r in rows:grouped[(r['index'],r['mode'],r['root_move'],r['reply_depth'])].append(r)
    if len(grouped)!=72:raise ValueError('unique arms mismatch')
    arms=[]
    for (idx,mode,root,depth),reps in sorted(grouped.items()):
        if sorted(x['repeat'] for x in reps)!=[1,2]:raise ValueError('cold repeat labels')
        if len({x['fen_before_root'] for x in reps})!=1 or len({x['fen_after_root'] for x in reps})!=1:raise ValueError('FEN repeat mismatch')
        b=chess.Board(reps[0]['fen_before_root']);m=chess.Move.from_uci(root)
        if m not in b.legal_moves:raise ValueError(('illegal first root',idx,root))
        b.push(m)
        if b.fen(en_passant='fen')!=reps[0]['fen_after_root']:raise ValueError(('root FEN mismatch',idx,root))
        responses=sorted([continuation(b,r) for r in list(b.legal_moves)],key=lambda v:v['reply'])
        response_map={x['reply']:x for x in responses}
        reported=sorted({x['move'] for rep in reps for x in rep['replies']})
        if not set(reported).issubset(response_map):raise ValueError('P11 reported illegal reply')
        counterexample=next((r['reply'] for r in responses if not r['strict_recapture_exists']),None)
        arms.append({'index':idx,'mode':mode,'root':root,'reply_depth':depth,
                     'legal_opponent_replies':len(responses),
                     'recapturable_opponent_replies':sum(v['strict_recapture_exists'] for v in responses),
                     'all_opponent_replies_have_strict_recapture':counterexample is None,
                     'counterexample_reply':counterexample,'responses':responses,
                     'reported_replies':reported,
                     'reported_all_strict_recapturable':all(response_map[x]['strict_recapture_exists'] for x in reported)})
    invariant=collections.defaultdict(set)
    for x in arms:
        invariant[(x['index'],x['root'])].add(json.dumps([(r['reply'],r['recaptures']) for r in x['responses']]))
    if len(invariant)!=18 or any(len(x)!=1 for x in invariant.values()):raise ValueError('cross mode/depth root chess-state invariance')
    groups=collections.defaultdict(list)
    for x in arms:groups[(x['index'],x['mode'],x['reply_depth'])].append(x)
    if len(groups)!=36:raise ValueError('comparison count')
    contrasts=[]
    for (idx,mode,depth),xs in sorted(groups.items()):
        if len(xs)!=2:raise ValueError('competing root number')
        a,b=sorted(xs,key=lambda x:x['root'])
        contrasts.append({'index':idx,'mode':mode,'reply_depth':depth,
                          'roots':[a['root'],b['root']],
                          'recapturable_counts':[a['recapturable_opponent_replies'],b['recapturable_opponent_replies']],
                          'all_responses_status':[a['all_opponent_replies_have_strict_recapture'],b['all_opponent_replies_have_strict_recapture']],
                          'counterexamples':[a['counterexample_reply'],b['counterexample_reply']]})
    return {'status':'STRICT_RECAPTURE_H2_CHESS_LEGAL_ONLY',
            'source_sha256':P11_SHA,'rows':144,'unique_arms':72,'unique_root_states':18,
            'comparisons':contrasts,'arms':arms,
            'horizon':'two plies AFTER first root: opponent reply then original mover response',
            'limitations':['Strict immediate recapture is not material benefit or strategic choice explanation',
                           'Original repetition history not preserved by FEN; no repetition claims',
                           'A single H2 run cannot determine minimal explanatory horizon across H',
                           'No human-study outcome']}
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--input',required=True,type=Path);p.add_argument('--output',required=True,type=Path);a=p.parse_args()
    result=main(a.input);a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(result,indent=2,ensure_ascii=False,sort_keys=True)+'\n')
    print('P2B_PASS',result['rows'],result['unique_arms'],result['unique_root_states'],len(result['comparisons']))
