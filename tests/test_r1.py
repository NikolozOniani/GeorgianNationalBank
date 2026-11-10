"""Accounting and measurement regressions for the R1 checkpoint."""
import csv
from decimal import Decimal as D
import json
from pathlib import Path
import unittest
from src.r1_accounts import gross_bounds

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'reports/r1_2026_11_10'


def rows(name):
    with (OUT/(name+'.csv')).open() as file:return list(csv.DictReader(file))


class R1Tests(unittest.TestCase):
    def test_net_does_not_identify_gross(self):
        for net in ['0','-16.2','101.7']:
            p,s=gross_bounds(net)
            self.assertEqual(p-s,D(net))
            # Arbitrary equal round trips leave net unchanged: no finite upper bound.
            self.assertEqual((p+1000)-(s+1000),D(net))
        d={r['window']:r for r in rows('episode_totals')}
        self.assertEqual(D(d['registered_episode']['net_purchases_usdm']),D('5803.15'))
        self.assertEqual(D(d['registered_episode']['purchases_lower_bound_usdm']),D('5819.35'))
        self.assertEqual(D(d['registered_episode']['sales_lower_bound_usdm']),D('16.2'))

    def test_no_synthetic_execution_dates(self):
        ledger=rows('episode_transaction_ledger')
        self.assertEqual(len(ledger),105)
        for r in ledger:
            for k in ['order_time','trade_date','settlement_date','first_disclosure_date','execution_price']:
                self.assertEqual(r[k],'')
        self.assertTrue(all(r['gross_market_purchases_upper_bound_usdm']=='' for r in rows('gross_flow_accounting_bounds')))
        self.assertTrue(all(r['auction_trade_date']=='' for r in rows('treasury_operations')))

    def test_quarter_bridge_and_unobserved_components(self):
        r=rows('reserve_flow_bridge');self.assertEqual(len(r),6)
        for x in r:
            self.assertEqual(D(x['reserve_change_usdm']),D(x['market_net_purchases_usdm'])+D(x['other_transactions_residual_usdm'])+D(x['valuation_other_volume_revision_residual_usdm']))
            self.assertEqual(x['government_transactions_usdm'],'')
        self.assertTrue(all(x['bop_reserve_transactions_usdm']=='' for x in rows('monthly_reserve_bridge')))

    def test_gold_difference_is_not_repaired(self):
        d={r['year']:r for r in rows('gold_source_concordance')}
        self.assertEqual(d['2024']['reconciled_within_rounding'],'False')
        self.assertGreater(abs(D(d['2024']['difference_usdm'])),D('.4'))
        self.assertEqual(d['2025']['reconciled_within_rounding'],'True')
        r={r['component']:r for r in rows('annual_2025_refined_bridge')}
        self.assertIn('approximate',r['remaining_transaction_residual_approx']['interpretation'])
        self.assertNotEqual(r['gold_holding_value_change']['value_usdm'],r['statistical_gold_value_change']['value_usdm'])

    def test_liquidity_identity_does_not_assign_causality(self):
        for r in rows('liquidity_changes'):
            total=sum(D(v) for k,v in r.items() if k.endswith('_contribution_gelm'))
            self.assertLessEqual(abs(D(r['monetary_base_change_gelm'])-total),D('.012'))
            self.assertIn('not causal',r['interpretation'])
        for r in rows('cd_financing_reconciliation'):
            total=sum(D(r[k]) for k in ['opening_gelm','interest_paid_gelm','cash_issuance_gelm','cash_redemption_gelm','interest_accrued_gelm'])
            self.assertEqual(total,D(r['closing_gelm']))

    def test_g1_stays_open(self):
        r=json.loads((OUT/'validation.json').read_text())
        self.assertTrue(r['all_computational_checks_passed'])
        self.assertTrue(r['source_qualifications_remain'])
        self.assertTrue(r['G1_status'].startswith('PARTIAL'))
        self.assertFalse(r['causal_estimation_performed'])
        self.assertTrue(r['new_source_qualifications'])


if __name__=='__main__':unittest.main()
