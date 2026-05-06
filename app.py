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
    layout="wide",
    initial_sidebar_state="expanded"
)

# ================= CUSTOM CSS =================
st.markdown("""
<style>

/* ================= GLOBAL ================= */

html, body, [class*="css"] {
    font-family: 'Segoe UI', sans-serif;
}

/* ================= MAIN CONTAINER ================= */

.block-container {
    padding-top: 2rem;
    padding-left: 2rem;
    padding-right: 2rem;
}

/* ================= BACKGROUND ================= */

.stApp {
    background-image:
    linear-gradient(
        rgba(0, 0, 0, 0.55),
        rgba(0, 0, 0, 0.72)
    ),
    url("https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?q=80&w=2070&auto=format&fit=crop");

    background-size: cover;
    background-position: center;
    background-attachment: fixed;
}

/* ================= REMOVE HEADER ================= */

[data-testid="stHeader"] {
    background: rgba(0,0,0,0);
}

/* ================= SIDEBAR ================= */

[data-testid="stSidebar"] {
    background: rgba(12,12,18,0.92);
    border-right: 1px solid rgba(255,255,255,0.08);
}

/* ================= TEXT ================= */

h1, h2, h3, h4, h5, h6,
p, div, label, span {
    color: white !important;
}

/* ================= METRIC CARDS ================= */

[data-testid="metric-container"] {
    background: rgba(15,15,25,0.78);
    border: 1px solid rgba(255,255,255,0.06);
    padding: 18px;
    border-radius: 16px;
    backdrop-filter: blur(8px);
}

/* ================= DATAFRAME ================= */

[data-testid="stDataFrame"] {
    background: rgba(15,15,25,0.78);
    border-radius: 16px;
    overflow: hidden;
}

/* ================= ALERT ================= */

[data-testid="stAlert"] {
    background: rgba(15,15,25,0.88);
    border-radius: 14px;
    border: 1px solid rgba(255,255,255,0.05);
}

/* ================= BUTTONS ================= */

.stButton > button {
    background: linear-gradient(90deg,#2563eb,#1d4ed8);
    color: white;
    border: none;
    border-radius: 12px;
    padding: 0.6rem 1.2rem;
    font-weight: 700;
}

.stButton > button:hover {
    background: linear-gradient(90deg,#1d4ed8,#1e40af);
    color: white;
}

/* ================= SCROLLBAR ================= */

::-webkit-scrollbar {
    width: 10px;
}

::-webkit-scrollbar-thumb {
    background: #1f2937;
    border-radius: 10px;
}

</style>
""", unsafe_allow_html=True)

# ================= CONFIG =================
API_KEY = st.secrets["API_KEY"]
API_SECRET = st.secrets["API_SECRET"]

kite = KiteConnect(api_key=API_KEY)

# ================= SESSION =================
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

        st.error(f"❌ Login Failed: {e}")

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

# ================= LOGIN PAGE =================
if not st.session_state["logged_in"]:

    login_url = kite.login_url()

    hero_html = f"""
    <div style="
        margin-top:40px;
        margin-left:20px;
        max-width:720px;
        background:rgba(12,12,22,0.72);
        padding:50px;
        border-radius:24px;
        backdrop-filter: blur(10px);
        border:1px solid rgba(255,255,255,0.08);
        box-shadow:0 0 30px rgba(0,0,0,0.35);
    ">

        <div style="
            font-size:16px;
            color:#93c5fd;
            letter-spacing:2px;
            margin-bottom:15px;
        ">
            AI MARKET INTELLIGENCE
        </div>

        <h1 style="
            color:white;
            font-size:72px;
            margin-bottom:5px;
            font-style:italic;
            font-weight:800;
            line-height:1;
        ">
            ⚡ PulseIQ
        </h1>

        <div style="
            width:120px;
            height:4px;
            background:#2563eb;
            border-radius:10px;
            margin-top:18px;
            margin-bottom:24px;
        "></div>

        <p style="
            color:white;
            font-size:21px;
            margin-top:10px;
            opacity:0.92;
            line-height:1.6;
            max-width:580px;
        ">
            Real-Time Option Chain Intelligence for Smarter Trading Decisions
        </p>

        <div style="
            margin-top:35px;
            font-size:18px;
            line-height:2.2;
            color:white;
        ">
            📈 Live Market Analytics<br>
            🧠 AI-Powered Options Insights<br>
            ⚡ Real-Time Open Interest Tracking
        </div>

        <div style="
            margin-top:20px;
            font-size:15px;
            color:#d1d5db;
            opacity:0.9;
        ">
            🔐 Secure Zerodha Authentication • Once Daily Login
        </div>

        <a href="{login_url}" target="_self">

            <button style="
                margin-top:38px;
                background:linear-gradient(90deg,#2563eb,#1d4ed8);
                color:white;
                padding:15px 34px;
                border:none;
                border-radius:16px;
                font-size:18px;
                cursor:pointer;
                font-weight:700;
                box-shadow:0 0 25px rgba(37,99,235,0.4);
            ">
                🔐 Login with Zerodha
            </button>

        </a>

    </div>
    """

    st.markdown(hero_html, unsafe_allow_html=True)

    st.stop()

# ================= DASHBOARD =================
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

# ================= CACHE =================
@st.cache_data(ttl=30)
def get_cached_data():
    return fetch_option_chain("NIFTY")

# ================= FETCH DATA =================
result = get_cached_data()

if result is None:

    st.error("❌ Unable to fetch Kite data")
    st.stop()

df, atm_strike, spot = result

# ================= LIVE DATA =================
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

# ================= METRICS =================
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

# ================= CHART =================
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

fig.add_vline(
    x=atm_strike,
    line_dash="dash",
    line_color="yellow",
    annotation_text="ATM"
)

fig.update_layout(
    template="plotly_dark",
    barmode="group",
    height=560,
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    xaxis_title="Strike Price",
    yaxis_title="Open Interest",
    legend_title="OI Type"
)

st.plotly_chart(
    fig,
    use_container_width=True
)

# ================= OPTION CHAIN =================
st.subheader("📋 ATM ±4 Option Chain")

st.dataframe(
    df.sort_values("Strike"),
    use_container_width=True,
    hide_index=True
)