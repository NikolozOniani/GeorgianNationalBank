import csv
from decimal import Decimal
from pathlib import Path
import unittest
P=Path(__file__).resolve().parents[1]/'reports/reserve_foundations'
def rows(n):
 with (P/n).open() as f:return list(csv.DictReader(f))
class FoundationsTests(unittest.TestCase):
 def test_weighted_components_independently(self):
  d={(r['year'],r['series']):Decimal(r['value']) for r in rows('ara_components.csv')}
  for r in rows('ara_reconstruction.csv'):
   v=lambda k:d[r['year'],k]
   x=(v('exports')+v('money_m2'))/20+v('std_residual')*Decimal('.3')+v('other_liabilities')*Decimal('.15')
   self.assertAlmostEqual(float(x),float(r['ara_rebuilt_usd_m']),places=8)
   self.assertLessEqual(abs(float(x-v('ara_reported'))),.8)
 def test_adjusted_discrepancies_not_forced_to_zero(self):
  r=rows('ara_reconstruction.csv');self.assertAlmostEqual(float(r[0]['adjustment_residual_usd_m']),270.4);self.assertAlmostEqual(float(r[1]['adjustment_residual_usd_m']),262.8)
 def test_historical_income_and_cross_vintage(self):
  r=rows('historical_interest.csv');self.assertEqual([int(x['year']) for x in r],list(range(2020,2025)))
  self.assertAlmostEqual(float(r[0]['reserve_interest_after_negative_gel_m']),123.411)
  for x in r:self.assertLess(abs(float(x['net_interest_identity_residual_gel_m'])),1e-8)
  for x in rows('comparative_column_checks.csv'):self.assertEqual(float(x['revision_gel_thousand']),0)
 def test_projections_and_conditional_cost_labelled(self):
  for r in rows('ara_components.csv'):
   if int(r['year'])>=2024:self.assertIn('projection',r['status'])
  for r in rows('reserve_level_scenarios.csv'):
   self.assertLessEqual(int(r['year']),2023)
   self.assertIn('assumed',r['scope'])
   self.assertAlmostEqual(float(r['extra_reserves_usd_m'])*float(r['assumed_net_carry_pct'])/100,float(r['conditional_annual_cost_usd_m']))
