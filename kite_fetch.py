from kiteconnect import KiteConnect
import pandas as pd
import streamlit as st

API_KEY = st.secrets["API_KEY"]

def get_kite():
    if "access_token" not in st.session_state:
        return None

    kite = KiteConnect(api_key=API_KEY)
    kite.set_access_token(st.session_state["access_token"])
    return kite


def fetch_option_chain(symbol="NIFTY", range_size=10, custom_strike=None):
    """
    Fetch option chain data.

    Args:
        symbol       : Index name e.g. "NIFTY"
        range_size   : Number of strikes on each side (default 10, supports up to ±20)
        custom_strike: If provided, centre the chain on this strike instead of ATM
    """
    try:
        kite = get_kite()
        if kite is None:
            return None

        instruments = kite.instruments("NFO")
        df = pd.DataFrame(instruments)

        df = df[
            (df["name"] == symbol) &
            (df["instrument_type"].isin(["CE", "PE"]))
        ]

        expiry = sorted(df["expiry"].unique())[0]
        df = df[df["expiry"] == expiry]

        df["symbol"] = df["exchange"] + ":" + df["tradingsymbol"]

        # ── Fetch ALL strikes (up to 300 symbols limit) ──────────────────────
        symbols = df["symbol"].tolist()[:300]
        quotes = kite.quote(symbols)

        rows = []
        for _, row in df.iterrows():
            sym = row["symbol"]
            if sym in quotes:
                q = quotes[sym]
                rows.append({
                    "Strike": row["strike"],
                    "Type": row["instrument_type"],
                    "OI": q.get("oi", 0)
                })

        temp = pd.DataFrame(rows)

        calls = temp[temp["Type"] == "CE"]
        puts  = temp[temp["Type"] == "PE"]

        merged = pd.merge(
            calls[["Strike", "OI"]],
            puts[["Strike", "OI"]],
            on="Strike",
            suffixes=("_Call", "_Put")
        )

        full_df = pd.DataFrame({
            "Strike":  merged["Strike"],
            "Call OI": merged["OI_Call"],
            "Put OI":  merged["OI_Put"]
        }).sort_values("Strike").reset_index(drop=True)

        # ── Spot & ATM ────────────────────────────────────────────────────────
        spot = kite.ltp(["NSE:NIFTY 50"])["NSE:NIFTY 50"]["last_price"]

        full_df["Distance"] = abs(full_df["Strike"] - spot)
        atm_strike = full_df.loc[full_df["Distance"].idxmin(), "Strike"]

        # ── Centre strike (ATM or user-selected) ─────────────────────────────
        centre = custom_strike if custom_strike else atm_strike

        all_strikes = sorted(full_df["Strike"].unique().tolist())

        # Snap centre to nearest available strike
        closest = min(all_strikes, key=lambda x: abs(x - centre))
        centre_idx = all_strikes.index(closest)

        lower_idx = max(0, centre_idx - range_size)
        upper_idx = min(len(all_strikes) - 1, centre_idx + range_size)

        selected_strikes = all_strikes[lower_idx : upper_idx + 1]

        filtered = full_df[full_df["Strike"].isin(selected_strikes)].drop(
            columns=["Distance"]
        )

        return filtered, atm_strike, spot

    except Exception as e:
        print("❌ Kite error:", e)
        return None