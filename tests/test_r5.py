"""Offline checks on the public aggregate disclosure, without survey microdata."""
import csv
from pathlib import Path
import unittest

REPORT = Path(__file__).resolve().parents[1]/'reports/r5_2026_11_13'


def rows(name):
    with (REPORT/name).open() as f:
        return list(csv.DictReader(f))


class HouseholdExposureTests(unittest.TestCase):
    def test_matched_plus_unmatched_partition(self):
        cats = rows('category_exposures.csv')
        for g in rows('groups.csv'):
            values=[c for c in cats if all(c[k]==g[k] for k in ('year','group','level'))]
            self.assertEqual(len(values),9)
            self.assertAlmostEqual(sum(float(c['share_pct']) for c in values)+float(g['unmatched_pct']),100,places=6)
            self.assertAlmostEqual(sum(float(c['dec_gel']) for c in values)*.0025,float(g['saving_025_dec_gel']),places=6)
            self.assertAlmostEqual(float(g['two_channel_all_usd_survey_gel']),float(g['saving_025_survey_gel'])-float(g['loss_all_usd_gel']),places=6)

    def test_benchmark_vintage_and_diagnostics(self):
        anchors=rows('geostat_checks.csv')
        self.assertEqual(len(anchors),19)
        self.assertLess(max(abs(float(r['gap_gel'])) for r in anchors),.05)
        specs=rows('price_diagnostics.csv')
        self.assertEqual(len(specs),27)
        self.assertTrue(all(r['last']=='2024-12' and int(r['appreciation_months'])+int(r['depreciation_months'])==int(r['n']) for r in specs))
