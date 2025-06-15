from math import log, sqrt, exp
from scipy.stats import norm

class GreeksCalculator:
    def __init__(self, model, option_type):
        self.model = model
        self.option_type = option_type
        self._d1 = None
        self._d2 = None

    def d1(self):
        if self._d1 is None:
            self._d1 = (log(self.model.spot / self.model.strike) +
                       (self.model.rate - self.model.dividend_yield + 0.5 * self.model.volatility ** 2) * self.model.maturity) / \
                       (self.model.volatility * sqrt(self.model.maturity))
        return self._d1

    def d2(self):
        if self._d2 is None:
            self._d2 = self.d1() - self.model.volatility * sqrt(self.model.maturity)
        return self._d2

    def bsm_delta(self):
        d1 = self.d1()
        if self.option_type == 'call':
            value = exp(-self.model.dividend_yield * self.model.maturity) * norm.cdf(d1)
        elif self.option_type == 'put':
            value = -exp(-self.model.dividend_yield * self.model.maturity) * norm.cdf(-d1)
        else:
            raise ValueError("Invalid option_type: choose 'call' or 'put'")
        print(f"Delta (\u2206): Sensitivity to spot price. Unit: ∆P/∆S = {value:.4f}")
        print("Formula: Delta = e^{-qT} N(d_1)")
        return value

    def bsm_gamma(self):
        d1 = self.d1()
        value = norm.pdf(d1) * exp(-self.model.dividend_yield * self.model.maturity) / \
                (self.model.spot * self.model.volatility * sqrt(self.model.maturity))
        print("Gamma (Γ): Second-order sensitivity to spot price. Unit: ∆^2P/∆S^2")
        print("Formula: Gamma = e^{-qT} N'(d_1) / (Sσ√T)")
        return value

    def bsm_vega(self):
        d1 = self.d1()
        value = self.model.spot * norm.pdf(d1) * sqrt(self.model.maturity)
        print("Vega (\u03bd): Sensitivity to volatility. Unit: ∆P/∆σ")
        print("Formula: Vega = S N'(d_1) √T")
        return value

    def bsm_theta(self):
        d1 = self.d1()
        d2 = self.d2()
        first_term = -(self.model.spot * norm.pdf(d1) * self.model.volatility *
                      exp(-self.model.dividend_yield * self.model.maturity)) / (2 * sqrt(self.model.maturity))
        if self.option_type == 'call':
            second_term = self.model.dividend_yield * self.model.spot * norm.cdf(d1) * exp(-self.model.dividend_yield * self.model.maturity)
            third_term = self.model.rate * self.model.strike * exp(-self.model.rate * self.model.maturity) * norm.cdf(d2)
            value = first_term - second_term - third_term
        elif self.option_type == 'put':
            second_term = self.model.dividend_yield * self.model.spot * norm.cdf(-d1) * exp(-self.model.dividend_yield * self.model.maturity)
            third_term = self.model.rate * self.model.strike * exp(-self.model.rate * self.model.maturity) * norm.cdf(-d2)
            value = first_term + second_term - third_term
        else:
            raise ValueError("Invalid option_type: choose 'call' or 'put'")
        print("Theta (Θ): Sensitivity to time decay. Unit: ∆P/∆t")
        print("Formula: Theta = - (S N'(d1) σ e^{-qT})/(2√T) - ...")
        return value

    def bsm_rho(self):
        d2 = self.d2()
        if self.option_type == 'call':
            value = self.model.strike * self.model.maturity * exp(-self.model.rate * self.model.maturity) * norm.cdf(d2)
        elif self.option_type == 'put':
            value = -self.model.strike * self.model.maturity * exp(-self.model.rate * self.model.maturity) * norm.cdf(-d2)
        else:
            raise ValueError("Invalid option_type: choose 'call' or 'put'")
        print("Rho (ρ): Sensitivity to interest rate. Unit: ∆P/∆r")
        print("Formula: Rho = K T e^{-rT} N(d2)")
        return value

    def compute_greeks(self):
        return {
            'delta': self.bsm_delta(),
            'gamma': self.bsm_gamma(),
            'vega': self.bsm_vega(),
            'theta': self.bsm_theta(),
            'rho': self.bsm_rho()
        }
