import streamlit as st
import plotly.graph_objects as go
from kiteconnect import KiteConnect
from streamlit_autorefresh import st_autorefresh
from supabase import create_client

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

.stApp {
    background-image:
    linear-gradient(rgba(0,0,0,0.45), rgba(0,0,0,0.72)),
    url("https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?q=80&w=2070&auto=format&fit=crop");
    background-size: cover;
    background-position: center;
    background-attachment: fixed;
}

[data-testid="stHeader"] { background: rgba(0,0,0,0); }

.block-container {
    padding-top: 1rem;
    padding-left: 2rem;
    padding-right: 2rem;
}

[data-testid="stSidebar"] { background-color: rgba(10,10,10,0.92); }

h1, h2, h3, h4, h5, h6, p, div, label, span { color: white !important; }

[data-testid="metric-container"] {
    background: rgba(20,20,20,0.72);
    border: 1px solid rgba(255,255,255,0.06);
    padding: 18px;
    border-radius: 16px;
    backdrop-filter: blur(8px);
}

[data-testid="stDataFrame"] {
    background: rgba(20,20,20,0.72);
    border-radius: 14px;
    overflow: hidden;
}

[data-testid="stAlert"] {
    background: rgba(20,20,20,0.80);
    border-radius: 14px;
}

.stButton > button {
    background: linear-gradient(90deg,#2563eb,#1d4ed8);
    color: white;
    border: none;
    border-radius: 12px;
    font-weight: 700;
}

::-webkit-scrollbar { width: 10px; }
::-webkit-scrollbar-thumb { background: #1f2937; border-radius: 10px; }

.top-right-brand {
    position: fixed;
    top: 70px;
    right: 40px;
    text-align: right;
    z-index: 999;
}

.brand-title {
    color: white;
    font-size: 58px;
    font-style: italic;
    font-weight: 800;
    text-shadow: 0 0 18px rgba(0,0,0,0.7);
}

.brand-subtitle {
    color: rgba(255,255,255,0.82);
    font-size: 14px;
    margin-top: -6px;
    letter-spacing: 0.5px;
}

.bottom-left {
    position: fixed;
    bottom: 90px;
    left: 40px;
    z-index: 999;
}

.feature-points {
    color: white;
    font-size: 20px;
    line-height: 2;
    margin-bottom: 18px;
    text-shadow: 0 0 18px rgba(0,0,0,0.8);
}

.login-btn {
    background: rgba(37,99,235,0.92);
    color: white;
    padding: 8px 18px;
    border: none;
    border-radius: 10px;
    font-size: 12px;
    font-weight: 600;
    cursor: pointer;
}

.login-btn:hover { opacity: 0.92; }

</style>
""", unsafe_allow_html=True)

# ================= CONFIG =================
API_KEY    = st.secrets["API_KEY"]
API_SECRET = st.secrets["API_SECRET"]
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

kite     = KiteConnect(api_key=API_KEY)
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# ================= SUPABASE HELPERS =================
def save_token(token: str):
    supabase.table("sessions").update({
        "access_token": token,
        "updated_at": "now()"
    }).eq("id", "main").execute()

def load_token() -> str | None:
    res = supabase.table("sessions").select("access_token").eq("id", "main").execute()
    if res.data and res.data[0]["access_token"]:
        return res.data[0]["access_token"]
    return None

def clear_token():
    supabase.table("sessions").update({
        "access_token": None,
        "updated_at": "now()"
    }).eq("id", "main").execute()

# ================= SESSION =================
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if "validated" not in st.session_state:
    st.session_state["validated"] = False

# ================= LOGIN HANDLER =================
if "request_token" in st.query_params and not st.session_state.get("logged_in"):

    try:
        request_token = st.query_params["request_token"]

        if isinstance(request_token, list):
            request_token = request_token[0]

        data = kite.generate_session(
            request_token=request_token,
            api_secret=API_SECRET
        )

        access_token = data["access_token"]
        kite.set_access_token(access_token)

        save_token(access_token)

        st.session_state["logged_in"]  = True
        st.session_state["validated"]  = True

    except Exception as e:
        st.error(f"❌ Login failed: {e}")
        st.stop()

# ================= VALIDATE SESSION FROM DB =================
if not st.session_state.get("validated"):

    try:
        token = load_token()

        if token:
            kite.set_access_token(token)
            kite.profile()

            st.session_state["logged_in"] = True
            st.session_state["validated"] = True

        else:
            st.session_state["logged_in"] = False

    except Exception:
        clear_token()
        st.session_state["logged_in"]  = False
        st.session_state["validated"]  = False

# ================= LOGIN SCREEN =================
if not st.session_state["logged_in"]:

    login_url = kite.login_url()

    st.markdown(
        f"""
        <div class="top-right-brand">
            <div class="brand-title">&#9889; PulseIQ</div>
            <div class="brand-subtitle">AI-Powered Option Chain Intelligence</div>
        </div>

        <div class="bottom-left">
            <div class="feature-points">
                &#128200; Live Market Analytics<br/>
                &#129504; AI-Powered Options Insights
            </div>
            <a href="{login_url}" target="_self">
                <button class="login-btn">&#128272; Login with Zerodha</button>
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

st.sidebar.markdown("---")
st.sidebar.subheader("🎯 Strike Settings")

manual_strike = st.sidebar.number_input(
    "Centre Strike Price (0 = use ATM)",
    min_value=0,
    max_value=100000,
    value=0,
    step=50,
    help="Enter a strike price to centre the chain on. Leave 0 to auto-use ATM."
)

atm_range = st.sidebar.number_input(
    "ATM Range (±N strikes)",
    min_value=1,
    max_value=20,
    value=4,
    step=1,
    help="Number of strikes to show on each side of the centre strike."
)

# ================= LOGOUT =================
st.sidebar.markdown("---")
if st.sidebar.button("Logout"):
    clear_token()
    st.session_state["logged_in"]  = False
    st.session_state["validated"]  = False
    st.success("✅ Logged out successfully")
    st.rerun()

# ================= AUTO REFRESH =================
if auto_refresh:
    st_autorefresh(interval=60 * 1000, key="live_refresh")

# ================= CACHE DATA =================
@st.cache_data(ttl=30)
def get_cached_data(range_size, custom_strike):
    return fetch_option_chain(
        "NIFTY",
        range_size=range_size,
        custom_strike=custom_strike
    )

# ================= FETCH DATA =================
custom = int(manual_strike) if manual_strike != 0 else None
result = get_cached_data(range_size=int(atm_range), custom_strike=custom)

if result is None:
    st.error("❌ Unable to fetch Kite data")
    st.stop()

df, atm_strike, spot = result

# ================= RESOLVE SELECTED STRIKE =================
all_strikes    = sorted(df["Strike"].unique().tolist())
centre_strike  = custom if custom else int(atm_strike)
closest_strike = min(all_strikes, key=lambda x: abs(x - centre_strike))

# ================= LIVE METRICS =================
st.subheader("📈 NIFTY Live Data")

colA, colB, colC = st.columns(3)
colA.metric("NIFTY Spot",        round(spot, 2))
colB.metric("ATM Strike (Auto)", int(atm_strike))
colC.metric("Selected Strike",   int(closest_strike))

# ================= ANALYSIS =================
pcr, support, resistance = calculate_metrics(df)

ai_msg = generate_ai_signal(pcr, support, resistance)

lines = [line.strip() for line in ai_msg.split("\n") if line.strip()]

try:
    sentiment = lines[0].replace("📊 Market Sentiment:", "").strip()
    insight   = lines[-1]
except Exception:
    sentiment = "Neutral"
    insight   = ai_msg

# ================= DISPLAY METRICS =================
col1, col2, col3, col4 = st.columns(4)
col1.metric("PCR",        round(pcr, 2))
col2.metric("Support",    int(support))
col3.metric("Resistance", int(resistance))
col4.metric("Trend",      sentiment)

# ================= AI INSIGHT =================
st.subheader("🧠 AI Insight")
st.info(insight)

# ================= TOTAL OI =================
total_call = df["Call OI"].sum()
total_put  = df["Put OI"].sum()

st.subheader("📊 Open Interest Strength")

colX, colY = st.columns(2)
colX.metric("🔴 Total Call OI", f"{int(total_call):,}")
colY.metric("🟢 Total Put OI",  f"{int(total_put):,}")

# ================= OI CHART =================
st.subheader(f"📉 OI Comparison — Strike {int(closest_strike)} ±{int(atm_range)}")

fig = go.Figure()

fig.add_trace(go.Bar(
    x=df["Strike"], y=df["Call OI"],
    name="Call OI", marker_color="red", opacity=0.65
))

fig.add_trace(go.Bar(
    x=df["Strike"], y=df["Put OI"],
    name="Put OI", marker_color="green", opacity=0.65
))

# Selected / custom strike line
fig.add_vline(
    x=closest_strike,
    line_dash="dash",
    line_color="yellow",
    annotation_text=f"Selected ({int(closest_strike)})"
)

# Real ATM line (only show if different from selected)
if closest_strike != int(atm_strike):
    fig.add_vline(
        x=atm_strike,
        line_dash="dot",
        line_color="cyan",
        annotation_text=f"ATM ({int(atm_strike)})"
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

st.plotly_chart(fig, use_container_width=True)

# ================= OPTION CHAIN TABLE =================
st.subheader(f"📋 Strike {int(closest_strike)} ±{int(atm_range)} Option Chain")

st.dataframe(
    df.sort_values("Strike"),
    use_container_width=True,
    hide_index=True
)