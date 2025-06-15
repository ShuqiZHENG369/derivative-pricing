
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
        mode = input("Choose input method - 'manual' or 'yfinance': ").strip().lower()
        if mode == 'yfinance':
            self._try_build_from_yfinance()
        elif mode == 'manual':
            self._build_from_manual()
        else:
            print("Invalid mode. Please enter 'manual' or 'yfinance'.")
            return self.build()

    def _try_build_from_yfinance(self):
        self.ticker = input("Enter ticker symbol (e.g. AAPL): ").upper()
        self.currency = 'USD'  # default

        try:
            yf_ticker = yf.Ticker(self.ticker)
            self.spot = yf_ticker.history(period="1d")["Close"][-1]
            print(f"→ Spot price: {self.spot:.2f}")
        except:
            print("Failed to fetch spot price. Using default 100.0.")

        try:
            hist = yf_ticker.history(period="90d")["Close"]
            returns = hist.pct_change().dropna()
            self.volatility = returns.std() * np.sqrt(252)
            print(f"→ Estimated annualized volatility: {self.volatility:.2%}")
        except:
            print("Failed to compute volatility. Using default 20%.")

        try:
            info = yf_ticker.info
            self.dividend_yield = info.get("dividendYield", 0.0) or 0.0
            print(f"→ Dividend yield: {self.dividend_yield:.2%}")
        except:
            print("Failed to fetch dividend yield. Using default 0.0.")

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
            print("Failed to parse maturity. Using default 0.5 years.")

        try:
            opt_chain = yf_ticker.option_chain(expiry_str)
            print("\nAvailable strikes (calls):")
            print(opt_chain.calls['strike'].values)
            self.strike = float(input("Enter strike price (K): "))
        except:
            print("Failed to fetch option chain. Using default strike 100.0.")

        use_default = input("Use default SOFR rate (3.5%)? (y/n): ").lower() == 'y'
        if not use_default:
            try:
                self.rate = float(input("Enter annual risk-free rate (as decimal): "))
            except:
                print("Invalid input. Using default rate 3.5%.")

    def _build_from_manual(self):
        self.ticker = input("Enter reference name (e.g. AAPL or custom): ").upper()
        self.spot = float(input("Enter spot price (S0): ") or self.spot)
        self.strike = float(input("Enter strike price (K): ") or self.strike)
        self.maturity = float(input("Enter time to maturity (T in years): ") or self.maturity)
        self.rate = float(input("Enter annual risk-free rate (r): ") or self.rate)
        self.volatility = float(input("Enter annual volatility (σ): ") or self.volatility)
        self.dividend_yield = float(input("Enter dividend yield (q): ") or self.dividend_yield)

    def to_model_inputs(self):
        return (self.spot, self.strike, self.maturity, self.rate, self.volatility, self.dividend_yield)

    def summary(self):
        print(f"""
        Market Environment Summary
        Ticker: {self.ticker}
        Spot: {self.spot}
        Strike: {self.strike}
        Maturity: {self.maturity:.3f} years
        Rate: {self.rate:.4f}
        Volatility: {self.volatility:.4f}
        Dividend Yield: {self.dividend_yield:.4f}
        """)
