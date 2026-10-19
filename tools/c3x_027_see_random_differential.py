import chess,random,json,sys,subprocess,importlib.util
from pathlib import Path
p=Path('tools/c3x_027_independent_see_algorithm_audit.py')
sp=importlib.util.spec_from_file_location('replay',p);mod=importlib.util.module_from_spec(sp);sys.argv=['checker','/dev/null','/dev/null'];sp.loader.exec_module(mod) if False else None
# Import is side-effectful; extract see_replay function by parsing AST.
import ast
tree=ast.parse(p.read_text());keep=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='see_replay']
code=compile(ast.Module(body=keep,type_ignores=[]),str(p),'exec')
ns={'chess':chess,'VALUES':{None:0,chess.PAWN:126,chess.KNIGHT:781,chess.BISHOP:825,chess.ROOK:1276,chess.QUEEN:2538,chess.KING:0},'MASK':(1<<64)-1};exec(code,ns)
rnd=random.Random(27023);samples=[]
for g in range(22):
 b=chess.Board()
 for i in range(rnd.randint(4,75)):
  if b.is_game_over():break
  b.push(rnd.choice(list(b.legal_moves)))
 if not b.is_valid() or b.is_game_over():continue
 moves=list(b.legal_moves);captures=[m for m in moves if b.is_capture(m)]
 chosen=(captures[:3]+rnd.sample(moves,min(3,len(moves))))
 for m in chosen:
  for th in (-1100,-200,-95,-43,0,126,500,1200):
   samples.append((b.fen(),m.uci(),th))
engine=subprocess.Popen([sys.argv[1]],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.DEVNULL,text=True,bufsize=1)
def query(fen,move,th):
 engine.stdin.write('position fen '+fen+'\n'+'c3xsee '+move+' '+str(th)+'\n');engine.stdin.flush()
 for _ in range(10):
  line=engine.stdout.readline().strip()
  if line.startswith('c3xsee '):
   z=line.split()
   if len(z)!=5:raise RuntimeError(line)
   return bool(int(z[3])),int(z[4])
 raise RuntimeError('oracle no reply')
result=[];mismatches=[];occupied=0
for fen,u,t in samples:
 b=chess.Board(fen);m=chess.Move.from_uci(u)
 native,occ=query(fen,u,t)
 ours,detail=ns['see_replay'](b,m,t)
 occupied+=int(occ!=0)
 if native!=ours:
  mismatches.append({'fen':fen,'uci':u,'threshold':t,'native':native,'independent':ours,'detail':detail})
result={'schema':'c3x027-source-pinned-see-differential-v1','seed':27023,'samples':len(samples),'mismatches':len(mismatches),'native_occupied_nonzero':occupied,'first_mismatches':mismatches[:35],'status':'MISMATCH_HOLD' if mismatches else 'PASS'}
Path('C3X_027_SEE_DIFFERENTIAL.json').write_text(json.dumps(result,indent=2)+'\n')
engine.stdin.write('quit\n');engine.stdin.flush();engine.wait(timeout=4)
print('C3X027_SEE_DIFFERENTIAL',result['samples'],result['mismatches'],'native_occupied_nonzero',occupied)
# Differences are scientific findings, not a CI execution error.
