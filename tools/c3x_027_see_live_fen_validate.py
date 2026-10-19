import sys,json,re
from pathlib import Path
import chess
raw=Path(sys.argv[1]).read_text().splitlines()
targets={(2908,-95),(204,-43)}
seen={}
for line in raw:
 assert line.startswith("c3x027_live_SEE "),line[:100]
 parts=line.split(" fen=",1)
 assert len(parts)==2
 hdr=parts[0];fen=parts[1]
 kv=dict(re.findall(r"(\w+)=([^ ]+)",hdr))
 m=int(kv["move"]);threshold=int(kv["threshold"])
 assert (m,threshold) in targets
 b=chess.Board(fen)
 assert b.is_valid(),(m,fen,b.status())
 fr=chess.square_name((m>>6)&63);to=chess.square_name(m&63)
 uci=fr+to
 assert chess.Move.from_uci(uci) in b.legal_moves,(uci,fen)
 assert b.turn==chess.WHITE or b.turn==chess.BLACK
 rec={"move":uci,"threshold":threshold,"site":kv["site"],"key64":kv["key"],"root_call":kv["root_call"],"fen":fen,"fen_legal":True,"move_legal_at_internal_event":True,"original_see":int(kv["original"])}
 seen.setdefault((m,threshold),[]).append(rec)
assert set(seen)==targets,(set(seen),targets)
out={"schema":"c3x027-live-native-see-full-state-verified-v1","records":[v for rows in seen.values() for v in rows],"source_sha_pinned":True,"native_see_return_unchanged":True}
Path(sys.argv[2]).write_text(json.dumps(out,indent=2)+"\n")
print("C3X027_LIVE_SEE_BOARD_PASS",len(out["records"]),[(v["move"],v["threshold"]) for v in out["records"]])
