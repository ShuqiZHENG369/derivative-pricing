import numpy as np
from greeks import GreeksCalculator

def maturity_factor(T):
    """
    Calculate SA-CCR Maturity Factor based on time to maturity (in years).
    """
    return np.sqrt(T) if T <= 1 else 1.0

def compute_saccr(
    model, 
    market_price, 
    notional, 
    asset_class='equity', 
    collateral=0.0, 
    option_type='call'
):
    """
    Compute SA-CCR EAD for a given option based on market price.

    Parameters:
    - model: Option pricing model object
    - market_price: Market price of the option (MtM)
    - notional: Notional value = spot * contract_size
    - asset_class: 'equity', 'fx', 'interest_rate', or 'commodity'
    - collateral: Value of collateral received (user input)
    - option_type: 'call' or 'put'

    Returns:
    A dictionary with EAD, RC, AddOn, Multiplier, Delta, Maturity Factor
    """
    alpha = 1.4
    floor = 0.05

    supervisory_factors = {
        'equity': 0.32,
        'fx': 0.04,
        'interest_rate': 0.005,
        'commodity': 0.15
    }

    if asset_class not in supervisory_factors:
        raise ValueError(f"Unsupported asset class: {asset_class}")

    sf = supervisory_factors[asset_class]
    rc = max(0, market_price - collateral)
    addon = notional * sf
    multiplier = min(1, floor + (1 - floor) * np.exp(-14 * rc / addon)) if addon > 0 else 1.0
    ead = alpha * (rc + multiplier * addon)

    greeks = GreeksCalculator(model, option_type).compute_greeks()
    delta = greeks.get("delta", 1.0)

    T = model.maturity
    mf = maturity_factor(T)

    return {
        "option_type": option_type,
        "EAD": ead,
        "RC": rc,
        "AddOn": addon,
        "Multiplier": multiplier,
        "Delta": delta,
        "MaturityFactor": mf
    }

def compute_both_eads(model, call_market_price, put_market_price, notional, asset_class='equity', collateral=0.0):
    """
    Compute EADs for both call and put options and return a dictionary of results.
    """
    call_result = compute_saccr(model, call_market_price, notional, asset_class, collateral, 'call')
    put_result = compute_saccr(model, put_market_price, notional, asset_class, collateral, 'put')
    return {"call": call_result, "put": put_result}