import numpy as np
from greeks import GreeksCalculator

def maturity_factor(T):
    return np.sqrt(T) if T <= 1 else 1.0

def compute_saccr(
    model,
    market_price,
    notional,
    asset_class='equity',
    collateral=0.0,
    option_type='call'
):
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
    T = model.maturity
    mf = maturity_factor(T)

    greeks = GreeksCalculator(model, option_type).compute_greeks(verbose=False)

    delta = abs(greeks.get("delta", 1.0))

    rc = max(0, market_price - collateral)
    addon = notional * sf * mf * delta

    if addon == 0:
        multiplier = 1.0
    else:
        multiplier = min(1, floor + (1 - floor) * np.exp(-14 * rc / addon))

    ead = alpha * (rc + multiplier * addon)

    return {
        "option_type": option_type,
        "EAD": ead,
        "RC": rc,
        "AddOn": addon,
        "Multiplier": multiplier,
        "Delta": delta,
        "MaturityFactor": mf,
        "SupervisoryFactor": sf,
        "Alpha": alpha
    }

def compute_both_eads(model, call_market_price, put_market_price, notional, asset_class='equity', collateral=0.0):
    call_result = compute_saccr(model, call_market_price, notional, asset_class, collateral, 'call')
    put_result = compute_saccr(model, put_market_price, notional, asset_class, collateral, 'put')
    return {"call": call_result, "put": put_result}

def run_saccr_analysis(env, model):
    contract_size = float(input("Enter contract size (e.g., 100 for equity options): ") or 100)
    collateral = float(input("Enter received collateral amount (default: 0): ") or 0.0)
    notional = env.spot * contract_size

    call_mkt_price = env.call_market_price
    put_mkt_price = env.put_market_price

    results = compute_both_eads(model, call_mkt_price, put_mkt_price, notional, asset_class="equity", collateral=collateral)

    print("\n🔐 SA-CCR Exposure Calculation (based on market price)")
    for option_type in ["call", "put"]:
        r = results[option_type]
        print(f"\n🧾 Option: {option_type.capitalize()}")
        print(f"  ➤ MtM (market): {call_mkt_price if option_type=='call' else put_mkt_price:.2f}")
        print(f"  ➤ Notional: {notional:.2f}")
        print(f"  ➤ RC (Replacement Cost): {r['RC']:.2f}")
        print(f"  ➤ AddOn: {r['AddOn']:.2f}")
        print(f"  ➤ Multiplier: {r['Multiplier']:.4f}")
        print(f"  ➤ Maturity Factor: {r['MaturityFactor']:.4f}")
        print(f"  ➤ Delta: {r['Delta']:.4f}")
        print(f"  ✅ Final EAD: {r['EAD']:.2f}")
