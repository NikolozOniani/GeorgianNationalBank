import itertools
import sys
import unittest
from decimal import Decimal as D
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from minimum_reserve_buffer import COVID, OUT, Event, Study, month_end, read, replay


class CashPathTests(unittest.TestCase):
    def check_path(self, amounts, floor=0):
        events = [Event(f'2020-04-{i+1:02}',str(i),D(v)) for i,v in enumerate(amounts)]
        return replay(COVID,events,1,D(floor))[0]

    def test_prefix_against_feasible_grid(self):
        for amounts in itertools.product([-2,0,3],repeat=3):
            floor = 2
            # Search all integer opening endowments directly, stopping on first breach.
            for opening in range(20):
                cash = opening
                if cash < floor:
                    continue
                for use in amounts:
                    cash -= use
                    if cash < floor:
                        break
                else:
                    break
            self.assertEqual(self.check_path(amounts,floor)['minimum'],opening)

    def test_late_receipts_and_unchanged_floor(self):
        self.assertEqual(self.check_path([8,-10])['minimum'],8)
        self.assertEqual(self.check_path([-10,8])['minimum'],0)
        funded = self.check_path([-10,8],4)
        self.assertEqual(funded['minimum'],4)
        self.assertEqual(funded['first_floor_breach_at_half'],COVID)
        self.assertEqual(funded['first_cash_failure_at_half'],'')

    def test_simultaneous_bills_and_duplicate(self):
        dues = [Event('2020-04-10','A',D(2)),Event('2020-04-10','B',D(3))]
        r, path = replay(COVID,dues,1,D(0))
        self.assertEqual((r['minimum'],r['binding_group']),(5,'A + B'))
        self.assertEqual(path[-1]['balance_at_minimum'],0)
        with self.assertRaises(ValueError):
            replay(COVID,dues+[dues[0]],1,D(0))

    def test_horizon_and_origin(self):
        self.assertEqual(month_end('2019-11-30',3),'2020-02-29')
        self.assertEqual(month_end(COVID,12),'2021-03-31')
        later = Event('2021-04-01','later',D(100))
        self.assertEqual(replay(COVID,[later],12,D(0))[0]['minimum'],0)
        with self.assertRaises(ValueError):
            replay(COVID,[Event(COVID,'already settled',D(1))],1,D(0))


class HistoricalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.study = Study()
        cls.study.build()
        cls.result = {(r['case'],r['months']):r for r in cls.study.results if r['floor']==0}

    def test_imf_year_and_gross_auction_legs(self):
        annual = read(OUT/'imf_2009_full_year.csv')
        self.assertEqual(sum(int(r['principal_paid_sdr']) for r in annual),17960000)
        self.assertEqual(sum(int(r['disbursed_sdr']) for r in annual),220800000)
        for h, peak in [(1,'3.15'),(3,'7.38'),(12,'7.38')]:
            self.assertEqual(self.result['2009_principal_actual',h]['minimum'],D(peak))
        self.assertEqual(self.result['2009_principal_no_receipts',12]['minimum'],D('17.96'))
        events = [r for r in self.study.events if r['case']=='2009_IMF_sales_actual_gross_face_late']
        auctions = [r['net_use'] for r in events if r['flow'].startswith('auction ')]
        self.assertEqual((sum(auctions),min(auctions)),(14,-5))
        self.assertEqual(self.result['2009_IMF_sales_actual_gross_face_late',3]['minimum'],D('22.31710406'))

    def test_treasury_ring_fence(self):
        for r in self.study.treasury:
            self.assertEqual(r['opening']+r['receipt']-r['externally_paid'],r['closing'])
            self.assertEqual(r['gross_bill'],r['externally_paid']+r['nbg_backstop'])
            self.assertGreaterEqual(r['closing'],0)
        for mode,expected in [('actual','17.9875'),('no_new_rescue','55.597262'),('inaccessible','104.4')]:
            r = self.result[f'2020_fiscal_{mode}_late',3]
            self.assertEqual(r['minimum'],D(expected))
            both = self.result[f'2020_fiscal_{mode}_late_sales',3]
            self.assertEqual(both['minimum']-r['minimum'],D('120.95'))
        self.assertEqual(self.result['2020_named_SDR',3]['minimum'],D('.592870'))

    def test_aggregate_buckets_and_timing(self):
        for h, scheduled, sales in [(1,'36.437260799','24.8'),(3,'114.770533455','120.95'),(12,'418.311542784','980.472')]:
            late = self.result['2020_schedule_sales',h]
            early = self.result['2020_schedule_sales_early_dues',h]
            self.assertEqual(late['minimum'],D(scheduled)+D(sales))
            self.assertEqual(early['minimum'],late['minimum'])
        self.assertEqual(self.result['2020_schedule_sales',12]['first_cash_failure_at_half'],'2020-10-31')
        self.assertEqual(self.result['2020_schedule_sales_early_dues',12]['first_cash_failure_at_half'],'2020-09-30')

    def test_asset_settlement_and_bank_separation(self):
        m, = [r for r in self.study.mobilization if r['months']==12 and r['floor']==0]
        self.assertEqual(m['conditional_deposits']+m['min_security_proceeds'],m['total_liquid_need'])
        self.assertAlmostEqual(m['market_value_to_sell_5pct_discount']*D('.95'),m['min_security_proceeds'])
        self.assertEqual(m['deposit_need_if_first_bucket_and_residual_sales_before_settlement'],D('41.237260799'))
        self.assertEqual(self.result['2009_named_bank_full_backstop',12]['minimum'],114)
        self.assertEqual(self.result['2009_named_bank_self_funded',12]['minimum'],0)
        self.assertEqual(self.result['2009_fiscal_bills_first',3]['minimum'],26)
