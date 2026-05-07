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

# ================= LOGO HTML =================
LOGO_HTML = """
<style>
.logo-wrapper {
    background: transparent;
    display: flex;
    align-items: center;
    gap: 16px;
    font-family: Arial, sans-serif;
    padding: 8px 0;
}
.bolt-wrap {
    position: relative;
    width: 70px;
    height: 90px;
    flex-shrink: 0;
}
.bolt {
    position: absolute;
    top: 50%; left: 50%;
    transform: translate(-50%, -50%);
    font-size: 64px;
    color: #00cfff;
    filter: drop-shadow(0 0 6px #00cfff) drop-shadow(0 0 18px #00cfff) drop-shadow(0 0 40px #0099ff);
    animation: boltFlicker 3s ease-in-out infinite;
    line-height: 1;
}
.bolt-ring {
    position: absolute;
    top: 50%; left: 50%;
    transform: translate(-50%, -50%);
    border-radius: 50%;
    border: 1px solid #00cfff;
    opacity: 0;
    animation: ringPulse 3s ease-out infinite;
}
.bolt-ring:nth-child(1) { width:40px; height:40px; animation-delay:0s; }
.bolt-ring:nth-child(2) { width:40px; height:40px; animation-delay:1s; }
.bolt-ring:nth-child(3) { width:40px; height:40px; animation-delay:2s; }
@keyframes boltFlicker {
    0%,100% { opacity:1; filter: drop-shadow(0 0 6px #00cfff) drop-shadow(0 0 18px #00cfff) drop-shadow(0 0 40px #0099ff); }
    89% { opacity:0.5; filter: drop-shadow(0 0 2px #00cfff); }
    90% { opacity:1; }
}
@keyframes ringPulse {
    0% { width:40px; height:40px; opacity:0.7; }
    100% { width:110px; height:110px; opacity:0; }
}
.brand-name {
    font-size: 48px;
    font-weight: 900;
    font-style: italic;
    color: #ffffff !important;
    letter-spacing: -1px;
    line-height: 1;
    text-shadow: 0 0 10px rgba(255,255,255,0.9), 0 0 20px rgba(0,180,255,0.6), 0 0 40px rgba(0,120,255,0.4);
    animation: textGlow 3s ease-in-out infinite;
    display: flex;
    align-items: center;
    gap: 4px;
}
@keyframes textGlow {
    0%,100% { text-shadow: 0 0 10px rgba(255,255,255,0.9), 0 0 20px rgba(0,180,255,0.6), 0 0 40px rgba(0,120,255,0.4); }
    50% { text-shadow: 0 0 16px #fff, 0 0 32px rgba(0,200,255,0.9), 0 0 60px rgba(0,150,255,0.6); }
}
.brand-sub {
    font-size: 10px;
    letter-spacing: 3px;
    color: #00cfff !important;
    text-transform: uppercase;
    opacity: 0.75;
    text-shadow: 0 0 8px #00cfff;
    margin-top: 2px;
}
.pulse-line {
    stroke-dasharray: 300;
    stroke-dashoffset: 300;
    animation: drawPulse 2s ease forwards, pulseFade 3s ease-in-out 2s infinite;
}
@keyframes drawPulse { to { stroke-dashoffset: 0; } }
@keyframes pulseFade {
    0%,100% { opacity:1; filter: drop-shadow(0 0 3px #00cfff); }
    50% { opacity:0.5; filter: drop-shadow(0 0 8px #00cfff); }
}
</style>

<div class="logo-wrapper">
  <div class="bolt-wrap">
    <div class="bolt-ring"></div>
    <div class="bolt-ring"></div>
    <div class="bolt-ring"></div>
    <div class="bolt">&#9889;</div>
  </div>
  <div>
    <div class="brand-name">
      PulseIQ
      <svg width="80" height="34" viewBox="0 0 110 44" fill="none"
        xmlns="http://www.w3.org/2000/svg"
        style="display:inline-block;vertical-align:middle;">
        <polyline class="pulse-line"
          points="0,22 15,22 22,8 28,36 36,4 44,38 50,22 62,22 68,14 74,30 80,22 110,22"
          stroke="#00cfff" stroke-width="2.5"
          stroke-linecap="round" stroke-linejoin="round" fill="none"
          style="filter: drop-shadow(0 0 4px #00cfff) drop-shadow(0 0 10px #0099ff);"/>
      </svg>
    </div>
    <div class="brand-sub">AI-Powered Option Chain Intelligence</div>
  </div>
</div>
"""

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

.login-page-wrap {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    min-height: 80vh;
    gap: 32px;
}

.login-logo-wrap {
    display: flex;
    align-items: center;
    gap: 20px;
    font-family: Arial, sans-serif;
}

.login-bolt-wrap {
    position: relative;
    width: 100px;
    height: 130px;
    flex-shrink: 0;
}

.login-bolt {
    position: absolute;
    top: 50%; left: 50%;
    transform: translate(-50%, -50%);
    font-size: 90px;
    color: #00cfff;
    filter: drop-shadow(0 0 8px #00cfff) drop-shadow(0 0 24px #00cfff) drop-shadow(0 0 60px #0099ff);
    animation: boltFlicker 3s ease-in-out infinite;
    line-height: 1;
}

.login-bolt-ring {
    position: absolute;
    top: 50%; left: 50%;
    transform: translate(-50%, -50%);
    border-radius: 50%;
    border: 1px solid #00cfff;
    opacity: 0;
    animation: loginRingPulse 3s ease-out infinite;
}
.login-bolt-ring:nth-child(1) { width:50px; height:50px; animation-delay:0s; }
.login-bolt-ring:nth-child(2) { width:50px; height:50px; animation-delay:1s; }
.login-bolt-ring:nth-child(3) { width:50px; height:50px; animation-delay:2s; }

@keyframes loginRingPulse {
    0% { width:50px; height:50px; opacity:0.8; }
    100% { width:160px; height:160px; opacity:0; }
}

.login-brand-name {
    font-size: 80px !important;
    font-weight: 900;
    font-style: italic;
    color: #ffffff !important;
    letter-spacing: -2px;
    line-height: 1;
    text-shadow: 0 0 12px rgba(255,255,255,0.95), 0 0 28px rgba(0,180,255,0.7), 0 0 55px rgba(0,120,255,0.5);
    animation: textGlow 3s ease-in-out infinite;
    display: flex;
    align-items: center;
    gap: 6px;
}

.login-brand-sub {
    font-size: 13px !important;
    letter-spacing: 4px;
    color: #00cfff !important;
    text-transform: uppercase;
    opacity: 0.8;
    text-shadow: 0 0 10px #00cfff;
    margin-top: 4px;
}

.login-features {
    font-size: 18px !important;
    color: rgba(255,255,255,0.88) !important;
    line-height: 2.2;
    text-align: center;
    text-shadow: 0 0 12px rgba(0,0,0,0.8);
}

.login-btn-wrap a {
    text-decoration: none;
}

.login-btn {
    background: rgba(37,99,235,0.92);
    color: white !important;
    padding: 14px 36px;
    border: none;
    border-radius: 12px;
    font-size: 15px;
    font-weight: 700;
    cursor: pointer;
    letter-spacing: 1px;
    box-shadow: 0 0 20px rgba(37,99,235,0.5);
    transition: all 0.2s;
}

.login-btn:hover { opacity: 0.88; box-shadow: 0 0 30px rgba(37,99,235,0.7); }

</style>
""", unsafe_allow_html=True)

# ================= CONFIG =================
API_KEY = st.secrets["API_KEY"]
API_SECRET = st.secrets["API_SECRET"]
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

kite = KiteConnect(api_key=API_KEY)
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# ================= SUPABASE HELPERS =================
def save_token(token: str):
    supabase.table("sessions").update({
        "access_token": token,
        "updated_at": "now()"
    }).eq("id", "main").execute()

def load_token():
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

        st.session_state["logged_in"] = True
        st.session_state["validated"] = True

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
        st.session_state["logged_in"] = False
        st.session_state["validated"] = False

# ================= LOGIN SCREEN =================
if not st.session_state["logged_in"]:

    login_url = kite.login_url()

    st.markdown(
        f"""
        <div class="login-page-wrap">

          <div class="login-logo-wrap">
            <div class="login-bolt-wrap">
              <div class="login-bolt-ring"></div>
              <div class="login-bolt-ring"></div>
              <div class="login-bolt-ring"></div>
              <div class="login-bolt">&#9889;</div>
            </div>
            <div>
              <div class="login-brand-name">
                PulseIQ
                <svg width="100" height="42" viewBox="0 0 110 44" fill="none"
                  xmlns="http://www.w3.org/2000/svg"
                  style="display:inline-block;vertical-align:middle;">
                  <polyline class="pulse-line"
                    points="0,22 15,22 22,8 28,36 36,4 44,38 50,22 62,22 68,14 74,30 80,22 110,22"
                    stroke="#00cfff" stroke-width="2.5"
                    stroke-linecap="round" stroke-linejoin="round" fill="none"
                    style="filter: drop-shadow(0 0 4px #00cfff) drop-shadow(0 0 10px #0099ff);"/>
                </svg>
              </div>
              <div class="login-brand-sub">AI-Powered Option Chain Intelligence</div>
            </div>
          </div>

          <div class="login-features">
            &#128200; Live Market Analytics<br/>
            &#129504; AI-Powered Options Insights<br/>
            &#128293; Real-Time OI Tracking
          </div>

          <div class="login-btn-wrap">
            <a href="{login_url}" target="_self">
              <button class="login-btn">&#128272; Login with Zerodha</button>
            </a>
          </div>

        </div>
        """,
        unsafe_allow_html=True
    )

    st.stop()

# ================= SIDEBAR LOGO =================
st.sidebar.markdown(LOGO_HTML, unsafe_allow_html=True)
st.sidebar.markdown("---")
st.sidebar.header("⚙ Settings")

auto_refresh = st.sidebar.checkbox(
    "Auto Refresh (1 Minute)",
    value=True
)

# ================= LOGOUT =================
if st.sidebar.button("Logout"):

    clear_token()
    st.session_state["logged_in"] = False
    st.session_state["validated"] = False

    st.success("✅ Logged out successfully")
    st.rerun()

# ================= AUTO REFRESH =================
if auto_refresh:

    st_autorefresh(
        interval=60 * 1000,
        key="live_refresh"
    )

# ================= DASHBOARD LOGO =================
st.markdown(LOGO_HTML, unsafe_allow_html=True)
st.markdown("---")

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

colA.metric("NIFTY Spot", round(spot, 2))
colB.metric("ATM Strike", int(atm_strike))

# ================= ANALYSIS =================
pcr, support, resistance = calculate_metrics(df)

ai_msg = generate_ai_signal(pcr, support, resistance)

lines = [line.strip() for line in ai_msg.split("\n") if line.strip()]

try:
    sentiment = lines[0].replace("📊 Market Sentiment:", "").strip()
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

colX.metric("🔴 Total Call OI", f"{int(total_call):,}")
colY.metric("🟢 Total Put OI", f"{int(total_put):,}")

# ================= OI CHART =================
st.subheader("📉 OI Comparison (ATM ±4)")

fig = go.Figure()

fig.add_trace(go.Bar(
    x=df["Strike"], y=df["Call OI"],
    name="Call OI", marker_color="red", opacity=0.65
))

fig.add_trace(go.Bar(
    x=df["Strike"], y=df["Put OI"],
    name="Put OI", marker_color="green", opacity=0.65
))

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

st.plotly_chart(fig, use_container_width=True)

# ================= OPTION CHAIN TABLE =================
st.subheader("📋 ATM ±4 Option Chain")

st.dataframe(
    df.sort_values("Strike"),
    use_container_width=True,
    hide_index=True
)