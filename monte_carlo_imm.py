
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm

def monte_carlo_exposure_paths(model, n_paths=1000, option_type='call'):
    """
    Simulate asset price paths and compute positive exposures max(V(t), 0)
    Automatically uses monthly steps based on maturity
    """
    n_steps = int(np.round(model.maturity * 12))
    dt = model.maturity / n_steps

    S0 = model.spot
    r = model.rate
    sigma = model.volatility
    K = model.strike

    # Simulate asset paths
    S = np.zeros((n_paths, n_steps + 1))
    S[:, 0] = S0
    for t in range(1, n_steps + 1):
        Z = np.random.standard_normal(n_paths)  
        S[:, t] = S[:, t - 1] * np.exp((r - 0.5 * sigma**2) * dt + sigma * np.sqrt(dt) * Z)


    # Compute option value at each step using BSM and extract positive exposure
    def option_value(s, t_step):
        T = model.maturity - t_step * dt
        T = max(T, 1e-6)  # Prevent division by zero
        d1 = (np.log(s / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
        d2 = d1 - sigma * np.sqrt(T)
        if option_type == 'call':
            return s * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)
        else:
            return K * np.exp(-r * T) * norm.cdf(-d2) - s * norm.cdf(-d1)

    V = np.zeros_like(S)
    for t in range(n_steps + 1):
      V[:, t] = np.maximum(option_value(S[:, t], t), 0)

    return V, dt


def compute_exposure_metrics(V, dt, quantile=0.95):
    """
    Compute EE, EPE, EEPE, and PFE
    """
    EE = V.mean(axis=0)
    EPE = EE.mean()
    discount_factors = np.exp(-np.arange(0, V.shape[1]) * dt)
    EEPE = np.sum(EE * discount_factors) / V.shape[1]
    PFE = np.percentile(V, quantile * 100, axis=0)  # ✅ Correct
    return EE, EPE, EEPE, PFE

def plot_exposure_metrics(EE, PFE, dt):
    """
    Plot EE and PFE over time
    """
    time_grid = np.arange(len(EE)) * dt
    plt.figure(figsize=(10, 5))
    plt.plot(time_grid, EE, label='Expected Exposure (EE)', linewidth=2)
    plt.plot(time_grid, PFE, label='Potential Future Exposure (95% PFE)', linestyle='--', linewidth=2)
    plt.xlabel("Time (years)")
    plt.ylabel("Exposure Value")
    plt.title("Counterparty Credit Risk Metrics")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()
