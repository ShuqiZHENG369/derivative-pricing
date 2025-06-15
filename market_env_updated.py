
import yfinance as yf
import numpy as np
from datetime import datetime
from fredapi import Fred

class MarketEnvironment:
    def __init__(self):
        self.ticker = None
        self.spot = 100.0
        self.strike = 100.0
        self.maturity = 0.5
        self.rate = 0.035
        self.volatility = 0.2
        self.dividend_yield = 0.0
        self.currency = 'USD'
        self.use_custom_vol_period = False
        self.vol_period = '90d'

    def _get_user_defaults(self):
        print("Please enter each parameter. These will be used as fallback defaults if real market data cannot be retrieved:")
        self.ticker = input("Enter ticker (default: AAPL): ") or "AAPL"
        self.spot = float(input("Enter spot price (S0, default: 100): ") or 100)
        self.strike = float(input("Enter strike price (K, default: 100): ") or 100)
        self.maturity = float(input("Enter maturity in years (T, default: 0.5): ") or 0.5)
        self.rate = float(input("Enter annual risk-free rate (r, default: 0.035): ") or 0.035)
        self.volatility = float(input("Enter annual volatility (σ, default: 0.2): ") or 0.2)
        self.dividend_yield = float(input("Enter dividend yield (q, default: 0.0): ") or 0.0)
        self.use_custom_vol_period = input("Use custom historical period to estimate volatility? (y/n, default: n): ").lower() == 'y'
        if self.use_custom_vol_period:
            self.vol_period = input("Enter historical period (e.g. '30d', '90d', '6mo', default: 90d): ") or "90d"
        else:
            self.vol_period = "90d"

    def build(self):
        self._get_user_defaults()
        mode = input("📌 Fetch real market data from yfinance? (y/n): ").strip().lower()
        if mode == 'y':
            self._try_build_from_yfinance()

    def _try_build_from_yfinance(self):
        self.currency = 'USD'
        try:
            yf_ticker = yf.Ticker(self.ticker)
            self.spot = yf_ticker.history(period="1d")["Close"][-1]
            print(f"→ Spot price: {self.spot:.2f}")
        except:
            print(f"⚠️ Failed to fetch spot price. Using fallback ({self.spot}).")

        try:
            hist = yf_ticker.history(period=self.vol_period)["Close"]
            returns = hist.pct_change().dropna()
            self.volatility = returns.std() * np.sqrt(252)
            print(f"→ Estimated annualized volatility: {self.volatility:.2%}")
        except:
            print(f"⚠️ Failed to compute volatility. Using fallback ({self.volatility:.2%}).")

        try:
            info = yf_ticker.info
            self.dividend_yield = info.get("dividendYield", 0.0) or 0.0
            print(f"→ Dividend yield: {self.dividend_yield:.2%}")
        except:
            print(f"⚠️ Failed to fetch dividend yield. Using fallback ({self.dividend_yield:.2%}).")

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
            print(f"⚠️ Failed to parse maturity. Using fallback ({self.maturity:.3f} years).")

        try:
            opt_chain = yf_ticker.option_chain(expiry_str)
            print("\nAvailable strikes (calls):")
            print(opt_chain.calls['strike'].values)
            self.strike = float(input("Enter strike price (K): "))
        except:
            print(f"⚠️ Failed to fetch option chain. Using fallback strike ({self.strike}).")

        use_fred = input("🎯 Try to fetch U.S. Treasury yield from FRED for maturity? (y/n): ").lower() == 'y'
        if use_fred:
            self.rate = self.get_risk_free_rate_by_maturity(self.maturity)

    def get_risk_free_rate_by_maturity(self, maturity_years):
        try:
            fred = Fred(api_key="YOUR_API_KEY")
            if maturity_years < 0.125:
                code = 'DGS1MO'
            elif maturity_years < 0.25:
                code = 'DGS3MO'
            elif maturity_years < 0.5:
                code = 'DGS6MO'
            elif maturity_years < 1:
                code = 'DGS1'
            elif maturity_years < 2:
                code = 'DGS2'
            elif maturity_years < 5:
                code = 'DGS5'
            else:
                code = 'DGS10'

            rate = fred.get_series_latest_release(code).iloc[-1] / 100
            print(f"→ UST rate from FRED ({code}): {rate:.4%}")
            return rate
        except:
            print(f"⚠️ Failed to fetch rate. Using fallback ({self.rate:.4%}).")
            return self.rate

    def to_model_inputs(self):
        return (self.spot, self.strike, self.maturity, self.rate, self.volatility, self.dividend_yield)

    def summary(self):
        print(f"Market Environment Summary\n"
              f"Ticker: {self.ticker}\n"
              f"Spot: {self.spot}\n"
              f"Strike: {self.strike}\n"
              f"Maturity: {self.maturity:.3f} years\n"
              f"Rate: {self.rate:.4f}\n"
              f"Volatility: {self.volatility:.4f}\n"
              f"Dividend Yield: {self.dividend_yield:.4f}\n")
