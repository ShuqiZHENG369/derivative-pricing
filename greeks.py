
from scipy.stats import norm
from math import log, sqrt, exp

class GreeksCalculator:
    def __init__(self, model, option_type="call"):
        self.model = model
        self.option_type = option_type.lower()
        self.S = model.spot
        self.K = model.strike
        self.T = model.maturity
        self.r = model.rate
        self.q = model.dividend_yield
        self.sigma = model.volatility

    def compute_greeks(self, verbose=True):
        d1 = (log(self.S / self.K) + (self.r - self.q + 0.5 * self.sigma ** 2) * self.T) / (self.sigma * sqrt(self.T))
        d2 = d1 - self.sigma * sqrt(self.T)

        delta = exp(-self.q * self.T) * norm.cdf(d1) if self.option_type == "call" else exp(-self.q * self.T) * (norm.cdf(d1) - 1)
        gamma = exp(-self.q * self.T) * norm.pdf(d1) / (self.S * self.sigma * sqrt(self.T))
        vega = self.S * exp(-self.q * self.T) * norm.pdf(d1) * sqrt(self.T)
        theta = (-self.S * norm.pdf(d1) * self.sigma * exp(-self.q * self.T) / (2 * sqrt(self.T)) -
                 self.r * self.K * exp(-self.r * self.T) * norm.cdf(d2) +
                 self.q * self.S * exp(-self.q * self.T) * norm.cdf(d1)) if self.option_type == "call" else                 (-self.S * norm.pdf(d1) * self.sigma * exp(-self.q * self.T) / (2 * sqrt(self.T)) +
                 self.r * self.K * exp(-self.r * self.T) * norm.cdf(-d2) -
                 self.q * self.S * exp(-self.q * self.T) * norm.cdf(-d1))
        rho = self.K * self.T * exp(-self.r * self.T) * norm.cdf(d2) if self.option_type == "call" else -self.K * self.T * exp(-self.r * self.T) * norm.cdf(-d2)

        if verbose:
            print("Formula: Delta = e^(-qT) N(d1)")
            print("Delta (Δ): Sensitivity to spot price. Unit: ΔP/ΔS = {:.4f}".format(delta))
            print("Formula: Gamma = e^(-qT) N'(d1) / (Sσ√T)")
            print("Gamma (Γ): Second-order sensitivity to spot price. Unit: Δ²P/ΔS²")
            print("Formula: Vega = S e^(-qT) N'(d1) √T")
            print("Vega (ν): Sensitivity to volatility. Unit: ΔP/Δσ")
            print("Formula: Theta = - (S N'(d1) σ e^(-qT)) / (2√T) - ...")
            print("Theta (θ): Sensitivity to time decay. Unit: ΔP/Δt")
            print("Formula: Rho = K T e^(-rT) N(d2)")
            print("Rho (ρ): Sensitivity to interest rate. Unit: ΔP/Δr")

        return {
            "delta": delta,
            "gamma": gamma,
            "vega": vega,
            "theta": theta,
            "rho": rho
        }
