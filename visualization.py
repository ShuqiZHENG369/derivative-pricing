
import numpy as np
import matplotlib.pyplot as plt
import yfinance as yf
from scipy.optimize import brentq
from scipy.stats import norm
from math import log, sqrt, exp
from market_env_updated import MarketEnvironment
from bsm_model import BlackScholesModel
from greeks import GreeksCalculator

def plot_historical_volatility(ticker="AAPL", period="6mo"):
    data = yf.download(ticker, period=period)["Close"]
    log_returns = np.log(data / data.shift(1)).dropna()
    vol = log_returns.rolling(window=21).std() * np.sqrt(252)

    plt.figure(figsize=(10, 4))
    plt.plot(vol, label="21-day Rolling Vol")
    plt.title(f"Historical Volatility: {ticker} ({period})")
    plt.xlabel("Date")
    plt.ylabel("Volatility (Annualized)")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.show()

def plot_price_vs_strike(env: MarketEnvironment):
    strikes = np.linspace(env.spot * 0.6, env.spot * 1.4, 50)
    call_prices = []
    put_prices = []

    for K in strikes:
        model = BlackScholesModel(env.spot, K, env.maturity, env.rate, env.volatility, env.dividend_yield)
        call_prices.append(model.bsm_call_price())
        put_prices.append(model.bsm_put_price())

    plt.figure(figsize=(10, 5))
    plt.plot(strikes, call_prices, label="Call")
    plt.plot(strikes, put_prices, label="Put", linestyle='--')
    plt.title("Call & Put Price vs Strike")
    plt.xlabel("Strike Price")
    plt.ylabel("Option Price")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.show()

def plot_greeks_vs_spot(env: MarketEnvironment):
    spot_range = np.linspace(env.spot * 0.6, env.spot * 1.4, 100)
    results = {"delta": [], "gamma": [], "vega": [], "theta": [], "rho": []}
    results_put = {"delta": [], "gamma": [], "vega": [], "theta": [], "rho": []}

    for S in spot_range:
        model = BlackScholesModel(S, env.strike, env.maturity, env.rate, env.volatility, env.dividend_yield)
        g_call = GreeksCalculator(model, "call").compute_greeks(verbose=False)
        g_put = GreeksCalculator(model, "put").compute_greeks(verbose=False)
        for key in results:
            results[key].append(g_call[key])
            results_put[key].append(g_put[key])

    for greek in results:
        plt.figure(figsize=(10, 4))
        plt.plot(spot_range, results[greek], label="Call")
        plt.plot(spot_range, results_put[greek], label="Put", linestyle='--')
        plt.title(f"{greek.capitalize()} vs Spot Price")
        plt.xlabel("Spot Price")
        plt.ylabel(greek.capitalize())
        plt.grid(True)
        plt.legend()
        plt.tight_layout()
        plt.show()

def implied_volatility(mid_price, S, K, T, r, q, call=True):
    def bs_price(sigma):
        d1 = (log(S/K) + (r - q + 0.5 * sigma**2) * T) / (sigma * sqrt(T))
        d2 = d1 - sigma * sqrt(T)
        if call:
            return exp(-q*T)*S*norm.cdf(d1) - exp(-r*T)*K*norm.cdf(d2)
        else:
            return exp(-r*T)*K*norm.cdf(-d2) - exp(-q*T)*S*norm.cdf(-d1)
    intrinsic = max(0.0, S - K) if call else max(0.0, K - S)
    if mid_price <= intrinsic:
        return np.nan
    try:
        return brentq(lambda sigma: bs_price(sigma) - mid_price, 1e-4, 5.0)
    except:
        return np.nan

def plot_implied_vol_smile(env: MarketEnvironment):
    if not env.ticker:
        print("⚠️ Ticker is not set.")
        return

    ticker_data = yf.Ticker(env.ticker)
    expiry_dates = ticker_data.options
    today = pd.Timestamp.today()
    target_date = today + pd.Timedelta(days=int(env.maturity * 365))
    closest_expiry = min(expiry_dates, key=lambda x: abs(pd.to_datetime(x) - target_date))

    opt_chain = ticker_data.option_chain(closest_expiry)
    calls = opt_chain.calls

    df = calls[['strike', 'bid', 'ask', 'volume']].copy()
    df = df[df['volume'] > 0]
    df['mid'] = (df['bid'] + df['ask']) / 2
    df = df[(df['ask'] - df['bid']) / df['mid'] < 0.1]  
    df = df[(df['strike'] >= env.strike * 0.6) & (df['strike'] <= env.strike * 1.4)]

    df['iv'] = df.apply(lambda row: implied_volatility(
        row['mid'], env.spot, row['strike'], env.maturity,
        env.rate, env.dividend_yield, call=True
    ), axis=1)
    df = df.dropna(subset=['iv'])

    plt.figure(figsize=(10, 5))
    plt.plot(df['strike'], df['iv'], marker='o')
    plt.axvline(env.strike, linestyle='--', color='gray', label="ATM Strike")
    plt.title(f"Implied Volatility Smile (Call Options near {closest_expiry})")
    plt.xlabel("Strike")
    plt.ylabel("Implied Volatility")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.show()


def run_full_visualization(env=None, ticker=None, period=None):
    if env is None:
        if not ticker:
            ticker = input("Enter stock ticker (e.g., AAPL): ").strip().upper()
        if not period:
            period = input("Enter historical period (e.g., 3mo, 6mo, 1y, 2y, 3y, 5y, 10y, ytd, max): ").strip().lower()
        env = MarketEnvironment()
        env.ticker = ticker
        env.build()
    else:
        if not env.ticker:
            if not ticker:
                ticker = input("Enter stock ticker (e.g., AAPL): ").strip().upper()
            env.ticker = ticker
        else:
            ticker = env.ticker
        if not period:
            period = input("Enter historical period (e.g., 3mo, 6mo, 1y, 2y, 3y, 5y, 10y, ytd, max): ").strip().lower()

    env.summary()
    plot_historical_volatility(ticker, period)
    plot_price_vs_strike(env)
    plot_greeks_vs_spot(env)
    plot_implied_vol_smile(env)
