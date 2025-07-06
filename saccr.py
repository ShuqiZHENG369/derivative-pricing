import numpy as np
from greeks import GreeksCalculator

def maturity_factor(T):
    """Maturity Factor: sqrt(T) if T <= 1 else 1"""
    if T <= 0:
        raise ValueError("Maturity must be positive.")
    return np.sqrt(T) if T <= 1 else 1.0

def compute_saccr(
    model,
    market_price,
    notional,
    asset_class='equity',
    collateral=0.0,
    option_type='call',
    use_abs_delta=True
):
    """
    Compute SA-CCR EAD for a single option based on market price and model inputs.
    
    Formula:
        AddOn = |Delta| × Notional × SF × MF
        Multiplier = min(1, floor + (1 - floor) × exp(-14 × RC / AddOn))
        EAD = alpha × (RC + Multiplier × AddOn)
    """

    # --- Constants
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
    raw_delta = greeks.get("delta", 1.0)
    delta = abs(raw_delta) if use_abs_delta else raw_delta

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
        "Delta": raw_delta,
        "Delta_used": delta,
        "MaturityFactor": mf,
        "SupervisoryFactor": sf,
        "Alpha": alpha
    }

def compute_both_eads(
    model,
    call_market_price,
    put_market_price,
    notional,
    asset_class='equity',
    collateral=0.0,
    use_abs_delta=True
):
    call_result = compute_saccr(model, call_market_price, notional, asset_class, collateral, 'call', use_abs_delta)
    put_result = compute_saccr(model, put_market_price, notional, asset_class, collateral, 'put', use_abs_delta)
    return {"call": call_result, "put": put_result}

def compute_cva(ead, discount_factor, recovery_rate, default_prob):
    return (1 - recovery_rate) * default_prob * discount_factor * ead

def run_saccr_analysis(env, model, contract_size=None, collateral=None, use_abs_delta=True):
    """
    Run full SA-CCR analysis using environment and pricing model.
    """

    if contract_size is None:
        contract_size = float(input("Enter contract size (e.g., 100 for equity options): ") or 100)
    if collateral is None:
        collateral = float(input("Enter received collateral amount (default: 0): ") or 0.0)

    notional = env.spot * contract_size
    call_mkt_price = env.call_market_price
    put_mkt_price = env.put_market_price

    results = compute_both_eads(
        model,
        call_mkt_price,
        put_mkt_price,
        notional,
        asset_class="equity",
        collateral=collateral,
        use_abs_delta=use_abs_delta
    )

    print("\n🔐 SA-CCR Exposure Calculation (based on market price)")
    for option_type in ["call", "put"]:
        r = results[option_type]
        print(f"\n🧾 Option: {option_type.capitalize()}")
        print(f"  ➤ MtM (market): {call_mkt_price if option_type == 'call' else put_mkt_price:.2f}")
        print(f"  ➤ Notional: {notional:.2f}")
        print(f"  ➤ RC (Replacement Cost): {r['RC']:.2f}")
        print(f"  ➤ AddOn: {r['AddOn']:.2f} (Delta used: {r['Delta_used']:.4f})")
        print(f"  ➤ Multiplier: {r['Multiplier']:.4f}")
        print(f"  ➤ Maturity Factor: {r['MaturityFactor']:.4f}")
        print(f"  ➤ Original Delta (sign preserved): {r['Delta']:.4f}")
        print(f"  ✅ Final EAD: {r['EAD']:.2f}")
        # Step 6: CVA calculation per option type
    
    print("\n📉 CVA Calculation:")

    recovery_rate = float(input("Enter recovery rate (e.g., 0.4): ") or 0.4)
    default_prob = float(input("Enter flat default probability (e.g., 0.01): ") or 0.01)
    discount_factor = np.exp(-model.rate * model.maturity)

    for option_type in ["call", "put"]:
        r = results[option_type]
        cva = compute_cva(r["EAD"], discount_factor, recovery_rate, default_prob)
        print(f"💳 CVA for {option_type.capitalize()}: {cva:.2f}")
        if option_type == "call":
            bsm_price = model.bsm_call_price()
        else:
            bsm_price = model.bsm_put_price()
        adjusted_price = bsm_price - cva
        print(f"SACCR-CVA-Adjusted BSM Price for {option_type.capitalize()}: {bsm_price:.2f} → {adjusted_price:.2f}")

        

