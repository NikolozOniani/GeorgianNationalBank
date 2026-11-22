import sys
import unittest
from decimal import Decimal as D
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from validate_historical_buffer import OUT, Event, accounts, check_transaction_coverage, bond_forecast, bond_scores, imf_scores, rankings, read, score


class ValidationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.origins=read(OUT/'origins.csv')
        cls.events=read(OUT/'imf_events.csv')
        cls.cov=read(OUT/'schedule_coverage.csv')
        cls.imf=imf_scores(cls.origins,cls.events,cls.cov)
        cls.bond=bond_scores(cls.origins,read(OUT/'bond_stocks.csv'))

    def test_population_and_coverage(self):
        self.assertEqual({o['episode'] for o in self.origins},
                         {'2010Q1','2012Q1','2013Q1','2014Q1','2018Q3','2021Q2','2022Q1'})
        self.assertEqual(len(self.imf),42)
        self.assertEqual(len(self.bond),21)
        self.assertTrue(all(c['rows']=='0' and c['selected']=='0' for c in self.cov if c['source'].endswith('_obl')))
        self.assertEqual(sum(int(c['selected']) for c in self.cov),7)
        self.assertTrue(all(c['last_scheduled_date'][:4]>str(int(c['origin'][:4])+1)
                            for c in self.cov if c['selected']=='1'))
        self.assertFalse(any(r['national_realized_gap'] for r in read(OUT/'wider_public_account.csv')))

    def test_missing_year_or_dropped_transaction_is_not_zero(self):
        annual=read(OUT/'transaction_coverage.csv')
        with self.assertRaisesRegex(ValueError,'Missing annual'):
            check_transaction_coverage(self.origins,self.events,[r for r in annual if r['year']!='2019'])
        rows=[r for r in self.events if not (r['source']=='tx2010' and r['day']=='2010-01-28')]
        with self.assertRaisesRegex(ValueError,'annual totals'):
            check_transaction_coverage(self.origins,rows,annual)

    def test_post_cutoff_draw_is_not_a_feature(self):
        key='2009-12-31_exp'
        original=accounts('2009-12-31',3,self.events,key)
        changed=[dict(r,draw_sdr=0) for r in self.events]
        without=accounts('2009-12-31',3,changed,key)
        self.assertEqual(original[:2],without[:2])
        self.assertEqual(original[0]['minimum'],D('4.05'))
        self.assertEqual(original[2]['minimum'],D('3.15'))
        self.assertEqual(without[2]['minimum'],D('4.05'))

    def test_models_can_disagree_with_eligible_credit(self):
        pred,simple,*_=accounts('2009-12-31',3,self.events,'2009-12-31_exp',Event('2010-01-01','fixture',D(-2)))
        self.assertEqual(pred['minimum'],D('2.05'))
        self.assertEqual(simple['minimum'],D('4.05'))
        o=dict(self.origins[0],credit_receipt_date='2010-01-01',forecast_credit_sdr=2000000,
               credit_publication_date='2010-01-02')
        with self.assertRaises(ValueError):
            imf_scores([o],self.events,self.cov)

    def test_interval_and_carry_units(self):
        a=score(D('517.1875'),D('517.15'),D('517.25'),3)
        self.assertEqual((a['uncovered_low'],a['uncovered_high']),(0,D('.0625')))
        self.assertEqual((a['excess_low'],a['excess_high']),(0,D('.0375')))
        self.assertEqual(score(D('4.05'),D('3.15'),D('3.15'),3)['carry_100bp_low'],D('.00225'))
        with self.assertRaises(ValueError):
            score(D(1),D(4),D(2),3)

    def test_closed_bond_and_horizon(self):
        self.assertEqual(bond_forecast('2018-06-30',3,D(500))[0]['minimum'],0)
        self.assertEqual(bond_forecast('2021-03-31',12,D(500))[0]['minimum'],D('517.1875'))
        self.assertFalse(any(r['model_usdm']!='' for r in self.bond if r['episode'] in ('2010Q1','2022Q1')))
        self.assertEqual(next(r['actual_high'] for r in self.bond if r['episode']=='2018Q3' and r['months']==1),D('.05'))

    def test_receipt_classification_and_omissions(self):
        realized={r['day']:D(r['draw_sdr']) for r in self.events if r['source'].startswith('tx') and D(r['draw_sdr'])}
        evidence=read(OUT/'drawing_evidence.csv')
        for r in evidence:
            self.assertEqual(realized[r['date']],D(r['sdr_million'])*1000000)
        for o in self.origins:
            from minimum_reserve_buffer import month_end
            self.assertEqual({k for k in realized if o['origin']<k<=month_end(o['origin'],12)},
                             {r['date'] for r in evidence if r['origin']==o['origin']})
        pairs=rankings(self.imf,self.bond)
        for r in pairs:
            if r['rule']=='cash path':
                other=next(s for s in pairs if s['account']==r['account'] and s['grade']==r['grade']
                           and s['exclude']==r['exclude'] and s['rule']=='gross debt service')
                self.assertEqual(r['excess_high'],other['excess_high'])
                self.assertEqual(r['uncovered_high'],other['uncovered_high'])
        omitted=next(r for r in pairs if r['exclude']=='2010Q1' and r['rule']=='cash path')
        self.assertEqual(omitted['excess_high'],0)
