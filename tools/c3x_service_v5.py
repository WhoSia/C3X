#!/usr/bin/env python3
import argparse,hashlib,json
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
STAGE="C3X 0.7.0-G9.5-P7"
def canon(o):return json.dumps(o,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()
def digest(o):return hashlib.sha256(canon(o)).hexdigest()
class Service:
 def __init__(self,field,dep):
  self.field=field;self.dep=dep;self.q=field.get("selected_q_level");self.map=field.get("state_map",{});self.public=bool(dep["public_global_authority"])
  fid={"q_level":self.q,"state_map":self.map}
  if digest(fid)!=dep["field_sha256"]:raise ValueError("field identity mismatch")
 def internal(self,p):
  if not self.q:return {"status":"ABSTAIN_NO_CERTIFIED_SEARCH_STATE","predicted_root_change":None,"state_id":None,"train_support":0}
  sid=p["state_ids"][self.q];z=self.map.get(sid)
  if not z:return {"status":"ABSTAIN_UNSEEN_STATE","predicted_root_change":None,"state_id":sid,"train_support":0}
  y=z["label"]=="ROOT_CHANGE"
  return {"status":"CERTIFIED_ROOT_CHANGE" if y else "CERTIFIED_NO_ROOT_CHANGE","predicted_root_change":y,"state_id":sid,"train_support":z["support"]}
 def query(self,p):
  q=self.internal(p)
  if not self.public:return {"schema":"c3x-p7-service-certificate-v1","scientific_stage":STAGE,"status":"ABSTAIN_UNCERTIFIED_FIELD",
   "predicted_root_change":None,"state_id":q["state_id"],"train_support":q["train_support"],"public_global_authority":False,
   "selected_q_level":self.q,"verdict":self.dep["verdict"]}
  st="ABSTAIN_UNSEEN_CONTEXT" if q["predicted_root_change"] is None else q["status"]
  return {"schema":"c3x-p7-service-certificate-v1","scientific_stage":STAGE,"status":st,"predicted_root_change":q["predicted_root_change"],
   "state_id":q["state_id"],"train_support":q["train_support"],"public_global_authority":True,"selected_q_level":self.q,"verdict":self.dep["verdict"]}
 def explain(self,p):
  q=self.query(p)
  if q["status"]=="CERTIFIED_ROOT_CHANGE":txt="This held-out-certified chess search state predicts that suppressing the selected TT semantic-use event changes the engine's root move."
  elif q["status"]=="CERTIFIED_NO_ROOT_CHANGE":txt="This held-out-certified chess search state predicts that the engine's root move is preserved under the exact-event suppression."
  elif q["status"]=="ABSTAIN_UNSEEN_CONTEXT":txt="This chess search prefix is outside the certified state map, so the service abstains."
  else:txt="No held-out-certified chess search-state field is authorized, so the service abstains."
  return {"schema":"c3x-p7-service-explanation-v1","scientific_stage":STAGE,"certificate":q,
   "ast":[{"type":"AUTHORITY","status":q["status"]},{"type":"CHESS_SEARCH_STATE","q_level":self.q,"state_id":q["state_id"]},
    {"type":"LIMITATION","text":"The state is an operational engine-search abstraction, not a human-intent claim."}],"text":txt,"llm_used":False}
 def diagnose(self,p,observed):
  q=self.internal(p)
  if q["predicted_root_change"] is None:cl=q["status"]
  elif bool(q["predicted_root_change"])!=bool(observed):cl="CONTRADICTED_SEARCH_STATE"
  else:cl="CONSISTENT_COVERED_STATE"
  return {"schema":"c3x-p7-service-diagnosis-v1","scientific_stage":STAGE,"authority":"POST_TARGET_DIAGNOSTIC_ONLY",
   "may_expand_public_authority":False,"internal_query":q,"observed_root_change":bool(observed),"classification":cl}
class H(BaseHTTPRequestHandler):
 service=None
 def sendj(self,code,o):
  b=(json.dumps(o,sort_keys=True)+"\n").encode();self.send_response(code);self.send_header("Content-Type","application/json");self.send_header("Content-Length",str(len(b)));self.end_headers();self.wfile.write(b)
 def body(self):return json.loads(self.rfile.read(int(self.headers.get("Content-Length","0"))) or b"{}")
 def do_GET(self):
  if self.path=="/health":self.sendj(200,{"status":"ok","scientific_stage":STAGE,"service":"c3x-p7-chess-search-state","llm_dependency":False,"public_global_authority":self.service.public,"selected_q_level":self.service.q,"verdict":self.service.dep["verdict"]})
  else:self.sendj(404,{"error":"not_found"})
 def do_POST(self):
  try:
   x=self.body()
   if self.path=="/v1/query":self.sendj(200,self.service.query(x["profile"]))
   elif self.path=="/v1/explain":self.sendj(200,self.service.explain(x["profile"]))
   elif self.path=="/v1/diagnose":self.sendj(200,self.service.diagnose(x["profile"],x["observed_root_change"]))
   else:self.sendj(404,{"error":"not_found"})
  except Exception as e:self.sendj(400,{"error":type(e).__name__,"detail":str(e)})
 def log_message(self,*args):pass
def main():
 ap=argparse.ArgumentParser();ap.add_argument("--field",required=True);ap.add_argument("--deployment",required=True);ap.add_argument("--host",default="127.0.0.1");ap.add_argument("--port",type=int,default=8767);a=ap.parse_args()
 f=json.loads(Path(a.field).read_text());d=json.loads(Path(a.deployment).read_text());H.service=Service(f,d);srv=ThreadingHTTPServer((a.host,a.port),H);print(f"C3X_P7_SERVICE_READY http://{a.host}:{a.port}",flush=True);srv.serve_forever()
if __name__=="__main__":main()
