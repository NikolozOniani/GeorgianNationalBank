"""Cross-source and no-false-intervention checks on committed policy outputs."""
import csv,datetime as dt,pathlib,unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]/'reports'
def rows(name):
    with (ROOT/name).open(newline='') as f:return list(csv.DictReader(f))
class PolicyOutputTests(unittest.TestCase):
    def test_complete_months_and_component_identity(self):
        data=rows('nbg_policy_monthly_2020_2024.csv')
        self.assertEqual(len(data),60)
        self.assertEqual(len(set(x['month'] for x in data)),60)
        self.assertEqual(data[0]['month'],'2020-01');self.assertEqual(data[-1]['month'],'2024-12')
        parts=['reserve_fx_usd_m','reserve_imf_usd_m','reserve_sdr_usd_m','reserve_gold_usd_m','reserve_other_usd_m']
        for x in data:
            self.assertLess(abs(float(x['official_reserves_usd_m'])-sum(float(x[p]) for p in parts)),1e-8)
            self.assertEqual(x['auction_sales_usd_m'],'')
            self.assertEqual(x['bmatch_sales_usd_m'],'')
            self.assertEqual(x['government_fx_usd_m'],'')
            self.assertGreater(float(x['policy_rate_end_pct']),0)
            self.assertGreater(float(x['official_usd_gel_month_end']),0)
            self.assertTrue(x['official_usd_rate_valid_from'][:7]<=x['month'])
    def test_annual_reporting_is_distinct_from_reserve_change(self):
        data={x['month']:x for x in rows('nbg_policy_monthly_2020_2024.csv')}
        annual=rows('nbg_fx_annual_benchmarks.csv')[0]
        self.assertAlmostEqual(float(annual['auction_net_sales_usd_m'])+float(annual['bmatch_net_sales_usd_m']),float(annual['total_net_sales_usd_m']))
        stock=float(data['2024-12']['official_reserves_usd_m'])
        prior=stock-sum(float(data[f'2024-{m:02d}']['reserve_stock_change_usd_m']) for m in range(1,13))
        self.assertAlmostEqual(stock-prior,-561.1,delta=.1)
        self.assertGreater(abs((stock-prior)+float(annual['total_net_sales_usd_m'])),100)
    def test_events_and_higher_frequency_preserved(self):
        events=[x for x in rows('nbg_policy_decisions_2008_onward.csv') if '2020-01'<=x['decision_date'][:7]<='2024-12']
        self.assertEqual(len(events),40)
        self.assertEqual(len(rows('nbg_tibr_daily_2020_2024.csv')),1250)
        self.assertEqual(len(rows('nbg_external_quarterly_2020_2024.csv')),20)
        self.assertEqual(len(rows('nbg_auction_events_verified.csv')),1)
if __name__=='__main__':unittest.main()
