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


class CPIIdentityTests(unittest.TestCase):
    @staticmethod
    def module():
        import importlib.util
        path = REPORT.parents[1]/'src/r5_cpi.py'
        spec = importlib.util.spec_from_file_location('r5_cpi',path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def test_same_numeric_code_at_another_level_never_overwrites(self):
        mod = self.module()
        required = [(lev, k, label, 100+k) for k,(lev,label) in mod.SERIES.items()]
        collisions = [(2, 11, 'Restaurants and hotels', 600), (2, 12, 'Miscellaneous goods and services', 500)]
        for layout in (required+collisions, collisions+required):
            selected = mod.select_series(layout)
            self.assertEqual(selected[11][1], (3, 11, 'Food', 111))
            self.assertEqual(selected[12][1], (3, 12, 'Non-alcoholic beverages', 112))

    def test_missing_or_ambiguous_series_fails(self):
        mod = self.module()
        required = [(level,code,label) for code,(level,label) in mod.SERIES.items()]
        for layout in (required[1:], required+[required[0]], [(3,11,'Wrong label')]+required[1:]):
            with self.assertRaises(ValueError):
                mod.select_series(layout)

    def test_published_series_and_diagnostic_effect_sizes(self):
        cross = {r['survey']:r for r in rows('crosswalk.csv')}
        for field,label,number in [('diary_food','Food',8),('diary_soft_drinks','Non-alcoholic beverages',9)]:
            record=cross[field]
            self.assertEqual((record['label'],int(record['source_row']),int(record['cpi_level'])),(label,number,3))
        fits = {(int(r['code']),int(r['lag_months'])):r for r in rows('price_diagnostics.csv')}
        self.assertAlmostEqual(float(fits[11,1]['appreciation_slope']),-.355497,places=5)
        self.assertAlmostEqual(float(fits[12,3]['appreciation_slope']),.151028,places=5)
