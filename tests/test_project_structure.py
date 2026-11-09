"""Preservation, authoritative scope, acquisition schema and transferred arithmetic."""
import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('repository_checks', ROOT / 'replication/check_repository.py')
checks = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checks)


class ProjectTests(unittest.TestCase):
    def test_retained_evidence_matches_original_hashes(self):
        self.assertEqual(checks.archive_check(), {'archived_unchanged': 120, 'git_history_only': 24, 'root_configuration': 2})

    def test_authoritative_identity_sources_and_links(self):
        self.assertEqual(checks.documentation_check()['requirements'], 18)

    def test_requirements_cover_each_evidence_gate(self):
        rows = json.loads((ROOT / 'research/data_requirements.json').read_text())['requirements']
        self.assertEqual({g for row in rows for g in row['gates']}, {'G1', 'G2', 'G3', 'G4', 'G5'})
        self.assertEqual(len([r for r in rows if r['priority'] == 'P0']), 7)
        self.assertTrue(all('publication' in ' '.join(r['variables']) for r in rows if r['id'] == 'D01'))

    def test_archived_partial_coverage_remains_partial(self):
        # Numerical assertions transferred from the retired editorial/speech test.
        rows = {r['id']: r for r in json.loads((ROOT / 'archive/legacy/reports/accountability/evidence_ledger.json').read_text())}
        self.assertAlmostEqual(rows['P02']['value'] + rows['P03']['value'], 100)
        self.assertLess(rows['P01']['value'], rows['P02']['value'])
        self.assertIn('Partial category exposure only', rows['P05']['uncertainty_and_limitations'])


if __name__ == '__main__':
    unittest.main()
