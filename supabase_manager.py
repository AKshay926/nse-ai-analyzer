from supabase import create_client
import streamlit as st

# ================= SUPABASE CLIENT =================

supabase = create_client(
    st.secrets["SUPABASE_URL"],
    st.secrets["SUPABASE_KEY"]
)

# ================= SAVE TOKEN =================

def save_token(token):

    supabase.table("sessions") \
        .update({
            "access_token": token
        }) \
        .eq("id", "main") \
        .execute()

# ================= LOAD TOKEN =================

def load_token():

    response = supabase.table("sessions") \
        .select("access_token") \
        .eq("id", "main") \
        .single() \
        .execute()

    data = response.data

    if data:
        return data["access_token"]

    return None