# Historical FX funding shocks in Georgia

**First step 1 release, 19 November 2026.** The [screen specification](../../research/HISTORICAL_FX_SHOCK_SCREEN.md) was committed at ab96e187 before ranking. The screen covers all 68 quarters from 2008Q1 through 2024Q4 on all three indicators. The first detailed case is 2008. No public reserve requirement is estimated at this stage.

## What the screen found

| Largest measured pressure | Quarter | Change relative to pre-shock exposure |
|---|---|---:|
| Goods and services export credits | 2020Q2 | 50.88% below the same quarter of 2019 |
| External loan liabilities of deposit-taking banks | 2013Q1 | Net repayments equal to 9.02% of opening external loans |
| Broad-money FX deposits in USD equivalent | 2009Q1 | 16.04% below the previous quarter-end |

The five most adverse observations on each indicator give eight contiguous flagged windows. In 2009Q2 all three indicators flag simultaneously. In 2020Q2–Q4 only exports flag. The 2022 named candidate never enters the top five on these particular measures. The pre-specified median-rank comparison is 2018Q3. A normalized repayment score can reflect routine scheduled deleveraging, a deposit stock can move on cross-currency valuation, and exports can be sold on credit. These observations prioritize historical investigation. Interpreting their sum as a call on NBG would double-count private transactions and assume a government guarantee. The screen omits within-quarter reversals, remittances, equity and other financing channels. The rank uses the revised full sample and has no predictive or probability interpretation. [All quarterly inputs, scores and ranks](screen.csv) · [Screened and named windows](windows.csv)

## The 2008 financing chronology

- Gross reserves declined from USD 1,464.75m at end-July to USD 1,122.86m at end-August. The contemporary IMF account records a USD 330m decline from **6 August**, and USD 187m in FX sales; the later review reports the August sales as USD 190m. The month-end stock decline of USD 341.89m and the within-month IMF figure use different openings. Subtracting USD 187m from the full-month decline leaves roughly USD 155m unallocated to those sales; it includes any other flows, valuation, coverage or rounding. The IMF names government imports and the FX reserve-requirement waiver. Neither item has a separately verified monthly cash amount here.
- Broad-money FX deposits fell from USD 1,289.10m to USD 1,129.68m equivalent in August, then recovered USD 68.96m in September. The July–August drop of USD 159.42m exceeded the **whole third quarter's** net drop of USD 48.05m. Depositors' bank claims, dollar notes available at branches, transferred funds and public reserve disbursements are four different quantities. Do not add this drop to NBG sales.
- In September the IMF approved approximately USD 750m of stand-by access. The first drawing was about USD 250m; government repatriation supplied another USD 50m from its own foreign assets. NBG reserves rose USD 250.47m that month. Relative to those two rounded inflows, the remaining stock change was about **minus USD 49.53m**, without a verified allocation. Omitting subsequent emergency financing from a stress scenario requires modeling how payments or policy would adjust.
- In October gross reserves fell USD 101.23m. In November they rose USD 67.66m while the official month-end quote moved from 1.421 to 1.650 GEL/USD. A contemporaneous review describes cumulative sales defending the peg from 7 August to 7 November as about a third of reserves. That overlapping figure cannot supply monthly execution amounts.
- Across 2008Q3 the stock fell USD 152.80m, of which net BOP reserve-asset transactions were minus USD 112.36m. The remaining minus USD 40.44m includes valuation, other volume movements and possible vintage differences. The quarterly residual cannot be distributed among particular August payments.

[Monthly NBG observations](georgia_2008_monthly.csv) · [Public financing chronology with individual IMF sources](war_chronology.csv) · [IMF contemporary assessment](https://www.elibrary.imf.org/view/journals/002/2008/328/article-A001-en.xml) · [IMF first review](https://www.imf.org/external/pubs/ft/scr/2009/cr0901.pdf)

## Verification and remaining coverage

Five previously pinned NBG workbooks supply all numerical screen inputs. Read the [manifest](../../data/source_manifest.json) for URLs, units and SHA-256 hashes. In the detailed BOP sheet the quarter columns are identified by period labels, exports by row 8, bank loan net incurrence by row 715 and reserve transactions by row 837. External debt sheet ED-GEO-Tb1 rows 36 and 42 supply the previous quarter's bank loan stocks. Monetary Ratios-eng column J supplies FX deposits in millions of GEL; the USD column of the consolidated daily FX workbook supplies the calendar-end conversion. The GIR sheet column B gives reserves in thousands of USD, converted to millions. Annual BOP totals never enter quarterly sums. Release and revision dates for individual historical cells remain unverified. The IMF chronology is a manual, source-linked transcription; a contemporaneous publication can describe several earlier dates. IMF narrative source bytes are not pinned in this checkpoint.

From the repository root, with the five pinned workbooks in their manifest paths, run:

```sh
python src/historical_fx_shocks.py --check
python -m unittest discover -s tests -p test_historical_fx_shocks.py
```

The screening and 2008 stock/flow bridge are reproducible. Still open in step 1 are borrower-level gross principal due versus renewed, dated public cash obligations, accessible bank-owned liquidity, exact public support and comparable monthly cash ledgers for other selected episodes. The simultaneous deposit, export and bank-funding pressure in 2009Q2 makes it the first extension of the 2008 case. The separate 2020 export interruption provides a contrasting case. Until those cash accounts reconcile, no score or historical maximum here is an adequate-reserve target.
