
import yfinance as yf
import numpy as np
from datetime import datetime
from fredapi import Fred

class MarketEnvironment:
    def __init__(self):
        self.ticker = "AAPL"
        self.spot = 100.0
        self.strike = 100.0
        self.maturity = 0.5
        self.rate = 0.036
        self.volatility = 0.2
        self.dividend_yield = 0.0
        self.currency = 'USD'
        self.vol_period = "90d"
        self.api_key = "your_fred_api_key"  # Replace this with your actual FRED API key

    def _get_user_defaults(self):
        print("📌 Please enter parameters. These will be used as fallback defaults if real data is unavailable.")
        self.ticker = input("Enter ticker (default: AAPL): ") or "AAPL"
        self.spot = float(input("Spot price (default: 100): ") or 100)
        self.strike = float(input("Strike price (default: 100): ") or 100)
        self.maturity = float(input("Maturity in years (default: 0.5): ") or 0.5)
        self.rate = float(input("Risk-free rate (default: 0.036): ") or 0.036)
        self.volatility = float(input("Volatility (default: 0.2): ") or 0.2)
        self.dividend_yield = float(input("Dividend yield (default: 0.0): ") or 0.0)
        use_custom_vol = input("Use custom volatility history period? (y/n, default: n): ").lower() == 'y'
        if use_custom_vol:
            self.vol_period = input("Enter historical period (e.g. '30d', '6mo', default: 90d): ") or "90d"

    def _fetch_sofr(self):
        try:
            fred = Fred(api_key=self.api_key)
            if self.maturity < 0.1:
                return fred.get_series_latest('SOFR') / 100
            elif self.maturity < 0.4:
                return fred.get_series_latest('FILSORF1M') / 100
            else:
                return fred.get_series_latest('FILSORF3M') / 100
        except:
            print("⚠️ Failed to fetch SOFR rate. Using fallback (3.6%).")
            return 0.036

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
            print(f"→ Annualized volatility: {self.volatility:.2%}")
        except:
            print(f"⚠️ Failed to compute volatility. Using fallback ({self.volatility:.2%}).")

        try:
            info = yf_ticker.info
            self.dividend_yield = info.get("dividendYield", 0.0) or 0.0
            print(f"→ Dividend yield: {self.dividend_yield:.2%}")
        except:
            print(f"⚠️ Failed to fetch dividend yield. Using fallback ({self.dividend_yield}).")

        try:
            expiries = yf_ticker.options
            print("Available expiries:")
            for i, date in enumerate(expiries):
                print(f"{i}: {date}")
            idx = int(input("Select expiry index: "))
            expiry_str = expiries[idx]
            expiry_date = datetime.strptime(expiry_str, "%Y-%m-%d")
            self.maturity = (expiry_date - datetime.today()).days / 365
            print(f"→ Maturity: {self.maturity:.3f} years")
        except:
            print(f"⚠️ Failed to parse maturity. Using fallback ({self.maturity}).")

        try:
            opt_chain = yf_ticker.option_chain(expiry_str)
            print("Available strikes (calls):")
            print(opt_chain.calls['strike'].values)
            self.strike = float(input("Enter strike price (K): "))
        except:
            print(f"⚠️ Failed to fetch option chain. Using fallback strike ({self.strike}).")

        rate_choice = input("Use SOFR for risk-free rate? (y/n): ").lower()
        if rate_choice == 'y':
            self.rate = self._fetch_sofr()
        else:
            try:
                self.rate = float(input("Enter risk-free rate: "))
            except:
                print(f"⚠️ Invalid input. Using fallback ({self.rate}).")

    def build(self):
        self._get_user_defaults()
        method = input("Do you want to fetch real market data from yfinance? (y/n): ").lower()
        if method == 'y':
            self._try_build_from_yfinance()

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
