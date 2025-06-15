
# entrypoint.py
# run market_env to get the parameters to calculate fair_prices using BSM model, greeks, and implied volatility

from market_env import MarketEnvironment
from bsm_model import BSMModel
from greeks import OptionGreeks
from implied_vol import implied_volatility

def run_full_pricing_flow(ticker='AAPL', currency='USD', option_type='call', market_price=None):
    print("📊 Initializing Market Environment...")
    env = MarketEnvironment(ticker=ticker, currency=currency)
    env.prompt_manual_or_auto()
    env.summary()

    params = env.to_model_inputs()
    spot = params['spot']
    strike = params['strike']
    maturity = params['maturity']
    rate = params['rate']
    volatility = params['volatility']
    dividend_yield = params['dividend_yield']

    print("\n⚙️ Pricing Option using BSM Model...")
    model = BSMModel(spot, strike, maturity, rate, volatility, dividend_yield)
    call_price = model.call_price()
    put_price = model.put_price()
    print(f"Call Price: {call_price:.4f}")
    print(f"Put Price: {put_price:.4f}")

    print("\n📈 Computing Greeks...")
    greeks = OptionGreeks(model)
    delta = greeks.delta(option_type)
    vega = greeks.vega()
    print(f"{option_type.title()} Delta: {delta:.4f}")
    print(f"Vega: {vega:.4f}")

    if market_price is None:
        try:
            market_price = float(input(f"Enter observed {option_type} option market price (or leave blank to skip): ") or 0)
        except:
            market_price = 0

    if market_price > 0:
        print("\n🔍 Calculating Implied Volatility...")
        iv = implied_volatility(
            market_price=market_price,
            spot=spot,
            strike=strike,
            maturity=maturity,
            rate=rate,
            dividend_yield=dividend_yield,
            option_type=option_type
        )
        print(f"Implied Volatility: {iv:.4%}")

    print("\n✅ Process Complete.")

if __name__ == "__main__":
    run_full_pricing_flow()
