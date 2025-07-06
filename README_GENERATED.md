
# 📘 Option Risk Analysis Toolkit

This project is an interactive Python toolkit for pricing options and analyzing counterparty credit risk using both **market-based** and **regulatory-based** approaches. It integrates data fetching (from Yahoo Finance and FRED), BSM pricing, Greeks, CVA estimation, Monte Carlo simulation, and SA-CCR exposure calculation.

---

## 🎯 Objectives

- Allow the user to interactively build a market environment by either manually inputting parameters or fetching real market data.
- Compute **Black-Scholes-Merton prices** for calls and puts.
- Visualize Greeks and Implied Volatility Smile.
- Estimate **CVA** using EE/PFE simulation and **SA-CCR**.
- Adjust market prices by CVA to obtain CVA-adjusted fair value.

---

## ⚙️ Modules Overview

| Module | Description |
|--------|-------------|
| `market_env_updated.py` | Build option market environment (spot, strike, maturity, volatility, interest rate, etc.). |
| `bsm_model.py` | Compute Black-Scholes prices for call and put options. |
| `greeks.py` | Calculate Delta, Gamma, Vega, Theta, Rho. |
| `monte_carlo_&_imm.py` | Simulate EE, EPE, EEPE, PFE, CVA via 1000-path Monte Carlo. |
| `saccr.py` | Compute SA-CCR exposures and CVA-adjusted prices. |
| `visualization.py` | Display historical vol, price vs strike, Greeks, and IV smile. |

---

## 📐 Mathematical Formulas

### 🔹 Black-Scholes-Merton

- Call Price:
  \[ C = S e^{-qT} N(d_1) - K e^{-rT} N(d_2) \]
- Put Price:
  \[ P = K e^{-rT} N(-d_2) - S e^{-qT} N(-d_1) \]
- Where:
  \[ d_1 = \frac{\ln(S/K) + (r - q + 0.5 \sigma^2) T}{\sigma \sqrt{T}}, \quad d_2 = d_1 - \sigma \sqrt{T} \]

### 🔹 Greeks

- Delta: \( \Delta = e^{-qT} N(d_1) \) for calls, \( e^{-qT}(N(d_1) - 1) \) for puts
- Gamma: \( \Gamma = \frac{e^{-qT} N'(d_1)}{S \sigma \sqrt{T}} \)
- Vega: \( \nu = S e^{-qT} N'(d_1) \sqrt{T} \)
- Theta (call): \( \Theta = -\frac{S N'(d_1) \sigma e^{-qT}}{2\sqrt{T}} - r K e^{-rT} N(d_2) + q S e^{-qT} N(d_1) \)
- Rho (call): \( \rho = K T e^{-rT} N(d_2) \)

### 🔹 CVA (Imm Approach)

- Continuous CVA:
  \[ CVA = (1 - R) \int_0^T EE(t) \, dPD(t) \]
- Discrete approximation:
  \[ CVA = (1 - R) \sum_{i=1}^{n} EE(t_i) \, \Delta PD(t_i) \cdot DF(t_i) \]
- Inputs:
  - \( R \): Recovery rate
  - \( EE(t) \): Expected exposure at time \( t \)
  - \( PD \): Default probability
  - \( DF \): Discount factor

### 🔹 SA-CCR

- Replacement Cost (RC): \( RC = \max(0, MtM - \text{Collateral}) \)
- Add-On: \( AddOn = \text{Notional} \cdot SF \cdot MF \cdot \Delta \)
- Multiplier:
  \[ Multiplier = \min\left(1, floor + (1 - floor) \cdot e^{-14 \cdot RC / AddOn} \right) \]
- EAD:
  \[ EAD = \alpha \cdot (RC + Multiplier \cdot AddOn) \]
- Typical values:
  - \( \alpha = 1.4 \)
  - \( floor = 0.05 \)
  - Supervisory Factors (SF): equity = 0.32, fx = 0.04, IR = 0.005, commodity = 0.15
  - Maturity Factor (MF): \( \sqrt{T} \) if \( T < 1 \), else 1

---

## 🧪 Example Workflow

1. 📥 Fetch data or manually input: spot, strike, vol, rate, dividend, maturity.
2. 📈 Compute BSM price and Greeks.
3. 🔁 Run Monte Carlo simulation to get EE, PFE, EPE, EEPE.
4. 💳 Calculate CVA from expected exposures.
5. 🧮 Run SA-CCR and CVA-adjusted EAD.
6. 💰 Print CVA-adjusted fair price.

---

## 📌 Notes

- The model assumes flat interest rate and constant volatility (BSM framework).
- Default probabilities are treated as flat or time-bucketed.
- CVA and EAD calculations are consistent with regulatory approximations but not intended for production risk engines.

---

## 📎 To Do

- [ ] Add support for American options (binomial trees).
- [ ] Dynamic default curves.
- [ ] Interactive Streamlit UI for full integration.

---

## 📚 References

- Basel Committee: "The standardised approach for measuring counterparty credit risk exposures" (SA-CCR)
- Hull, J.: Options, Futures and Other Derivatives.
- Andersen & Pykhtin (2011): Exposure at Default and CVA.

---
