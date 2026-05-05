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


def fetch_option_chain(symbol="NIFTY"):
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
        puts = temp[temp["Type"] == "PE"]

        merged = pd.merge(
            calls[["Strike", "OI"]],
            puts[["Strike", "OI"]],
            on="Strike",
            suffixes=("_Call", "_Put")
        )

        final_df = pd.DataFrame({
            "Strike": merged["Strike"],
            "Call OI": merged["OI_Call"],
            "Put OI": merged["OI_Put"]
        }).sort_values("Strike")

        # Spot
        spot = kite.ltp(["NSE:NIFTY 50"])["NSE:NIFTY 50"]["last_price"]

        final_df["Distance"] = abs(final_df["Strike"] - spot)
        atm_strike = final_df.loc[final_df["Distance"].idxmin(), "Strike"]

        strikes = sorted(final_df["Strike"].unique())
        atm_index = strikes.index(atm_strike)

        selected = strikes[max(0, atm_index-4): atm_index+5]

        filtered = final_df[final_df["Strike"].isin(selected)]

        return filtered, atm_strike, spot

    except Exception as e:
        print("❌ Kite error:", e)
        return None