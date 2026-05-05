import streamlit as st
import time
import plotly.graph_objects as go
from kiteconnect import KiteConnect
import os

from kite_fetch import fetch_option_chain
from analysis import calculate_metrics
from ai_engine import generate_ai_signal

st.set_page_config(page_title="Kite AI Analyzer", layout="wide")

# ===== CONFIG =====
API_KEY = st.secrets["API_KEY"]
API_SECRET = st.secrets["API_SECRET"]

kite = KiteConnect(api_key=API_KEY)

# ===== HANDLE REQUEST TOKEN FIRST (CRITICAL) =====
params = st.query_params

if "request_token" in params and "access_token" not in st.session_state:
    try:
        data = kite.generate_session(
            params["request_token"],
            api_secret=API_SECRET
        )

        st.session_state["access_token"] = data["access_token"]

        # Clear URL params to avoid infinite loop
        st.query_params.clear()

        st.success("✅ Login successful")
        st.rerun()

    except Exception as e:
        st.error("❌ Login failed. Try again.")
        st.query_params.clear()
        st.stop()

# ===== VALIDATE TOKEN =====
kite_obj = None

if "access_token" in st.session_state:
    try:
        kite.set_access_token(st.session_state["access_token"])
        kite.profile()  # validate token
        kite_obj = kite
    except:
        st.session_state.pop("access_token", None)

# ===== LOGIN SCREEN =====
if kite_obj is None:

    login_url = kite.login_url()

    st.title("🔐 Login Required")

    st.markdown("""
    Use your Zerodha Client ID or Mobile Number.
    Email login is not supported.
    """)

    st.markdown(f"""
    <a href="{login_url}" target="_self">
        <button style="padding:12px 24px; font-size:16px;">
            Login with Zerodha
        </button>
    </a>
    """, unsafe_allow_html=True)

    st.stop()

# ===== MAIN APP =====
st.title("📊 Kite AI Options Analyzer")

# Sidebar
auto_refresh = st.sidebar.checkbox("Auto Refresh (1 min)", value=True)

# ===== LOGOUT =====
if st.sidebar.button("Logout"):
    st.session_state.clear()
    st.query_params.clear()
    st.success("Logged out successfully")
    st.rerun()

# ===== LOAD DATA =====
result = fetch_option_chain("NIFTY")

if result is None:
    st.error("❌ Unable to fetch Kite data")
    st.stop()

df, atm_strike, spot = result

# ===== DISPLAY =====
st.subheader("📊 NIFTY Live")

colA, colB = st.columns(2)
colA.metric("NIFTY Spot", round(spot, 2))
colB.metric("ATM Strike", int(atm_strike))

# ===== METRICS =====
pcr, support, resistance = calculate_metrics(df)
ai_msg = generate_ai_signal(pcr, support, resistance)

lines = [line.strip() for line in ai_msg.split("\n") if line.strip()]
sentiment_line = lines[0] if lines else ""
sentiment = sentiment_line.replace("📊 Market Sentiment:", "").strip()
insight = lines[-1] if len(lines) > 1 else ""

# Color logic
if "Bullish" in sentiment:
    color = "#00ff9f"
    emoji = "🟢"
elif "Bearish" in sentiment:
    color = "#ff4b4b"
    emoji = "🔴"
else:
    color = "#f1c40f"
    emoji = "🟡"

col1, col2, col3, col4 = st.columns(4)

col1.metric("PCR", round(pcr, 2))
col2.metric("Support", int(support))
col3.metric("Resistance", int(resistance))
col4.metric("Trend", sentiment)

# ===== AI INSIGHT =====
st.subheader("🧠 AI Insight")

st.markdown(f"""
<div style="
    background-color:#111;
    padding:16px;
    border-radius:12px;
    border-left:5px solid {color};
    font-size:13px;
">

<div style="font-size:15px; font-weight:bold; color:{color}; margin-bottom:8px;">
{emoji} {sentiment}
</div>

<div style="display:flex; gap:40px; margin-bottom:10px;">
    <div>📉 <b>Support</b><br>{int(support)}</div>
    <div>📈 <b>Resistance</b><br>{int(resistance)}</div>
</div>

<div style="opacity:0.85;">
💡 {insight}
</div>

</div>
""", unsafe_allow_html=True)

# ===== CHART =====
st.subheader("📊 OI Comparison")

fig = go.Figure()

fig.add_trace(go.Bar(
    x=df["Strike"],
    y=df["Call OI"],
    name="Call OI",
    marker_color="red"
))

fig.add_trace(go.Bar(
    x=df["Strike"],
    y=df["Put OI"],
    name="Put OI",
    marker_color="green"
))

fig.add_vline(
    x=atm_strike,
    line_width=2,
    line_dash="dash",
    line_color="yellow",
    annotation_text="ATM",
    annotation_position="top"
)

fig.update_layout(
    barmode="group",
    template="plotly_dark",
    height=400
)

st.plotly_chart(fig, use_container_width=True)

# ===== TABLE =====
st.subheader("📋 ATM ±4 Option Chain")
st.dataframe(df.sort_values("Strike"), use_container_width=True)

# ===== AUTO REFRESH =====
if auto_refresh:
    time.sleep(60)
    st.rerun()