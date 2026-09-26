#!/usr/bin/env python3
import argparse,json
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path

STAGE="C3X 0.7.0-G9.5-P3"

class FieldService:
 def __init__(self,field):
  self.field=field
  if field.get("schema")!="c3x-field-p3-discovery-v1":raise ValueError("field schema")
  self.schema=field.get("selected_global_schema")
  if not self.schema:raise ValueError("no selected global schema")
  self.coords=list(self.schema["coordinates"]);self.cells=self.schema["cells"]
 def cell_key(self,p):
  return "||".join([p["fiber_id"]]+[f"{c}={p['context'][c]}" for c in self.coords])
 def query(self,p):
  k=self.cell_key(p);c=self.cells.get(k)
  if not c:return {"schema":"c3x-service-certificate-v1","scientific_stage":STAGE,"record_id":p.get("record_id"),"schema_id":self.schema["id"],"cell_key":k,"status":"ABSTAIN_UNSEEN_CONTEXT","predicted_root_change":None,"discovery_support":0}
  y=c["label"]=="ROOT_CHANGE"
  return {"schema":"c3x-service-certificate-v1","scientific_stage":STAGE,"record_id":p.get("record_id"),"schema_id":self.schema["id"],"cell_key":k,"status":"CERTIFIED_ROOT_CHANGE" if y else "CERTIFIED_NO_ROOT_CHANGE","predicted_root_change":y,"discovery_support":c["support"]}
 def explain(self,p):
  q=self.query(p)
  if q["status"]=="ABSTAIN_UNSEEN_CONTEXT":
   text=f"{p.get('record_id','event')}: ABSTAIN_UNSEEN_CONTEXT. The event's topology-aware context cell was not observed in the frozen discovery field, so no ROOT_CHANGE label is licensed."
  else:
   text=f"{p.get('record_id','event')}: {q['status']}. The frozen {q['schema_id']} field contains this F0/context cell with discovery support {q['discovery_support']}. This licenses only the tested singleton-removal ROOT_CHANGE query under the frozen execution envelope."
  return {"schema":"c3x-service-explanation-v1","scientific_stage":STAGE,"certificate":q,"ast":[{"type":"FIBER","fiber_id":p["fiber_id"]},{"type":"CONTEXT_SCHEMA","schema_id":q["schema_id"],"coordinates":{c:p["context"][c] for c in self.coords}},{"type":"AUTHORITY","status":q["status"],"support":q["discovery_support"]},{"type":"LIMITATION","text":"No universal mechanism, cognition, strategy, or out-of-scope transport claim."}],"text":text,"llm_used":False}
 def diagnose(self,p,observed):
  q=self.query(p);contradiction=q["predicted_root_change"] is not None and bool(q["predicted_root_change"])!=bool(observed)
  return {"schema":"c3x-service-diagnosis-v1","scientific_stage":STAGE,"authority":"POST_TARGET_DIAGNOSTIC_ONLY","may_modify_field":False,"certificate":q,"observed_root_change":bool(observed),"contradiction":contradiction,"classification":"ABSTAIN_UNSEEN_CONTEXT" if q["predicted_root_change"] is None else "CONTRADICTED_CONTEXT_CELL" if contradiction else "CONSISTENT_COVERED_CONTEXT"}

class Handler(BaseHTTPRequestHandler):
 service=None
 def _send(self,code,obj):
  b=(json.dumps(obj,sort_keys=True)+"\n").encode();self.send_response(code);self.send_header("Content-Type","application/json");self.send_header("Content-Length",str(len(b)));self.end_headers();self.wfile.write(b)
 def _json(self):
  n=int(self.headers.get("Content-Length","0"));return json.loads(self.rfile.read(n) or b"{}")
 def do_GET(self):
  if self.path=="/health":self._send(200,{"status":"ok","scientific_stage":STAGE,"service":"c3x-explanation-service","llm_dependency":False})
  else:self._send(404,{"error":"not_found"})
 def do_POST(self):
  try:
   x=self._json()
   if self.path=="/v1/query":self._send(200,self.service.query(x["profile"]))
   elif self.path=="/v1/explain":self._send(200,self.service.explain(x["profile"]))
   elif self.path=="/v1/diagnose":self._send(200,self.service.diagnose(x["profile"],x["observed_root_change"]))
   else:self._send(404,{"error":"not_found"})
  except Exception as e:self._send(400,{"error":type(e).__name__,"detail":str(e)})
 def log_message(self,*args):pass

def main():
 ap=argparse.ArgumentParser(description="Deterministic C3X explanation-service API. No LLM required.")
 ap.add_argument("--field",required=True);ap.add_argument("--host",default="127.0.0.1");ap.add_argument("--port",type=int,default=8765);a=ap.parse_args()
 field=json.loads(Path(a.field).read_text());Handler.service=FieldService(field);srv=ThreadingHTTPServer((a.host,a.port),Handler)
 print(f"C3X_SERVICE_READY http://{a.host}:{a.port}",flush=True);srv.serve_forever()

if __name__=="__main__":main()
