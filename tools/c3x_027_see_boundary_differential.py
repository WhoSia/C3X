import ast,json,sys,subprocess,chess,importlib.util
from pathlib import Path
p=Path("tools/c3x_027_independent_see_v2_exact_pins.py")
spec=importlib.util.spec_from_file_location("c3x027_see_v2",p)
checker=importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)
see=checker.see_replay
fixtures=[
("pinned_knight","4k3/8/8/8/8/4n3/4r3/4K2R w - - 0 1"),
("pinned_knight_capture_target","8/6k1/8/8/3n4/5p2/8/B4R1K w - - 0 1"),
("pin_rook","4k3/4r3/8/8/8/8/4R3/4K3 w - - 0 1"),
("xray_rooks","4k3/8/3r4/8/3r4/8/3R4/3RK3 w - - 0 1"),
("bishop_xray","4k3/8/8/5b2/4p3/3B4/2B5/4K3 w - - 0 1"),
("king_retake","4k3/8/8/4p3/4K3/8/8/8 w - - 0 1"),
("en_passant","4k3/8/8/3pP3/8/8/8/4K3 w - d6 0 1"),
("promotion","4k3/P7/8/8/8/8/8/4K3 w - - 0 1"),
("castling","4k3/8/8/8/8/8/8/R3K2R w KQ - 0 1"),
("knight_exchange","4k3/8/8/3p4/4N3/8/8/4K3 w - - 0 1"),
("rook_exchange","4k3/8/8/3p4/3R4/8/8/4K3 w - - 0 1")]
thresholds=[-1100,-200,-95,-43,0,1,126,500,1200]
engine=subprocess.Popen([sys.argv[1]],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.DEVNULL,text=True,bufsize=1)
def query(fen,m,t):
 engine.stdin.write("position fen "+fen+"\nc3xsee "+m+" "+str(t)+"\n");engine.stdin.flush()
 for _ in range(40):
  z=engine.stdout.readline().strip()
  if z.startswith("c3xsee "):
   v=z.split()
   if v[1]=="invalid":return None,0,0
   if len(v)!=6:raise RuntimeError(z)
   return bool(int(v[3])),int(v[4]),int(v[5])
 raise RuntimeError("no oracle response")
rows=[];excluded=[];mismatches=[];labels={}
for label,fen in fixtures:
 b=chess.Board(fen)
 if not b.is_valid():
  excluded.append({"label":label,"reason":"INVALID_BOARD","status":b.status()});continue
 legal=list(b.legal_moves)
 chosen=[m for m in legal if b.is_capture(m) or b.is_en_passant(m) or m.promotion or b.is_castling(m)]
 chosen+= [m for m in legal if m not in chosen][:4]
 for m in chosen:
  for threshold in thresholds:
   native,occ,mask=query(fen,m.uci(),threshold)
   if native is None:
    excluded.append({"label":label,"uci":m.uci(),"threshold":threshold,"reason":"NATIVE_UCI_UNRECOGNIZED"});continue
   independent,detail=see(b,m,threshold)
   item={"label":label,"fen":fen,"uci":m.uci(),"threshold":threshold,"native":native,"independent":independent,"occupied":occ,"native_branch_mask":mask,"independent_terminal":detail.get("terminal",detail.get("first_gate"))}
   rows.append(item)
   labels[label]=labels.get(label,0)+1
   if native!=independent:mismatches.append(item)
engine.stdin.write("quit\n");engine.stdin.flush();engine.wait(timeout=4)
report={"schema":"c3x027-see-boundary-differential-v1","fixtures_attempted":len(fixtures),"comparisons":len(rows),"per_fixture_counts":labels,"exclusions":excluded,"mismatch_count":len(mismatches),"mismatches":mismatches[:100],"native_occupied_nonzero":sum(bool(x["occupied"]) for x in rows),"native_branch_counts":{str(i):sum(bool(r["native_branch_mask"]&(1<<i)) for r in rows) for i in range(21)},"castle_compared":sum(r["label"]=="castling" and r["uci"] in ("e1g1","e1c1") for r in rows),"targeted_pin_tested":sum(r["label"]=="pinned_knight_capture_target" and r["uci"]=="f1f3" for r in rows)}
Path("C3X_027_SEE_BOUNDARY_DIFFERENTIAL.json").write_text(json.dumps(report,indent=2)+"\n")
print("C3X027_SEE_BOUNDARY",report["comparisons"],report["mismatch_count"],"occupied",report["native_occupied_nonzero"],"excluded",len(excluded),"castle",report["castle_compared"])
print("C3X027_NATIVE_BRANCHES",report["native_branch_counts"])
for m in mismatches[:6]:print("C3X027_BOUNDARY_MISMATCH",m["label"],m["uci"],m["threshold"],m["native"],m["independent"])
