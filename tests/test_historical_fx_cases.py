import csv
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'reports/historical_fx_shocks/cases'


def read(path):
    with path.open() as stream:
        return list(csv.DictReader(stream))


class FundingCases(unittest.TestCase):
    def test_cash_dates_and_monthly_coverage(self):
        cash = read(OUT/'imf_cash.csv')
        monthly = read(OUT/'monthly.csv')
        self.assertEqual(len(cash), 8)
        self.assertEqual(len(monthly), 18)
        self.assertEqual(sum(int(r['principal_paid_sdr']) for r in cash), 8_280_000)
        self.assertEqual(sum(int(r['disbursed_sdr']) for r in cash), 352_200_000)
        for row in monthly:
            tx = [r for r in cash if r['date'][:7] == row['month']]
            for key, src in [('imf_drawn_sdr','disbursed_sdr'), ('imf_principal_paid_sdr','principal_paid_sdr')]:
                self.assertEqual(int(row[key]),sum(int(r[src]) for r in tx))
            self.assertEqual(row['all_market_net_sales_usdm']=='',row['month']<'2020')

    def test_quarterly_source_overlap(self):
        screen = {r['quarter']:r for r in read(OUT.parent/'screen.csv')}
        rows = read(OUT/'quarterly.csv')
        self.assertEqual(len(rows),6)
        for row in rows:
            before=screen[row['quarter']]
            f=lambda k:float(row[k])
            self.assertAlmostEqual(f('banks_net_short_loan_incurrence_usdm')+f('banks_net_long_loan_incurrence_usdm'),
                                   float(before['bank_net_loan_incurrence_usdm']),places=5)
            self.assertAlmostEqual(f('reserve_transactions_usdm'),float(before['reserve_transactions_usdm']),places=5)
            self.assertAlmostEqual(f('reserve_stock_change_usdm'),float(before['reserves_change_usdm']),places=5)
            self.assertAlmostEqual(f('imf_net_usdm')+f('exceptional_financing_usdm')-f('overall_balance_usdm'),
                                   f('reserve_transactions_usdm'),places=5)
