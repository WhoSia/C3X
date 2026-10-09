#!/usr/bin/env python3
"""C3X 0.15 P0: score-blind provider-disjoint original PGN source census.
No engine evaluation, executable engine, TT traces or treatment outcomes read.
"""
from __future__ import annotations
import argparse,collections,hashlib,io,json,zipfile
from pathlib import Path
import chess,chess.pgn
from c3x_014_source_only_official_TCEC_pin_subtype_freeze import pin_ray_witness,PIECE

MAX_PLY=120
MIN_PLY=18
CAP=64
EVENT_CAP=8
RUN_TAG='R2_PRE_OUTCOME_MATCH_REPAIR'
def digest(b):return hashlib.sha256(b).hexdigest()
def encode(x):return json.dumps(x,sort_keys=True,ensure_ascii=False,separators=(',',':'))
def fen(b):return b.fen(en_passant='fen')
def read_games(b):
    f=io.StringIO(b.decode('utf-8-sig',errors='replace'))
    while True:
        game=chess.pgn.read_game(f)
        if game is None:break
        yield game
def extract(z):
    if not z.startswith(b'PK\x03\x04'):raise RuntimeError('SOURCE_IS_NOT_ZIP')
    with zipfile.ZipFile(io.BytesIO(z)) as arc:
        members=[m for m in arc.infolist() if m.filename.lower().endswith('.pgn') and not m.is_dir()]
        if len(members)!=1:raise RuntimeError('EXPECTED_ONE_PGN_MEMBER')
        if members[0].file_size>60000000:raise RuntimeError('PGN_UNBOUNDED_BYTES')
        b=arc.read(members[0])
        return b,members[0].filename
def history_key(start,moves):
    return digest(encode({'start':start,'moves':moves}).encode())
def pin_objects(b):
    res=[]
    for sq,pc in sorted(b.piece_map().items()):
        if pc.color!=b.turn or pc.piece_type==chess.KING or not b.is_pinned(b.turn,sq):continue
        ray=pin_ray_witness(b,b.turn,sq)
        if ray is None:raise RuntimeError('PIN_GEOMETRIC_WITNESS_FAILED')
        mask=chess.BB_SQUARES[sq]
        legal=list(b.generate_legal_moves(from_mask=mask))
        pseudo=list(b.generate_pseudo_legal_moves(from_mask=mask))
        capture=any(m.to_square==chess.parse_square(ray['pinning_square']) and b.is_capture(m) for m in legal)
        law={'pinned_piece':PIECE[pc.piece_type],
            'pinning_piece':ray['pinning_piece'],'axis':ray['axis'],
            'legal_pinned_piece_mobility':'NONZERO' if legal else 'ZERO',
            'can_legally_capture_pinner':capture}
        res.append({'pinned_square':chess.square_name(sq),'pinner_square':ray['pinning_square'],
          'king_square':ray['king_square'],'pinned_piece_symbol':pc.symbol(),'law':law,
          'legal_moves':[m.uci() for m in legal],
          'excluded_pseudolegal_moves':[m.uci() for m in pseudo if m not in legal]})
    return res
def prior_games(paths):
    seen_games=set();seen_six=set();seen_four=set();meta=[]
    for p in paths:
        raw=p.read_bytes();count=0
        for g in read_games(raw):
            count+=1
            if g.errors:raise RuntimeError('PRIOR_TCEC_PGN_PARSE_FAIL')
            board=g.board();start=fen(board);hist=[]
            for mv in g.mainline_moves():
                if mv not in board.legal_moves:raise RuntimeError('PRIOR_TCEC_HISTORY_ILLEGAL')
                board.push(mv);hist.append(mv.uci())
                if MIN_PLY<=len(hist)<=MAX_PLY:
                    s=fen(board);seen_six.add(s);seen_four.add(' '.join(s.split()[:4]))
            seen_games.add(history_key(start,hist))
        meta.append({'name':p.name,'sha256':digest(raw),'games':count})
    return seen_games,seen_six,seen_four,meta
def main():
    a=argparse.ArgumentParser()
    a.add_argument('--zip',type=Path,required=True)
    a.add_argument('--prior-pgn',type=Path,action='append',default=[])
    a.add_argument('--outdir',type=Path,required=True)
    args=a.parse_args()
    args.outdir.mkdir(parents=True,exist_ok=True)
    archived=args.zip.read_bytes();raw,member=extract(archived)
    prior_g,prior_s,prior_f,meta=prior_games(args.prior_pgn)
    counts=collections.Counter();seen=set();pin=[];nonpin=[];errors=[]
    for game_no,g in enumerate(read_games(raw),1):
        counts['original_games_parsed']+=1
        if g.errors:
            counts['invalid_pgn_games']+=1
            if len(errors)<20:errors.append({'game':game_no,'errors':[str(e)[:120] for e in g.errors[:3]]})
            continue
        board=g.board();start=fen(board);history=[];pfirst=None;nscenes={}
        for ply,m in enumerate(g.mainline_moves(),1):
            if m not in board.legal_moves:raise RuntimeError('SOURCE_ILLEGAL_MAINLINE')
            board.push(m);history.append(m.uci())
            if not MIN_PLY<=ply<=MAX_PLY or board.is_game_over():continue
            sf=fen(board)
            if sf in prior_s or ' '.join(sf.split()[:4]) in prior_f:
                counts['tcec_overlap_position_excluded']+=1;continue
            counts['positions_checked']+=1
            pp=pin_objects(board)
            if pp:counts['absolute_pin_witnesses']+=len(pp)
            if pp and pfirst is None:pfirst=(ply,sf,pp,len(board.piece_map()),board.legal_moves.count())
            if not pp:
                key=(ply//8,ply%2)
                nscenes.setdefault(key,(ply,sf,len(board.piece_map()),board.legal_moves.count()))
        counts['full_legally_replayed_games']+=1
        key=history_key(start,history)
        if key in prior_g:counts['prior_game_collision']+=1;continue
        if key in seen:counts['within_archive_duplicate_game']+=1;continue
        seen.add(key)
        headers={x:g.headers.get(x,'') for x in ('Event','Site','Date','Round','White','Black','Result')}
        common={'game_ordinal':game_no,'game_key_sha256':key,'initial_fen':start,
                'headers':headers,'full_history_uci':history,'total_plies':len(history)}
        if pfirst:
            ply,sf,pp,np,nl=pfirst
            pin.append({**common,'root_ply':ply,'root_sixfield_fen':sf,'objects':pp,
                        'source_context':{'ply_bin':ply//16,'turn':ply%2,'pieces':np,'legal_move_count':nl}})
        for ply,sf,np,nl in nscenes.values():
            nonpin.append({**common,'root_ply':ply,'root_sixfield_fen':sf,'objects':[],
              'source_context':{'ply_bin':ply//16,'turn':ply%2,'pieces':np,'legal_move_count':nl}})
    selected=[];selected_games=set();selected_fens=set();types=set();events=collections.Counter()
    def add(row):
        if row['game_key_sha256'] in selected_games or row['root_sixfield_fen'] in selected_fens:return False
        event=row['headers'].get('Event','')
        if events[event]>=EVENT_CAP:return False
        selected.append(row);selected_games.add(row['game_key_sha256']);selected_fens.add(row['root_sixfield_fen']);events[event]+=1;return True
    for row in pin:
        k=encode(row['objects'][0]['law'])
        if k not in types and add(row):types.add(k)
        if len(selected)==CAP:break
    for row in pin:
        if len(selected)==CAP:break
        add(row)
    controls=[];used_controls=set()
    for row in selected:
        desired=row['source_context'];best=None
        for c in nonpin:
            if c['game_key_sha256'] in selected_games|used_controls or c['root_sixfield_fen'] in selected_fens:continue
            x=c['source_context']
            if x['turn']!=desired['turn']:continue
            cost=8*abs(c['root_ply']-row['root_ply'])+4*abs(x['pieces']-desired['pieces'])+abs(x['legal_move_count']-desired['legal_move_count'])+(40 if c['headers'].get('Event','')!=row['headers'].get('Event','') else 0)
            if best is None or (cost,c['game_ordinal'])<(best[0],best[1]['game_ordinal']):best=(cost,c)
        if best:
            ctrl={**best[1],'matched_pin_game_key':row['game_key_sha256'],'match_cost':best[0]}
            controls.append(ctrl);used_controls.add(ctrl['game_key_sha256']);selected_fens.add(ctrl['root_sixfield_fen'])
    for row in selected+controls:
        board=chess.Board(row['initial_fen'])
        for ply,m in enumerate(row['full_history_uci'],1):
            move=chess.Move.from_uci(m)
            if move not in board.legal_moves:raise RuntimeError('FROZEN_REPLAY_ILLEGAL')
            board.push(move)
            if ply==row['root_ply']:
                if fen(board)!=row['root_sixfield_fen']:raise RuntimeError('FROZEN_REPLAY_FEN_MISMATCH')
                if pin_objects(board)!=row['objects']:raise RuntimeError('FROZEN_REPLAY_PIN_MISMATCH')
    result={'schema':'c3x015-provider-source-scoreblind-v1','state':'C3X015_P0_SOURCE_CENSUS_ONLY',
      'source_url':'https://theweekinchess.com/zips/twic1665g.zip','provider':'TWIC','issue':1665,
      'source_reuse_scope':'TWIC personal use only: do not rehost raw PGN publicly',
      'original_zip_sha256':digest(archived),'original_zip_bytes':len(archived),
      'pgn_member':member,'pgn_member_sha256':digest(raw),'pgn_bytes':len(raw),
      'prior_tcec_originals':meta,'prior_tcec_unique_sixfield_fens':len(prior_s),
      'prior_lichess_013_overlap_status':'PENDING_REFERENCE_OBJECT_ACQUISITION',
      'counts':dict(counts),'parse_error_examples':errors,
      'pin_candidate_distinct_games':len(pin),'nonpin_candidate_distinct_games':len(nonpin),
      'chosen_pin_games':len(selected),'chosen_nonpin_games':len(controls),
      'types_chosen':len(types),'selected_event_count':len(events),'selected_pin_event_counts':dict(events),'selection':'R2: first game per new chess-law subtype then chronological fill, cap8 per event; at most 64 PIN games. For each 8-ply bin and turn, keep first NONPIN of each distinct other source game, match same turn nearest abs ply, piece count, legal moves and event (40 cost); outcomes untouched.',
      'selection_revision':'R2_PRE_OUTCOME_MATCH_REPAIR, preserves R1 SHA and original pre-engine code at git commit 34e0d1b566d53716ed158c962ed8d8859c0ede14',
      'maximum_selected_games_per_event':EVENT_CAP,
      'engine_output_accessed':False,'causal_transport_pass':False,
      'pin_roots':selected,'nonpin_controls':controls}
    path=args.outdir/'C3X015_TWIC1665_SCOREBLIND_SOURCE_MANIFEST_R2.json'
    path.write_text(json.dumps(result,indent=2,sort_keys=True,ensure_ascii=False)+'\n')
    summary={k:v for k,v in result.items() if k not in ('pin_roots','nonpin_controls','parse_error_examples')}
    summary['manifest_sha256']=digest(path.read_bytes())
    from statistics import median
    links={x['game_key_sha256']:x for x in selected}
    summary['match_quality']={'pin_root_median_ply':median(x['root_ply'] for x in selected) if selected else None,
       'control_root_median_ply':median(x['root_ply'] for x in controls) if controls else None,
       'same_event_pairs':sum(x['headers'].get('Event','')==links[x['matched_pin_game_key']]['headers'].get('Event','') for x in controls),
       'abs_ply_le_8_pairs':sum(abs(x['root_ply']-links[x['matched_pin_game_key']]['root_ply'])<=8 for x in controls),
       'abs_ply_le_16_pairs':sum(abs(x['root_ply']-links[x['matched_pin_game_key']]['root_ply'])<=16 for x in controls),
       'max_event_count':max(events.values()) if events else 0}
    summary['verdict']='SOURCE_COHORT_FROZEN_PROVISIONAL_LEGACY_DEDUP_PENDING' if len(selected)==CAP and len(controls)==CAP else 'SOURCE_COHORT_QUOTA_FAIL'
    (args.outdir/'C3X015_TWIC1665_SOURCE_CUSTODY_RECEIPT_R2.json').write_text(json.dumps(summary,indent=2,sort_keys=True)+'\n')
    print('C3X015_SOURCE_ONLY_CENSUS',json.dumps({'zip_sha256':digest(archived),'original_pgn_sha256':digest(raw),
      'counts':dict(counts),'pin_roots':len(selected),'nonpin_roots':len(controls),
      'manifest_sha256':summary['manifest_sha256'],'verdict':summary['verdict']}),flush=True)
    if len(selected)!=CAP or len(controls)!=CAP:raise SystemExit(2)
if __name__=='__main__':main()
