"""Mechanism, timing, accounting and release gates for the reopened R3 model."""
from pathlib import Path
import csv,hashlib,json,sys,unittest
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
import r3_reopen as r3


class R3ReopenTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows=r3.panel();cls.y,cls.z=r3.arrays(cls.rows)
        cls.cfg=next(c for c in r3.read('research/r3_reopen_calibration.json') if c['primary'])
        cls.model=r3.fit(cls.y,cls.z,list(range(3,60)),cls.cfg)

    def test_calibration_sign_units_and_lags(self):
        self.assertEqual(self.cfg['b_gel_per_usd'],[-v for v in self.cfg['source_b_appreciation']])
        self.assertAlmostEqual(self.cfg['b_gel_per_usd'][0],1.913)
        b=self.cfg['b_gel_per_usd'];rho=self.cfg['rho']
        impulse=[b[0],rho*b[0]+b[1]]
        self.assertAlmostEqual(impulse[1],1.738523)
        self.assertEqual(self.rows[60]['month'],'2025-01')
        self.assertEqual(self.rows[59]['month'],'2024-12')
        self.assertEqual(len(self.rows),81)

    def test_unrestricted_reconstruction_recursively_preserves_observations(self):
        rows,err=r3.simulate(self.model,self.rows,self.y,self.z,constrain=False)
        self.assertLess(err,1e-9)
        for out,source in zip(rows,self.rows[60:]):
            self.assertAlmostEqual(out['candidate_gel_per_usd'],source['gel_per_usd'],places=10)
            self.assertAlmostEqual(out['conditional_reserves_usdm'],source['reserves_usdm'],places=7)
            self.assertAlmostEqual(out['accumulated_fx_cash_difference_gelm'],0,places=7)

    def test_constraint_satisfies_both_equations_and_complementarity(self):
        history=self.y[:60].copy()
        for t in range(60,81):
            u=r3.shocks(self.model,self.y,self.z,t)
            price,rate,q=r3.step(self.model,history,self.z[t],u,True)
            self.assertLessEqual(q,1e-10)
            demand=np.append(r3.xi(history,self.z[t]),rate)@self.model['aq']+u[2]+self.model['theta']*(price-history[-1,0])
            if q<0:self.assertAlmostEqual(q,demand,places=10)
            else:self.assertGreaterEqual(demand,-1e-10)
            supply=self.model['rho']*history[-1,0]+sum(self.model['b'][j]*history[-j,2] for j in range(1,4))+r3.zy(history,self.z[t],rate)@self.model['ay']+u[1]+self.model['b'][0]*q
            self.assertAlmostEqual(supply,price,places=10)
            history=np.vstack((history,[price,rate,q]))

    def test_reserve_bridge_and_nonconstant_emergency_sales(self):
        rows,_=r3.simulate(self.model,self.rows,self.y,self.z)
        delta=0
        for out,source in zip(rows,self.rows[60:]):
            delta=delta*(1+source['sofr_mean_pct']/1200)+out['candidate_net_intervention_usdm']-source['net_purchases_usdm']
            self.assertAlmostEqual(out['conditional_reserves_usdm']-source['reserves_usdm'],delta)
        march=next(r for r in rows if r['month']=='2026-03')
        self.assertNotAlmostEqual(march['candidate_net_intervention_usdm'],-16.2,places=2)

    def test_post_period_outcomes_never_enter_fit(self):
        altered=self.y.copy();altered[60:]+=1000
        fit=r3.fit(altered,self.z,list(range(3,60)),self.cfg)
        for key in ['ai','ay','aq','b']:np.testing.assert_array_equal(fit[key],self.model[key])
        self.assertEqual(fit['theta'],self.model['theta'])

    def test_alternative_scale_applies_to_flows_and_reserves_consistently(self):
        y,z=r3.arrays(self.rows,True);fit=r3.fit(y,z,list(range(3,60)),self.cfg)
        alternative,_=r3.simulate(fit,self.rows,y,z,scale2025=True)
        primary,_=r3.simulate(self.model,self.rows,self.y,self.z)
        self.assertGreater(alternative[-1]['candidate_gel_per_usd'],primary[-1]['candidate_gel_per_usd'])
        self.assertAlmostEqual(sum(r['candidate_net_intervention_usdm'] for r in alternative),sum(r['candidate_net_intervention_usdm'] for r in primary),places=7)

    def test_zero_kernel_is_not_mislabeled_zero_total_policy_effect(self):
        cfg=dict(self.cfg,b_gel_per_usd=[0]*4);model=r3.fit(self.y,self.z,list(range(3,60)),cfg)
        out,_=r3.simulate(model,self.rows,self.y,self.z)
        self.assertGreater(abs(out[-1]['actual_over_candidate_gap_pct']),.01)

    def test_frozen_rejection_and_output_hashes(self):
        outputs=r3.main_outputs()
        for name,data in outputs.items():
            self.assertEqual((r3.OUT/name).read_bytes(),data.encode(),name)
        info=json.loads(outputs['validation.json'])
        self.assertFalse(info['preferred_path_released'])
        self.assertFalse(info['causal_identification'])
        self.assertEqual(info['bootstrap_draws'],199)
        self.assertLess(info['admissible_bootstrap_draws']/199,.9)
        self.assertEqual(info['design_commit'],'3546bce794d093ef6458fa8813d570b14a68e42c')


if __name__=='__main__':unittest.main()
