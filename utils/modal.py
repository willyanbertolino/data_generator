import streamlit as st

def modal(modal_name, on_submit, **fields):
        with st.expander(modal_name):
            inputs = {}
            for field_name, type in fields.items():
                if type == "text":
                    inputs[field_name] = st.text_input(field_name)
                elif type == "number":
                    inputs[field_name] = st.number_input(field_name)
                elif type == "checkbox":
                    inputs[field_name] = st.checkbox(field_name)
                elif type == "date":
                    inputs[field_name] = st.date_input(field_name)

            if st.button("Salvar", key=f"{modal_name}_save"):
                if on_submit:
                    on_submit(inputs)
                st.rerun()
