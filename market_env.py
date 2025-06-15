
import yfinance as yf
import numpy as np
from datetime import datetime


class MarketEnvironment:
    def __init__(self):
        self.ticker = None
        self.spot = 100.0
        self.strike = 100.0
        self.maturity = 0.5  # in years
        self.rate = 0.035
        self.volatility = 0.2
        self.dividend_yield = 0.0
        self.currency = 'USD'

    def build(self):
        self._get_user_defaults()
        choice = input("👉 是否尝试从 yfinance 获取真实数据？(y/n): ").strip().lower()
        if choice == 'y':
            self._try_build_from_yfinance()

    def _get_user_defaults(self):
        print("请输入各项默认参数（若从 yfinance 获取失败将使用这些值）：")
        self.ticker = input("Enter ticker (default: AAPL): ") or "AAPL"
        self.spot = float(input("Enter spot price (S0, default: 100): ") or 100)
        self.strike = float(input("Enter strike price (K, default: 100): ") or 100)
        self.maturity = float(input("Enter maturity in years (T, default: 0.5): ") or 0.5)
        self.rate = float(input("Enter annual risk-free rate (r, default: 0.035): ") or 0.035)
        self.volatility = float(input("Enter annual volatility (σ, default: 0.2): ") or 0.2)
        self.dividend_yield = float(input("Enter dividend yield (q, default: 0.0): ") or 0.0)

    def _try_build_from_yfinance(self):
        self.currency = 'USD'
        try:
            yf_ticker = yf.Ticker(self.ticker)
            self.spot = yf_ticker.history(period="1d")["Close"][-1]
            print(f"→ Spot price: {self.spot:.2f}")
        except:
            print("⚠️ Failed to fetch spot price. Using default.")

        try:
            hist = yf_ticker.history(period="90d")["Close"]
            returns = hist.pct_change().dropna()
            self.volatility = returns.std() * np.sqrt(252)
            print(f"→ Estimated annualized volatility: {self.volatility:.2%}")
        except:
            print("⚠️ Failed to compute volatility. Using default.")

        try:
            info = yf_ticker.info
            self.dividend_yield = info.get("dividendYield", 0.0) or 0.0
            print(f"→ Dividend yield: {self.dividend_yield:.2%}")
        except:
            print("⚠️ Failed to fetch dividend yield. Using default.")

        try:
            expiries = yf_ticker.options
            print("\nAvailable option expiries:")
            for i, date in enumerate(expiries):
                print(f"{i}: {date}")
            idx = int(input("Select expiry index: "))
            expiry_str = expiries[idx]
            expiry_date = datetime.strptime(expiry_str, "%Y-%m-%d")
            today = datetime.today()
            self.maturity = (expiry_date - today).days / 365
            print(f"→ Maturity: {self.maturity:.3f} years")
        except:
            print("⚠️ Failed to parse maturity. Using default.")

        try:
            opt_chain = yf_ticker.option_chain(expiry_str)
            print("\nAvailable strikes (calls):")
            print(opt_chain.calls['strike'].values)
            self.strike = float(input("Enter strike price (K): "))
        except:
            print("⚠️ Failed to fetch option chain. Using default strike.")

        use_default = input("Use default SOFR rate (3.5%)? (y/n): ").lower() == 'y'
        if not use_default:
            try:
                self.rate = float(input("Enter annual risk-free rate (as decimal): "))
            except:
                print("⚠️ Invalid input. Using default rate.")

    def to_model_inputs(self):
        return (self.spot, self.strike, self.maturity, self.rate, self.volatility, self.dividend_yield)

    def summary(self):
        print(f"""
        ✅ Market Environment Summary
        Ticker: {self.ticker}
        Spot: {self.spot}
        Strike: {self.strike}
        Maturity: {self.maturity:.3f} years
        Rate: {self.rate:.4f}
        Volatility: {self.volatility:.4f}
        Dividend Yield: {self.dividend_yield:.4f}
        """)
