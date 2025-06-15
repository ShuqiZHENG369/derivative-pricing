
import yfinance as yf
import numpy as np
from datetime import datetime


class MarketEnvironment:
    def __init__(self):
        self.ticker = None
        self.spot = None
        self.strike = None
        self.maturity = None  # in years
        self.rate = None
        self.volatility = None
        self.dividend_yield = None
        self.currency = 'USD'  # default USD

    def build(self):
        mode = input("📌 Choose input method - 'manual' or 'yfinance': ").strip().lower()
        if mode == 'yfinance':
            self._build_from_yfinance()
        elif mode == 'manual':
            self._build_from_manual()
        else:
            print("Invalid mode. Please enter 'manual' or 'yfinance'.")
            return self.build()

    def _build_from_yfinance(self):
        self.ticker = input("Enter ticker symbol (e.g. AAPL): ").upper()
        yf_ticker = yf.Ticker(self.ticker)

        # Spot price
        try:
            self.spot = yf_ticker.history(period="1d")["Close"][-1]
            print(f"→ Spot price: {self.spot:.2f}")
        except:
            raise ValueError("⚠️ Failed to fetch spot price.")

        # Volatility estimate
        try:
            hist = yf_ticker.history(period="90d")["Close"]
            returns = hist.pct_change().dropna()
            self.volatility = returns.std() * np.sqrt(252)
            print(f"→ Estimated annualized volatility: {self.volatility:.2%}")
        except:
            raise ValueError("⚠️ Failed to compute volatility.")

        # Dividend yield
        try:
            info = yf_ticker.info
            self.dividend_yield = info.get("dividendYield", 0.0) or 0.0
            print(f"→ Dividend yield: {self.dividend_yield:.2%}")
        except:
            self.dividend_yield = 0.0
            print("⚠️ Dividend yield not found. Default to 0.0")

        # Show option expiry dates
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

        # Show option chain for that expiry
        opt_chain = yf_ticker.option_chain(expiry_str)
        print("\nAvailable strikes (calls):")
        print(opt_chain.calls['strike'].values)
        self.strike = float(input("Enter strike price (K): "))

        # Get risk-free rate
        use_default = input("Use default SOFR rate (3.5%)? (y/n): ").lower() == 'y'
        if use_default:
            self.rate = 0.035
        else:
            self.rate = float(input("Enter annual risk-free rate (as decimal): "))

    def _build_from_manual(self):
        self.ticker = input("Enter reference name (e.g. AAPL or custom): ").upper()
        self.spot = float(input("Enter spot price (S0): "))
        self.strike = float(input("Enter strike price (K): "))
        self.maturity = float(input("Enter time to maturity (T in years): "))
        self.rate = float(input("Enter annual risk-free rate (r): "))
        self.volatility = float(input("Enter annual volatility (σ): "))
        self.dividend_yield = float(input("Enter dividend yield (q): "))

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
