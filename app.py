import streamlit as st
import plotly.graph_objects as go
from kiteconnect import KiteConnect
from streamlit_autorefresh import st_autorefresh

from kite_fetch import fetch_option_chain
from analysis import calculate_metrics
from ai_engine import generate_ai_signal

# ================= PAGE CONFIG =================
st.set_page_config(
    page_title="PulseIQ",
    layout="wide"
)

# ================= CUSTOM CSS =================
st.markdown("""
<style>

/* ================= BACKGROUND ================= */

.stApp {
    background-image:
    linear-gradient(
        rgba(0, 0, 0, 0.45),
        rgba(0, 0, 0, 0.60)
    ),
    url("https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?q=80&w=2070&auto=format&fit=crop");

    background-size: cover;
    background-position: center;
    background-attachment: fixed;
}

/* ================= REMOVE STREAMLIT HEADER ================= */

[data-testid="stHeader"] {
    background: rgba(0,0,0,0);
}

/* ================= SIDEBAR ================= */

[data-testid="stSidebar"] {
    background-color: rgba(10,10,10,0.88);
}

/* ================= TEXT COLORS ================= */

h1, h2, h3, h4, h5, h6, p, div, label {
    color: white !important;
}

/* ================= METRIC CARDS ================= */

[data-testid="metric-container"] {
    background-color: rgba(20,20,20,0.72);
    border: 1px solid rgba(255,255,255,0.08);
    padding: 15px;
    border-radius: 14px;
}

/* ================= DATAFRAME ================= */

[data-testid="stDataFrame"] {
    background-color: rgba(20,20,20,0.72);
    border-radius: 12px;
}

/* ================= BUTTONS ================= */

.stButton>button {
    background-color: #2563eb;
    color: white;
    border-radius: 10px;
    border: none;
    padding: 10px 18px;
    font-weight: 600;
}

.stButton>button:hover {
    background-color: #1d4ed8;
}

/* ================= INFO BOX ================= */

[data-testid="stAlert"] {
    background-color: rgba(20,20,20,0.85);
    border-radius: 12px;
}

</style>
""", unsafe_allow_html=True)

# ================= CONFIG =================
API_KEY = st.secrets["API_KEY"]
API_SECRET = st.secrets["API_SECRET"]

kite = KiteConnect(api_key=API_KEY)

# ================= SESSION INIT =================
if "access_token" not in st.session_state:
    st.session_state["access_token"] = None

if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if "validated" not in st.session_state:
    st.session_state["validated"] = False

# ================= QUERY PARAMS =================
params = dict(st.query_params)

# ================= LOGIN HANDLER =================
if "request_token" in params and not st.session_state["logged_in"]:

    try:
        request_token = params["request_token"]

        if isinstance(request_token, list):
            request_token = request_token[0]

        data = kite.generate_session(
            request_token,
            api_secret=API_SECRET
        )

        st.session_state["access_token"] = data["access_token"]
        st.session_state["logged_in"] = True
        st.session_state["validated"] = False

        kite.set_access_token(data["access_token"])

        st.query_params.clear()

        st.success("✅ Login Successful")

        st.rerun()

    except Exception as e:

        st.error(f"❌ Login failed: {e}")

        st.session_state["access_token"] = None
        st.session_state["logged_in"] = False
        st.session_state["validated"] = False

        st.query_params.clear()

        st.stop()

# ================= VALIDATE SESSION =================
kite_obj = None

if st.session_state["access_token"]:

    try:

        kite.set_access_token(
            st.session_state["access_token"]
        )

        if not st.session_state["validated"]:

            kite.profile()

            st.session_state["validated"] = True

        kite_obj = kite
        st.session_state["logged_in"] = True

    except Exception:

        st.session_state["access_token"] = None
        st.session_state["logged_in"] = False
        st.session_state["validated"] = False

# ================= LOGIN SCREEN =================
if not st.session_state["logged_in"]:

    login_url = kite.login_url()

    st.markdown(
        """
        <div style="
            margin-top:-10px;
            margin-left:30px;
        ">

            <h1 style="
                color:white;
                font-size:62px;
                margin-bottom:0px;
                font-style:italic;
                font-weight:800;
            ">
                ⚡ PulseIQ
            </h1>

            <p style="
                color:white;
                font-size:20px;
                margin-top:5px;
                font-style:italic;
                opacity:0.92;
            ">
                Real-Time Option Chain Intelligence for Smarter Trading
            </p>

            <div style="
                margin-top:35px;
                font-size:18px;
                line-height:2;
                color:white;
            ">
                📈 Live Market Analytics<br>
                🧠 AI-Powered Options Insights
            </div>

            <div style="
                margin-top:25px;
                font-size:16px;
                color:white;
                opacity:0.9;
            ">
                🔐 Secure Zerodha Login <i>(Once Daily)</i>
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )

    # ================= LOGIN BUTTON =================

    st.markdown(
        f"""
        <div style="
            margin-top:35px;
            margin-left:30px;
        ">
            <a href="{login_url}" target="_self">
                <button style="
                    background-color:#2563eb;
                    color:white;
                    padding:14px 34px;
                    border:none;
                    border-radius:14px;
                    font-size:18px;
                    cursor:pointer;
                    font-weight:700;
                    box-shadow:0 0 20px rgba(37,99,235,0.35);
                ">
                    🔐 Login with Zerodha
                </button>
            </a>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.stop()

# ================= MAIN APP =================
st.title("📊 PulseIQ Dashboard")

# ================= SIDEBAR =================
st.sidebar.header("⚙ Settings")

auto_refresh = st.sidebar.checkbox(
    "Auto Refresh (1 Minute)",
    value=True
)

# ================= LOGOUT =================
if st.sidebar.button("Logout"):

    for key in list(st.session_state.keys()):
        del st.session_state[key]

    st.query_params.clear()

    st.success("✅ Logged out successfully")

    st.rerun()

# ================= AUTO REFRESH =================
if auto_refresh:

    st_autorefresh(
        interval=60 * 1000,
        key="live_refresh"
    )

# ================= CACHE DATA =================
@st.cache_data(ttl=30)
def get_cached_data():
    return fetch_option_chain("NIFTY")

# ================= FETCH DATA =================
result = get_cached_data()

if result is None:

    st.error("❌ Unable to fetch Kite data")

    st.stop()

df, atm_strike, spot = result

# ================= LIVE METRICS =================
st.subheader("📈 NIFTY Live Data")

colA, colB = st.columns(2)

colA.metric(
    "NIFTY Spot",
    round(spot, 2)
)

colB.metric(
    "ATM Strike",
    int(atm_strike)
)

# ================= ANALYSIS =================
pcr, support, resistance = calculate_metrics(df)

ai_msg = generate_ai_signal(
    pcr,
    support,
    resistance
)

lines = [
    line.strip()
    for line in ai_msg.split("\n")
    if line.strip()
]

try:

    sentiment = (
        lines[0]
        .replace("📊 Market Sentiment:", "")
        .strip()
    )

    insight = lines[-1]

except Exception:

    sentiment = "Neutral"
    insight = ai_msg

# ================= DISPLAY METRICS =================
col1, col2, col3, col4 = st.columns(4)

col1.metric("PCR", round(pcr, 2))
col2.metric("Support", int(support))
col3.metric("Resistance", int(resistance))
col4.metric("Trend", sentiment)

# ================= AI INSIGHT =================
st.subheader("🧠 AI Insight")

st.info(insight)

# ================= TOTAL OI =================
total_call = df["Call OI"].sum()
total_put = df["Put OI"].sum()

st.subheader("📊 Open Interest Strength")

colX, colY = st.columns(2)

colX.metric(
    "🔴 Total Call OI",
    f"{int(total_call):,}"
)

colY.metric(
    "🟢 Total Put OI",
    f"{int(total_put):,}"
)

# ================= OI CHART =================
st.subheader("📉 OI Comparison (ATM ±4)")

fig = go.Figure()

fig.add_trace(
    go.Bar(
        x=df["Strike"],
        y=df["Call OI"],
        name="Call OI",
        marker_color="red",
        opacity=0.65
    )
)

fig.add_trace(
    go.Bar(
        x=df["Strike"],
        y=df["Put OI"],
        name="Put OI",
        marker_color="green",
        opacity=0.65
    )
)

fig.add_trace(
    go.Scatter(
        x=df["Strike"],
        y=[total_call] * len(df),
        name="Total Call OI",
        mode="lines",
        line=dict(
            color="red",
            width=3
        )
    )
)

fig.add_trace(
    go.Scatter(
        x=df["Strike"],
        y=[total_put] * len(df),
        name="Total Put OI",
        mode="lines",
        line=dict(
            color="green",
            width=3
        )
    )
)

fig.add_vline(
    x=atm_strike,
    line_dash="dash",
    line_color="yellow",
    annotation_text="ATM"
)

fig.update_layout(
    template="plotly_dark",
    barmode="group",
    height=550,
    xaxis_title="Strike Price",
    yaxis_title="Open Interest",
    legend_title="OI Type"
)

st.plotly_chart(
    fig,
    use_container_width=True
)

# ================= OPTION CHAIN TABLE =================
st.subheader("📋 ATM ±4 Option Chain")

st.dataframe(
    df.sort_values("Strike"),
    use_container_width=True,
    hide_index=True
)