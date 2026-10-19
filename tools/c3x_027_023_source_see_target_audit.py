import json,hashlib
from pathlib import Path
import chess
SOURCE=Path("source/C3X023_P1_MAY_BROADCAST_CC0_NONMATE32_SOURCE_ONLY.json")
TARGET=Path("targets/C3X023_P1_R2_T2_PREACTUATOR_EXACT_TARGETS_MAY_CC_BY_SA.json")
def checked(p,sha):
 b=p.read_bytes()
 assert hashlib.sha256(b).hexdigest()==sha,(p,"source SHA mismatch")
 return json.loads(b)
s=checked(SOURCE,"0ff43e28dcb3a5e48dea6b61e4450fc8bb9e1f96363871c33c4b73524664db61")
t=checked(TARGET,"830536f445330b739a7a3b7e88ce4227e9ab9db43cf277f08a01ed5f9dc0ef69")
rows=[]
for row in t["cases"]:
 q=row["source_exact_pruning_SEE_target"]
 if not q:continue
 original=s["per_ecology"]["may2026_broadcast"]["selected"][row["game_id"]-1]
 fen=original["fen4"]+" "+str(original["source_halfmove_clock"])+" "+str(original["source_fullmove_number"])
 b=chess.Board(fen)
 assert b.is_valid()
 move=q["move"];from_sq=chess.square_name((move>>6)&63);to_sq=chess.square_name(move&63)
 uci=from_sq+to_sq
 native_uci=chess.square_name((q["root_move"]>>6)&63)+chess.square_name(q["root_move"]&63)
 record={"id":row["game_id"],"original_game_sha256":original["source_game_sha256"],"root_fen":fen,"root_position_legal_move_count":b.legal_moves.count(),"root_candidate_native_uci":native_uci,"event_site":q["site"],"event_uci_from_native_bitfields":uci,"event_native_move":move,"event_threshold_cp":q["threshold"],"event_depth":q["t1_depth"],"event_ply":q["t1_ply"],"event_alpha":q["t1_alpha"],"event_beta":q["t1_beta"],"event_rule50":q["t1_rule50"],"event_source_key64":str(q["key64"]),"event_path":q["t1_path"],"event_move_is_legal_AT_ROOT_not_at_event":chess.Move.from_uci(uci) in b.legal_moves,"event_native_position_reconstructed":False}
 rows.append(record)
assert len(rows)==2
out={"schema":"c3x027-023-recovered-source-target-audit-v1","source_event_position_available":False,"tested_scope":"source root legal chess + native SEE event signatures; not event-state SEE exchange","cases":rows}
Path("C3X_027_023_SOURCE_SEE_TARGET_AUDIT.json").write_text(json.dumps(out,indent=2)+"\n")
for r in rows:print("SEE_SOURCE_TARGET_AUDIT",r["id"],r["event_uci_from_native_bitfields"],r["event_threshold_cp"],r["event_move_is_legal_AT_ROOT_not_at_event"])
print("SEE_SOURCE_TARGET_AUDIT_PASS",len(rows))
