"""R6 dimensional, liquidity, pricing and provenance failure checks."""
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
import r6_benefits as r6
import r2_model


class R6Tests(unittest.TestCase):
    def test_principal_is_not_cost_and_terminal_fx_is_used(self):
        for row in r6.read('reports/r4_2026_11_12/conditional_carry.csv'):
            p=float(row['principal_usdm']);x=float(row['gel_per_usd_change_pct'])/100
            u=float(row['usd_return_proxy_pct'])/100;f=float(row['gel_cost_pct'])/100
            liability_usd=p*(1+f)/(1+x)
            asset_usd=p*(1+u)
            stored=-float(row['terminal_net_gelm'])/(float(row['initial_gel_per_usd'])*(1+x))
            self.assertAlmostEqual(stored,liability_usd-asset_usd)

    def test_probability_threshold_units_and_nonnegative_hurdle(self):
        self.assertAlmostEqual(100*r6.hazard_threshold(4.22,3810),.110761154855643)
        self.assertEqual(r6.hazard_threshold(-3.87,3810),0)
        with self.assertRaises(ValueError): r6.hazard_threshold(1,0)

    def test_liquidity_dollar_used_once_and_saturation(self):
        for need in (0,40,50,75,100,150,1000):
            benefit=r6.avoided_shortfall(50,100,need)
            self.assertGreaterEqual(benefit,0)
            self.assertLessEqual(benefit,min(100,max(need-50,0)))
        self.assertEqual(r6.avoided_shortfall(50,100,75),25)
        self.assertEqual(r6.avoided_shortfall(50,100,150),100)
        self.assertEqual(r6.avoided_shortfall(50,0,150),0)
        with self.assertRaises(ValueError): r6.avoided_shortfall(-1,100,50)

    def test_bond_price_independent_annuity_and_reported_rounding(self):
        rate=.05375/2;n=10
        closed_form=500*.05125/2*(1-(1+rate)**(-n))/rate+500*(1+rate)**(-n)
        self.assertAlmostEqual(r6.bond_price(500,.05125,.05375),closed_form)
        self.assertEqual(round(100*closed_form/500,3),98.917)
        self.assertAlmostEqual(r6.bond_price(100,.04,.04),100)

    def test_pricing_threshold_inverse_and_spread_floor(self):
        required=r6.price_spread_threshold(500,.05125,.05375,18,.01519)
        gain=r6.bond_price(500,.05125,.05375-required)-r6.bond_price(500,.05125,.05375)
        self.assertAlmostEqual(gain,18)
        self.assertIsNone(r6.price_spread_threshold(500,.05125,.05375,35,.01519))
        self.assertEqual(r6.price_spread_threshold(500,.05125,.05375,-1,.01519),0)

    def test_history_windows_exclude_gaps_and_purchases_offset_sales(self):
        rows=[dict(month=m,net_market_purchases_usdm=v) for m,v in [('2020-01','-100'),('2020-02','90'),('2020-04','-90')]]
        result=r6.rolling_sales(rows,2)
        self.assertEqual(result['complete_windows'],1)
        self.assertEqual(result['max_net_sales_usdm'],10)
        with self.assertRaises(ValueError): r6.rolling_sales(rows+rows[:1],1)
        with self.assertRaises(ValueError): r6.rolling_sales(rows,3)

    def test_model_loss_finite_change_matches_independent_function(self):
        r=6159.276627264/38100;d=100/38100
        rows=r6.read('reports/r6_2026_11_15/financing_and_model_channels.csv')
        value=float(rows[0]['isolated_dollarization_crisis_loss_reduction_usdm'])
        self.assertAlmostEqual(value,38100*(r2_model.crisis_loss(r)-r2_model.crisis_loss(r+d)),places=8)

    def test_outputs_reproduce_and_no_unidentified_verdict(self):
        outputs=r6.generate()
        for name,text in outputs.items():
            self.assertEqual((r6.OUT/name).read_bytes(),text.encode(),name)
        v=json.loads(outputs['validation.json'])
        for key in ['observed_episode_benefit_usdm','optimal_reserves_usdm','achieved_hazard_reduction']:
            self.assertIsNone(v[key])
        self.assertEqual(len(r6.read('reports/r6_2026_11_15/joint_liquidity.csv')),264)

    def test_raw_hash_tampering_is_rejected_before_extraction(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);(root/'data').mkdir()
            (root/'data/raw.pdf').write_bytes(b'changed')
            (root/'data/r6_source_manifest.json').write_text(json.dumps([dict(id='test',local_path='data/raw.pdf',sha256=hashlib.sha256(b'original').hexdigest())]))
            with patch.object(r6,'ROOT',root):
                with self.assertRaisesRegex(ValueError,'Missing or changed'): r6.verify_sources()


if __name__=='__main__': unittest.main()
