import streamlit as st
import pandas as pd
import random
from io import BytesIO
from routes.data.db_router import get_data_ids, get_data_fields, get_all_data_filtered, save_data, save_df, get_user_df
from routes.data.analysis import data_analysis_total_problems

#def create_table():
    #n = st.number_input("Quantidade de pedidos", min_value=1, max_value=1000, key="data_table_quantity")
    #st.button("Gerar tabela", on_click=get_order_data, key="create_table_data_btn")

def create_initial_order_data(user_id):
    orders_amount = random.randint(230, 240)
    duplicates = random.randint(20, 30)

    orders_id = get_data_ids("orders")
    selected_orders = random.sample(orders_id, orders_amount)
    id_to_duplicate = random.choice(selected_orders)
    duplicate = [id_to_duplicate] * duplicates
    final_orders = selected_orders + duplicate
    random.shuffle(final_orders)
    df_to_save = init_df_order(final_orders)
    df_to_save["valor total"] = None
    df = save_df(df_to_save)

    if df is not None and "valor total" in df.columns:
        df = df.drop(columns=["valor total"])
    else:
        st.info("Não foi possível salvar os dados")
        st.stop()
    created_problems = data_analysis_total_problems(df)
    new_data = {
                    "user_id": user_id,
                    "orders": final_orders,
                    "created_issue": created_problems,
                    "solved_issue": 0,
                    "new_issue": 0,
                    "submission": 0,
                    "score": 0
                }
    
    res = save_data(new_data, "user_work", True)
    return {"user_work": res[0], "df": df}

def get_user_work():
    user_id = st.session_state["user"]["id"]
    user_work = get_all_data_filtered("user_work", "user_id", user_id)

    if not user_work:
        user_work_res = create_initial_order_data(user_id)
        user_work = user_work_res["user_work"]
        user_df = user_work_res["df"]
    else:
        saved_df = get_user_df()

        if saved_df is not None:
            order_ids = user_work["orders"]
            initial_df = init_df_order(order_ids)

            if len(initial_df) != len(saved_df):
                raise ValueError("Número de linhas do DataFrame reconstruído e salvo não bate.")
            
            initial_df = initial_df.copy()
            initial_df["id"] = saved_df["id"].reset_index(drop=True)
            #change "id" column order
            cols = user_df.columns.tolist()
            cols.insert(0, cols.pop(cols.index("id")))
            user_df = user_df[cols]
        else:
            st.info("Não foi possivel carregar os dados. Recarregue a página.")
            st.stop()

    return {
                "df": user_df,
                "created_issue": user_work["created_issue"],
                "solved_issue": user_work["solved_issue"],
                "new_issue": user_work["new_issue"],
                "submission": user_work["submission"],
                "score": user_work["score"]
            }

def init_df_order(order_ids):
    orders_data = get_data_fields("orders","id, client_id", "id", order_ids)
    
    client_ids = list(set([order["client_id"] for order in orders_data]))
    clients_data = get_data_fields("clients", "id, city, zip", "id", client_ids)

    order_items_data = get_data_fields("order_items","order_id, product_id, quantity", "order_id", order_ids)

    product_ids = list(set([item["product_id"] for item in order_items_data]))
    products_data = get_data_fields("products", "id, gender, category, subcategory, price", "id", product_ids)

    clients_dict = {c["id"]: c for c in clients_data}
    products_dict = {p["id"]: p for p in products_data}
    orders_dict = {o["id"]: o for o in orders_data}

    data = []
    if not orders_data or not clients_data or not order_items_data or not products_data:
        st.warning("Não foi possível carregar todos os dados necessários. Recarregue a página")
        st.stop()

    for order_id in order_ids:
        order = orders_dict.get(order_id)
        if not order:
            continue

        client = clients_dict.get(order["client_id"])
        items = [item for item in order_items_data if item["order_id"] == order_id]

        for item in items:
            product = products_dict.get(item["product_id"])
            if not product:
                continue

            row = {
                "pedido": order_id,
                "cliente": order["client_id"],
                "cidade": client["city"] if client else None,
                "cep": client["zip"] if client else None,
                "genero": product["gender"] if product else None,
                "categoria": product["category"] if product else None,
                "subcategoria": product["subcategory"] if product else None,
                "preço un.": product["price"] if product else None,
                "quantidade": item["quantity"],
            }

            data.append(row)
    
    df = pd.DataFrame(data)
    return df

def to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Dados')
    processed_data = output.getvalue()
    return processed_data