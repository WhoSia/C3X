#!/usr/bin/env python3
"""Outcome-blind metadata census for frozen C3X 0.11 six-source PGNs.

Python stdlib only. It cannot validate SAN legality, FEN disjointness, or grant a seal.
"""
import argparse, hashlib, json, re
from collections import Counter, defaultdict
from pathlib import Path
TAG = re.compile(r'^\[([A-Za-z][A-Za-z0-9_]*)\s+"((?:\\.|[^"\\])*)"\]$')
FILES = {'Charlotte':'C3X_G10_P25_Charlotte_Spring_Norm_2026_GM_Lichess_0zfikbXR.pgn','NZ':'NZ.pgn','Golders':'Golders.pgn','Radnicki':'Radnicki.pgn','Berjaya':'Berjaya_Masters.pgn','Milton':'Milton.pgn'}
ROLES = {'Charlotte':'calibration','NZ':'calibration','Golders':'calibration','Radnicki':'transfer','Berjaya':'transfer','Milton':'transfer'}
def games(path):
    tags, moves = {}, []
    for line in path.read_text(encoding='utf-8-sig').splitlines():
        line = line.strip()
        if not line: continue
        match = TAG.fullmatch(line)
        if match:
            if moves:
                yield tags, ' '.join(moves)
                tags, moves = {}, []
            tags[match.group(1)] = match.group(2)
        elif tags: moves.append(line)
    if tags: yield tags, ' '.join(moves)
def norm(text): return ' '.join(text.casefold().split())
def census(folder):
    cross_keys=defaultdict(list); out={}; roles=Counter()
    for sid, filename in FILES.items():
        path=folder/filename
        if not path.is_file(): raise FileNotFoundError(path)
        counts=Counter();dates=set();players=set();rounds=set();parents=set();game_urls=set()
        tc=Counter(); variants=Counter(); dup_urls=0
        for idx,(tags,mt) in enumerate(games(path),1):
            counts['games']+=1
            players_pair=tuple(sorted([norm(tags.get('White','')),norm(tags.get('Black',''))]))
            key=(tags.get('Date','?'),tags.get('Round','?'),norm(tags.get('Event','')),players_pair)
            cross_keys[key].append((sid,idx))
            players.update(players_pair);dates.add(tags.get('Date','?'));rounds.add(tags.get('Round','?'))
            counts['eval_annotation_games']+=int('[%eval' in mt)
            counts['clock_annotation_games']+=int('[%clk' in mt)
            counts['fide_id_pair_games']+=int(bool(tags.get('WhiteFideId') and tags.get('BlackFideId')))
            counts['missing_movetext']+=int(not mt)
            variants[tags.get('Variant','MISSING')]+=1
            tc[tags.get('TimeControl','MISSING')]+=1
            if tags.get('BroadcastURL'):parents.add(tags['BroadcastURL'])
            url=tags.get('GameURL')
            if url in game_urls and url:dup_urls+=1
            if url:game_urls.add(url)
        out[sid]={'role':ROLES[sid],'raw_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
                  'bytes':path.stat().st_size,'game_count':counts['games'],
                  'dates':sorted(dates),'rounds':sorted(rounds),'distinct_players':len(players),
                  'broadcast_parent_urls':sorted(parents),'game_url_count':len(game_urls),
                  'duplicate_game_urls':dup_urls,'timecontrols':dict(tc),'variant_counts':dict(variants),
                  'eval_annotation_games':counts['eval_annotation_games'],
                  'clock_annotation_games':counts['clock_annotation_games'],
                  'fide_id_pair_games':counts['fide_id_pair_games'],
                  'missing_movetext':counts['missing_movetext']}
        roles[ROLES[sid]]+=counts['games']
    repeated={str(k):v for k,v in cross_keys.items() if len(set(x[0] for x in v))>1}
    return {'schema':'c3x-0.11-outcome-blind-provenance-census-v1',
            'verdict':'METADATA_CENSUS_ONLY',
            'sources':out,'total_game_headers':sum(x['game_count'] for x in out.values()),
            'games_by_role':dict(roles),'cross_source_same_event_date_round_playerpair_keys':len(repeated),
            'cross_source_repeat_examples':list(repeated.values())[:10],
            'san_legality_verified':False,'historical_fen_exclusion_verified':False,
            'scientific_source_preseal':False,'activation_outcomes_opened':False}
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--pgn-dir',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
    a=p.parse_args();r=census(a.pgn_dir);a.out.write_text(json.dumps(r,indent=2,ensure_ascii=False)+'\n')
    print('METADATA_CENSUS_ONLY',r['total_game_headers'],r['games_by_role'])
