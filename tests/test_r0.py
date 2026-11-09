"""R0 regression checks: fail closed on absent required outputs and damaged sources."""
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from src import validate_episode
from replication.audit_r0 import audit


class R0Tests(unittest.TestCase):
    def test_previously_optional_output_is_required(self):
        for name in ['reserve_liquidity_cells.csv','money_transfers_country.csv']:
            with tempfile.TemporaryDirectory() as folder:
                root=Path(folder)
                (root/'catalogue.json').write_text(json.dumps([{'file':name,'sha256':'0'*64}]))
                with patch.object(validate_episode,'ROOT',root),patch.object(validate_episode,'DATA',root):
                    with self.assertRaisesRegex(ValueError,'Missing required derived outputs'):
                        validate_episode.validate()

    def test_access_audit_distinguishes_absent_and_damaged(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);(root/'data/derived/episode_2026_11_09').mkdir(parents=True)
            source={'id':'x','url':'https://example.invalid/x','local_path':'x.json','sha256':'0'*64,'bytes':2,'format':'json'}
            (root/'data/source_manifest.json').write_text(json.dumps([source]))
            (root/'data/derived/episode_2026_11_09/catalogue.json').write_text('[]')
            absent,_=audit(root)
            self.assertEqual(absent[0]['local_verification'],'absent')
            (root/'x.json').write_text('{}')
            broken,_=audit(root)
            self.assertEqual(broken[0]['local_verification'],'mismatch')
            self.assertFalse(broken[0]['remote_vintage_recovery_tested_in_R0'])


if __name__=='__main__':unittest.main()
