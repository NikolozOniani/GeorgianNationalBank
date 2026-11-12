"""Public equations in Cangul–Abel SIP/2026/051. GDP = 1, rates in fractions.

The baseline and Annex equations are separate specifications. No missing
Georgian parameter is assigned a default or inferred from the reported target.
"""
from math import expm1, log, log1p


def baseline(private_debt, output_loss, premium, probability, risk_aversion):
    """PDF p6, including footnote 2, with its denominator grouped as in JR."""
    if not (0 < probability < 1 and 0 <= premium < 1 - probability
            and risk_aversion > 0 and private_debt >= 0 and 0 <= output_loss < 1):
        raise ValueError("Baseline inputs outside formula domain")
    price = 1 + premium / (probability * (1 - premium - probability))
    return private_debt + output_loss + expm1(-log(price) / risk_aversion)


def spread(r, intercept, slope):
    return intercept - slope * log1p(r)


def carrying_margin(r, intercept, slope):
    return spread(r, intercept, slope) - slope * r / (1 + r)


def crisis_loss(r):
    dollarization = 0.60 - 0.10 * log1p(r)
    if r < 0 or not 0 <= dollarization <= 1:
        raise ValueError("Outside printed dollarization domain")
    return 0.10 * (1 + 0.50 * dollarization)


def loss_derivative(r):
    return -0.005 / (1 + r)


def utility(c, sigma):
    if c <= 0 or sigma <= 0:
        raise ValueError("CRRA requires positive consumption and curvature")
    return log(c) if sigma == 1 else expm1((1 - sigma) * log(c)) / (1 - sigma)


def annex_utility(r, probability, loss, sigma, intercept, slope):
    """PDF p13. The subtraction of a utility constant leaves rankings unchanged."""
    if r < 0 or not 0 < probability < 1 or slope < 0:
        raise ValueError("Invalid p13 input")
    normal = 1 - r * spread(r, intercept, slope)
    crisis = 1 - loss + r
    return (1 - probability) * utility(normal, sigma) + probability * utility(crisis, sigma)


def annex_derivative(r, probability, loss, sigma, intercept, slope):
    normal = 1 - r * spread(r, intercept, slope)
    crisis = 1 - loss + r
    if min(normal, crisis) <= 0:
        raise ValueError("Outside consumption domain")
    return (probability * crisis ** (-sigma) -
            (1 - probability) * normal ** (-sigma) * carrying_margin(r, intercept, slope))


def average_loss_cost_intercept(r, probability, loss, slope):
    """Sum rho + s0 required for r to solve the p14 average-loss equation."""
    if r <= 0 or not 0 < probability < 1 or loss <= 0 or slope <= 0:
        raise ValueError("Positive reserve ratio, loss and slope required")
    return probability / (1 - probability) * loss / r + slope * (log1p(r) + r / (1 + r))


def minimum_intercept(probability, loss, slope):
    """Unique minimum of required intercept. Below/at/above gives 0/1/2 roots."""
    if not 0 < probability < 1 or not loss > 0 or not slope > 0:
        raise ValueError("Positive loss and slope and interior probability required")
    a = probability * loss / (1 - probability)
    def residual(r):
        return slope * r ** 2 * (r + 2) / (1 + r) ** 2 - a
    lo, hi = 0.0, 1.0
    while residual(hi) < 0:
        hi *= 2
    for _ in range(90):
        mid = (lo + hi) / 2
        if residual(mid) < 0:
            lo = mid
        else:
            hi = mid
    r = (lo + hi) / 2
    return r, average_loss_cost_intercept(r, probability, loss, slope)
