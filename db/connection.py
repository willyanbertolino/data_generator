from supabase import create_client, Client
import streamlit as st
import os

if "access_token" not in st.session_state:
    st.session_state["access_token"] = None

def get_supabase_local():
    from dotenv import load_dotenv
    load_dotenv()

    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")

    if not url or not key:
        raise ValueError("SUPABASE_URL ou SUPABASE_KEY não definidos no .env")

    supabase: Client = create_client(url, key)

    if st.session_state["access_token"]:
        supabase.auth.set_session(st.session_state["access_token"], "")
    return supabase


def get_supabase():
    try:
        url = st.secrets["SUPABASE_URL"]
        key = st.secrets["SUPABASE_KEY"]

        supabase: Client = create_client(url, key)

        if st.session_state["access_token"]:
            supabase.auth.set_session(st.session_state["access_token"], "")
        return supabase

    except KeyError as e:
        st.error(f"⚠️ Variável de segredo ausente: {e}. Verifique seus `secrets.toml` no Streamlit Cloud.")
        raise

    except Exception as e:
        st.error(f"❌ Erro inesperado ao inicializar Supabase: {str(e)}")
        raise