
# 📘 Mathematical Formulas (Improved Version)

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

- Call: 
  $$
  \Delta_{\text{call}} = e^{-qT} N(d_1)
  $$

- Put:
  $$
  \Delta_{\text{put}} = e^{-qT}(N(d_1) - 1)
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
