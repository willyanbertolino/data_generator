import streamlit as st
from db.connection import get_supabase

def login():
    try:
        supabase = get_supabase()
        res = supabase.auth.sign_in_with_password({
            "email": st.session_state["email_input"],
            "password": st.session_state["password_input"]
        })

        if res.user:
            st.session_state["access_token"] = res.session.access_token
            uid = res.user.id
        else:
            with st.sidebar:
                st.warning("Não foi possível fazer o login")

    except Exception as e:
        with st.sidebar:
            st.error(f"Não foi possível fazer o login. Verifique o e-mail e senha.")
        return

    try:
        # 2. Tentativa de buscar informações extras
        user = supabase.table("users").select("*").eq("id", uid).execute()

        if user.data and len(user.data) > 0:
            user = user.data[0]
            st.session_state["logged"] = True
            st.session_state["user"] = user
        else:
            with st.sidebar:
                st.warning("Não foi possível fazer o login")
    except Exception as e:
        with st.sidebar:
            st.error(f"Erro ao fazer o login")
        logout()

def create_user(data):
    name = data["name"]
    email = data["email"]
    password = data["password"]

    try:
        supabase = get_supabase()
        auth = supabase.auth.sign_up({"email":email, "password": password})

        if(auth.user):
            log = supabase.auth.sign_in_with_password({"email": email, "password": password})
            if(not log.user):
                st.warning("Não foi possível fazer o login")
                return
            else:
                st.session_state["access_token"] = log.session.access_token
        else:
            st.warning("Não foi possível fazer o registro")
            return

    except Exception as e:
        st.error(f"Ocorreu um erro ao registrar ou logar o usuário: {str(e)}")
        return

    try:
        user = supabase.table("users").insert({
                "id":log.user.id,
                "name": name,
                "email":log.user.email,
                "role": "USER",
            }).execute()

        if user.data and len(user.data) > 0:
            user = user.data[0]
            st.success(f"Usuário '{user["name"]}' cadastrado com sucesso!")
            st.session_state["user"] = user
        else:
            st.warning("Não foi possível fazer o registro")

    except Exception as e:
        st.error(f"Ocorreu um erro em salvar o nome do usuário.: {str(e)}")


def logout():
    try:
        supabase = get_supabase()
        supabase.auth.sign_out()
        st.session_state["logged"] = False
        st.session_state["user"] = None
        st.session_state["access_token"] = None
    except Exception as e:
        st.error(f"Por favor, atualize a página.")

def getUsers():
    try:
        supabase = get_supabase()
        users = supabase.table("users").select("*").execute()

        if users.data:
            for user in users.data:
                nome = user["name"]
                email = user["email"]
                st.markdown(f"📧 **{nome}** ({email})")
        else:
            st.info("Nenhum usuário encontrado.")

    except Exception as e:
        st.error(f"Ocorreu um erro ao buscar os usuários: {e}")

