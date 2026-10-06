#!/usr/bin/env python3
import argparse,json,shutil,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
LOCKS={"stockfish_19":"edb0d9db6731067ec50ce619ff372b463bc4dd5d","berserk":"32628515050b83805bab4afa1026dd2bcaa93f55","ethereal":"0e47e9b67f345c75eb965d9fb3e2493b6a11d09a"}
def one(t,a,b,label):
 n=t.count(a)
 if n!=1:raise SystemExit(f"{label}_ANCHOR_{n}")
 return t.replace(a,b,1)
def head(r):return subprocess.check_output(["git","-C",str(r),"rev-parse","HEAD"],text=True).strip()
def install(r):
 dst=r/"src"/"c3x_p20_reduction.inc";shutil.copyfile(ROOT/"tools"/"g10_p20_reduction_common.inc",dst);return str(dst.relative_to(r))
def stockfish(r):
 inc=install(r);p=r/"src"/"search.cpp";s=p.read_text()
 s=one(s,'#include "c3x_p31_semantic.inc"','#include "c3x_p31_semantic.inc"\n#include "c3x_p20_reduction.inc"',"SF_INC")
 s=one(s,'if (depth >= 2 && moveCount > 1)\n        {','if (depth >= 2 && moveCount > 1 && !c3x_p20_no_reduction())\n        {',"SF_LMR_GATE")
 s=one(s,'Depth d = std::max(1, std::min(newDepth - r / 1024, newDepth + 2)) + PvNode;\n\n            ss->reduction = newDepth - d;',
 '''Depth d = std::max(1, std::min(newDepth - r / 1024, newDepth + 2)) + PvNode;
            c3x_p20_reduction_decision("MAIN",ss->ply,(int)depth,moveCount,(int)(r/1024),(int)newDepth,(int)d,(int)alpha,(int)beta,!capture);

            ss->reduction = newDepth - d;''',"SF_DECISION")
 s=one(s,'if (newDepth > d)\n                    value = -search<NonPV>(pos, ss + 1, -(alpha + 1), -alpha, newDepth, !cutNode);',
 '''if (newDepth > d)
                {
                    c3x_p20_reduction_research("MAIN",ss->ply,(int)depth,moveCount,(int)d,(int)newDepth,(int)alpha,(int)beta);
                    value = -search<NonPV>(pos, ss + 1, -(alpha + 1), -alpha, newDepth, !cutNode);
                }''',"SF_RESEARCH")
 s=one(s,'newDepth - (r > 5234) - (r > 5487 && newDepth > 2), !cutNode);',
 'newDepth - (c3x_p20_no_reduction() ? 0 : ((r > 5234) + (r > 5487 && newDepth > 2))), !cutNode);',"SF_FALLBACK")
 p.write_text(s);return {"files":["src/search.cpp"],"include":inc}
def berserk(r):
 inc=install(r);p=r/"src"/"search.c";s=p.read_text()
 s=one(s,'#include "c3x_p31_semantic.inc"','#include "c3x_p31_semantic.inc"\n#include "c3x_p20_reduction.inc"',"BE_INC")
 s=one(s,'if (depth > 1 && legalMoves > 1 && !(isPV && IsCap(move))) {','if (depth > 1 && legalMoves > 1 && !(isPV && IsCap(move)) && !c3x_p20_no_reduction()) {',"BE_LMR_GATE")
 s=one(s,'int lmrDepth = newDepth - R;\n      score        = -Negamax(-alpha - 1, -alpha, lmrDepth, 1, thread, &childPv, ss + 1);',
 '''int lmrDepth = newDepth - R;
      c3x_p20_reduction_decision("MAIN",ss->ply,depth,legalMoves,R,newDepth,lmrDepth,alpha,beta,!IsCap(move));
      score        = -Negamax(-alpha - 1, -alpha, lmrDepth, 1, thread, &childPv, ss + 1);''',"BE_DECISION")
 s=one(s,'if (newDepth - 1 > lmrDepth)\n          score = -Negamax(-alpha - 1, -alpha, newDepth - 1, !cutnode, thread, &childPv, ss + 1);',
 '''if (newDepth - 1 > lmrDepth) {
          c3x_p20_reduction_research("MAIN",ss->ply,depth,legalMoves,lmrDepth,newDepth-1,alpha,beta);
          score = -Negamax(-alpha - 1, -alpha, newDepth - 1, !cutnode, thread, &childPv, ss + 1);
        }''',"BE_RESEARCH")
 p.write_text(s);return {"files":["src/search.c"],"include":inc}
def ethereal(r):
 inc=install(r);p=r/"src"/"search.c";s=p.read_text()
 s=one(s,'#include "c3x_p31_semantic.inc"','#include "c3x_p31_semantic.inc"\n#include "c3x_p20_reduction.inc"',"ET_INC")
 s=one(s,'if (depth > 2 && played > 1) {','if (depth > 2 && played > 1 && !c3x_p20_no_reduction()) {',"ET_LMR_GATE")
 s=one(s,'// Perform reduced depth search on a Null Window\n            value = -search(thread, &lpv, -alpha-1, -alpha, newDepth-R, true);',
 '''// Perform reduced depth search on a Null Window
            c3x_p20_reduction_decision("MAIN",thread->height,depth,played,R,newDepth,newDepth-R,alpha,beta,isQuiet);
            value = -search(thread, &lpv, -alpha-1, -alpha, newDepth-R, true);''',"ET_DECISION")
 s=one(s,'if (newDepth - 1 > lmrDepth)\n                    value = -search(thread, &lpv, -alpha-1, -alpha, newDepth-1, !cutnode);',
 '''if (newDepth - 1 > lmrDepth) {
                    c3x_p20_reduction_research("MAIN",thread->height,depth,played,lmrDepth,newDepth-1,alpha,beta);
                    value = -search(thread, &lpv, -alpha-1, -alpha, newDepth-1, !cutnode);
                }''',"ET_RESEARCH")
 p.write_text(s);return {"files":["src/search.c"],"include":inc}
def main():
 ap=argparse.ArgumentParser();ap.add_argument("--root",required=True);ap.add_argument("--engine",choices=LOCKS,required=True);ap.add_argument("--manifest",required=True)
 a=ap.parse_args();r=Path(a.root);h=head(r)
 if h!=LOCKS[a.engine]:raise SystemExit(f"SOURCE_LOCK {h}")
 edit={"stockfish_19":stockfish,"berserk":berserk,"ethereal":ethereal}[a.engine](r)
 subprocess.check_call(["git","diff","--check"],cwd=r)
 m={"schema":"c3x-g10-p20-reduction-instrument-v1","stage":"C3X 0.10.0-G10-P20","engine":a.engine,"source_commit":h,"modes":["BASE","NO_REDUCTION"],"direct_lmr_decision":True,"proxy_reduction":False,"edit":edit}
 Path(a.manifest).parent.mkdir(parents=True,exist_ok=True);Path(a.manifest).write_text(json.dumps(m,indent=2,sort_keys=True)+"\n")
 print(json.dumps(m,sort_keys=True))
if __name__=="__main__":main()
