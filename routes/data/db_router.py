import streamlit as st
from db.connection import get_supabase
import pandas as pd
from utils.mock_data import df_cols
import numpy as np

def save_data(new_data: dict, table: str, res: bool = False):
    try:
        supabase = get_supabase()
        result = supabase.table(table).insert(new_data).execute()
        
        if result.data:
            if res:
                return result.data
            else:
                return
        else:
            return st.info("Não foi possível salvar.")
    except Exception as e:
        st.error(f"Ocorreu um erro ao salvar os dados: {str(e)}")
        return

def update_data(new_data: dict, table: str):
    user_id = st.session_state["user"]["id"]
    try:
        supabase = get_supabase()
        res = supabase.table(table).update(new_data).eq("user_id", user_id).execute()
        
        if res.data:
            return
        else:
            return st.info("Não foi possível atualisar o desempenho.")
    except Exception as e:
        st.error(f"Ocorreu um erro ao salvar os dados: {str(e)}")
        return
    
def save_df(df):
    user_id = st.session_state["user"]["id"]
    try:
        supabase = get_supabase()
        df["user_id"] = user_id
        df = df.replace({np.nan: None})
        data = df.to_dict(orient="records")
        res = supabase.table("dataframe").upsert(data, on_conflict=["id", "user_id"]).execute()

        if res.data:
            df_res = pd.DataFrame(res.data)
            df_res = df_res[df_cols]
            return df_res
        else:
            return False
    except Exception as e:
        st.error(f"Ocorreu um erro ao salvar os dados: {str(e)}")
        return None

def get_user_df():
    user_id = st.session_state["user"]["id"]
    try:
        supabase = get_supabase()
        res = supabase.table("dataframe").select("*").eq("user_id", user_id).order("id").execute()
        #res_work_dup = supabase.table("user_work").select("solved_dup").eq("user_id", user_id).execute()

        if res.data:
            return pd.DataFrame(res.data)
        else:
            return st.info("Não foi possível carregar os dados")
    except Exception as e:
        st.error(f"Ocorreu um erro ao buscar os dados: {str(e)}")
        return
    
def get_dup_solved():
    user_id = st.session_state["user"]["id"]
    try:
        supabase = get_supabase()
        res_work_dup = supabase.table("user_work").select("solved_dup").eq("user_id", user_id).execute()

        if res_work_dup.data:
            return res_work_dup.data
        else:
            return st.info("Não foi possível saber se resolveu duplicatas")
    except Exception as e:
        st.error(f"Ocorreu um erro ao buscar os dados: {str(e)}")
        return
    
    
def get_all_data(table:str):
    try:
        supabase = get_supabase()
        res = supabase.table(table).select("*").execute()
        
        if res.data:
            return res.data
        else:
            return st.info("Não foi possível carregar os dados")
    except Exception as e:
        st.error(f"Ocorreu um erro ao salvar os dados: {str(e)}")
        return
    
def get_all_data_filtered(table:str, condition: str, value: str):
    try:
        supabase = get_supabase()
        res = supabase.table(table).select("*").eq(condition, value).execute()
        
        if res.data:
            return res.data[0]
        else:
            return {}
    except Exception as e:
        st.error(f"Ocorreu um erro ao salvar os dados: {str(e)}")
        return

def get_data_ids(table: str):
    try:
        supabase = get_supabase()
        res = supabase.table(table).select("id").execute()
        
        if res.data:
            return [item["id"] for item in res.data]
        else:
            return st.info("Não foi possível carregar os dados")
    except Exception as e:
        st.error(f"Ocorreu um erro ao salvar os dados: {str(e)}")
        return
    
def get_data_fields(table: str, fields: str, filter_by: str, values):
    try:
        supabase = get_supabase()
        values = values if isinstance(values, list) else [values]

        res = supabase.table(table).select(fields).in_(filter_by, values).execute()

        if res.data:
            return res.data
        else:
            return []
    except Exception as e:
        st.error(f"Ocorreu um erro ao carregar os dados: {str(e)}")
        return []