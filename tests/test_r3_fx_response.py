"""Checks on release timing, source reconciliation and the registered response estimators."""
import csv
from datetime import date, timedelta
import math
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT/'data/derived/r3_fx_response'
OUT = ROOT/'reports/r3_fx_response'


def read(p):
    with p.open() as stream:
        return list(csv.DictReader(stream))


class FXResponses(unittest.TestCase):
    def test_auction_dates_and_matching_without_future_quotes(self):
        dates = {date.fromisoformat(r['date']) for r in read(DATA/'auctions.csv')}
        prices = {date.fromisoformat(r['date']):float(r['gel_usd']) for r in read(DATA/'daily.csv')}
        for row in read(OUT/'auction_pairs.csv'):
            day = date.fromisoformat(row['date'])
            delta = timedelta(days=int(row['h_days']))
            self.assertIn(day,dates)
            if not row['control']:
                continue
            control = date.fromisoformat(row['control'])
            self.assertLess(control+delta,day)
            self.assertEqual(day.weekday(),control.weekday())
            self.assertEqual(day.year,control.year)
            self.assertNotIn(control,dates)
            for anchor,k in [(day,'other_auctions'),(control,'control_other_auctions')]:
                self.assertEqual(sum(anchor<d<=anchor+delta for d in dates),int(row[k]))
            ratio = prices[day+delta]*prices[control]/(prices[day]*prices[control+delta])
            self.assertAlmostEqual(100*math.log(ratio),float(row['difference_pp']),places=10)

    def test_source_leg_discrepancies_cancel_over_full_history(self):
        records = read(OUT/'auction_reconciliation.csv')
        self.assertEqual(len(records),6)
        for leg in ('sales_usd','purchases_usd'):
            self.assertAlmostEqual(sum(float(r['dated_less_workbook_usdm']) for r in records if r['leg']==leg),0)
        prior = {r['month']:r for r in read(ROOT/'data/derived/episode_2026_11_09/intervention_monthly.csv')}
        for r in read(DATA/'monthly.csv'):
            if r['month'] in prior:
                for before,after in [('auction_buy_usdm','auction_purchases_usdm'),
                                     ('auction_sell_usdm','auction_sales_usdm'),('net_usdm','net_market_purchases_usdm')]:
                    self.assertAlmostEqual(float(r[before]),float(prior[r['month']][after]))

    def test_independent_full_monthly_slopes_and_bartlett_variance(self):
        # Rebuild the monthly panel by calendar aggregation, then estimate the purchase
        # coefficient via scalar partial regression and the scalar HAC influence series.
        closes = {}
        for r in read(DATA/'daily.csv'):
            closes[r['date'][:7]] = 100*math.log(float(r['gel_usd']))
        flows = read(DATA/'monthly.csv')
        prices = np.array([closes[r['month']] for r in flows])
        q = np.array([float(r['net_usdm'])/100 for r in flows])
        for row in read(OUT/'monthly_projections.csv'):
            if row['spec']!='full':
                continue
            h = int(row['h_months'])
            t = np.arange(2,len(q)-max(0,h))
            before = prices[t-1]-prices[t-2]
            y = before if h<0 else prices[t+h]-prices[t-1]
            controls = [np.ones(len(t)),np.maximum(-q[t],0),q[t-1]]
            if h>=0:
                controls.append(before)
            basis,_ = np.linalg.qr(np.array(controls).T)
            x = np.maximum(q[t],0)
            x = x-basis@(basis.T@x)
            y = y-basis@(basis.T@y)
            slope = (x@y)/(x@x)
            self.assertAlmostEqual(slope,float(row['buy_logpct_per_100m']),places=9)
            influence = x*(y-slope*x)/(x@x)
            bw = max(1,h+1)
            var = influence@influence
            for j in range(1,bw+1):
                var += 2*(1-j/(bw+1))*(influence[j:]@influence[:-j])
            var *= len(t)/(len(t)-len(controls)-1)
            self.assertAlmostEqual(math.sqrt(var),float(row['buy_hac_se']),places=9)

    def test_optimized_python_rejects_altered_output(self):
        # Point the actual check at an isolated, intentionally corrupt first table.
        with tempfile.TemporaryDirectory() as folder:
            table = Path(folder) / 'auction_pairs.csv'
            table.write_text('damaged')
            code = ("import sys; from pathlib import Path; sys.path.insert(0, 'src'); "
                    "import r3_fx_response as fx; fx.OUT = Path(sys.argv[1]); fx.run(True)")
            run = subprocess.run([sys.executable, '-O', '-c', code, folder], cwd=ROOT,
                                 capture_output=True, text=True)
            self.assertNotEqual(run.returncode, 0)
            self.assertIn('ValueError: Response output differs: auction_pairs.csv', run.stderr)
            self.assertEqual(table.read_text(), 'damaged')

    def test_conditional_response_inverse(self):
        for r in read(OUT/'selection_sensitivity.csv'):
            self.assertAlmostEqual(float(r['assumed_partial_correlation']),float(r['check_correlation']),places=10)


if __name__=='__main__':
    unittest.main()
