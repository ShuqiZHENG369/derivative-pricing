# 🧮 Derivatives Pricing & Visualization Toolkit

A modular option pricing and analysis engine, designed for hands-on exploration of theoretical models and real-market data. Built to support roles in structured products, risk modeling, and QIS (Quantitative Investment Strategies).

---

## 🔍 Core Capabilities

- 📈 **Black-Scholes Model** (European call/put pricing)
- ⚙️ **Greeks Analysis**: Delta, Gamma, Vega, Theta, Rho
- 🧮 **Implied Volatility Solver** (Brent/fsolve method)
- 📊 **Market Environment Builder** (real-time data via `yfinance`)
- 📉 **Volatility Analytics**: Realized vol, IV smile
- 🧠 **Visualization Modules**:
  - Historical volatility chart (multi-period)
  - Greeks vs. parameters (strike, time, vol)
  - Model price vs. market price comparisons *(in progress)*

---

## 📁 Project Structure

```
derivative-pricing/
├── bsm_model.py
├── greeks.py
├── implied_vol.py
├── market_env_updated.py
├── visualization.py
├── primary_demo.py
└── README.md
```

---

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
