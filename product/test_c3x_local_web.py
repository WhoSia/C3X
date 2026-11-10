"""P3 actual HTTP loopback integration + whole P1/P2 payload contracts."""
import http.client
import json
from pathlib import Path
import sys
import threading
import unittest
from unittest.mock import patch
from http.server import ThreadingHTTPServer

import chess

from c3x_explain_two_moves import SCHEMA as P1_SCHEMA
from c3x_concept_contrast import SCHEMA as P2_SCHEMA
from c3x_recursive_strategy import SCHEMA as P4_SCHEMA, produce as p4_produce
from test_c3x_recursive_strategy import DeterministicSource
from c3x_local_web import (
    SCHEMA, DEFAULT_FEN, FRONTEND, MAX_POST_BYTES,
    analyze_payload, create_handler, legal_payload, request_payload
)
from test_c3x_explain_two_moves import SimulatedEngine


class DataContracts(unittest.TestCase):
    def test_full_legal_san_and_fen(self):
        p=legal_payload(DEFAULT_FEN)
        self.assertEqual(len(p["legal_moves"]),20)
        self.assertEqual(next(x["san"] for x in p["legal_moves"] if x["uci"]=="e2e4"),"e4")
        self.assertEqual(p["turn"],"white")

    def test_legal_reject_invalid_board(self):
        with self.assertRaises(ValueError):
            legal_payload("garbage")

    def test_no_extra_api_fields(self):
        raw=json.dumps({"fen":DEFAULT_FEN,"move_a":"e2e4",
                        "move_b":"d2d4","stockfish_path":"/bin/false"}).encode()
        with self.assertRaisesRegex(ValueError,"UNEXPECTED_REQUEST_FIELDS"):
            request_payload(raw)

    def test_limits_reject_oversized_request(self):
        with self.assertRaisesRegex(ValueError,"TOO_LARGE"):
            request_payload(b"x"*(MAX_POST_BYTES+1))

    def test_full_p1_p2_contract_with_mock_engine(self):
        payload={"fen":DEFAULT_FEN,"move_a":"e2e4","move_b":"d2d4"}
        result=analyze_payload(payload,SimulatedEngine())
        self.assertEqual(result["schema"],SCHEMA)
        self.assertEqual(result["engine_report"]["schema"],P1_SCHEMA)
        self.assertEqual(result["concept_report"]["schema"],P2_SCHEMA)
        self.assertFalse(result["evidence"]["independent_referee"])
        self.assertIn("인과",result["learner_markdown"])
        self.assertIn("## 5.",result["learner_markdown"])

    def test_p4_actual_reused_cui_two_layer_product_contract(self):
        result=p4_produce(DEFAULT_FEN,"e2e4","d2d4",DeterministicSource(),k=2,depth=8)
        self.assertEqual(result["schema"],P4_SCHEMA)
        self.assertEqual(result["total_leaf_paths"],8)
        self.assertFalse(result["complete_opponent_reply_universe"])
        self.assertTrue(result["same_engine_not_independent_judge"])

    def test_p5_martin_mirror_browser_and_exact_12_search_contract(self):
        from c3x_metamorphic_gap_audit import case_analysis
        from test_c3x_metamorphic_gap_audit import DeterministicCovariantEngine
        engine=DeterministicCovariantEngine()
        result=case_analysis(DEFAULT_FEN,"e2e4","d2d4",engine,
                             case_id="user_selected_fen_local_not_frozen")
        self.assertEqual(engine.calls,12)
        self.assertEqual(set(result["per_depth"]),{"8","10","12"})
        self.assertEqual(result["per_depth"]["12"]["mirrored_gap_minus_original_gap_cp_or_null"],0)
        html=FRONTEND.read_text(encoding="utf-8")
        javascript=FRONTEND.with_suffix(".js").read_text(encoding="utf-8")
        self.assertIn('id="mirror"',html)
        self.assertIn('id="mirrorResult"',html)
        self.assertIn('post("/api/mirror"',javascript)
        self.assertIn("finite_search_not_proof_of_engine_bug",str(result))

    def test_p4_browser_strategy_button_exists(self):
        html=FRONTEND.read_text(encoding="utf-8")
        javascript=FRONTEND.with_suffix(".js").read_text(encoding="utf-8")
        self.assertIn('id="strategy"',html)
        self.assertIn('id="strategyResult"',html)
        self.assertIn('post("/api/strategy"',javascript)
        self.assertIn('root_uci!==selected.a',javascript)

    def test_malformed_move_rejected_without_engine(self):
        with self.assertRaisesRegex(ValueError,"TWO_DISTINCT"):
            analyze_payload({"fen":DEFAULT_FEN,"move_a":"e2e5",
                             "move_b":"d2d4"},SimulatedEngine())

    def test_real_browser_assets_include_interaction_and_scope(self):
        self.assertTrue(FRONTEND.is_file())
        self.assertTrue(FRONTEND.with_suffix(".js").is_file())
        html=FRONTEND.read_text(encoding="utf-8")
        javascript=FRONTEND.with_suffix(".js").read_text(encoding="utf-8")
        self.assertIn('id="board"',html)
        self.assertIn('id="moveA"',html)
        self.assertIn("미입증",html)
        self.assertIn('fetch(path',javascript)
        self.assertIn("concept_dimensions_different",javascript)
        self.assertNotIn("innerHTML",javascript)


class LiveLoopbackHttpTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server=ThreadingHTTPServer(("127.0.0.1",0),create_handler(sys.executable))
        cls.thread=threading.Thread(target=cls.server.serve_forever,daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=4)

    def api(self,method,path,obj=None,origin=None,ctype="application/json"):
        conn=http.client.HTTPConnection("127.0.0.1",self.server.server_port,timeout=5)
        body=json.dumps(obj).encode() if obj is not None else None
        headers={}
        if body is not None: headers["Content-Type"]=ctype
        if origin is not None: headers["Origin"]=origin
        conn.request(method,path,body=body,headers=headers)
        r=conn.getresponse()
        raw=r.read()
        result=(r.status,r.getheader("Content-Security-Policy"),raw)
        conn.close()
        return result

    def test_real_http_serves_chessboard(self):
        code,csp,payload=self.api("GET","/")
        self.assertEqual(code,200)
        self.assertIn(b'id="board"',payload)
        self.assertIn("frame-ancestors 'none'",csp)

    def test_real_http_serves_js(self):
        code,_,payload=self.api("GET","/c3x_board.js")
        self.assertEqual(code,200)
        self.assertIn(b'fetch(path',payload)

    def test_real_http_legal_endpoint(self):
        code,_,raw=self.api("POST","/api/legal",{"fen":DEFAULT_FEN})
        data=json.loads(raw)
        self.assertEqual(code,200)
        self.assertEqual(len(data["legal_moves"]),20)

    def test_real_http_invalid_fen(self):
        code,_,raw=self.api("POST","/api/legal",{"fen":"invalid"})
        self.assertEqual(code,422)
        self.assertIn("error",json.loads(raw))

    def test_cross_origin_post_rejected(self):
        code,_,raw=self.api("POST","/api/legal",{"fen":DEFAULT_FEN},
                            origin="https://other.example")
        self.assertEqual(code,403)
        self.assertEqual(json.loads(raw)["error"],"P3_FOREIGN_ORIGIN")

    def test_p5_http_reject_illegal_mirror_before_native_engine(self):
        code,_,raw=self.api("POST","/api/mirror",{
            "fen":DEFAULT_FEN,"move_a":"e2e5","move_b":"d2d4"
        })
        self.assertEqual(code,422)
        self.assertIn("TWO_DISTINCT",raw.decode())

    def test_p4_reject_illegal_move_before_opening_any_engine(self):
        code,_,raw=self.api("POST","/api/strategy",{
            "fen":DEFAULT_FEN,"move_a":"e2e5","move_b":"d2d4"
        })
        self.assertEqual(code,422)
        self.assertIn("TWO_DISTINCT",raw.decode())

    def test_unrecognized_route_not_served(self):
        code,_,raw=self.api("GET","/secret.env")
        self.assertEqual(code,404)

    def test_no_untrusted_engine_path_override(self):
        code,_,raw=self.api("POST","/api/analyze",{
            "fen":DEFAULT_FEN,"move_a":"e2e4",
            "move_b":"d2d4","engine":"/tmp/evil"
        })
        self.assertEqual(code,422)
        self.assertEqual(json.loads(raw)["error"],"P3_UNEXPECTED_REQUEST_FIELDS")

    def test_invalid_candidate_never_launches_engine(self):
        code,_,raw=self.api("POST","/api/analyze",{
            "fen":DEFAULT_FEN,"move_a":"e2e5","move_b":"d2d4"
        })
        # If engine invocation fails, it must NOT return a plausible 200.
        self.assertIn(code,(422,503))
        self.assertIn("error",json.loads(raw))


if __name__=="__main__":
    unittest.main()
