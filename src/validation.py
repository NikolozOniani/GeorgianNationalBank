"""Accounting and crosswalk gates; never treat missing inputs as zero."""
import math

def reconcile(stock_change, intervention, other_transactions, fx_valuation, gold_valuation, income, other_adjustments):
    components=(stock_change, intervention, other_transactions, fx_valuation, gold_valuation, income, other_adjustments)
    if any(x is None or not math.isfinite(x) for x in components):
        return {'status':'blocked_missing_components','residual':None}
    return {'status':'computed_not_attributed','residual':stock_change-sum(components[1:])}

def unmatched_share(rows, mapping):
    """Rows contain expenditure and survey weight; mapping is independently reviewed."""
    total=missing=0.0
    for row in rows:
        value=row['expenditure'];weight=row['weight']
        if not all(math.isfinite(v) and v>=0 for v in (value,weight)):
            raise ValueError('Invalid spending or weight')
        amount=value*weight;total+=amount
        if row['code'] not in mapping:missing+=amount
    return None if total==0 else missing/total
