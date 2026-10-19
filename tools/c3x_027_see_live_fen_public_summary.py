import json,sys,hashlib
from pathlib import Path
v=json.loads(Path(sys.argv[1]).read_text()); rows=v["records"]
safe=[{"move":r["move"],"threshold":r["threshold"],"site":r["site"],"legal_at_actual_SEE_board":r["move_legal_at_internal_event"],"native_see_boolean":r["original_see"],"live_fen_sha256":hashlib.sha256(r["fen"].encode()).hexdigest()} for r in rows]
Path(sys.argv[2]).write_text(json.dumps({"schema":"c3x027-public-source-event-minimal-audit","count":len(safe),"events":safe,"not_full_game_PGN_or_live_fen":True,"native_SEE_mediation_not_proven":True},indent=2)+"\n")
print("C3X027_SEE_PUBLIC_SUMMARY_PASS",len(safe))
