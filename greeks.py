# greeks.py

def compute_greeks(model, option_type):
    """
    Compute all Greeks for a given BSM model instance.

    Parameters
    ----------
    model : BlackScholesModel
        An instance of the Black-Scholes-Merton model.
    option_type : str
        'call' or 'put'

    Returns
    -------
    dict
        A dictionary of Delta, Gamma, Vega, Theta, Rho.
    """
    return {
        'delta': model.bsm_delta(option_type),
        'gamma': model.bsm_gamma(),
        'vega': model.bsm_vega(),
        'theta': model.bsm_theta(option_type),
        'rho': model.bsm_rho(option_type)
    }
