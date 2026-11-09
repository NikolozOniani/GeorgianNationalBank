"""Independent accounting and derivative checks for the integrated paper."""
import importlib.util
import json
import math
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
s=importlib.util.spec_from_file_location('paper',ROOT/'src/paper_analysis.py')
p=importlib.util.module_from_spec(s);s.loader.exec_module(p)


class PaperTests(unittest.TestCase):
    def test_source_and_accounting_integrity(self):
        rows=p.read('annual_accounts.csv')
        self.assertEqual(len(rows),64)
        self.assertEqual(len({(r['series'],r['year']) for r in rows}),64)
        for r in p.read('accounting_checks.csv'):self.assertLess(abs(float(r['residual_gel_million'])),.0011)

    def test_expense_is_not_net_loss(self):
        rows={r['year']:r for r in p.read('annual_results.csv')}
        self.assertAlmostEqual(float(rows['2024']['monetary_interest_expense_gel_m']),95.361)
        self.assertAlmostEqual(float(rows['2024']['monetary_net_interest_gel_m']),414.498)
        self.assertGreater(float(rows['2024']['bank_net_interest_received_gel_m']),0)
        self.assertLess(float(rows['2024']['currency_plus_gel_bank_liabilities_gel_m']),float(rows['2023']['currency_plus_gel_bank_liabilities_gel_m']))

    def test_reserve_bridge_separates_stock_and_transaction(self):
        for r in p.read('reserve_bridges.csv'):
            self.assertAlmostEqual(float(r['reserve_stock_change_usd_m']),float(r['net_intervention_purchase_usd_m'])+float(r['unexplained_composite_usd_m']),places=8)
        self.assertAlmostEqual(float(p.read('reserve_bridges.csv')[0]['unexplained_composite_usd_m']),-1170.626287100917)

    def test_dollarization_derivative_and_sign(self):
        for r in (.1,.2,.3):
            h=1e-5
            finite=(p.crisis_loss(r+h)-p.crisis_loss(r-h))/(2*h)
            self.assertAlmostEqual(finite,p.crisis_loss_derivative(r),places=10)
            self.assertLess(finite,0)
            # The printed subtraction of a negative derivative raises cost.
            self.assertGreater(.02-.1/.9*finite,.02)
            # In a welfare objective -cost - expected crisis loss, it is a benefit.
            self.assertGreater(-.1*finite,0)

    def test_isolated_channel_magnitude_and_spread_units(self):
        benefit=.1*.1*.5*.1*math.log(1.2/1.1)
        self.assertAlmostEqual(benefit,.1*(p.crisis_loss(.1)-p.crisis_loss(.2)),places=14)
        self.assertAlmostEqual(100*benefit,.00435056884948,places=11)
        self.assertAlmostEqual(10000*.0575*math.log(1.2/1.1),50.0315417695,places=7)


if __name__=='__main__':unittest.main()
