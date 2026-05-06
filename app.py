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

/* ================= BACKGROUND ================= */

.stApp {
    background-image:
    linear-gradient(
        rgba(0,0,0,0.45),
        rgba(0,0,0,0.72)
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

/* ================= REMOVE TOP SPACE ================= */

.block-container {
    padding-top: 1rem;
    padding-left: 2rem;
    padding-right: 2rem;
}

/* ================= SIDEBAR ================= */

[data-testid="stSidebar"] {
    background-color: rgba(10,10,10,0.92);
}

/* ================= TEXT ================= */

h1, h2, h3, h4, h5, h6,
p, div, label, span {
    color: white !important;
}

/* ================= METRIC CARDS ================= */

[data-testid="metric-container"] {
    background: rgba(20,20,20,0.72);
    border: 1px solid rgba(255,255,255,0.06);
    padding: 18px;
    border-radius: 16px;
    backdrop-filter: blur(8px);
}

/* ================= DATAFRAME ================= */

[data-testid="stDataFrame"] {
    background: rgba(20,20,20,0.72);
    border-radius: 14px;
    overflow: hidden;
}

/* ================= INFO BOX ================= */

[data-testid="stAlert"] {
    background: rgba(20,20,20,0.80);
    border-radius: 14px;
}

/* ================= BUTTON ================= */

.stButton > button {
    background: linear-gradient(90deg,#2563eb,#1d4ed8);
    color: white;
    border: none;
    border-radius: 12px;
    font-weight: 700;
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

# ================= SESSION INIT =================
if "access_token" not in st.session_state:
    st.session_state["access_token"] = None

if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if "validated" not in st.session_state:
    st.session_state["validated"] = False

# ================= LOGIN HANDLER =================
if "request_token" in st.query_params:

    try:

        # ALREADY LOGGED IN
        if st.session_state.get("logged_in"):

            st.query_params.clear()
            st.rerun()

        request_token = st.query_params["request_token"]

        if isinstance(request_token, list):
            request_token = request_token[0]

        data = kite.generate_session(
            request_token=request_token,
            api_secret=API_SECRET
        )

        access_token = data["access_token"]

        kite.set_access_token(access_token)

        # SAVE SESSION
        st.session_state["access_token"] = access_token
        st.session_state["logged_in"] = True
        st.session_state["validated"] = True

        # REMOVE TOKEN FROM URL
        st.query_params.clear()

        st.success("✅ Login Successful")

        st.rerun()

    except Exception as e:

        st.error(f"❌ Login failed: {e}")

        st.stop()

# ================= VALIDATE SESSION =================
if st.session_state.get("access_token"):

    try:

        kite.set_access_token(
            st.session_state["access_token"]
        )

        kite.profile()

        st.session_state["logged_in"] = True

    except Exception:

        st.session_state["logged_in"] = False
        st.session_state["access_token"] = None

# ================= LOGIN SCREEN =================
if not st.session_state["logged_in"]:

    login_url = kite.login_url()

    login_html = f"""
    <style>

    .hero-container {{
        position: relative;
        height: 82vh;
    }}

    .top-right-brand {{
        position: absolute;
        top: 10px;
        right: 30px;
        text-align: right;
    }}

    .brand-title {{
        color: white;
        font-size: 58px;
        font-style: italic;
        font-weight: 800;
        text-shadow: 0 0 18px rgba(0,0,0,0.7);
    }}

    .brand-subtitle {{
        color: rgba(255,255,255,0.82);
        font-size: 14px;
        margin-top: -6px;
        letter-spacing: 0.5px;
    }}

    .bottom-left {{
        position: absolute;
        bottom: 90px;
        left: 25px;
    }}

    .feature-points {{
        color: white;
        font-size: 20px;
        line-height: 2;
        margin-bottom: 18px;
        text-shadow: 0 0 18px rgba(0,0,0,0.8);
    }}

    .login-btn {{
        background: rgba(37,99,235,0.92);
        color: white;
        padding: 8px 18px;
        border: 1px solid rgba(255,255,255,0.12);
        border-radius: 9px;
        font-size: 12px;
        font-weight: 600;
        cursor: pointer;
        backdrop-filter: blur(8px);
    }}

    .login-btn:hover {{
        opacity: 0.92;
    }}

    </style>

    <div class="hero-container">

        <div class="top-right-brand">

            <div class="brand-title">
                ⚡ PulseIQ
            </div>

            <div class="brand-subtitle">
                AI-Powered Option Chain Intelligence
            </div>

        </div>

        <div class="bottom-left">

            <div class="feature-points">
                📈 Live Market Analytics<br>
                🧠 AI-Powered Options Insights
            </div>

            <a href="{login_url}" target="_self">

                <button class="login-btn">
                    🔐 Login with Zerodha
                </button>

            </a>

        </div>

    </div>
    """

    st.markdown(login_html, unsafe_allow_html=True)

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

    st.session_state.clear()

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

# ================= OPTION CHAIN TABLE =================
st.subheader("📋 ATM ±4 Option Chain")

st.dataframe(
    df.sort_values("Strike"),
    use_container_width=True,
    hide_index=True
)