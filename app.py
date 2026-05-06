import streamlit as st
import time
import plotly.graph_objects as go
from kiteconnect import KiteConnect

from kite_fetch import fetch_option_chain
from analysis import calculate_metrics
from ai_engine import generate_ai_signal

st.set_page_config(page_title="Kite AI Analyzer", layout="wide")

# ===== CONFIG =====
API_KEY = st.secrets["API_KEY"]
API_SECRET = st.secrets["API_SECRET"]

kite = KiteConnect(api_key=API_KEY)

# ===== INIT SESSION =====
if "access_token" not in st.session_state:
    st.session_state["access_token"] = None

if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

# ===== HANDLE LOGIN TOKEN =====
params = st.query_params

if "request_token" in params and not st.session_state["logged_in"]:
    try:
        data = kite.generate_session(
            params["request_token"],
            api_secret=API_SECRET
        )

        st.session_state["access_token"] = data["access_token"]
        st.session_state["logged_in"] = True

        # Clear params to avoid loop
        st.query_params.clear()

        st.success("✅ Login successful")
        st.rerun()

    except Exception as e:
        st.error("❌ Login failed")
        st.query_params.clear()
        st.stop()

# ===== VALIDATE SESSION =====
kite_obj = None

if st.session_state["access_token"]:
    try:
        kite.set_access_token(st.session_state["access_token"])
        kite.profile()
        kite_obj = kite
        st.session_state["logged_in"] = True
    except:
        st.session_state["access_token"] = None
        st.session_state["logged_in"] = False

# ===== LOGIN SCREEN =====
if not st.session_state["logged_in"]:
    login_url = kite.login_url()

    st.title("🔐 Login Required")

    st.markdown("""
    👉 Login using Zerodha Client ID or Mobile Number  
    🔒 Login required once per day
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
sentiment = lines[0].replace("📊 Market Sentiment:", "").strip()
insight = lines[-1]

col1, col2, col3, col4 = st.columns(4)
col1.metric("PCR", round(pcr, 2))
col2.metric("Support", int(support))
col3.metric("Resistance", int(resistance))
col4.metric("Trend", sentiment)

# ===== TOTAL OI =====
total_call = df["Call OI"].sum()
total_put = df["Put OI"].sum()

st.subheader("📊 OI Strength")

colX, colY = st.columns(2)
colX.metric("🔴 Total Call OI", f"{int(total_call):,}")
colY.metric("🟢 Total Put OI", f"{int(total_put):,}")

# ===== CHART =====
st.subheader("📊 OI Comparison (ATM ±4)")

fig = go.Figure()

# CALL = RED
fig.add_trace(go.Bar(
    x=df["Strike"],
    y=df["Call OI"],
    name="Call OI",
    marker_color="red",
    opacity=0.6
))

# PUT = GREEN
fig.add_trace(go.Bar(
    x=df["Strike"],
    y=df["Put OI"],
    name="Put OI",
    marker_color="green",
    opacity=0.6
))

# TOTAL CALL LINE
fig.add_trace(go.Scatter(
    x=df["Strike"],
    y=[total_call]*len(df),
    name="Total Call",
    mode="lines",
    line=dict(color="red", width=4)
))

# TOTAL PUT LINE
fig.add_trace(go.Scatter(
    x=df["Strike"],
    y=[total_put]*len(df),
    name="Total Put",
    mode="lines",
    line=dict(color="green", width=4)
))

# ATM LINE
fig.add_vline(
    x=atm_strike,
    line_dash="dash",
    line_color="yellow",
    annotation_text="ATM"
)

fig.update_layout(
    barmode="group",
    template="plotly_dark",
    height=500
)

st.plotly_chart(fig, use_container_width=True)

# ===== TABLE =====
st.subheader("📋 ATM ±4 Option Chain")
st.dataframe(df.sort_values("Strike"), use_container_width=True)

# ===== AUTO REFRESH =====
if auto_refresh:
    time.sleep(60)
    st.rerun()