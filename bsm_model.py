
from math import log, exp, sqrt
from scipy.stats import norm


class BlackScholesModel:
    """Black-Scholes-Merton model for European option pricing."""

    def __init__(self, spot, strike, maturity, rate, volatility, dividend_yield=0.0):
        self.spot = spot                      # S0
        self.strike = strike                  # K
        self.maturity = maturity              # T in years
        self.rate = rate                      # r
        self.volatility = volatility          # sigma
        self.dividend_yield = dividend_yield  # q

    def d1(self):
        numerator = log(self.spot / self.strike) +                     (self.rate - self.dividend_yield + 0.5 * self.volatility ** 2) * self.maturity
        denominator = self.volatility * sqrt(self.maturity)
        return numerator / denominator

    def d2(self):
        return self.d1() - self.volatility * sqrt(self.maturity)

    def call_price(self):
        d1 = self.d1()
        d2 = self.d2()
        call = (exp(-self.dividend_yield * self.maturity) * self.spot * norm.cdf(d1) -
                exp(-self.rate * self.maturity) * self.strike * norm.cdf(d2))
        return call

    def put_price(self):
        d1 = self.d1()
        d2 = self.d2()
        put = (exp(-self.rate * self.maturity) * self.strike * norm.cdf(-d2) -
               exp(-self.dividend_yield * self.maturity) * self.spot * norm.cdf(-d1))
        return put
