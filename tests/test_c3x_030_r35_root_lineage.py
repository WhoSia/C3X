"""Tests of the R33-040 R34 retroactive root lineage gate."""
import json
import os
from pathlib import Path
import unittest
from zipfile import ZipFile

from r35_root_lineage import audit, records, one

ARCHIVE=Path(os.getenv('C3X_R34_ZIP','/mnt/data/C3X_030_R34_fixed_depth_20261121.zip'))

class R35Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result=audit(ARCHIVE)

    def test_entire_manifest_and_replays(self):
        self.assertEqual(self.result['manifest_files_verified'],185)
        self.assertEqual(self.result['sha256_zip'], 'c4f01a19665e7bb8781316e4f1a13d9a91c2cf4b0bf35eea5d962851c53f697a')
        self.assertEqual(len(self.result['results']),2)

    def test_distinct_event_sources_converge(self):
        a,b=self.result['results']
        self.assertEqual((a['event_attempt'],a['event_root'],a['target_event']),(20,'a5c7',32))
        self.assertEqual((b['event_attempt'],b['event_root'],b['target_event']),(24,'d4b3',102))
        self.assertEqual((a['event_before'],a['event_after']),('401','952'))
        self.assertEqual((b['event_before'],b['event_after']),('528','454'))
        for x in (a,b):
            self.assertEqual(x['final_moves'],['h2h3','a5c7'])
            self.assertEqual(x['same_window_h3_competition']['base_update'],'1')
            self.assertEqual(x['same_window_h3_competition']['treated_update'],'0')
            self.assertEqual(x['same_window_h3_competition']['base_value'],392)
            self.assertEqual((x['matched_root_window']['alpha'],x['matched_root_window']['beta']),(367,407))
            self.assertEqual(x['treated_aspiration_retry_start']['attempt'],'25')
            self.assertEqual(x['treated_aspiration_retry_end']['move'],'a5c7')
        self.assertEqual((a['same_window_h3_competition']['treated_value'],b['same_window_h3_competition']['treated_value']),(363,367))

    def test_repeat_is_full_trace_identical(self):
        with ZipFile(ARCHIVE) as z:
            for s,target in [('0',32),('1',102)]:
                a,b=one(z,s,0,target),one(z,s,1,target)
                for k in a:
                    if k!='repeat':self.assertEqual(a[k],b[k])

    def test_reject_malformed(self):
        with self.assertRaisesRegex(ValueError,'malformed'):
            records(b'C3X_R23_START attempt=1 damaged\n','C3X_R23_START')
        with self.assertRaisesRegex(ValueError,'duplicate key'):
            records(b'C3X_R23_START attempt=1 attempt=2\n','C3X_R23_START')

    def test_no_false_claim_of_mediation(self):
        self.assertIn('not yet mapped',self.result['results'][0]['comparison_limit'])
        self.assertIn('independent board superiority',self.result['unproven'])

if __name__=='__main__':unittest.main()
