import streamlit as st
import plotly.graph_objects as go
from kiteconnect import KiteConnect
from streamlit_autorefresh import st_autorefresh
from supabase import create_client
import streamlit.components.v1 as components

from kite_fetch import fetch_option_chain
from analysis import calculate_metrics
from ai_engine import generate_ai_signal

# ================= PAGE CONFIG =================
st.set_page_config(
    page_title="PulseIQ",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ================= LOGO HTML (sidebar + dashboard) =================
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
.bolt-svg {
    position: absolute;
    top: 50%; left: 50%;
    transform: translate(-50%, -50%);
    filter:
        drop-shadow(0 0 4px #00cfff)
        drop-shadow(0 0 14px #00cfff)
        drop-shadow(0 0 35px #0099ff)
        drop-shadow(0 0 70px #006fff);
    animation: boltFlicker 3s ease-in-out infinite;
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
@keyframes ringPulse {
    0%   { width:40px;  height:40px;  opacity:0.7; }
    100% { width:110px; height:110px; opacity:0;   }
}
@keyframes boltFlicker {
    0%,100% { opacity:1; filter: drop-shadow(0 0 4px #00cfff) drop-shadow(0 0 14px #00cfff) drop-shadow(0 0 35px #0099ff) drop-shadow(0 0 70px #006fff); }
    88%     { opacity:1; }
    89%     { opacity:0.4; filter: drop-shadow(0 0 2px #00cfff); }
    90%     { opacity:1; }
    94%     { opacity:0.7; }
    95%     { opacity:1; }
}
.brand-name {
    font-size: 48px !important;
    font-weight: 900;
    font-style: italic;
    color: #ffffff !important;
    letter-spacing: -1px;
    line-height: 1;
    text-shadow:
        0 0 10px rgba(255,255,255,0.9),
        0 0 20px rgba(0,180,255,0.6),
        0 0 40px rgba(0,120,255,0.4);
    animation: textGlow 3s ease-in-out infinite;
    display: flex;
    align-items: center;
    gap: 4px;
}
@keyframes textGlow {
    0%,100% { text-shadow: 0 0 10px rgba(255,255,255,0.9), 0 0 20px rgba(0,180,255,0.6), 0 0 40px rgba(0,120,255,0.4); }
    50%      { text-shadow: 0 0 16px #fff, 0 0 32px rgba(0,200,255,0.9), 0 0 60px rgba(0,150,255,0.6); }
}
.brand-sub {
    font-size: 10px !important;
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
    0%,100% { opacity:1;   filter: drop-shadow(0 0 3px #00cfff) drop-shadow(0 0 8px #0099ff); }
    50%      { opacity:0.5; filter: drop-shadow(0 0 10px #00cfff) drop-shadow(0 0 20px #0099ff); }
}
</style>

<div class="logo-wrapper">
  <div class="bolt-wrap">
    <div class="bolt-ring"></div>
    <div class="bolt-ring"></div>
    <div class="bolt-ring"></div>
    <svg class="bolt-svg" width="52" height="68" viewBox="0 0 60 80" xmlns="http://www.w3.org/2000/svg">
      <polygon points="38,2 14,42 30,42 22,78 46,38 30,38"
        fill="#00cfff" stroke="#ffffff" stroke-width="1"/>
    </svg>
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

    components.html(
        f"""
        <!DOCTYPE html>
        <html>
        <head>
        <style>
        * {{ margin:0; padding:0; box-sizing:border-box; }}

        body {{
            background: transparent;
            font-family: Arial, sans-serif;
            width: 100vw;
            height: 100vh;
            overflow: hidden;
            position: relative;
        }}

        /* ── TOP RIGHT: Logo ── */
        .top-right {{
            position: fixed;
            top: 70px;
            right: 40px;
            display: flex;
            align-items: center;
            gap: 16px;
            z-index: 999;
        }}

        .ln-bolt-wrap {{
            position: relative;
            width: 90px;
            height: 115px;
            flex-shrink: 0;
        }}
        .ln-bolt-ring {{
            position: absolute;
            top: 50%; left: 50%;
            transform: translate(-50%, -50%);
            border-radius: 50%;
            border: 1px solid #00cfff;
            opacity: 0;
            animation: lnRingPulse 3s ease-out infinite;
        }}
        .ln-bolt-ring:nth-child(1) {{ width:44px; height:44px; animation-delay:0s; }}
        .ln-bolt-ring:nth-child(2) {{ width:44px; height:44px; animation-delay:1s; }}
        .ln-bolt-ring:nth-child(3) {{ width:44px; height:44px; animation-delay:2s; }}
        @keyframes lnRingPulse {{
            0%   {{ width:44px;  height:44px;  opacity:0.8; }}
            100% {{ width:150px; height:150px; opacity:0;   }}
        }}
        .ln-bolt-svg {{
            position: absolute;
            top: 50%; left: 50%;
            transform: translate(-50%, -50%);
            filter:
                drop-shadow(0 0 4px #00cfff)
                drop-shadow(0 0 14px #00cfff)
                drop-shadow(0 0 35px #0099ff)
                drop-shadow(0 0 70px #006fff);
            animation: lnBoltFlicker 3s ease-in-out infinite;
        }}
        @keyframes lnBoltFlicker {{
            0%,100% {{ opacity:1; filter: drop-shadow(0 0 4px #00cfff) drop-shadow(0 0 14px #00cfff) drop-shadow(0 0 35px #0099ff) drop-shadow(0 0 70px #006fff); }}
            88%     {{ opacity:1; }}
            89%     {{ opacity:0.4; filter: drop-shadow(0 0 2px #00cfff); }}
            90%     {{ opacity:1; }}
            94%     {{ opacity:0.7; }}
            95%     {{ opacity:1; }}
        }}
        .ln-spark {{
            position: absolute;
            width: 3px; height: 3px;
            border-radius: 50%;
            background: #00cfff;
            box-shadow: 0 0 6px 2px #00cfff;
            opacity: 0;
            animation: lnSpark 3s ease-in-out infinite;
        }}
        .ln-spark:nth-child(5) {{ top:15%; left:8%;  animation-delay:0.3s; }}
        .ln-spark:nth-child(6) {{ top:20%; left:85%; animation-delay:1.1s; }}
        .ln-spark:nth-child(7) {{ top:75%; left:80%; animation-delay:0.7s; }}
        .ln-spark:nth-child(8) {{ top:80%; left:12%; animation-delay:1.9s; }}
        .ln-spark:nth-child(9) {{ top:45%; left:92%; animation-delay:2.4s; }}
        @keyframes lnSpark {{
            0%   {{ opacity:0; transform:translate(0,0) scale(1); }}
            30%  {{ opacity:1; }}
            100% {{ opacity:0; transform:translate(20px,-20px) scale(0); }}
        }}

        .ln-text-col {{
            display: flex;
            flex-direction: column;
            gap: 4px;
            text-align: right;
        }}
        .ln-brand-name {{
            font-size: 62px;
            font-weight: 900;
            font-style: italic;
            color: #ffffff;
            letter-spacing: -2px;
            line-height: 1;
            text-shadow:
                0 0 10px rgba(255,255,255,0.95),
                0 0 25px rgba(0,190,255,0.7),
                0 0 55px rgba(0,130,255,0.5);
            animation: lnTextGlow 3s ease-in-out infinite;
            display: flex;
            align-items: center;
            gap: 6px;
            justify-content: flex-end;
        }}
        @keyframes lnTextGlow {{
            0%,100% {{ text-shadow: 0 0 10px rgba(255,255,255,0.95), 0 0 25px rgba(0,190,255,0.7), 0 0 55px rgba(0,130,255,0.5); }}
            50%      {{ text-shadow: 0 0 18px #fff, 0 0 38px rgba(0,210,255,0.95), 0 0 70px rgba(0,160,255,0.65); }}
        }}
        .ln-pulse-line {{
            stroke-dasharray: 300;
            stroke-dashoffset: 300;
            animation: lnDrawPulse 2s ease forwards, lnPulseFade 3s ease-in-out 2s infinite;
        }}
        @keyframes lnDrawPulse {{ to {{ stroke-dashoffset: 0; }} }}
        @keyframes lnPulseFade {{
            0%,100% {{ opacity:1;   filter: drop-shadow(0 0 3px #00cfff) drop-shadow(0 0 8px #0099ff); }}
            50%      {{ opacity:0.5; filter: drop-shadow(0 0 10px #00cfff) drop-shadow(0 0 20px #0099ff); }}
        }}
        .ln-brand-sub {{
            font-size: 11px;
            letter-spacing: 3.5px;
            color: #00cfff;
            text-transform: uppercase;
            opacity: 0.8;
            text-shadow: 0 0 10px #00cfff;
        }}

        /* ── BOTTOM LEFT: features + button ── */
        .bottom-left {{
            position: fixed;
            bottom: 90px;
            left: 40px;
            z-index: 999;
        }}
         .login-features {{

    display: flex;

    flex-direction: column;

    gap: 18px;

    font-family:
        "Inter",
        "Segoe UI",
        sans-serif;

    font-size: 24px;

    font-weight: 700;

    letter-spacing: 0.4px;

    color: rgba(255,255,255,0.96);

    line-height: 1.6;

    text-shadow:
        0 0 8px rgba(255,255,255,0.08),
        0 0 18px rgba(0,180,255,0.12);

    margin-bottom: 28px;
      }}
        .feature-item {{

    position: relative;

    padding-left: 8px;

    transition: all 0.25s ease;
     }}

.feature-item:hover {{

    transform: translateX(6px);

    color: #38bdf8;

    text-shadow:
        0 0 12px rgba(56,189,248,0.65);
        }}
        .login-btn {{
            background: rgba(37,99,235,0.92);
            color: white;
            padding: 12px 28px;
            border: none;
            border-radius: 10px;
            font-size: 14px;
            font-weight: 700;
            cursor: pointer;
            letter-spacing: 1px;
            box-shadow: 0 0 24px rgba(37,99,235,0.55);
            text-decoration: none;
            display: inline-block;
        }}
        .login-btn:hover {{ opacity: 0.88; }}
        </style>
        </head>
        <body>

          <!-- TOP RIGHT: Logo -->
          <div class="top-right">
            <div class="ln-text-col">
              <div class="ln-brand-name">
                PulseIQ
                <svg width="90" height="38" viewBox="0 0 110 44" fill="none"
                  xmlns="http://www.w3.org/2000/svg"
                  style="display:inline-block;vertical-align:middle;">
                  <polyline class="ln-pulse-line"
                    points="0,22 15,22 22,8 28,36 36,4 44,38 50,22 62,22 68,14 74,30 80,22 110,22"
                    stroke="#00cfff" stroke-width="2.5"
                    stroke-linecap="round" stroke-linejoin="round" fill="none"
                    style="filter: drop-shadow(0 0 4px #00cfff) drop-shadow(0 0 12px #0099ff);"/>
                </svg>
              </div>
              <div class="ln-brand-sub">AI-Powered Option Chain Intelligence</div>
            </div>
            <div class="ln-bolt-wrap">
              <div class="ln-bolt-ring"></div>
              <div class="ln-bolt-ring"></div>
              <div class="ln-bolt-ring"></div>
              <svg class="ln-bolt-svg" width="72" height="92"
                viewBox="0 0 60 80" xmlns="http://www.w3.org/2000/svg">
                <polygon points="38,2 14,42 30,42 22,78 46,38 30,38"
                  fill="#00cfff" stroke="#ffffff" stroke-width="1"/>
              </svg>
              <div class="ln-spark"></div>
              <div class="ln-spark"></div>
              <div class="ln-spark"></div>
              <div class="ln-spark"></div>
              <div class="ln-spark"></div>
            </div>
          </div>

          <!-- BOTTOM LEFT: features + login -->
          <div class="bottom-left">
            <div class="login-features">

             <div class="feature-item">
               📈 Live Market Analytics
            </div>

             <div class="feature-item">
              🧠 AI-Powered Options Insights
            </div>

            <div class="feature-item">
             🔥 Real-Time OI Tracking
             </div>

        </div>
            <a href="{login_url}" target="_top" class="login-btn">
              &#128272; Login with Zerodha
            </a>
          </div>

        </body>
        </html>
        """,
        height=800,
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