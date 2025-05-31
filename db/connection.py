from supabase import create_client, Client
import streamlit as st
import os

def get_supabase():
    try:
        url = st.secrets["SUPABASE_URL"]
        key = st.secrets["SUPABASE_KEY"]

    except Exception as e:
        from dotenv import load_dotenv
        load_dotenv()

        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")

        if not url or not key:
            st.error("❌ SUPABASE_URL ou SUPABASE_KEY não definidos nem nos secrets nem no .env.")
            raise ValueError("Configuração da Supabase ausente.")

    try:
        supabase: Client = create_client(url, key)

        # Autenticação com access_token (se disponível)
        token = st.session_state.get("access_token")
        if token:
            supabase.auth.set_session(token, "")

        return supabase

    except Exception as e:
        st.error(f"❌ Erro ao criar cliente Supabase: {str(e)}")
        raise