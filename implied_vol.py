# implied_vol.py

from scipy.optimize import fsolve
from bsm_model import BlackScholesModel

def auto_implied_vol(env, model):
    from scipy.optimize import fsolve
    spot, strike, T, r, sigma, q = env.to_model_inputs()

    results = {}

    if env.call_market_price:
        def call_diff(vol):
            model.volatility = vol
            return model.bsm_call_price() - env.call_market_price
        iv_call = fsolve(call_diff, sigma)[0]
        results['Call Implied Vol'] = iv_call

    if env.put_market_price:
        def put_diff(vol):
            model.volatility = vol
            return model.bsm_put_price() - env.put_market_price
        iv_put = fsolve(put_diff, sigma)[0]
        results['Put Implied Vol'] = iv_put

    if results:
        print("\n📌 Implied Volatility (from market data):")
        for k, v in results.items():
            print(f"{k}: {v:.4%}")
    else:
        print("⚠️ No market prices available. Cannot compute implied vol.")

    return results

