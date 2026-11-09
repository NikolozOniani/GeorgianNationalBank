"""Independent arithmetic and publication-boundary tests for accountability edition."""
import csv
import decimal
import importlib.util
import json
from pathlib import Path
import re
import unittest

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('accountability',ROOT/'src/accountability_scenarios.py')
mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)


class AccountabilityTests(unittest.TestCase):
    def test_chain_not_sum_and_missing_rejected(self):
        self.assertAlmostEqual(mod.chain([10,10]),1.21)
        self.assertAlmostEqual(mod.chain([10,-10]),.99)
        for bad in ([],[float('nan')],[-100],[float('inf')]):
            with self.assertRaises(ValueError):mod.chain(bad)

    def test_independent_decimal_chain(self):
        D=decimal.Decimal
        factor=D(1)
        for row in mod.rows('reports/nbg_policy_monthly_2020_2024.csv'):
            factor*=1+D(row['cpi_monthly_pct'])/100
        values={r['id']:r['value'] for r in mod.compute()[0]}
        self.assertAlmostEqual(values['N01'],float(100*(factor-1)),places=9)
        self.assertAlmostEqual(values['N02'],1311.304322900161,places=8)
        self.assertAlmostEqual(values['N03'],762.599483991892,places=8)
        self.assertNotAlmostEqual(values['N01'],values['N04'])

    def test_interest_pass_through_and_fx_opposite_exposures(self):
        self.assertEqual(mod.interest_increment(10000,2),200)
        self.assertEqual(mod.interest_increment(10000,2,.5),100)
        self.assertEqual(mod.interest_increment(10000,2,0),0)
        self.assertAlmostEqual(mod.fx_increment(100,2.8068,.1),28.068)
        # Same currency conversion: outflow hurts debtor, inflow benefits recipient.
        self.assertAlmostEqual(mod.fx_increment(300,2.8068,.1),3*mod.fx_increment(100,2.8068,.1))

    def test_reserve_sign_and_residual_not_loss(self):
        self.assertEqual(mod.reserve_residual(-500,400),-100)
        ledger={r['id']:r for r in mod.compute()[0]}
        self.assertAlmostEqual(ledger['N09']['value'],-126.299801974189,places=7)
        self.assertIn('not missing money',ledger['N09']['uncertainty_and_limitations'])

    def test_inputs_locked_and_outputs_reproducible(self):
        mod.verify_inputs()
        generated=mod.compute()[0]
        stored=json.loads((ROOT/'reports/accountability/evidence_ledger.json').read_text())
        self.assertEqual(generated,stored)
        self.assertEqual(len({r['id'] for r in generated}),len(generated))
        sources=json.loads((ROOT/'reports/accountability/source_register.json').read_text())
        for row in generated:
            self.assertTrue(row['uncertainty_and_limitations'])
            for source in row['source_id'].split(';'):self.assertIn(source,sources)
        for row in generated:
            if row['id'].startswith('S_'):self.assertIn('Hypothetical',row['period'])

    def test_speech_claims_have_briefing_and_partial_coverage_survives(self):
        speech=(ROOT/'reports/accountability/Speech_ka.md').read_text()
        briefing=(ROOT/'reports/accountability/Fact_check.md').read_text()
        markers=re.findall(r'^\[(S\d+)\]$',speech,re.M)
        self.assertEqual(markers,[f'S{i:02}' for i in range(1,18)])
        for marker in markers:self.assertIn(marker+':',briefing)
        rows={r['id']:r for r in mod.compute()[0]}
        self.assertAlmostEqual(rows['P02']['value']+rows['P03']['value'],100)
        self.assertLess(rows['P01']['value'],rows['P02']['value'])
        self.assertIn('Partial category exposure only',rows['P05']['uncertainty_and_limitations'])


if __name__=='__main__':unittest.main()
