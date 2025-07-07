# 🧮 Derivatives Pricing & Visualization Toolkit

A modular option pricing and analysis engine, designed for hands-on exploration of theoretical models and real-market data. Built to support roles in structured products, risk modeling, and QIS (Quantitative Investment Strategies).

---

## 🔍 Core Capabilities

-  **Black-Scholes Model** (European call/put pricing)
-  **Greeks Analysis**: Delta, Gamma, Vega, Theta, Rho
-  **Implied Volatility Solver** (Brent/fsolve method)
-  **Market Environment Builder** (real-time data via `yfinance`)
-  **Volatility Analytics**: Realized vol, IV smile
-  **Visualization Modules**:
  - Historical volatility chart (multi-period)
  - Greeks vs. parameters (strike, time, vol)
  - Model price vs. market price comparisons 


##  🔐Counterparty Risk Analytics (New Additions)

-  **Exposure Simulation**  
  Monte Carlo engine to compute time-paths of Expected Exposure (EE), Effective Expected Positive Exposure (EEPE), and 95% Potential Future Exposure (PFE) based on simulated mark-to-market evolution.

-  **CVA Engine**  
  IMM-style CVA calculator supporting both discrete and continuous formulations. Fully customizable inputs: Loss Given Default (LGD), hazard rate, and discounting.

-  **SA-CCR Calculator**  
  Market-standard Exposure at Default (EAD) calculator using SA-CCR framework. Incorporates:
  - Market MtM (non-model)
  - Replacement Cost
  - Supervisory Factors
  - Delta (with sign preservation)
  - Multiplier and Maturity Factor

-  **XVA Adjustment Module**  
  Integrates CVA into pricing to produce risk-adjusted fair value. Useful for comparing pre- and post-credit-adjusted option prices.

---
---


### 📌 File Descriptions:
- `bsm_model.py` – Black-Scholes pricing engine
- `greeks.py` – Greeks (Delta, Gamma, Vega, etc.)
- `implied_vol.py` – Implied volatility solver
- `market_env_updated.py` – Live market data interface
- `monte_carlo_imm.py` – EE/PFE/EPE CVA exposure simulation
- `saccr.py` – SA-CCR CVA computation
- `visualization.py` – Plotting Greeks and exposures
- `primary_demo.py` – Main script to run the toolkit


## ⚡ Example: Price a European Call

```python
from bsm_model import BlackScholesModel

model = BlackScholesModel(S=100, K=100, T=1, r=0.02, sigma=0.25)
call_price = model.price(option_type='call')
print(f"Call price: {call_price:.2f}")
```

---

## 🧠 Why I Built This

As a CFA & FRM Level II candidate with training in financial engineering and a strong interest in derivatives strategy, I created this toolkit to:

- Bridge theory and live market behavior
- Test pricing logic under real-world assumptions
- Visualize Greeks and volatility in a trader-oriented way

It showcases my ability to model, analyze, and communicate market data using clean code.

---

## 👤 About Me

**Shuqi ZHENG**  
ESSEC Business School (Grande École), Financial Markets Track  
📍 Seeking apprenticeship from **July 2025**  
📬 [LinkedIn](https://www.linkedin.com/in/Shuqi-Thea-ZHENG)

---

## 📄 License

This project is for educational and demonstrative use. MIT License applies unless otherwise noted.


# 📘 Mathematical Formulas 

---

## 🔹 Black-Scholes-Merton

$$
\text{Call Price: } C = S e^{-qT} N(d_1) - K e^{-rT} N(d_2)
$$

$$
\text{Put Price: } P = K e^{-rT} N(-d_2) - S e^{-qT} N(-d_1)
$$

$$
\text{Where: } d_1 = \frac{\ln(S/K) + (r - q + 0.5 \sigma^2) T}{\sigma \sqrt{T}}, \quad d_2 = d_1 - \sigma \sqrt{T}
$$

---

## 🔹 Greeks



**Delta**

$$
\begin{aligned}
\Delta_{\text{call}} &= e^{-qT} \cdot N(d_1) \\
\Delta_{\text{put}} &= e^{-qT} \cdot \left( N(d_1) - 1 \right)
\end{aligned}
$$


**Gamma**

$$
\Gamma = \frac{e^{-qT} N'(d_1)}{S \sigma \sqrt{T}}
$$

**Vega**

$$
\nu = S e^{-qT} N'(d_1) \sqrt{T}
$$

**Theta (Call)**

$$
\Theta = -\frac{S N'(d_1) \sigma e^{-qT}}{2\sqrt{T}} - r K e^{-rT} N(d_2) + q S e^{-qT} N(d_1)
$$

**Rho (Call)**

$$
\rho = K T e^{-rT} N(d_2)
$$

---

## 🔹 CVA (IMM Approach)

**Continuous:**

$$
\text{CVA} = (1 - R) \int_0^T EE(t) \cdot dPD(t)
$$

**Discrete:**

$$
\text{CVA} = (1 - R) \sum_{i=1}^{n} EE(t_i) \cdot \Delta PD(t_i) \cdot DF(t_i)
$$

Where:

- $R$: Recovery rate  
- $EE(t)$: Expected exposure  
- $PD$: Default probability  
- $DF$: Discount factor

---

## 🔹 SA-CCR

**Replacement Cost:**

$$
RC = \max(0, MtM - \text{Collateral})
$$

**Add-On:**

$$
\text{AddOn} = \text{Notional} \cdot SF \cdot MF \cdot \Delta
$$

**Multiplier:**

$$
\text{Multiplier} = \min\left(1, \text{floor} + (1 - \text{floor}) \cdot e^{-14 \cdot \frac{RC}{\text{AddOn}}} \right)
$$

**EAD:**

$$
\text{EAD} = \alpha \cdot (RC + \text{Multiplier} \cdot \text{AddOn})
$$

---

📌 **Note:** All values are derived from the Black-Scholes pricing model and are adapted to support market-standard regulatory calculations.
