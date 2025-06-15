# implied_vol.py

from scipy.optimize import fsolve
from bsm_model import BlackScholesModel

def implied_volatility(price, env, option_type='call', initial_vol=0.2):
    """
    Computes implied volatility from observed market price.

    Parameters
    ----------
    price : float
        Observed market option price
    env : MarketEnvironment object
        Contains market data
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
        model = BlackScholesModel(env.spot, env.strike, env.maturity, env.rate, vol, env.dividend_yield)
        if option_type == 'call':
            return model.bsm_call_price() - price
        elif option_type == 'put':
            return model.bsm_put_price() - price
        else:
            raise ValueError("Invalid option_type. Use 'call' or 'put'.")

    return fsolve(objective, initial_vol)[0]
