import sys
import unittest
from collections import Counter
from decimal import Decimal as D
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
import reserve_buffer_policy as policy


class ReservePolicyTest(unittest.TestCase):
    def test_all_origins_and_asset_access(self):
        rows = policy.read(policy.OUT/'opening_assets.csv')
        self.assertEqual(len({r['date'] for r in rows}), 25)
        opening, = [r for r in rows if r['date'] == '2024-12-31']
        self.assertEqual(D(opening['deposits_only_conditional']), D(opening['deposits']) + D(opening['other']))
        self.assertEqual(D(opening['fx_at_par_conditional']) - D(opening['fx_securities_5pct_discount']),
                         D('.05') * D(opening['securities']))
        for r in rows:
            self.assertEqual(D(r['all_at_par_conditional']), D(r['headline']))
            self.assertEqual(D(r['sensitivity_floor_usdm']), D('.01') * D(r['headline']))
            self.assertEqual(r['verified_free_cash'], '')
        self.assertEqual(rows[0]['deposits_only_conditional'], '')
        self.assertEqual(D(rows[1]['deposits_only_conditional']), D('860.511854700'))
        self.assertEqual(D(rows[1]['fx_split_residual_usdm']), D('.000350742'))
        self.assertTrue(all(r['pledge'] == r['lent'] == '' for r in rows))

    def test_horizons_and_known_schedule(self):
        calls = policy.read(policy.OUT/'scheduled_calls.csv')
        self.assertEqual(len({(r['date'], r['months']) for r in calls}), 75)
        early = [r for r in calls if r['date'].startswith('2008')]
        self.assertTrue(all(r['II1_signed'] == '' for r in early))
        march = {r['months']:D(r['II1_signed']) for r in calls if r['date'] == '2020-03-31'}
        self.assertEqual(march['3'], D('-114.770533455'))
        self.assertLess(march['12'], march['3'])
        self.assertEqual(march['1'], D('-36.437260799'))
        expected = policy.read(policy.R2/'liquidity_schedule.csv')
        by_key = {(r['date'],r['months']):r for r in calls}
        for r in expected:
            actual = by_key[r['date'],r['horizon_months']]
            self.assertEqual(actual['II1_signed'], r['reported_II_1_signed_usdm'])
            self.assertEqual(actual['III1_signed'], r['reported_III_1_signed_usdm'])

    def test_funding_cutoff_and_native_currency(self):
        facilities = policy.financing()
        sba = [r for r in facilities if r['receipt'] == '2009-03-25']
        self.assertEqual(sum(D(r['actual_gross_face']) for r in sba), 126200000)
        self.assertEqual(sum(D(r['no_new_rescue_gross_face']) for r in sba), 63100000)
        eff = [r for r in facilities if r['facility'].startswith('EFF')]
        self.assertTrue(all(r['no_new_rescue_gross_face'] == 0 for r in eff))
        wb, = [r for r in facilities if r['facility'].startswith('World Bank')]
        self.assertEqual((wb['unit'],wb['effective'],wb['receipt']), ('EUR','2020-04-30','2020-05-06'))
        self.assertEqual(D(wb['no_new_rescue_gross_face']),45000000)
        self.assertTrue(all(r['usable_net_cash'] == '' for r in facilities))

    def test_no_duplicate_venue_or_private_call(self):
        matrix = policy.payment_matrix()
        self.assertEqual(len(matrix),len(set(r['id'] for r in matrix)))
        self.assertTrue(all(r['public_float'] == 'off' for r in matrix if r['account'] in ('bank_support_candidate','sales_replay')))
        q2 = [r for r in matrix if r['account'] == 'sales_replay' and r['date_or_interval'] in ('2020-04','2020-05','2020-06')]
        self.assertEqual(sum(D(r['amount']) for r in q2),D('120.95'))
        self.assertEqual(Counter(r['account'] for r in matrix)['projected_public_payment'],4)
        self.assertFalse(any('Purchase (SBA)' in r['description'] for r in matrix))

    def test_bank_assets_are_separate(self):
        banks = policy.read(policy.OUT/'bank_assets.csv')
        march, = [r for r in banks if r['date'] == '2020-03-31']
        self.assertEqual(D(march['full_access_usdm']),D('790.592208600'))
        self.assertTrue(all(D(r['half_access_usdm'])*2 == D(r['full_access_usdm']) for r in banks))
        self.assertTrue(all(r['verified_bank_specific_usable_usdm'] == '' for r in banks))

    def test_settlement_location_and_excess_funds(self):
        for bill, outside, inside in [(10,0,0),(10,20,0),(10,2,20),(10,2,5),(0,5,6)]:
            r = policy.settle_treasury(bill,outside,inside)
            self.assertEqual(r['gross_nbg_delivery'] + r['external_treasury_used'],bill)
            self.assertEqual(r['gross_nbg_delivery'],r['treasury_at_nbg_used'] + r['assumed_public_backstop'])
            self.assertEqual(r['assumed_public_backstop'],max(0,bill-outside-inside))
        with self.assertRaises(ValueError):
            policy.settle_treasury(10,-1,5)
        self.assertEqual(policy.coupon_routes()[1]['gross_nbg_delivery'],D('17187500'))
