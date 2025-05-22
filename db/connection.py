from supabase import create_client, Client
import streamlit as st
from dotenv import load_dotenv
import os

load_dotenv()

if "access_token" not in st.session_state:
    st.session_state["access_token"] = None

@st.cache_resource
def get_supabase():
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    if not url or not key:
        raise ValueError("SUPABASE_URL ou SUPABASE_KEY não encontrados nas variáveis de ambiente")

    supabase: Client = create_client(url, key)

    if st.session_state["access_token"]:
        supabase.auth.set_session(st.session_state["access_token"],"")
    return supabase