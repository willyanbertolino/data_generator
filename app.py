import streamlit as st
import pandas as pd

from utils.modal import modal
from utils.mock_data import df_cols
from routes.auth.authentication import login, create_user, logout, getUsers
from routes.data.create_data import client_generator, product_generator, order_generator
from routes.data.table_generator import get_user_work
from routes.data.analysis import set_sent_and_send, check_missing_col, test_df, data_analysis_problems, data_analysis_total_problems
from routes.data.db_router import get_user_df

if "logged" not in st.session_state:
    st.session_state["logged"] = False

if "user" not in st.session_state:
    st.session_state["user"] = None

if "user" not in st.session_state or st.session_state["user"] is None:
    with st.sidebar:
        st.text_input("Email", key="email_input")
        st.text_input("Senha", type="password", key="password_input")
        st.button("Login", on_click=login)

if "sent_btn" not in st.session_state:
    st.session_state["sent_btn"] = False

if "upload_df" not in st.session_state:
    st.session_state["upload_df"] = None

if "uploaded_data" not in st.session_state:
    st.session_state["uploaded_data"] = False

# # Interface
st.title("Gerador de dados para análise")

if not st.session_state["logged"]:
    st.write("Faça o login para continuar")
else:
    name = st.session_state["user"]["name"]
    role = st.session_state["user"]["role"]

    st.sidebar.write(f"👋 Bem-vindo, **{name}**!")
    st.sidebar.button("Sair", on_click=logout)

    if role == "ADMIN":
        tab1, tab2, tab3 = st.tabs([":bust_in_silhouette: Usuários", "📊 Dados", "⚙️ Configurações"])
        with tab1:

            st.markdown("### 👥 Usuários")

            modal("Criar usuário", on_submit=create_user, name="text", email="text", password="text")

            st.markdown("---")

            # Lista de usuários cadastrados
            user_head, get_users = st.columns([5,1])
            with user_head:
                st.subheader("Usuários cadastrados:")
            with get_users:
                if st.button("🔄 Atualizar", key="refresh_users_list"):
                    st.rerun()

            getUsers()

        with tab2:
            st.header("Dados")
            create_data, get_data = st.tabs(["Criar", "Analisar"])

            with create_data:
                #modal("Cadastrar cliente",on_submit=create_client, cidade="text", cep="text", n="number", erro="type")
                with st.expander("Criar Clientes"):
                    client_generator()
                with st.expander("Criar Produtos"):
                    product_generator()
                with st.expander("Criar Pedidos"):
                    order_generator()
                with st.expander("Gerar Tabela"):
                    st.write("mostrar dados dos estudantes")
                    #create_table()
        with tab3:
            st.header("Configurações")
            st.write("Ajustes e preferências.")

    # Not admin area
    else:
        user_work = get_user_work()

        with st.container():
            st.header("📈 Seu desempenho atual")
            col01, col02 = st.columns(2)
            with col01:
                st.metric("📨 Submissões", f"{user_work["submission"]} / 3")
            with col02:
                st.metric("📝 Nota", f"{user_work["score"]}")

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("⚠️ Problemas iniciais", f"{user_work['created_issue']}")
            with col2:
                st.metric("✅ Problemas resolvidos", f"{user_work['solved_issue']}")
            with col3:
                st.metric("🛠️ Novos Problemas", user_work['new_issue'])

            st.markdown("---")
        
        with st.expander("Visualizar os dados"):
            st.subheader("📊 Dados para análise")
            st.dataframe(user_work["df"], height=400, use_container_width=True)
            
        st.header("📊 Submissão de Dados para Análise")
        upload_df = None

        if user_work["submission"] < 3:
            if not st.session_state["uploaded_data"]:
                st.subheader("📥 Enviar planilha para análise")
                uploaded_file = st.file_uploader("Escolha um arquivo Excel ou CSV", type=["csv", "xlsx"])

                if uploaded_file:
                    try:
                        if uploaded_file.name.endswith(".csv"):
                            upload_df = pd.read_csv(uploaded_file)
                        else:
                            upload_df = pd.read_excel(uploaded_file)

                        if "df" in user_work and not upload_df.empty and not user_work["df"].empty:
                            check = check_missing_col(upload_df)
                            if check:
                                st.info(f"Colunas faltando: {check}")
                                st.info("As colunas citadas são obrigatórias. Caso tenha as colunas, verifique se o nome está correto.")
                                st.stop()
                            else:
                                st.session_state["uploaded_data"] = True
                                df_select_cols = upload_df[df_cols]
                                st.session_state["upload_df"] = df_select_cols
                                st.rerun()
                        else:
                            st.warning("⚠️ O arquivo está vazio ou os dados de referência não foram encontrados.")
                    except Exception as e:
                        st.error(f"❌ Erro ao processar o arquivo: {e}")
            else:
                if not st.session_state["sent_btn"]:
                    upload_df = st.session_state.get("upload_df")
                    st.success("✅ Dados carregados com sucesso!")
                    st.dataframe(upload_df, height=400, use_container_width=True)
                    st.button(
                        "Enviar",
                        on_click=lambda: set_sent_and_send(upload_df, user_work['created_issue'], user_work["submission"]),
                        key="submit_data_btn"
                    )
                else:
                    st.success(f"✅ Dados enviados! Você ainda tem {3-user_work["submission"]} tentativa(s) para melhorar a nota.")
        else:
            st.info(f"Você atingiu o limite de tentativas. Parabéns, sua nota final é {user_work['score']}")
            final_df = get_user_df()
            unsolved = data_analysis_total_problems(final_df)
            st.markdown(f'## Faltou resolver <span style="color:FireBrick; font-size:40px;"><b>{unsolved}</b></span> problemas:', unsafe_allow_html=True)
            st.write(data_analysis_problems(final_df))


