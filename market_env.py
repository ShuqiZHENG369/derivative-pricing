
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
        choice = input("👉 want to try to get the real data from yfinance? (y/n): ").strip().lower()
        if choice == 'y':
            self._try_build_from_yfinance()

    def _get_user_defaults(self):
        print("Please enter each parameter. These will be used as fallback defaults if real market data cannot be retrieved:")
    
        self.ticker = input("Enter ticker (default: AAPL): ") or "AAPL"
        self.spot = float(input("Enter spot price (S0, default: 100): ") or 100)
        self.strike = float(input("Enter strike price (K, default: 100): ") or 100)
        self.maturity = float(input("Enter maturity in years (T, default: 0.5): ") or 0.5)
        self.rate = float(input("Enter annual risk-free rate (r, default: 0.035): ") or 0.035)
        self.volatility = float(input("Enter annual volatility (σ, default: 0.2): ") or 0.2)
        self.dividend_yield = float(input("Enter dividend yield (q, default: 0.0): ") or 0.0)
    
        # New: let user decide volatility estimation period
        self.use_custom_vol_period = input("Use custom historical period to estimate volatility? (y/n, default: n): ").lower() == 'y'
        if self.use_custom_vol_period:
            self.vol_period = input("Enter historical period (e.g. '30d', '90d', '6mo', default: 90d): ") or "90d"
        else:
            self.vol_period = "90d"

    def _try_build_from_yfinance(self):
        self.currency = 'USD'
        today = datetime.today()
        
        # spot price
        try:
            yf_ticker = yf.Ticker(self.ticker)
            self.spot = yf_ticker.history(period="1d")["Close"][-1]
            print(f"→ Spot price: {self.spot:.2f}")
        except:
            print(f"⚠️ Failed to fetch spot price. Using fallback ({self.spot}).")

        # volatility
        try:
            hist = yf_ticker.history(period=self.vol_period)["Close"]
            returns = hist.pct_change().dropna()
            self.volatility = returns.std() * np.sqrt(252)
            print(f"→ Estimated annualized volatility: {self.volatility:.2%}")
        except:
            print(f"⚠️ Failed to compute volatility. Using fallback ({self.volatility:.2%}).")

        # dividend yield
        try:
            info = yf_ticker.info
            self.dividend_yield = info.get("dividendYield", 0.0) or 0.0
            print(f"→ Dividend yield: {self.dividend_yield:.2%}")
        except:
            print(f"⚠️ Failed to fetch dividend yield. Using fallback ({self.dividend_yield:.2%}).")
            
        # maturity
        try:
            expiries = yf_ticker.options
            print("\nAvailable option expiries:")
            for i, date in enumerate(expiries):
                print(f"{i}: {date}")
            idx = int(input("Select expiry index: "))
            expiry_str = expiries[idx]
            expiry_date = datetime.strptime(expiry_str, "%Y-%m-%d")
            self.maturity = (expiry_date - today).days / 365
            print(f"→ Maturity: {self.maturity:.3f} years")
        except:
            print(f"⚠️ Failed to parse maturity. Using fallback ({self.maturity:.3f} years).")

        # strike price
        try:
            opt_chain = yf_ticker.option_chain(expiry_str)
            print("\nAvailable strikes (calls):")
            print(opt_chain.calls['strike'].values)
            self.strike = float(input("Enter strike price (K): "))
        except:
            print(f"⚠️ Failed to fetch option chain. Using fallback strike ({self.strike}).")

        # -----------------------
        # SOFR rate integration
        # -----------------------
        use_fallback_rate = input(f"🎯 Attempt to fetch SOFR rate based on maturity (~{self.maturity:.2f}y)? (y/n): ").lower() != 'y'
        if use_fallback_rate:
            print(f"ℹ️ Using fallback rate: {self.rate:.3%}")
        else:
            try:
                # Fetch recent SOFR curve from US Treasury website (as example source)
                sofr_url = "https://home.treasury.gov/resource-center/data-chart-center/interest-rates/Datasets/yield.xml"
                df = pd.read_xml(sofr_url)
                latest = df.iloc[-1]
                sofr_curve = {
                    '1M': float(latest['BC_1MONTH']),
                    '3M': float(latest['BC_3MONTH']),
                    '6M': float(latest['BC_6MONTH']),
                    '1Y': float(latest['BC_1YEAR']),
                    '2Y': float(latest['BC_2YEAR']),
                    '5Y': float(latest['BC_5YEAR']),
                    '10Y': float(latest['BC_10YEAR']),
                }

                # Match maturity to nearest tenor
                maturity_years = self.maturity
                if maturity_years <= 0.1:
                    self.rate = sofr_curve['1M'] / 100
                elif maturity_years <= 0.3:
                    self.rate = sofr_curve['3M'] / 100
                elif maturity_years <= 0.75:
                    self.rate = sofr_curve['6M'] / 100
                elif maturity_years <= 1.5:
                    self.rate = sofr_curve['1Y'] / 100
                elif maturity_years <= 3:
                    self.rate = sofr_curve['2Y'] / 100
                elif maturity_years <= 7:
                    self.rate = sofr_curve['5Y'] / 100
                else:
                    self.rate = sofr_curve['10Y'] / 100

                print(f"→ Risk-free rate (SOFR-based): {self.rate:.3%}")
            except:
                print(f"⚠️ Failed to fetch SOFR rate. Using fallback ({self.rate:.3%}).")
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
