# 🧮 Option Pricing Engine (BSM, Binomial Tree, Monte Carlo)

This is a self-built option pricing engine developed as part of my preparation for structured products, risk modeling, and QIS-related roles.

It covers essential pricing techniques (Black-Scholes, binomial tree, Monte Carlo simulation) and includes Greeks analytics (Delta, Gamma, Vega, Theta, Rho) for risk sensitivity visualization.

🧾 The valuation logic is based on real-world methodologies and best practices in derivatives pricing, as introduced in academic and practitioner-oriented references (notably *Derivatives Analytics with Python*).

---

## 📌 Features

- Black-Scholes pricing for European options  
- Binomial Tree method for American/European options  
- Monte Carlo simulation for path-dependent payoffs  
- Greeks: Delta, Gamma, Vega, Theta, Rho  
- Visualizations for price/sensitivity vs. key parameters  

---

## 📂 Structure

```
option-pricing-engine/
├── dx/
│   ├── __init__.py
│   ├── valuation.py
│   └── greeks.py
├── notebooks/
│   └── demo.ipynb
├── README.md
└── .gitignore
```

---

## 💻 Sample Usage

```python
from dx.valuation import bsm_price

price = bsm_price(S=100, K=95, T=1, r=0.03, sigma=0.2, option_type='call')
print(price)
```

---

## 🧠 Why I built this

As a CFA & FRM Level II candidate with a background in financial markets and engineering, I wanted to connect theoretical derivatives models with executable Python code.

This project helps demonstrate my technical and modeling capabilities in a modular, professional format — applicable to structured product prototyping, pricing model testing, and risk analytics.

---

## 👤 About Me

Shuqi ZHENG  
ESSEC Business School (Grande École), Financial Markets Track  
📍 Apprenticeship search: July 2025 onward  
📬 [LinkedIn](https://www.linkedin.com/in/Shuqi-Thea-ZHENG)

---

## 📄 License

This project is for demonstration and educational purposes. MIT License applies unless otherwise noted.