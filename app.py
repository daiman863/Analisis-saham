import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import ta

# Konfigurasi Halaman
st.set_page_config(page_title="Alpha Stock Pro", layout="wide")

# Sidebar untuk Input User
st.sidebar.title("🔍 Stock Settings")
ticker_input = st.sidebar.text_input("Enter Ticker (e.g. AAPL, BBRI.JK)", value="AAPL").upper()
period = st.sidebar.selectbox("Timeframe", ["1y", "2y", "5y", "max"])

# Fungsi Ambil Data
@st.cache_data(ttl=3600) # Simpan data di cache selama 1 jam
def load_data(ticker, p):
    import time
    # Tambahkan sedikit delay agar tidak dianggap bot yang agresif
    time.sleep(1) 
    stock = yf.Ticker(ticker)
    df = stock.history(period=p)
    return df, stock.info

# Judul Utama
st.title(f"📊 Analysis: {ticker_input}")

try:
    df, info = load_data(ticker_input, period)

    if not df.empty:
        # Kalkulasi Teknikal
        df['EMA_50'] = ta.trend.EMAIndicator(df['Close'], window=50).ema_indicator()
        df['EMA_200'] = ta.trend.EMAIndicator(df['Close'], window=200).ema_indicator()
        df['RSI'] = ta.momentum.RSIIndicator(df['Close']).rsi()

        # Metrik Utama (Baris Atas)
        m1, m2, m3, m4 = st.columns(4)
        latest_price = df['Close'].iloc[-1]
        m1.metric("Current Price", f"${latest_price:.2f}")
        m2.metric("RSI (14)", f"{df['RSI'].iloc[-1]:.1f}")
        m3.metric("Market Cap", f"{info.get('marketCap', 'N/A'):,}")
        m4.metric("ROE", f"{info.get('returnOnEquity', 0)*100:.2f}%")

        # Grafik Interaktif
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.05, row_heights=[0.7, 0.3])
        fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name="Price"), row=1, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df['EMA_50'], name="EMA 50", line=dict(color='orange')), row=1, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df['EMA_200'], name="EMA 200", line=dict(color='blue')), row=1, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df['RSI'], name="RSI", line=dict(color='purple')), row=2, col=1)
        
        fig.update_layout(height=600, template="plotly_dark", xaxis_rangeslider_visible=False)
        st.plotly_chart(fig, use_container_width=True)

        # Analisis Risiko & Fundamental
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("📋 Fundamentals")
            st.write(f"**Sector:** {info.get('sector', 'N/A')}")
            st.write(f"**P/E Ratio:** {info.get('trailingPE', 'N/A')}")
            st.write(f"**P/B Ratio:** {info.get('priceToBook', 'N/A')}")
        
        with c2:
            st.subheader("🚨 Risk Warning")
            if df['RSI'].iloc[-1] > 70: st.error("RSI > 70: Overbought (Jenuh Beli)")
            elif df['RSI'].iloc[-1] < 30: st.success("RSI < 30: Oversold (Jenuh Jual)")
            else: st.info("Momentum is Neutral")

    else:
        st.error("Data tidak ditemukan. Cek kembali ticker Anda.")

except Exception as e:
    st.error(f"Terjadi kesalahan: {e}")

