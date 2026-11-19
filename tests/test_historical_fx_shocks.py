import csv
from pathlib import Path
import unittest

OUT = Path(__file__).resolve().parents[1] / "reports/historical_fx_shocks"


def read(name):
    with (OUT / name).open() as f:
        return list(csv.DictReader(f))


class FundingStress(unittest.TestCase):
    def test_registered_channels_and_time(self):
        rows = read("screen.csv")
        self.assertEqual([r["quarter"] for r in rows], [f"{y}Q{q}" for y in range(2008,2025) for q in range(1,5)])
        for r in rows:
            for k, numerator, denominator in [
                ("exports", float(r["prior_year_exports_usdm"])-float(r["exports_usdm"]), "prior_year_exports_usdm"),
                ("bank_loans", -float(r["bank_net_loan_incurrence_usdm"]), "opening_bank_external_loans_usdm"),
                ("fx_deposits", float(r["opening_fx_deposits_usdm"])-float(r["closing_fx_deposits_usdm"]), "opening_fx_deposits_usdm")]:
                score = float(r[k+"_pressure_pct"])
                self.assertAlmostEqual(100*numerator/float(r[denominator]), score, places=5)
                rank = 1+sum(float(other[k+"_pressure_pct"]) > score for other in rows)
                self.assertEqual(rank, int(r[k+"_rank"]))
                self.assertEqual(k in r["flagged_channels"].split("|"), rank <= 5 and score > 0)

    def test_august_and_quarterly_bridge(self):
        months = read("georgia_2008_monthly.csv")
        self.assertEqual(len(months), 12)
        self.assertAlmostEqual(float(months[7]["reserves_change_usdm"]), -341.894, places=3)
        for i,r in enumerate(read("screen.csv")[:4]):
            monthly = sum(float(m["reserves_change_usdm"]) for m in months[3*i:3*i+3])
            self.assertAlmostEqual(monthly, float(r["reserve_transactions_usdm"])+float(r["other_stock_changes_usdm"]), places=5)
