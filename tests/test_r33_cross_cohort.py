"""Reproducibility tests for R33. Needs the two sealed archives at supplied paths."""
import copy
import json
import os
from pathlib import Path
import sys
import unittest
from zipfile import ZipFile

from r33_cross_cohort import (
    audit, inspect_case, public_signature, require, run, stable_read, verify_manifest
)

BASE=Path('/mnt/data')
R29=Path(os.getenv('C3X_R29_ZIP',BASE/'C3X-030-R29-native-unseen-20261121.zip'))
R30=Path(os.getenv('C3X_R30_ZIP',BASE/'C3X-R30-TWIC1664-20261121.zip'))


class R33Unit(unittest.TestCase):
    def test_signature_is_score_pv_only(self):
        before=b'info depth 8 seldepth 10 multipv 1 score cp 31 nodes 200 nps 999 time 1 pv e2e4 e7e5\nbestmove e2e4\n'
        after=b'info depth 8 seldepth 20 multipv 1 score cp 31 nodes 400 nps 2 time 100 pv e2e4 e7e5\nbestmove e2e4\n'
        self.assertEqual(public_signature(before), public_signature(after))
        self.assertNotEqual(public_signature(before),public_signature(after.replace(b'score cp 31',b'score cp 30')))
        self.assertNotEqual(public_signature(before),public_signature(after.replace(b'e7e5',b'c7c5')))
        self.assertNotEqual(public_signature(before),public_signature(after.replace(b'pv e2e4',b'lowerbound pv e2e4')))

    def test_incomplete_public_line_fails(self):
        with self.assertRaisesRegex(ValueError,'incomplete info'):
            public_signature(b'info depth 10 score cp 4\n')

    def test_mask_only_changes_dynamic_read(self):
        r={'seq':'100','attempt':'3','key':'7','mask':'0','effective':'a2a3',
           'root':'h2h3','value':'-2'}
        masked=dict(r,mask='1',effective='(none)')
        self.assertEqual(stable_read(r),stable_read(masked))
        masked['key']='8'
        self.assertNotEqual(stable_read(r),stable_read(masked))

    def test_all_sha_entries_and_cross_cohort_numbers(self):
        result=run(R29,R30)
        self.assertEqual(result['source']['R29']['manifest_files_verified'],300)
        self.assertEqual(result['source']['R30']['manifest_files_verified'],262)
        self.assertEqual(result['counts']['R29']['interventions'],25)
        self.assertEqual(result['counts']['R30']['interventions'],32)
        self.assertEqual(result['counts']['all']['positions'],51)
        self.assertEqual(result['counts']['all']['direct_child_return_changed'],28)
        self.assertEqual(result['counts']['all']['direct_child_return_changed_unobserved'],2)
        self.assertEqual(result['counts']['all']['changed_child_invisible_in_score_pv'],15)
        self.assertEqual(result['counts']['all']['final_recommendation_changed'],3)
        self.assertEqual(result['counts']['all']['local_leader_changed_but_final_move_stable'],2)
        self.assertEqual(result['counts']['all']['post_intervention_third_move'],1)
        self.assertEqual((result['source']['R29']['no_selected_event'],result['source']['R30']['no_selected_event']),(10,3))

    def test_claims_and_third_candidate_coverage(self):
        result=run(R29,R30)
        by_id={(r['id'],r['policy']):r for r in result['rows']}
        self.assertEqual(by_id[('R29-018','move')]['explanation_permission'],'local_search_effect_only')
        self.assertTrue(by_id[('R30-028','move')]['root_candidate_leader_update_changed'])
        self.assertFalse(by_id[('R30-028','move')]['final_recommendation_changed'])
        self.assertEqual(by_id[('R30-017','move')]['final_bestmove'],{'before':'e2f3','after':'e2d3'})
        self.assertTrue(by_id[('R30-017','move')]['post_intervention_third_move'])
        self.assertFalse(by_id[('R30-017','move')]['post_intervention_independent_judge_coverage'])
        self.assertEqual({r['independent_reference_judge_label'] for r in result['rows'] if r['final_recommendation_changed']},{'unresolved'})

    def test_corrupt_restore_rejected(self):
        with ZipFile(R29) as z:
            j=json.loads(z.read('unseen-logs/result.json'))
            c=copy.deepcopy(j['positions'][0]);c['arms']['move']['restore']['best']['move']='0000'
            with self.assertRaisesRegex(ValueError, 'restore mismatch'):
                inspect_case('R29',c,'move',c['arms']['move'],z)

    def test_corrupt_source_child_identity_rejected(self):
        with ZipFile(R29) as z:
            j=json.loads(z.read('unseen-logs/result.json'))
            c=copy.deepcopy(j['positions'][0]);a=c['arms']['move']
            a['mask']['read']['root']='0000'
            with self.assertRaisesRegex(ValueError, 'pre-treatment read mismatch'):
                inspect_case('R29',c,'move',a,z)

    def test_public_trajectory_does_not_use_nodes_as_credential(self):
        sig=public_signature(b'info depth 1 multipv 1 score cp 4 nodes 1 nps 2 time 1 pv e2e4\n')
        self.assertEqual(sig,[dict(depth=1,multipv=1,score_type='cp',score_value=4,bound='exact',pv=['e2e4'])])

    def test_unobserved_child_retained(self):
        result=run(R29,R30)
        bad=[r for r in result['rows'] if r['direct_child_return_changed'] is None]
        self.assertEqual(len(bad),2)
        self.assertTrue(all(r['explanation_permission']=='child_effect_unobserved' for r in bad))


if __name__=='__main__':unittest.main()
