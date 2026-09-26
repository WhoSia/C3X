#!/usr/bin/env python3
import argparse,hashlib,json
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path

STAGE="C3X 0.7.0-G9.5-P4"

def canon(o):return json.dumps(o,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()
def digest(o):return hashlib.sha256(canon(o)).hexdigest()

class FieldService:
 def __init__(self,field,deployment):
  self.field=field
  self.deployment=deployment
  if deployment.get("schema")!="c3x-g95-p4-public-deployment-v1":raise ValueError("deployment schema")
  if deployment.get("scientific_stage")!=STAGE:raise ValueError("deployment stage")
  self.schema=field.get("selected_global_schema")
  self.public=bool(deployment.get("public_global_authority"))
  self.field_sha256=None if self.schema is None else digest(self.schema)
  if self.field_sha256!=deployment.get("field_sha256"):raise ValueError("field identity mismatch")

 def _cell(self,p):
  if self.schema is None:return None,None
  parts=[p["fiber_id"]]
  for c in self.schema["coordinates"]:parts.append(f"{c}={p['context'][c]}")
  k="||".join(parts);return k,self.schema["cells"].get(k)

 def internal_query(self,p):
  k,c=self._cell(p)
  if self.schema is None:return {"status":"ABSTAIN_NO_GLOBAL_FIELD","predicted_root_change":None,"cell_key":None,"support":0}
  if c is None:return {"status":"ABSTAIN_UNSEEN_CONTEXT","predicted_root_change":None,"cell_key":k,"support":0}
  y=c["label"]=="ROOT_CHANGE"
  return {"status":"CERTIFIED_ROOT_CHANGE" if y else "CERTIFIED_NO_ROOT_CHANGE","predicted_root_change":y,"cell_key":k,"support":c["support"]}

 def query(self,p):
  q=self.internal_query(p)
  if not self.public:
   return {"schema":"c3x-p4-service-certificate-v1","scientific_stage":STAGE,
    "status":"ABSTAIN_UNCERTIFIED_FIELD","predicted_root_change":None,"cell_key":q["cell_key"],
    "discovery_support":q["support"],"public_global_authority":False,
    "field_sha256":self.field_sha256,"verdict":self.deployment["verdict"]}
  return {"schema":"c3x-p4-service-certificate-v1","scientific_stage":STAGE,
   "status":q["status"],"predicted_root_change":q["predicted_root_change"],"cell_key":q["cell_key"],
   "discovery_support":q["support"],"public_global_authority":True,
   "field_sha256":self.field_sha256,"verdict":self.deployment["verdict"]}

 def explain(self,p):
  q=self.query(p)
  if q["status"]=="CERTIFIED_ROOT_CHANGE":
   text="The held-out-certified P4 field licenses ROOT_CHANGE for this covered context under the frozen replay regime."
  elif q["status"]=="CERTIFIED_NO_ROOT_CHANGE":
   text="The held-out-certified P4 field licenses NO_ROOT_CHANGE for this covered context under the frozen replay regime."
  elif q["status"]=="ABSTAIN_UNSEEN_CONTEXT":
   text="This context was not represented by a certified field cell, so the service abstains."
  else:
   text="No held-out-certified global P4 field is authorized for public certification, so the service abstains."
  ast=[
   {"type":"AUTHORITY","status":q["status"],"public_global_authority":q["public_global_authority"]},
   {"type":"PROVENANCE","source_stratum":p.get("source_stratum"),"sampling_stratum":p.get("sampling_stratum")},
   {"type":"LIMITATION","text":"The service cannot expand authority beyond the frozen P4 field and held-out transport certificate."}
  ]
  return {"schema":"c3x-p4-service-explanation-v1","scientific_stage":STAGE,"certificate":q,"ast":ast,"text":text,"llm_used":False}

 def diagnose(self,p,observed):
  q=self.internal_query(p)
  if q["predicted_root_change"] is None:classification=q["status"]
  elif bool(q["predicted_root_change"])!=bool(observed):classification="CONTRADICTED_CONTEXT_CELL"
  else:classification="CONSISTENT_COVERED_CONTEXT"
  return {"schema":"c3x-p4-service-diagnosis-v1","scientific_stage":STAGE,
   "authority":"POST_TARGET_DIAGNOSTIC_ONLY","may_expand_public_authority":False,
   "internal_field_query":q,"observed_root_change":bool(observed),"classification":classification}

class Handler(BaseHTTPRequestHandler):
 service=None
 def _send(self,code,obj):
  b=(json.dumps(obj,sort_keys=True)+"\n").encode()
  self.send_response(code);self.send_header("Content-Type","application/json")
  self.send_header("Content-Length",str(len(b)));self.end_headers();self.wfile.write(b)
 def _json(self):
  n=int(self.headers.get("Content-Length","0"));return json.loads(self.rfile.read(n) or b"{}")
 def do_GET(self):
  if self.path=="/health":
   self._send(200,{"status":"ok","scientific_stage":STAGE,"service":"c3x-authority-conservative-explanation-service",
    "llm_dependency":False,"deterministic_core":True,"public_global_authority":self.service.public,
    "field_sha256":self.service.field_sha256,"verdict":self.service.deployment["verdict"]})
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
 ap=argparse.ArgumentParser(description="C3X P4 authority-conservative deterministic explanation service")
 ap.add_argument("--field",required=True);ap.add_argument("--deployment",required=True)
 ap.add_argument("--host",default="127.0.0.1");ap.add_argument("--port",type=int,default=8765)
 a=ap.parse_args()
 field=json.loads(Path(a.field).read_text());deployment=json.loads(Path(a.deployment).read_text())
 Handler.service=FieldService(field,deployment);srv=ThreadingHTTPServer((a.host,a.port),Handler)
 print(f"C3X_P4_SERVICE_READY http://{a.host}:{a.port}",flush=True);srv.serve_forever()

if __name__=="__main__":main()
