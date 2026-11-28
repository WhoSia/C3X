#!/usr/bin/env python3
"""R57: replay archived exact PV prefixes via pinned Stockfish position parser, no search."""
import argparse, hashlib, json, re, subprocess, zipfile
from pathlib import Path
from collections import Counter
ZIP='d95bdf101a0868151baa364357036ad58c0a6c408f48e7c46d54a8ebdde9980c'
ENGINE='78cae269c73eb080c8a508e839dcde15ce48888b3fc4317fa3311de49e5ee7bb'
IDS=('T04-TAC-1','T04-QUI-1','T04-QUI-2','T04-PRO-1','T04-PRO-4','T04-END-1')
DEPTHS=(8,10,14,18,22); H=(1,3,5,7,9)
FEATURES=('material','passed_pawns','pawn_islands')
def sha(b):return hashlib.sha256(b).hexdigest()
def require(x,m):
    if not x:raise ValueError(m)
def features(fen,mover):
    board={}
    for r,row in enumerate(reversed(fen.split()[0].split('/'))):
        f=0
        for x in row:
            if x.isdigit():f+=int(x)
            else:board[f,r]=x;f+=1
        require(f==8,'board width')
    own={s:p for s,p in board.items() if p.isupper()==(mover=='w')}
    opp={s:p for s,p in board.items() if s not in own}
    ownp=[s for s,p in own.items() if p.lower()=='p']; oppp=[s for s,p in opp.items() if p.lower()=='p']
    passed=sum(not any(abs(f-g)<=1 and ((r<t) if mover=='w' else (r>t)) for g,t in oppp) for f,r in ownp)
    files=sorted({f for f,r in ownp}); islands=sum(i==0 or f-files[i-1]>1 for i,f in enumerate(files))
    weights={'p':100,'n':320,'b':330,'r':500,'q':900,'k':0}
    return {'material':sum(weights[p.lower()] for p in own.values())-sum(weights[p.lower()] for p in opp.values()),'passed_pawns':passed,'pawn_islands':islands}
def sign(x):return (x>0)-(x<0)
def main():
    p=argparse.ArgumentParser();p.add_argument('archive',type=Path);p.add_argument('engine',type=Path);p.add_argument('out',type=Path);a=p.parse_args()
    require(sha(a.archive.read_bytes())==ZIP and sha(a.engine.read_bytes())==ENGINE,'identity')
    with zipfile.ZipFile(a.archive) as z:
        require(z.testzip() is None,'CRC');cohort={r['id']:r for r in json.loads(z.read('cohort.json'))['cohort']}; pv={}; jobs=[]
        for ident in IDS:
            c=cohort[ident];r=json.loads(z.read(ident+'.json'))
            for side in ('A','B'):
                text=z.read(ident+'_'+side+'.txt').decode()
                for d in DEPTHS:
                    obs=r['arms'][side]['depths'][str(d)];require(obs['status']=='exact_cp','score status')
                    matches=[]
                    for line in text.splitlines():
                        m=re.search(r'^info depth (\d+)\b.*?\bscore cp (-?\d+)\b.*?\bnodes (\d+)\b.*?\bpv (.+)$',line)
                        if m and (int(m[1]),int(m[2]),int(m[3]))==(d,obs['value'],obs['nodes']) and 'bound' not in line:matches.append(m[4].split())
                    require(len(matches)==1 and matches[0][0]==c[side],'PV identity')
                    moves=matches[0];pv[ident,side,d]=moves
                    for h in H:
                        if len(moves)>=h:jobs.append((ident,side,d,h,c['fen'],moves[:h]))
    commands=['uci','isready']
    for ident,side,d,h,fen,moves in jobs:commands+=['position fen '+fen+' moves '+' '.join(moves),'d']
    commands.append('quit')
    proc=subprocess.run([str(a.engine.resolve())],cwd=a.engine.parent,input='\n'.join(commands)+'\n',capture_output=True,text=True,timeout=60,check=True)
    fens=re.findall(r'^Fen: (.+)$',proc.stdout,re.M);require(len(fens)==len(jobs),'debug FEN count')
    states={}
    for (ident,side,d,h,fen,moves),f in zip(jobs,fens):
        fields=fen.split();got=f.split();require(len(got)==6,'FEN field count');mover=fields[1]
        start=2*(int(fields[5])-1)+int(mover=='b');end=2*(int(got[5])-1)+int(got[1]=='b');require(end-start==h,'prefix truncated or illegal')
        states[ident,side,d,h]={'fen4':' '.join(got[:4]),'features':features(f,mover)}
    rows=[]; summary=Counter();shared=[]; counts=Counter()
    for ident in IDS:
        for h in H:
            A=[states.get((ident,'A',d,h)) for d in DEPTHS];B=[states.get((ident,'B',d,h)) for d in DEPTHS]
            present=sum(x is not None for x in A+B);counts[h]+=present
            overlaps=sorted({x['fen4'] for x in A if x}&{x['fen4'] for x in B if x});shared.append({'id':ident,'horizon':h,'shared_boards':len(overlaps)})
            for feat in FEATURES:
                av=[x['features'][feat] for x in A if x];bv=[x['features'][feat] for x in B if x]
                row={'id':ident,'horizon':h,'feature':feat,'support_A':len(av),'support_B':len(bv),'single_d22':None if not A[-1] or not B[-1] else A[-1]['features'][feat]-B[-1]['features'][feat]}
                if len(av)==len(bv)==5:
                    lo=min(av)-max(bv);hi=max(av)-min(bv);s=row['single_d22'];strict=lo>0 or hi<0
                    row.update(A=av,B=bv,range=[lo,hi],strict=strict,opposite=(s>0 and lo<0) or (s<0 and hi>0));summary['complete']+=1;summary['strict']+=strict
                    if s:summary['single_nonzero']+=1;summary['single_nonzero_not_strict']+=not strict;summary['opposite']+=row['opposite']
                    if h>1 and s:summary['tail_single_nonzero']+=1;summary['tail_nonzero_not_strict']+=not strict;summary['tail_opposite']+=row['opposite']
                else:summary['partial']+=1
                rows.append(row)
    result={'scope':'archived exposed R54 PV factual stress audit; no engine search, FEN-only, not utility or causality','archive_sha256':ZIP,'engine_sha256':ENGINE,'PV_count':len(pv),'available_prefixes':len(jobs),'possible_prefixes':60*len(H),'prefix_count_by_horizon':dict(counts),'native_searches':0,'summary':dict(summary),'shared_boards':shared,'rows':rows}
    a.out.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='rows'},indent=2));print('result_sha',sha(a.out.read_bytes()))
if __name__=='__main__':main()
