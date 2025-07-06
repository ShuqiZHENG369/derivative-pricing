
# 📘 Option Pricing, Greeks, CVA & SA-CCR Analysis Tool

This project is a complete interactive toolkit to analyze European options using Black-Scholes-Merton (BSM) model and simulate counterparty credit risk through CVA and SA-CCR. It integrates real-time market data from Yahoo Finance and FRED, and provides both visualization and risk calculation modules.

---

## 🛠️ Key Features

- **Market Data Integration**: Choose between real-time data (via `yfinance` and FRED) or manual input.
- **Option Chain Navigation**: Select option maturity and strike interactively.
- **Pricing Engine**: Compute call/put prices using the BSM model.
- **Greeks Calculation**: Delta, Gamma, Vega, Theta, Rho – all evaluated and visualized.
- **Volatility Analysis**: Historical volatility plot & implied volatility smile.
- **CVA Calculation**: Based on expected exposure (EE), PFE, EPE using Monte Carlo simulation.
- **SA-CCR Module**: Dynamic user interaction to compute EAD and CVA with supervisory parameters.

---

## 📐 Mathematical Formulas

### 🔹 Black-Scholes-Merton

Call price:  
$$ 
/C = S e^{-qT} N(d_1) - K e^{-rT} N(d_2)
$$

Put price:  
$$ 
/P = K e^{-rT} N(-d_2) - S e^{-qT} N(-d_1)
$$

Where:  
$$
d_1 = \frac{\ln(S/K) + (r - q + 0.5 \sigma^2) T}{\sigma \sqrt{T}}, \quad d_2 = d_1 - \sigma \sqrt{T}
$$

---

### 🔹 Greeks

**Delta**  
Call:  
$$ \Delta_{\text{call}} = e^{-qT} N(d_1) $$  
Put:  
$$ \Delta_{\text{put}} = e^{-qT}(N(d_1) - 1) $$

**Gamma**  
$$ \Gamma = \frac{e^{-qT} N'(d_1)}{S \sigma \sqrt{T}} $$

**Vega**  
$$ \nu = S e^{-qT} N'(d_1) \sqrt{T} $$

**Theta (Call)**  
$$ \Theta = -\frac{S N'(d_1) \sigma e^{-qT}}{2\sqrt{T}} - r K e^{-rT} N(d_2) + q S e^{-qT} N(d_1) $$

**Rho (Call)**  
$$ \rho = K T e^{-rT} N(d_2) $$

---

### 🔹 CVA (IMM-style)

**Continuous CVA**  
$$ \text{CVA} = (1 - R) \int_0^T EE(t) \cdot dPD(t) $$

**Discrete approximation**  
$$ \text{CVA} = (1 - R) \sum_{i=1}^{n} EE(t_i) \cdot \Delta PD(t_i) \cdot DF(t_i) $$

**Inputs**:  
- \( R \): Recovery rate  
- \( EE(t) \): Expected exposure at time \( t \)  
- \( PD \): Default probability  
- \( DF \): Discount factor

---

### 🔹 SA-CCR

**Replacement Cost (RC)**  
$$ RC = \max(0, \text{MtM} - \text{Collateral}) $$

**Add-On**  
$$ \text{AddOn} = \text{Notional} \cdot SF \cdot MF \cdot \Delta $$

**Multiplier**  
$$ \text{Multiplier} = \min\left(1, \text{floor} + (1 - \text{floor}) \cdot e^{-14 \cdot \frac{RC}{\text{AddOn}}} \right) $$

**EAD**  
$$ \text{EAD} = \alpha \cdot (RC + \text{Multiplier} \cdot \text{AddOn}) $$

---

## 📈 Output Examples

- Spot price and implied volatility from `yfinance`
- Interactive expiry & strike selection
- Greeks and price visualization
- Monte Carlo paths for EE/PFE/EPE/EEPE
- CVA breakdown and pricing adjustment
- SA-CCR EAD for call and put separately

---

## 📎 File Structure

- `market_env_updated.py`: environment builder, data fetcher
- `bsm_model.py`: Black-Scholes pricing class
- `greeks.py`: computes delta, gamma, etc.
- `saccr.py`: SA-CCR logic with delta and maturity inputs
- `cva.py`: expected exposure simulation and CVA calculation
- `primary_demo.py`: main interface to run full workflow

---

## ✍️ Author

Qi Zhang, 2025 – Personal project to learn, simulate and apply option pricing and counterparty risk assessment tools.
