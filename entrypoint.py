# entrypoint.py

from market_env import MarketEnvironment
from bsm_model import BlackScholesModel
from greeks import compute_greeks
from implied_vol import implied_volatility

def main():
    print("📈 Welcome to the BSM Option Pricing Interface\n")

    # Step 1: 构建市场环境
    env = MarketEnvironment()
    env.build()
    env.summary()

    # Step 2: 实例化BSM模型
    model = BlackScholesModel(env.spot, env.strike, env.maturity, env.rate, env.volatility, env.dividend_yield)

    # Step 3: 用户选择call还是put
    otype = input("Option type ('call' or 'put'): ").strip().lower()
    if otype not in ['call', 'put']:
        otype = 'call'

    # Step 4: 计算价格
    price = model.call_price() if otype == 'call' else model.put_price()
    print(f"\n✅ {otype.capitalize()} Option Price: {price:.4f}")

    # Step 5: 显示Greeks
    greeks = compute_greeks(model, otype=otype)
    print("\n📊 Greeks:")
    for k, v in greeks.items():
        print(f"{k}: {v:.4f}")

    # Step 6: 可选 - implied volatility
    iv_request = input("\n🎯 Do you want to compute implied volatility from market price? (y/n): ").strip().lower()
    if iv_request == 'y':
        try:
            market_price = float(input("Enter observed market option price: "))
            iv = implied_volatility(market_price, env, otype=otype)
            print(f"📌 Implied Volatility: {iv:.4%}")
        except:
            print("⚠️ Invalid input or failed computation.")

if __name__ == "__main__":
    main()
