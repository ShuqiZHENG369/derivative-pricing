# greeks.py


from math import log, sqrt, exp
from scipy.stats import norm


def bsm_d1(spot, strike, maturity, rate, volatility, dividend_yield=0.0):
    return (log(spot / strike) + (rate - dividend_yield + 0.5 * volatility ** 2) * maturity) /            (volatility * sqrt(maturity))


def bsm_d2(d1, volatility, maturity):
    return d1 - volatility * sqrt(maturity)


def bsm_vega(spot, strike, maturity, rate, volatility, dividend_yield=0.0):
    d1 = bsm_d1(spot, strike, maturity, rate, volatility, dividend_yield)
    return spot * norm.pdf(d1) * sqrt(maturity)


def bsm_delta(spot, strike, maturity, rate, volatility, dividend_yield=0.0, option_type='call'):
    d1 = bsm_d1(spot, strike, maturity, rate, volatility, dividend_yield)
    if option_type == 'call':
        return exp(-dividend_yield * maturity) * norm.cdf(d1)
    elif option_type == 'put':
        return -exp(-dividend_yield * maturity) * norm.cdf(-d1)
    else:
        raise ValueError("Invalid option_type: choose 'call' or 'put'")


def bsm_gamma(spot, strike, maturity, rate, volatility, dividend_yield=0.0):
    d1 = bsm_d1(spot, strike, maturity, rate, volatility, dividend_yield)
    return norm.pdf(d1) * exp(-dividend_yield * maturity) / (spot * volatility * sqrt(maturity))


def bsm_theta(spot, strike, maturity, rate, volatility, dividend_yield=0.0, option_type='call'):
    d1 = bsm_d1(spot, strike, maturity, rate, volatility, dividend_yield)
    d2 = bsm_d2(d1, volatility, maturity)
    first_term = -(spot * norm.pdf(d1) * volatility * exp(-dividend_yield * maturity)) / (2 * sqrt(maturity))
    if option_type == 'call':
        second_term = dividend_yield * spot * norm.cdf(d1) * exp(-dividend_yield * maturity)
        third_term = rate * strike * exp(-rate * maturity) * norm.cdf(d2)
        return first_term - second_term - third_term
    elif option_type == 'put':
        second_term = dividend_yield * spot * norm.cdf(-d1) * exp(-dividend_yield * maturity)
        third_term = rate * strike * exp(-rate * maturity) * norm.cdf(-d2)
        return first_term + second_term - third_term
    else:
        raise ValueError("Invalid option_type: choose 'call' or 'put'")


def bsm_rho(strike, maturity, rate, d2, option_type='call'):
    if option_type == 'call':
        return strike * maturity * exp(-rate * maturity) * norm.cdf(d2)
    elif option_type == 'put':
        return -strike * maturity * exp(-rate * maturity) * norm.cdf(-d2)
    else:
        raise ValueError("Invalid option_type: choose 'call' or 'put'")



def compute_greeks(model, option_type):
    return {
        'delta': bsm_delta(model.spot, model.strike, model.maturity, model.rate, model.volatility, model.dividend_yield, option_type),
        'gamma': bsm_gamma(model.spot, model.strike, model.maturity, model.rate, model.volatility, model.dividend_yield),
        'vega': bsm_vega(model.spot, model.strike, model.maturity, model.rate, model.volatility, model.dividend_yield),
        'theta': bsm_theta(model.spot, model.strike, model.maturity, model.rate, model.volatility, model.dividend_yield, option_type),
        'rho': bsm_rho(model.strike, model.maturity, model.rate, bsm_d2(
            bsm_d1(model.spot, model.strike, model.maturity, model.rate, model.volatility, model.dividend_yield),
            model.volatility, model.maturity), option_type)
    }
