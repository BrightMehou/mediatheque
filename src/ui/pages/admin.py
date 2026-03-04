import logging
import os

import pandas as pd
import requests
import streamlit as st

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")


@st.cache_data
def load_types() -> list[str]:
    response = requests.get(f"{API_BASE_URL}/livre_type")
    response.raise_for_status()
    return response.json()


@st.dialog("Ajouter un type de livre")
def create_type():
    new_type = st.text_input("Type de livre")
    if st.button("Ajouter"):
        response = requests.post(f"{API_BASE_URL}/livre_type/?type={new_type}")
        response.raise_for_status()
        logging.info(response.json())
        load_types.clear()
        st.rerun()


st.set_page_config(page_title="Médiathèque - Admin", page_icon="⚙️", layout="wide")
st.title("⚙️ Administration de la Médiathèque")
try:
    if st.button("Ajouter un type de livre"):
        create_type()
    livre_types = load_types()
    df = pd.DataFrame(livre_types)
    event = st.dataframe(
        df, on_select="rerun", selection_mode="single-row", column_order=("type",)
    )
    row = event.selection.rows
    if row:
        record = df.iloc[row].to_dict(orient="records")[0]
        with st.form("Modifier le type de livre"):
            new_type = st.text_input("Type de livre", value=record["type"])
            submitted = st.form_submit_button("Modifier")
            if submitted:
                with st.spinner("Modification en cours..."):
                    response = requests.put(
                        f"{API_BASE_URL}/livre_type/{record['id']}?type={new_type}"
                    )
                    response.raise_for_status()
                    logging.info(response.json())
                    load_types.clear()
                    st.rerun()
except Exception as e:
    st.error(f"Erreur: {e}")
