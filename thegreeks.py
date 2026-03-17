#This will be used to calculate the Greeks for the options in the IV surface. 
#Currently only Vega is implemented, but I will add more later. 
#This is also where the create_iv_surface function is located, which is called by IVSurface.py to fetch real market data and 
#compute IV values for each option using Brent's method.

import numpy as np
from scipy.stats import norm
from black_scholes import d1, d2

#Below will calculate Delta for the given option 
def delta(S, K, T, r, sigma, q, option_type):
    d1_value = d1(S, T, K, r, q, sigma)
    if option_type == "Call":
        return np.exp(-q * T) * norm.cdf(d1_value)
    elif option_type == "Put":
        return -np.exp(-q * T) * norm.cdf(-d1_value)
    
#Below will calculate Gamma for the given option
def gamma(S, K, T, r, sigma, q):
    d1_value = d1(S, T, K, r, q, sigma)
    return np.exp(-q * T) * norm.pdf(d1_value) / (S * sigma * np.sqrt(T))

#Below will calculate Vega for the given option
def vega(S, K, T, r, sigma, q):
    d1_value = d1(S, T, K, r, q, sigma)
    return S * np.exp(-q * T) * norm.pdf(d1_value) * np.sqrt(T)

#Below will calculate Theta for the given option
def theta(S, K, T, r, sigma, q, option_type):
    d1_value = d1(S, T, K, r, q, sigma)
    d2_value = d2(d1_value, sigma, T)
    if option_type == "Call":
        return (-S * np.exp(-q * T) * norm.pdf(d1_value) * sigma / (2 * np.sqrt(T)) 
                - r * K * np.exp(-r * T) * norm.cdf(d2_value) 
                + q * S * np.exp(-q * T) * norm.cdf(d1_value))
    elif option_type == "Put":
        return (-S * np.exp(-q * T) * norm.pdf(d1_value) * sigma / (2 * np.sqrt(T)) 
                + r * K * np.exp(-r * T) * norm.cdf(-d2_value) 
                - q * S * np.exp(-q * T) * norm.cdf(-d1_value))

#Below will calculate Rho for the given option
def rho(S, K, T, r, sigma, q, option_type):
    d1_value = d1(S, T, K, r, q, sigma)
    d2_value = d2(d1_value, sigma, T)
    if option_type == "Call":
        return K * T * np.exp(-r * T) * norm.cdf(d2_value)
    elif option_type == "Put":
        return -K * T * np.exp(-r * T) * norm.cdf(-d2_value)
    
#Computes all the greeks 
def compute_greeks(df, r, option_type):
    df = df.copy()
    df['delta'] = df.apply(lambda row: delta(row['S'], row['K'], row['T'], r, row['iv'], row['q'], option_type), axis=1)
    df['gamma'] = df.apply(lambda row: gamma(row['S'], row['K'], row['T'], r, row['iv'], row['q']), axis=1)
    df['vega']  = df.apply(lambda row: vega( row['S'], row['K'], row['T'], r, row['iv'], row['q']), axis=1)
    df['theta'] = df.apply(lambda row: theta(row['S'], row['K'], row['T'], r, row['iv'], row['q'], option_type), axis=1)
    df['rho']   = df.apply(lambda row: rho(  row['S'], row['K'], row['T'], r, row['iv'], row['q'], option_type), axis=1)
    return df



