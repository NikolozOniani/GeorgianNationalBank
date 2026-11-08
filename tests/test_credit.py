"""Tests of extraction accounting, date alignment and synthetic debt contracts."""
import csv
from decimal import Decimal, localcontext
import datetime as dt
import importlib.util
import json
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'reports/peer_review'
spec=importlib.util.spec_from_file_location('credit',ROOT/'src/credit_analysis.py')
credit=importlib.util.module_from_spec(spec);spec.loader.exec_module(credit)


class CreditTests(unittest.TestCase):
    def test_full_cartesian_month_coverage_and_provenance(self):
        rows=credit.rows(OUT/'credit_observations.csv')
        self.assertEqual(len(rows),2760)
        self.assertEqual(len({(r['month'],r['series']) for r in rows}),2760)
        self.assertEqual(len({r['series'] for r in rows}),46)
        for r in rows:
            self.assertNotEqual(r['value'],'')
            self.assertEqual(len(r['source_sha256']),64)
            self.assertTrue(r['cell']);self.assertTrue(r['date_cell'])
            self.assertGreaterEqual(float(r['value']),0)

    def test_accounting_matches_across_source_tables(self):
        checks=credit.rows(OUT/'reconciliation.csv')
        self.assertEqual(len(checks),360)
        for row in checks:self.assertLessEqual(abs(float(row['difference_gel_m'])),.01)

    def test_annuity_against_decimal_formula_and_zero_rate(self):
        with localcontext() as c:
            c.prec=40;r=Decimal('10.7')/1200
            answer=Decimal(100000)*r/(1-(1+r)**(-240))
        self.assertAlmostEqual(credit.payment(100000,10.7,240),float(answer),places=9)
        self.assertEqual(credit.payment(1200,0,12),100)
        for args in [(-1,5,12),(1,-1,12),(1,5,0)]:
            with self.assertRaises(ValueError):credit.payment(*args)

    def test_rate_uses_effective_date_without_lookahead(self):
        decisions=credit.rows(ROOT/'reports/nbg_policy_decisions_2008_onward.csv')
        self.assertEqual(credit.policy_on(dt.date(2022,3,1),decisions),10.5)
        self.assertEqual(credit.policy_on(dt.date(2022,4,1),decisions),11)
        self.assertEqual(credit.policy_on(dt.date(2021,1,1),decisions),8)

    def test_monthly_balance_and_terminal_debt_identity(self):
        paths=credit.simulate(100000,240,1)
        for r in paths:
            self.assertAlmostEqual(r['opening_balance_gel']+r['interest_gel']-r['payment_gel'],r['closing_balance_gel'],places=9)
        delta_debt=paths[-1]['closing_balance_gel']-paths[-1]['reference_closing_balance_gel']
        self.assertAlmostEqual(sum(r['extra_payment_gel'] for r in paths),sum(r['extra_interest_gel'] for r in paths)-delta_debt,places=7)
        self.assertGreater(delta_debt,0)

    def test_fixed_rate_and_scale_invariance(self):
        p=credit.simulate(100000,240,1,pass_through=0)
        self.assertTrue(all(abs(r['extra_payment_gel'])<1e-9 for r in p))
        a=credit.simulate(100000,240,1);b=credit.simulate(50000,240,1)
        for x,y in zip(a,b):self.assertAlmostEqual(x['extra_payment_gel'],2*y['extra_payment_gel'],places=8)

    def test_observed_prices_do_not_all_increase(self):
        table={r['series']:r for r in credit.rows(OUT/'table1_observed.csv')}
        self.assertAlmostEqual(float(table['hh_all_gel_new_housing_rate']['change_2020_2022']),1.74)
        self.assertAlmostEqual(float(table['hh_all_gel_new_consumer_rate']['change_2020_2022']),-1.15)
        self.assertAlmostEqual(float(table['hh_all_gel_deposit_term_rate']['change_2020_2022']),1.61)

    def test_stored_simulation_and_all_sensitivity_identities(self):
        result=json.loads((OUT/'results.json').read_text())['indexed_monthly_main']
        p=credit.simulate(100000,240,1)
        self.assertAlmostEqual(result['extra_payments_48m_gel'],sum(r['extra_payment_gel'] for r in p),places=8)
        for r in credit.rows(OUT/'table3_reset_sensitivity.csv'):
            self.assertAlmostEqual(float(r['extra_payments_48m_gel']),float(r['extra_interest_48m_gel'])-float(r['extra_terminal_debt_gel']),places=7)


if __name__=='__main__':unittest.main()
