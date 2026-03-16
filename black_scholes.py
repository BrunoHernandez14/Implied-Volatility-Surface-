from scipy.stats import norm
import numpy as np
import yfinance as yf
import pandas as pd
from scipy.optimize import brentq

#Black-Scholes formulas for call and put prices, and Vega for IV calculation
#We are using Brent's method for solving volatility from real time market prices
#S = Spot Price
#K = Strike Price
#T = Time to Expiration (in years)
#r = Risk-Free Rate
#sigma = Volatility(initial sigma is just a guess for the solver)
#q = Dividend Yield
def black_scholes_call_price(S, K, T, r, sigma, q):
    d1 = (np.log(S / K) + (r - q + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    return S * np.exp(-q * T) * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)

def black_scholes_put_price(S, K, T, r, sigma, q):
    d1 = (np.log(S / K) + (r - q + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    return K * np.exp(-r * T) * norm.cdf(-d2) - S * np.exp(-q * T) * norm.cdf(-d1)

def vega(S, K, T, r, sigma, q):
    d1 = (np.log(S / K) + (r - q + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
    return S * np.exp(-q * T) * norm.pdf(d1) * np.sqrt(T)

#This method will be called by IVSurface.py to create the implied volatility surface 
#dataframe using real market data
def create_iv_surface(ticker_symbol, r, q, min_strike, max_strike):
    ticker = yf.Ticker(ticker_symbol)
    today = pd.Timestamp('today').normalize()

    #Gathers spot price
    try:
        history = ticker.history(period='5d')
        if history.empty:
            return pd.DataFrame(), None
        spot_price = history['Close'].iloc[-1]
    except Exception:
        return pd.DataFrame(), None

    #Expirations and option chain data with IV calculation using Brent's method
    try:
        expirations = ticker.options
    except Exception:
        return pd.DataFrame(), None

    exp_dates = [
        pd.Timestamp(exp) for exp in expirations
        if pd.Timestamp(exp) > today + pd.Timedelta(days=7)
    ]

    if not exp_dates:
        return pd.DataFrame(), spot_price

    records = []
    for exp_date in exp_dates:
        try:
            calls = ticker.option_chain(exp_date.strftime('%Y-%m-%d')).calls
        except Exception:
            continue

        calls = calls[(calls['bid'] > 0) & (calls['ask'] > 0)]

        T = (exp_date - today).days / 365

        for _, row in calls.iterrows():
            K = row['strike']

            if not (min_strike <= K <= max_strike):
                continue

            mid = (row['bid'] + row['ask']) / 2

            try:
                iv = brentq(
                    lambda sigma: black_scholes_call_price(spot_price, K, T, r, sigma, q) - mid,
                    1e-6, 5.0
                )
            except (ValueError, RuntimeError):
                iv = np.nan

            if not np.isnan(iv):
                records.append({'T': T, 'K': K, 'iv': iv})

    return pd.DataFrame(records), spot_price