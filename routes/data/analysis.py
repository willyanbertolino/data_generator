import pandas as pd
import streamlit as st
from utils.mock_data import cities, all_zips, all_gender, all_categories, all_subcategories, df_cols, products, address
from routes.data.db_router import update_data, save_df, get_dup_solved

def data_analysis_problems_dict(df):
    typos = typo_problems_total(df)
    dup = duplicated_problems_total(df)
    empty = empty_problems_total(df)
    outliers = outliers_problems_total(df)
    gen_cat_sub_inv = verify_gen_cat_sub_total(df)
    city_zip_inv = verify_city_zip_total(df)

    err = typos | dup | empty | outliers | gen_cat_sub_inv | city_zip_inv
    return err

def data_analysis_total_problems(df):
    err = data_analysis_problems_dict(df)
    total = sum(err.values())
    return total

def data_analysis_problems_ids(df):
    typos_p = typo_problem_ids(df)
    dup_p = duplicated_problem_ids(df)
    empty = empty_problem_ids(df)
    new_city_zip = verify_city_zip_ids(df)
    new_gen_cat_sub = verify_gen_cat_sub_ids(df)
    out_p = outliers_problems_ids(df)

    all_errs = dup_p | typos_p | new_city_zip | new_gen_cat_sub | empty | out_p
    return all_errs

def errs_types(df):
    issues = data_analysis_problems_ids(df)
    keys = [k for k, v in issues.items() if v]
    return keys

def num_string_format(array):
    return [f"R$ {v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") for v in array]

def get_ids(sub_df):
    return sub_df["id"].tolist() if "id" in sub_df.columns else sub_df.index.tolist()

def typo_problem_ids(df):
    city_typos = df[df["cidade"].notna() & ~df["cidade"].str.lower().isin([c.lower() for c in cities])]
    zip_typos = df[df["cep"].notna() & ~df["cep"].isin([z for z in all_zips])]
    gender_typos = df[df["genero"].notna() & ~df["genero"].str.lower().isin([g.lower() for g in all_gender])]
    category_typos = df[df["categoria"].notna() & ~df["categoria"].str.lower().isin([cat.lower() for cat in all_categories])]
    subcategory_typos = df[df["subcategoria"].notna() & ~df["subcategoria"].str.lower().isin([s.lower() for s in all_subcategories])]

    typos = {
        "cidade_typos": get_ids(city_typos),
        "cep_typos": get_ids(zip_typos),
        "genero_typos": get_ids(gender_typos),
        "categoria_typos": get_ids(category_typos),
        "subcategoria_typos": get_ids(subcategory_typos),
    }
    return typos

def typo_problems_total(df):
    typos = typo_problem_ids(df)
    total_values = {col: len(s) for col, s in typos.items()}
    return total_values

def duplicated_problem_ids(df):
    df_wo_id = df.drop(columns=["id"], errors="ignore")
    duplicates = df_wo_id.duplicated(keep=False)

    if "id" in df.columns:
        ids = df.loc[duplicates, "id"].tolist()
    else:
        ids = df[duplicates].index.tolist()

    return {"duplicatas": ids}

def duplicated_problems_total(df):
    dup = duplicated_problem_ids(df)
    return {"duplicatas": len(dup["duplicatas"])}

def empty_problem_ids(df):
    empty_rows = df.isnull().any(axis=1)
    
    if "id" in df.columns:
        ids = df.loc[empty_rows, "id"].tolist()
    else:
        ids = df[empty_rows].index.tolist()

    return {"vazios": ids}

def empty_problems_total(df):
    total_missing = df.isna().sum().sum()
    return {"empty": int(total_missing)}

def verify_city_zip_ids(df):
    err_ids = []

    for idx, row in df.iterrows():
        city = row.get("cidade")
        zip_code = row.get("cep")

        if pd.isna(city) or pd.isna(zip_code):
            continue

        city = str(city).strip()
        zip_code = str(zip_code).strip()

        if city in address and zip_code not in address[city]:
            if "id" in df.columns:
                err_ids.append(row["id"])
            else:
                err_ids.append(idx)

    return {"cidade_cep_incompatíveis": err_ids}

def verify_city_zip_total(df):
    err = verify_city_zip_ids(df)
    return {"cidade_cep_incompatível": len(err["cidade_cep_incompatíveis"])}

def verify_gen_cat_sub_ids(df):
    err_ids = []

    for idx, row in df.iterrows():
        gender = row.get("genero")
        category = row.get("categoria")
        subcategory = row.get("subcategoria")

        if pd.isna(gender) or pd.isna(category) or pd.isna(subcategory):
            continue

        gender = str(gender).strip().lower()
        category = str(category).strip()
        subcategory = str(subcategory).strip()

        if gender not in products:
            err_ids.append(row["id"] if "id" in df.columns else idx)
            continue

        if category not in products[gender]:
            err_ids.append(row["id"] if "id" in df.columns else idx)
            continue

        if subcategory not in products[gender][category]:
            err_ids.append(row["id"] if "id" in df.columns else idx)

    return {"genero_cat_sub_incompatíveis": err_ids}

def verify_gen_cat_sub_total(df):
    err = verify_gen_cat_sub_ids(df)
    return {"genero_cat_sub_incompatíveis": len(err["genero_cat_sub_incompatíveis"])}

def outliers_problems_ids(df):
    city_outliers = df[df["cidade"] == "Manaus"]
    zip_outliers = df[df["cep"] == "86082-580"]
    quantity_outliers = df[df["quantidade"] > 3]
    price_outliers = df[df["preço un."] > 300]

    outliers = {
        "cidade_outliers": get_ids(city_outliers),
        "cep_outliers": get_ids(zip_outliers),
        "quantidade_outliers": get_ids(quantity_outliers),
        "preço_outliers": get_ids(price_outliers),
    }

    if "valor total" in df.columns and df["valor total"].notna().any():
        q1 = df["valor total"].quantile(0.25)
        q3 = df["valor total"].quantile(0.75)
        iqr = q3 - q1
        inf = q1 - 1.5 * iqr
        sup = q3 + 1.5 * iqr
        outliers_total_value = df[(df["valor total"] < inf) | (df["valor total"] > sup)]
        outliers["valor_total_outliers"] = get_ids(outliers_total_value)

    return outliers

def outliers_problems_total(df):
    outliers_total = outliers_problems_ids(df)
    keys = [
        "cidade_outliers",
        "cep_outliers",
        "quantidade_outliers",
        "preço_outliers",
        "valor_total_outliers"
    ]
    total_values = {key: len(outliers_total.get(key, [])) for key in keys}
    return total_values

def check_missing_col(upload_df):
    uploaded_cols = set(col.lower() for col in upload_df.columns)
    df_col = pd.DataFrame(columns=df_cols)
    missing = set(df_col) - set(uploaded_cols)
    return missing

def set_sent_and_send(df_initial, upload_df, submission):
    res = send_data(df_initial, upload_df, submission)
    if res:
        st.session_state["sent_btn"] = True

def send_data(df_initial, upload_df, num_submission):
    res = score_data(df_initial, upload_df, num_submission)
    if res:
        return True
    return False

def score_data(df_initial, upload_df, n_submission):
    res = compare_result(df_initial, upload_df)
    solved_percent = res["solved_issue"]/res["total"]
    new_percent = res["new_issue"]/res["total"]

    score = (solved_percent * 0.7 - new_percent * 0.3)*(10/7)
    if score < 0:
        score = 0
    
    new_data = {
        "score": round(score * 10, 1),
        "created_issue": res["total"],
        "solved_issue": res["solved_issue"],
        "new_issue": res["new_issue"],
        "solved_dup": res["solved_dup"],
        "submission": n_submission+1
        }

    update_data(new_data, "user_work")
    res = save_df(upload_df)
    return isinstance(res, pd.DataFrame)

def compare_result(df_initial, df_upload):
    df_upload = df_upload[df_cols]
    df_upload = df_upload[df_upload["id"].notna()]
    initial_problems = data_analysis_problems_dict(df_initial)
    uploaded_problems = data_analysis_problems_dict(df_upload)
    initial_problems["cidade_cep_incompatível"] = 0
    initial_problems["genero_cat_sub_incompatíveis"] = 0

    dup = (uploaded_problems.get("duplicatas", 0) == 0)
    total = sum(initial_problems.values())
    solved = 0
    new = 0

    for key in initial_problems:
        before = initial_problems[key]
        after = uploaded_problems.get(key, 0)
        if after > before:
            new += after-before
        elif after < before:
            solved += before-after
    
    return {"total": total, "solved_issue": solved, "new_issue": new, "solved_dup": dup}

def solved_dup(df):
    solved = get_dup_solved()

    if solved:
        duplicates_mask = df.drop(columns=["id"], errors="ignore").duplicated(keep=False)
        df_no_duplicates = df[~duplicates_mask]
        return df_no_duplicates
    else:
        return df