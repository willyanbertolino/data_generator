import streamlit as st
import random
import string

from utils.mock_data import address, products
from routes.data.db_router import save_data, get_data_ids

def create_inputs(name: str) -> dict:
    values = {}

    with st.container():
        # Slider -> probability (0-100), checkboxes: empty and typo (swap, remove, insert, replace)
        st.markdown(f"##### Adicionar problemas no campo {name}")
        issue_pct = st.slider(f"Porcentagem de dados defeituosos", 0, 100, 0, key=f"{name}_issue_pct")
        issue_rate = issue_pct / 100
        values["issue_rate"] = issue_rate

        if issue_pct != 0:
            empty_issue = st.checkbox("Inserir campos vazios", value=True, key=f"{name}_empty")
            values["empty_issue"] = empty_issue

            col1, col2 = st.columns([3,3])
            with col1:
                typo_swap = st.checkbox("Typos do tipo inverter caractere", value=False, key=f"{name}_typo_swap")
                values["typo_swap"] = typo_swap
                typo_remove = st.checkbox("Typos do tipo remover caractere", value=False, key=f"{name}_typo_remove")
                values["typo_remove"] = typo_remove
            with col2:
                typo_insert = st.checkbox("Typos do tipo inserir caractere", value=False, key=f"{name}_typo_insert")
                values["typo_insert"] = typo_insert
                typo_replace = st.checkbox("Typos do tipo substituir caractere", value=False, key=f"{name}_typo_replace")
                values["typo_replace"] = typo_replace

    return values

def typo_empty_issues(desc: str, text: str, issues: dict) -> dict:
    result = {desc: text}

    rand_value_typo = random.random()
    rand_value_empty = random.random()

    if rand_value_typo < issues["issue_rate"]:
        filtered_issues = {k: v for k, v in issues.items() if k != "issue_rate" and k != "empty_issue"}
        result = apply_random_typo(desc, text, filtered_issues)
        return result
    if rand_value_empty < issues["issue_rate"]:
        if issues["empty_issue"]:
            result = {desc: None}

    return result

def apply_random_typo(desc: str, text: str, issues: dict) -> dict:
    result = {desc: text}
    
    selected_issues = [key for key, value in issues.items() if value]
    if not selected_issues or not text or len(text) < 2:
        return result
    else:
        typo_type = random.choice(selected_issues)
        idx = random.randint(0, len(text) - 2)
        new_text = result[desc]
        
        if typo_type == "typo_swap":
            chars = list(text)
            chars[idx], chars[idx + 1] = chars[idx + 1], chars[idx]
            new_text = ''.join(chars)
        elif typo_type == "typo_remove":
            new_text = text[:idx] + text[idx+1:]
        elif typo_type == "typo_insert":
            new_text = text[:idx] + random.choice(string.ascii_lowercase) + text[idx:]
        elif typo_type == "typo_replace":
            new_text = text[:idx] + random.choice(string.ascii_lowercase) + text[idx+1:]
        
        if result[desc] != new_text:
            result[desc] = new_text
        return result

# Client data generator
def client_generator():
    st.title("Criar clientes fictícios")
    selected_cities = st.multiselect("Escolha as cidades:", list(address.keys()), key="mts_client")
    num = st.number_input("Quantidade de entradas", min_value=1, max_value=100, value=10, key="city_quantity")
    city_issues = create_inputs("cidade")
    st.divider()
    zip_issues = create_inputs("cep")

    if st.button("Gerar", key="generate_client_btn"):
        if selected_cities:
            result = create_clients(selected_cities, num, city_issues=city_issues, zip_issues=zip_issues)
            st.write(result)
            st.button("Salvar", on_click=save_data, args=(result, "clients"), key="save_client_btn")
            st.success(f'dados inseridos com sucesso na tabela')
        else:
            st.warning("Escolha pelo menos uma cidade.")

def create_clients(selected_cities, n=5, city_issues={}, zip_issues={}):
    for _ in range(n):
        city = random.choice(selected_cities)
        zip = random.choice(address[city])

        city_data = typo_empty_issues("name", city, city_issues)
        zip_data = typo_empty_issues("number", zip, zip_issues)

    return {"city": city_data["name"], "zip": zip_data["number"]}

# Product generator
def product_generator():
    st.title("Criar produtos fictícios")

    female = st.checkbox("Feminino", value=True, key="female_checkbox")
    if female:
        selected_products_f = st.multiselect("Escolha os produtos femininos:", list(products["feminino"].keys()), key="mts_f_product")
        product_issues_f = create_inputs("female_product")
        n_f = st.number_input("Quantidade de entradas femininas", min_value=1, max_value=1000, value=10, key="product_quantity_f")
    
    st.divider()

    male = st.checkbox("Masculino", value=True, key="male_checkbox")
    if male:
        selected_products_m = st.multiselect("Escolha os produtos masculinos:", list(products["masculino"].keys()), key="mts_m_product")
        product_issues_m = create_inputs("male_product")
        n_m = st.number_input("Quantidade de entradas masculinas", min_value=1, max_value=1000, value=10, key="product_quantity_m")
    
    if st.button("Gerar", key="generate_product_btn"):
        selected = {}
        if male and selected_products_m:
            selected["masculino"] = selected_products_m
            selected["product_issues_m"] = product_issues_m
            selected["n_m"] = n_m

        if female and selected_products_f:
            selected["feminino"] = selected_products_f
            selected["product_issues_f"] = product_issues_f
            selected["n_f"] = n_f

        if selected:
            result = create_products(selected)
            st.write(result)
            st.button("Salvar", on_click=save_data, args=(result, "products"), key="save_product_btn")
            st.success(f'dados inseridos com sucesso na tabela')
        else:
            st.warning("Escolha pelo menos uma categoria e subcategoria.")
    return

def create_products(selected):
    if selected.get("masculino"):
        selected_products_m = selected["masculino"]
        product_issues_m = selected["product_issues_m"]
        n_m = selected["n_m"]
        products_m = create_products_by_category("masculino", selected_products_m, product_issues_m, n_m)
        
    if selected.get("feminino"):
        
        selected_products_f = selected["feminino"]
        product_issues_f = selected["product_issues_f"]
        n_f = selected["n_f"]
        products_f = create_products_by_category("feminino", selected_products_f, product_issues_f, n_f)

    return products_m + products_f

def create_products_by_category(gender, selected_products, product_issues, n):
    data = []

    for _ in range(n):
        selected_category = random.choice(selected_products)
        selected_subcategory = random.choice(products[gender][selected_category])
        price = round(random.uniform(70.0, 300.0), 2)
        
        if product_issues.get('issue_rate', 0) > 0:
            gender_text = typo_empty_issues("gender", gender, product_issues)
            category_text = typo_empty_issues("category", selected_category, product_issues)
            subcategory_text = typo_empty_issues("subcategory", selected_subcategory, product_issues)
            price_num = {"price": price}
            res = {**gender_text, **category_text, **subcategory_text, **price_num}

        data.append(res)
    return data

def order_generator():
    n = st.number_input("Quantidade de pedidos", min_value=1, max_value=1000, value=10, key="data_quantity")
    st.button("Gerar", on_click=create_order, args=(n,), key="create_order_btn")
    st.success(f'dados inseridos com sucesso na tabela')

def create_order(n):
    clients = get_data_ids("clients")

    if clients:
        for _ in range(n):
            selected_client = random.choice(clients)
            client = {"client_id": selected_client}
        
            order = save_data(client,"orders", True)
            order_id = order[0]["id"]
            create_product_list(order_id)
            
def create_product_list(order_id):
    products = get_data_ids("products")

    bag_quantity = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    weigths = [30, 25, 20, 10, 5, 4, 2, 2, 1, 1]

    n = random.choices(bag_quantity, weights=weigths, k=1)[0]
    items = []

    q = [1, 2, 3]
    w = [90, 8, 2]
    choose_products = random.sample(products, k=n)

    for product in choose_products:
        quantity = random.choices(q, weights=w, k=1)[0]
        item = {"order_id": order_id, "product_id": product, "quantity": quantity}
        items.append(item)

    save_data(items, "order_items")
    return