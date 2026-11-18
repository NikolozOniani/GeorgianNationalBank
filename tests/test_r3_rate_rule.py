import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
import r3_rate_rule as rule


class MeetingRuleTests(unittest.TestCase):
    def test_inputs_predate_decisions_and_preserve_prior_rate(self):
        rows,excluded = rule.meetings()
        self.assertEqual(excluded,['2018-01-31'])
        archive = rule.read(rule.DECISIONS)
        priors = {b['decision_date']:float(a['policy_rate_pct']) for a,b in zip(archive,archive[1:])}
        for r in rows:
            age = rule.month_number(r['decision_date'])-rule.month_number(r['report_month'])
            self.assertIn(age,range(1,5))
            self.assertEqual(r['prior_rate'],priors[r['decision_date']])
            self.assertEqual(r['rate']-r['prior_rate'],r['change'])

    def test_chronological_prediction_and_adoption(self):
        tables,result = rule.model_outputs()
        dates = [r['decision_date'] for r in tables['meetings.csv']]
        for r in tables['predictions.csv']:
            self.assertEqual(r['n_train'],dates.index(r['date']))
        self.assertTrue(result['criteria']['beats_hold'])
        self.assertFalse(result['standalone_candidate_accepted'])
        self.assertEqual(result['holdout'],16)


if __name__=='__main__':
    unittest.main()
