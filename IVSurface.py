#Creates an implied volatility surface for a given ticker using 
#real market data and the Black-Scholes model.
import streamlit as st
import numpy as np
import plotly.graph_objects as go
import yfinance as yf
from black_scholes import create_iv_surface
from scipy.interpolate import griddata

#Streamlit UI setup
st.set_page_config(page_title="IV Surface", layout="wide")
st.title("Implied Volatility Surface")
st.markdown("Black-Scholes Model - Brent's Method IV Solver - Real Market Data")
st.sidebar.header("Parameters")

ticker_symbol = st.sidebar.text_input("Ticker Symbol", value="SPY").upper()
risk_free_rate = st.sidebar.number_input("Risk-Free Rate",  value=0.05, step=0.01, format="%.3f")
dividend_yield = st.sidebar.number_input("Dividend Yield",  value=0.02, step=0.01, format="%.3f")
option_type = st.sidebar.selectbox("Option Type", ["Call", "Put"])

try:
    history = yf.Ticker(ticker_symbol).history(period="1d")
    if history.empty:
        st.error(f"No price data for '{ticker_symbol}'.")
        st.stop()
    stock_price = history["Close"].iloc[-1]
except Exception as e:
    st.error(f"Could not fetch '{ticker_symbol}': {e}")
    st.stop()

st.write(f"**{ticker_symbol}** last price: **${stock_price:.2f}**")

st.sidebar.subheader("Strike Range ($)")
K_min = st.sidebar.number_input("Min Strike ($)", min_value=0.01,
    value=round(stock_price * 0.80, 2), step=1.0)
K_max = st.sidebar.number_input("Max Strike ($)", min_value=0.01,
    value=round(stock_price * 1.20, 2), step=1.0)

if K_min >= K_max:
    st.error("Min Strike must be less than Max Strike.")
    st.stop()

#Fetch option data and also compute IV for each option using the create_iv_surface function from black_scholes.py
with st.spinner("Fetching option chain and computing IV..."):
    df, spot_price = create_iv_surface(ticker_symbol, risk_free_rate,
                                        dividend_yield, K_min, K_max)

if df.empty:
    st.error("No option data returned. Try a different ticker or wider strike range.")
    st.stop()

#Create grid for surface plot
ti = np.linspace(df['T'].min(), df['T'].max(), 50)
ki = np.linspace(df['K'].min(), df['K'].max(), 50)
T_grid, K_grid = np.meshgrid(ti, ki)

#Interpolate IV values onto the grid for surface plotting
Z = griddata(
    (df['T'].values, df['K'].values),
    df['iv'].values * 100,
    (T_grid, K_grid),
    method='linear'
)

#Creating the 3D surface plot using Plotly
fig = go.Figure(data=[go.Surface(
    x=ki,
    y=ti,
    z=Z,
    colorscale="Viridis",
    colorbar=dict(title="IV (%)"),
    hovertemplate=(
        "Strike: %{x:.1f}<br>"
        "Expiry: %{y:.2f} yrs<br>"
        "IV: %{z:.2f}%<extra></extra>"
    )
)])

fig.update_layout(
    scene=dict(
        xaxis_title="Strike Price ($)",
        yaxis_title="Time to Expiry (yrs)",
        zaxis_title="Implied Volatility (%)",
        camera=dict(eye=dict(x=1.5, y=-1.5, z=0.8))
    ),
    width=900,
    height=850,
    margin=dict(l=65, r=50, t=90, b=65)
)

st.plotly_chart(fig, use_container_width=True)

#IV summary metrics
valid = df['iv'].values * 100
col1, col2, col3 = st.columns(3)
col1.metric("Min IV",  f"{valid.min():.2f}%")
col2.metric("Max IV",  f"{valid.max():.2f}%")
col3.metric("Mean IV", f"{valid.mean():.2f}%")