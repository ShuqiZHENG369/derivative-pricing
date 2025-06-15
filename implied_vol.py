
# implied_vol.py

from scipy.optimize import fsolve
from bsm_model import bsm_call_price, bsm_put_price

def compute_implied_vol(price, spot, strike, maturity, rate, dividend_yield=0.0, 
                        option_type='call', initial_vol=0.2):
    """
    Computes implied volatility by minimizing difference between market price and model price.

    Parameters
    ----------
    price : float
        Observed option price
    spot : float
        Spot price of underlying asset
    strike : float
        Strike price of option
    maturity : float
        Time to maturity in years
    rate : float
        Risk-free interest rate
    dividend_yield : float
        Continuous dividend yield
    option_type : str
        'call' or 'put'
    initial_vol : float
        Initial guess for volatility

    Returns
    -------
    float
        Implied volatility
    """
    def objective(vol):
        if option_type == 'call':
            return bsm_call_price(spot, strike, maturity, rate, vol, dividend_yield) - price
        elif option_type == 'put':
            return bsm_put_price(spot, strike, maturity, rate, vol, dividend_yield) - price
        else:
            raise ValueError("option_type must be 'call' or 'put'.")

    result = fsolve(objective, initial_vol)[0]
    return result
