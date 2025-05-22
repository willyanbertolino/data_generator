import pandas as pd
import streamlit as st
from utils.mock_data import cities, all_zips, all_gender, all_categories, all_subcategories, df_cols
from routes.data.db_router import update_data, save_df

def data_analysis_total_problems(df):
    dup = duplicated_total_problems(df)
    typos = typo_total_problems(df)
    empty = empty_problems(df)
    outliers = outliers_total_problems(df)

    err = typos | dup | empty | outliers
    total = sum(err.values())
    return total

def data_analysis_problems(df):
    msg = {"Dados duplicados": "", "Erros de digitação": "", "Valores atípicos": "", "Valores ausentes": ""}
    dup_p = duplicated_problem_ids(df)
    typos_p = typo_unique_err(df)
    out_p = outliers_unique_err(df)
    empty = empty_problems(df)

    # Duplicates
    if len(dup_p) > 0:
        ids_str = [str(n) for n in dup_p]
        msg["Dados duplicados"] = "❌ Existem dados duplicados! ids: " + ", ".join(map(str, ids_str))
    else:
        msg["Dados duplicados"] = "✅ Não há dados duplicados."

    # Typos
    typos_err = {k: v for k, v in typos_p.items() if v}
    if not typos_err:
        msg["Erros de digitação"] = "✅ Nenhum erro encontrado."
    else:
        typos_err = sum(typos_err.values(),[])
        msg["Erros de digitação"] = "❌ " + ", ".join(map(str, typos_err))

    # Outliers
    if out_p["quantidade_outliers"]:
        out_p["quantidade_outliers"] = ["Quantidade: "] + [str(n) for n in out_p["quantidade_outliers"]]

    if out_p["preço_outliers"]:
        out_p["preço_outliers"] = ['Preço un.: '] + num_string_format(out_p["preço_outliers"])

    if out_p["valor_total_outliers"]:
        out_p["valor_total_outliers"] = ['Valor total: '] + num_string_format(out_p["valor_total_outliers"])

    out_err = {k: v for k, v in out_p.items() if v}
    if out_err:
        out_err = sum(out_err.values(),[])
        msg["Valores atípicos"] = "❌ " + ", ".join(map(str, out_err))
    else:
        msg["Valores atípicos"] = "✅ Não há valores atípicos."

    # Empty
    if len(empty) > 0:
        msg["Valores ausentes"] = "❌ Existem celulas vazias!"
    else:
        msg["Valores ausentes"] = "✅ Não há vazios."

    return msg

def num_string_format(array):
    return [f"R$ {v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") for v in array]

def typo_problems(df):
    city_typos = df[~df["cidade"].str.lower().isin([c.lower() for c in cities] + [None])]
    zip_typos = df[~df["cep"].str.lower().isin([z.lower() for z in all_zips] + [None])]
    gender_typos = df[~df["genero"].str.lower().isin([g.lower() for g in all_gender] + [None])]
    category_typos = df[~df["categoria"].str.lower().isin([cat.lower() for cat in all_categories] + [None])]
    subcategory_typos = df[~df["subcategoria"].str.lower().isin([s.lower() for s in all_subcategories]+ [None])]
    typos = {
        "cidade_typos": city_typos["cidade"],
        "cep_typos": zip_typos["cep"],
        "genero_typos": gender_typos["genero"],
        "categoria_typos": category_typos["categoria"],
        "subcategoria_typos": subcategory_typos["subcategoria"]
        }
    return typos

def typo_total_problems(df):
    typos = typo_problems(df)
    total_values = {col: len(s) for col, s in typos.items()}
    return total_values

def typo_unique_err(df):
    typos = typo_problems(df)
    values = {col: s.unique().tolist() for col, s in typos.items()}
    return values

def duplicated_problem_ids(df):
    df_wo_id = df.drop(columns=["id"], errors="ignore")
    duplicates = df_wo_id.duplicated(keep=False)
    if "id" in df.columns:
        return df.loc[duplicates, "id"].tolist()
    return df[duplicates].index.tolist()

def duplicated_total_problems(df):
    dup = duplicated_problem_ids(df)
    return {"duplicates": len(dup)}

def empty_problems(df):
    total_missing = df.isna().sum().sum()
    return {"empty": int(total_missing)}

def outliers_problems(df):
    city_outliers = df[df["cidade"] == "Manaus"]
    zip_outliers = df[df["cep"] == "86082-580"]
    quantity_outliers = df[df["quantidade"] > 3]
    price_outliers = df[df["preço un."] > 300]

    if "valor total" not in df.columns:
        df["valor total"] = df["preço un."] * df["quantidade"]

    q1 = df["valor total"].quantile(0.25)
    q3 = df["valor total"].quantile(0.75)
    iqr = q3 - q1
    inf = q1 - 1.5 * iqr
    sup = q3 + 1.5 * iqr
    outliers_total_value = df[(df["valor total"] < inf) | (df["valor total"] > sup)]
    outliers = {
        "cidade_outliers": city_outliers,
        "cep_outliers": zip_outliers,
        "quantidade_outliers": quantity_outliers,
        "preço_outliers": price_outliers,
        "valor_total_outliers": outliers_total_value
        }
    return outliers

def outliers_total_problems(df):
    outliers_total = outliers_problems(df)
    total_values = {col: len(s) for col, s in outliers_total.items()}
    return total_values

def outliers_unique_err(df):
    outliers = outliers_problems(df)
    values = {
        "cidade_outliers": outliers["cidade_outliers"]["cidade"].unique().tolist(),
        "cep_outliers": outliers["cep_outliers"]["cep"].unique().tolist(),
        "quantidade_outliers": outliers["quantidade_outliers"]["quantidade"].unique().tolist(),
        "preço_outliers": outliers["preço_outliers"]["preço un."].unique().tolist(),
        "valor_total_outliers": outliers["valor_total_outliers"]["valor total"].unique().tolist(),
    }
    return values

def check_missing_col(upload_df):
    uploaded_cols = set(col.lower() for col in upload_df.columns)
    df_col = pd.DataFrame(columns=df_cols)
    missing = set(df_col) - set(uploaded_cols)
    return missing

def set_sent_and_send(upload_df, created_issue, submission):
    st.session_state["sent_btn"] = True
    send_data(upload_df, created_issue, submission)

def send_data(df, initial_issues, num_submission):
    res = score_data(df, initial_issues, num_submission)
    if res:
        st.session_state["uploaded_data"] = False
        st.session_state["upload_df"] = None
        st.session_state["sent_btn"] = False

        st.success("✅ Dados enviados com sucesso! Você pode enviar outro arquivo.")
        st.rerun()
    else:
        st.info("Algo deu errado ao atualizar os dados")
    return

def score_data(upload_df, issues, n_submission):
    upload_problems = data_analysis_total_problems(upload_df)
    solved_issue = issues - upload_problems
    score = 0
    if solved_issue > 0:
        score = (issues - upload_problems) / issues
    
    new_data = {"score": round(score * 10, 1), "solved_issue": solved_issue, "submission": n_submission+1}
    update_data(new_data, "user_work")
    res = save_df(upload_df)
    return isinstance(res, pd.DataFrame)

# def test_df(df):
#     df = df.copy()
#     df["Valor Total"] = df["preço un."] * df["quantidade"]
#     df = solve_problems(df)
#     return df

# def drop_duplicates(df):
#     return df.drop_duplicates()

# def solve_problems(df):
#     df = drop_duplicates(df)
#     df.loc[df["cidade"].str.lower() == "ambé", "cidade"] = "Cambé"
#     df.loc[df["cidade"].str.lower() == "marhngá", "cidade"] = "Maringá"
#     df.loc[df["cidade"].str.lower() == "pucarana", "cidade"] = "Apucarana"
#     df.loc[df["genero"].str.lower() == "mascujlino", "genero"] = "masculino"
#     df.loc[df["genero"].str.lower() == "eminino", "genero"] = "feminino"
#     df.loc[df["genero"].str.lower() == "maasculino", "genero"] = "masculino"
#     df.loc[df["genero"].str.lower() == "feminno", "genero"] = "feminino"
#     df.loc[df["genero"].str.lower() == "nmasculino", "genero"] = "masculino"
#     df.loc[df["genero"].str.lower() == "femiino", "genero"] = "feminino"
#     df.loc[df["genero"].str.lower() == "feminhino", "genero"] = "feminino"
#     df.loc[df["genero"].str.lower() == "masiculino", "genero"] = "masculino"
#     df.loc[df["genero"].str.lower() == "mapsculino", "genero"] = "masculino"
#     df.loc[df["genero"].str.lower() == "femitnino", "genero"] = "feminino"
#     df.loc[df["genero"].str.lower() == "femitnino", "genero"] = "feminino"

#     return df
