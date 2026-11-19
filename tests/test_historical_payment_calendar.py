import sys
import unittest
from decimal import Decimal as D
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
import historical_payment_calendar as calendar


class TestPaymentCalendar(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.events = calendar.read(calendar.OUT / 'payments.csv')
        cls.peaks = calendar.peaks(cls.events)
        cls.funding = calendar.read(calendar.OUT / 'financing.csv')

    def test_schedule_to_transaction_match(self):
        early = [r for r in self.events if r['quarter'] == '2009Q1' and r['transaction_date'] and D(r['gross_out'])]
        self.assertEqual(len(early), 4)
        self.assertTrue(all(r['nominal_due'] == r['transaction_date'] for r in early))
        self.assertEqual(sum(D(r['gross_out']) for r in early), 7380000)
        self.assertEqual(sum(D(r['usd_out']) for r in early), D('11033232.30'))

    def test_tentative_dates_and_valuation(self):
        charges = [r for r in self.events if r['evidence'] == 'IMF projection']
        self.assertEqual(len(charges), 4)
        self.assertTrue(all(not r['transaction_date'] for r in charges))
        self.assertEqual(charges[0]['sdr_quote_date'], '2009-01-30')
        self.assertEqual(sum(int(r['gross_out']) for r in charges if r['quarter'] == '2020Q2'), 592870)
        bond, = [r for r in self.events if r['currency'] == 'USD']
        self.assertEqual(D(bond['gross_out']), 17187500)
        self.assertFalse(bond['transaction_date'])

    def test_approvals_do_not_fund_earlier_obligations(self):
        sba = [r for r in self.funding if r['facility'].startswith('SBA')]
        self.assertEqual(sum(int(r['face_amount']) for r in sba), 126200000)
        self.assertEqual({r['draw_date'] for r in sba}, {'2009-03-25'})
        adb, = [r for r in self.funding if 'ADB' in r['facility']]
        self.assertLess(adb['approval_or_availability'], '2020-07-01')
        self.assertGreater(adb['draw_date'], '2020-06-30')
        self.assertEqual(self.peaks[3]['peak_usd'], '17999298.56')
        self.assertEqual(self.peaks[3]['first_peak_date'], '2020-05-01')
        self.assertEqual(self.peaks[0]['first_peak_date'], '2009-03-20')

    def test_bridge_and_perimeters(self):
        bridges, comparison = calendar.reconciliations(calendar.read(calendar.OUT/'opening_template.csv'),
                                                       calendar.read(calendar.OUT/'quarter_inputs.csv'))
        for r in bridges:
            self.assertEqual(r['closing_gross_usdm']-r['opening_gross_usdm'],
                             -r['sales_usdm']+r['other_net_transactions_usdm']+r['valuation_other_and_vintage_usdm'])
        row, = comparison
        self.assertEqual(row['principal_plus_interest_usdm'], D('104.3'))
        self.assertEqual(row['government_plus_nbg_service_usdm'], D('104.4'))
        self.assertAlmostEqual(row['nbg_opening_3m_scheduled_loan_security_deposit_outflows_usdm'], D('114.770533'), places=6)

    def test_changed_principal_is_rejected(self):
        schedules = calendar.read(calendar.OUT/'imf_schedules.csv')
        schedules[0]['amount_sdr'] = '1'
        with self.assertRaisesRegex(ValueError, 'disagrees'):
            calendar.payment_events(schedules, calendar.read(calendar.OUT/'sdr_rates.csv'),
                                    calendar.read(calendar.CASES/'imf_cash.csv'))
