"""Numerical and attribution guardrails for R4."""
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
import r4_carry as r4


class R4Tests(unittest.TestCase):
    def test_cd_accrual_telescopes_to_discount(self):
        values = [r4.book(97, 100, day, 91) for day in range(92)]
        self.assertAlmostEqual(sum(b-a for a,b in zip(values, values[1:])), 3)

    def test_audited_expense_and_unresolved_stock_residual(self):
        months = r4.monthly()
        self.assertEqual(len(months), 21)
        self.assertAlmostEqual(sum(r['cd_effective_interest_gelm'] for r in months[:12]), 4.772, places=3)
        self.assertIsNone(months[-1]['no_purchase_average_funding_gelm'])
        _, bridge = r4.reconciliations(months)
        residual = next(r['residual_gelm'] for r in bridge if r['item']=='closing_book_end_of_day')
        self.assertGreater(residual, .010)
        self.assertLess(residual, .012)

    def test_break_even_includes_terminal_principal(self):
        for r in r4.scenarios():
            gain = (1+r['breakeven_quote_change_pct']/100)*(1+r['usd_return_proxy_pct']/100)
            self.assertAlmostEqual(gain, 1+r['gel_cost_pct']/100)
