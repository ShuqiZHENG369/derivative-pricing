
import numpy as np
import matplotlib.pyplot as plt
import yfinance as yf
from scipy.optimize import fsolve
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
    strikes = np.linspace(env.spot * 0.8, env.spot * 1.2, 50)
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
    spot_range = np.linspace(env.spot * 0.8, env.spot * 1.2, 100)
    results = {"delta": [], "gamma": [], "vega": [], "theta": [], "rho": []}
    results_put = {"delta": [], "gamma": [], "vega": [], "theta": [], "rho": []}

    for S in spot_range:
        model = BlackScholesModel(S, env.strike, env.maturity, env.rate, env.volatility, env.dividend_yield)
        g_call = GreeksCalculator(model, "call").compute_greeks()
        g_put = GreeksCalculator(model, "put").compute_greeks()
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

def plot_implied_vol_smile(env: MarketEnvironment):
    if not env.ticker:
        print("⚠️ Ticker is not set.")
        return

    ticker = yf.Ticker(env.ticker)
    expiry = ticker.options[0]
    opt_chain = ticker.option_chain(expiry)
    strikes = opt_chain.calls['strike'].values
    vols = []

    for K in strikes:
        try:
            price = float(opt_chain.calls[opt_chain.calls['strike'] == K]['lastPrice'].values[0])
            def diff(vol):
                model = BlackScholesModel(env.spot, K, env.maturity, env.rate, vol, env.dividend_yield)
                return model.bsm_call_price() - price
            iv = fsolve(diff, env.volatility)[0]
            vols.append(iv)
        except:
            vols.append(np.nan)

    plt.figure(figsize=(10, 5))
    plt.plot(strikes, vols, marker='o')
    plt.title("Implied Volatility Smile (Calls)")
    plt.xlabel("Strike")
    plt.ylabel("Implied Volatility")
    plt.grid(True)
    plt.tight_layout()
    plt.show()

def run_full_visualization(env=None, ticker=None, period=None):
    if env is None:
        if not ticker:
            ticker = input("Enter stock ticker (e.g., AAPL): ").strip().upper()
        if not period:
            period = input("Enter historical period (e.g., 3mo, 6mo, 1y): ").strip().lower()
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
            period = input("Enter historical period (e.g., 3mo, 6mo, 1y): ").strip().lower()

    env.summary()
    plot_historical_volatility(ticker, period)
    plot_price_vs_strike(env)
    plot_greeks_vs_spot(env)
    plot_implied_vol_smile(env)
