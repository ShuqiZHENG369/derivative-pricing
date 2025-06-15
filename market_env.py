
import yfinance as yf
from datetime import datetime
import numpy as np

class MarketEnvironment:
    def __init__(self):
        self.ticker = None
        self.spot = None
        self.strike = None
        self.maturity = None
        self.rate = 0.03  # fallback
        self.volatility = None
        self.dividend_yield = 0.0
        self.vol_period = "90d"

    def build(self):
        print("Please enter each parameter. These will be used as fallback if real market data cannot be retrieved:")
        self.ticker = input("Enter ticker (default: AAPL): ") or "AAPL"
        self.spot = float(input("Enter spot price (S0, default: 100): ") or 100)
        self.strike = float(input("Enter strike price (K, default: 100): ") or 100)
        self.maturity = float(input("Enter maturity in years (T, default: 0.5): ") or 0.5)
        self.rate = float(input("Enter annual risk-free rate (r, default: 0.03): ") or 0.03)
        self.volatility = float(input("Enter annual volatility (σ, default: 0.2): ") or 0.2)
        self.dividend_yield = float(input("Enter dividend yield (q, default: 0.0): ") or 0.0)

        custom_vol = input("Use custom historical period for volatility? (y/n, default: n): ").lower()
        if custom_vol == 'y':
            self.vol_period = input("Enter historical period (e.g. 30d, 90d, 6mo): ") or "90d"

        # Try FRED risk-free rate fetch
        use_fred = input("🎯 Try to fetch U.S. Treasury yield from FRED for maturity? (y/n): ").lower() == 'y'
        if use_fred:
            self.get_risk_free_rate_by_maturity()

    def try_build_from_yfinance(self):
        try:
            yf_ticker = yf.Ticker(self.ticker)
            self.spot = yf_ticker.history(period="1d")["Close"][-1]
            print(f"→ Spot price: {self.spot:.2f}")
        except:
            print("⚠️ Failed to fetch spot price. Using fallback.")

        try:
            hist = yf_ticker.history(period=self.vol_period)["Close"]
            returns = hist.pct_change().dropna()
            self.volatility = returns.std() * np.sqrt(252)
            print(f"→ Estimated annualized volatility: {self.volatility:.2%}")
        except:
            print("⚠️ Failed to compute volatility. Using fallback.")

        try:
            info = yf_ticker.info
            self.dividend_yield = info.get("dividendYield", 0.0) or 0.0
            print(f"→ Dividend yield: {self.dividend_yield:.2%}")
        except:
            print("⚠️ Failed to fetch dividend yield. Using fallback.")

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
            print("⚠️ Failed to parse maturity. Using fallback.")

        try:
            opt_chain = yf_ticker.option_chain(expiry_str)
            print("\nAvailable strikes (calls):")
            print(opt_chain.calls['strike'].values)
            self.strike = float(input("Enter strike price (K): "))
        except:
            print("⚠️ Failed to fetch option chain. Using fallback.")

    def get_risk_free_rate_by_maturity(self, maturity_years=None):
        try:
            from fredapi import Fred
            fred = Fred(api_key="eccf4a9305a2ae1c3d70dc2c57f61c6f")

            if maturity_years is None:
                maturity_years = self.maturity

            terms = [
                (1/12, 'DGS1MO'),
                (3/12, 'DGS3MO'),
                (6/12, 'DGS6MO'),
                (1, 'DGS1'),
                (2, 'DGS2'),
                (3, 'DGS3'),
                (5, 'DGS5'),
                (7, 'DGS7'),
                (10, 'DGS10')
            ]

            for i in range(len(terms) - 1):
                t1, code1 = terms[i]
                t2, code2 = terms[i + 1]
                if t1 <= maturity_years <= t2:
                    r1 = fred.get_series_latest_release(code1).iloc[-1] / 100
                    r2 = fred.get_series_latest_release(code2).iloc[-1] / 100
                    interpolated = r1 + (r2 - r1) * (maturity_years - t1) / (t2 - t1)
                    print(f"→ Interpolated UST rate ({code1}-{code2}) for {maturity_years:.2f}Y: {interpolated:.4%}")
                    self.rate = interpolated
                    return

            final_code = terms[-1][1]
            final_rate = fred.get_series_latest_release(final_code).iloc[-1] / 100
            print(f"→ Using long-term UST rate ({final_code}) for {maturity_years:.2f}Y: {final_rate:.4%}")
            self.rate = final_rate

        except Exception as e:
            print(f"⚠️ Failed to fetch or interpolate UST rate. Using fallback ({self.rate:.4%}).")
