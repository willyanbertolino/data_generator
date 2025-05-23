from supabase import create_client, Client
import streamlit as st
import os

if "access_token" not in st.session_state:
    st.session_state["access_token"] = None

@st.cache_resource
def get_supabase():
    access_local = False
    if access_local:
        from dotenv import load_dotenv
        load_dotenv()
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")
    else:
        url = st.secrets["SUPABASE_URL"]
        key = st.secrets["SUPABASE_KEY"]

    if not url or not key:
        raise ValueError("SUPABASE_URL ou SUPABASE_KEY não encontrados nas variáveis de ambiente")

    supabase: Client = create_client(url, key)

    if st.session_state["access_token"]:
        supabase.auth.set_session(st.session_state["access_token"],"")
    return supabase