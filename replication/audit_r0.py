"""R0 provenance/concordance audit. Reads existing evidence only; no network."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'replication/local-results/r0-audit'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def audit(root=ROOT):
    sources = json.loads((root/'data/source_manifest.json').read_text())
    catalogue = json.loads((root/'data/derived/episode_2026_11_09/catalogue.json').read_text())
    access = []
    for row in sources:
        path = root / row['local_path']
        assert row.get('sha256') and row.get('url') and row.get('bytes'), row['id']
        status = 'absent'
        if path.exists():
            status = 'verified' if digest(path)==row['sha256'] and path.stat().st_size==row['bytes'] else 'mismatch'
        access.append(dict(source_id=row['id'],original_url=row['url'],recorded_final_url=row.get('final_url'),
            local_path=row['local_path'],sha256=row['sha256'],bytes=row['bytes'],format=row['format'],
            requirements=row.get('requirements',[]),retrieved_utc=row.get('retrieved_utc'),
            local_verification=status,redistribution='Not established; raw source is not redistributed',
            recovery='Retrieve original_url and require exact SHA/size; if revised, obtain lawful original-vintage copy from provider/author; never reset pin',
            remote_vintage_recovery_tested_in_R0=False,
            publication_information='Retrieval time is not first-publication time; observation-level historical releases incomplete'))
    known={r['source_id']:r for r in access}
    concordance=[]
    for row in catalogue:
        assert all(s in known for s in row['source_ids']), row['file']
        p=root/row['file']
        status='absent' if not p.exists() else 'verified' if digest(p)==row['sha256'] else 'mismatch'
        concordance.append(dict(**row,verification=status,
            source_hashes={s:known[s]['sha256'] for s in row['source_ids']},
            period_caveat='First/last are catalogue labels; mixed annual/quarterly and reference-schedule rows are not an independently observed monthly panel',
            row_count_caveat='Rows may be source cells, categories, calendar-valid rates or repeated periods; not independent statistical observations'))
    return access,concordance


def claim_register(root=ROOT):
    definitions=[
        ('C01','Measured aggregate','reports/acquisition_2026_11_09/intervention_reconciliation.csv','year=2025; total_net_purchases_usdm',
         'USD million; calendar 2025','Sum of monthly net market purchases; already computed in linked output',
         '2025 net market purchases were USD 2,432.50 million; gross non-auction sides are unknown.',
         'Provider revisions, rounding and gross/net scope; not a causal effect','R1'),
        ('C02','Accounting identity','reports/acquisition_2026_11_09/annual_reserve_bridge.csv','year=2025; valuation_and_other_volume_residual_usdm',
         'USD million; end-2024 to end-2025','Reserve stock change minus annual BOP reserve transactions',
         'The USD 502.957 million residual combines valuation, other-volume and revision effects.',
         'No identified pure valuation or government-flow decomposition','R1'),
        ('C03','Measured audited category','data/derived/episode_2026_11_09/annual_interest_accounts.csv','year=2025; series=reserve_interest_total / policy_expense_total',
         'GEL million; 2025 accrual','Direct extracted statement categories; expenses signed negative',
         'Reserve interest was GEL 401.870 million; monetary-operation expense magnitude was GEL 129.331 million.',
         'Not matched portfolio yield or marginal reserve carry','R4'),
        ('C04','Unreconciled published benchmarks','reports/acquisition_2026_11_09/ara_component_inputs.csv','year=2025; imf_published_ara_ratio / nbg_reported_ara_pct',
         'IMF ratio versus NBG percent; 2025, different source vintages','Multiply IMF ratio by 100 for display only',
         'IMF published 94.8533% and NBG 104.8%; definitions/vintages remain unresolved.',
         'Neither proves an optimum or an institutional calculation error','R2'),
        ('C05','Historical partial exposure','archive/legacy/reports/Pilot2017_Methods_and_Results.md','Result and interpretation; Sources, validation, and crosswalk',
         'Percent of weighted 2017 household consumption','Existing six-category mapping; unmatched spending retained in denominator',
         'The pilot maps 40.92% of consumption and leaves 59.08% unmatched.',
         'Not full household inflation, current exposure or policy-attributed welfare; incomplete survey-design information','R5'),
        ('C06','Limited algebraic audit','archive/legacy/reports/reserve_readiness/Assessment_and_Design.md','Sections 2–3; model critique and reproducibility',
         'Published equations; 2026 model version','Derivative and unit checks on printed isolated channel; no new optimum',
         'Published equations raise implementation and objective questions; total optimal reserves have not been independently replicated.',
         'Printed presentation is not unpublished code; isolated channel is not total benefit','R2'),
        ('C07','Unmeasured causal estimand','research/R0_REGISTRATION.md','Section 2, primary FX estimand',
         'Percent FX gap; Jan 2025–Sep 2026','100*(E_actual/E_no_purchase-1)',
         'No numeric prevented-appreciation result is available.',
         'Execution, assignment and dynamics unresolved; require accepted identification or explicitly conditional structural model','R3'),
        ('C08','Unmeasured joint welfare estimand','research/R0_REGISTRATION.md','Sections 2 and 5',
         'December 2024 real GEL; registered window plus continuation','Common-path incremental resources and insurance; no calculation yet',
         'Whether purchases improved or reduced net welfare remains unresolved.',
         'Funding, exposures, price response, insurance and terminal value not jointly identified','R7')]
    records=[]
    for ident,kind,path,locator,units,formula,wording,uncertainty,gate in definitions:
        records.append(dict(id=ident,evidence_class=kind,source_path=path,source_sha256=digest(root/path),
            locator=locator,units_and_period=units,calculation=formula,allowed_wording=wording,
            uncertainty_and_limitations=uncertainty,next_stage=gate,
            failure_action='Remove or narrow dependent claim; preserve original evidence and record amendment'))
    return records


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--output-dir',type=Path,default=OUT)
    parser.add_argument('--require-raw',action='store_true')
    args=parser.parse_args()
    access,coverage=audit()
    args.output_dir.mkdir(parents=True,exist_ok=True)
    for name,data in [('source_access.json',access),('coverage_concordance.json',coverage),('claim_register.json',claim_register())]:
        (args.output_dir/name).write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n')
    summary=dict(sources=len(access),raw_verified=sum(r['local_verification']=='verified' for r in access),
        raw_absent=[r['source_id'] for r in access if r['local_verification']=='absent'],
        raw_mismatch=[r['source_id'] for r in access if r['local_verification']=='mismatch'],
        outputs=len(coverage),outputs_verified=sum(r['verification']=='verified' for r in coverage),
        baseline_commit='3a16715b6e8c79e4abb2dbb1a596b6e290e3b8e6',registration_date='2026-11-10',
        new_source_downloads=0,new_empirical_estimation=False,
        interpretation='Local hash verification and metadata concordance only; not proof of remote vintage permanence or economic identification')
    (args.output_dir/'audit.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps(summary,indent=2))
    if summary['raw_mismatch'] or summary['outputs_verified']!=summary['outputs'] or (args.require_raw and summary['raw_absent']):
        raise SystemExit(1)


if __name__=='__main__':main()
