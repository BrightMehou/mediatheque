import os
import logging
import requests
import streamlit as st
import pandas as pd
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

@st.cache_data
def load_types() -> list[str]:
    response = requests.get(f"{API_BASE_URL}/livre_type")
    response.raise_for_status()
    return response.json()

@st.dialog('Ajouter un type de livre')
def create_type():
    new_type = st.text_input("Type de livre")
    if st.button("Ajouter"):
        response = requests.post(f"{API_BASE_URL}/livre_type/?type={new_type}")
        response.raise_for_status()
        logging.info(response.json())
        st.rerun()

@st.dialog('Modifier un type de livre')
def update_type(record: dict):
    type_id = record["id"]
    new_type = st.text_input("Type de livre", value=record["type"])
    if st.button("Modifier"):
        response = requests.put(f"{API_BASE_URL}/livre_type/{type_id}?type={new_type}")
        response.raise_for_status()
        logging.info(response.json())
        st.rerun()

st.set_page_config(page_title="Médiathèque - Admin", page_icon="⚙️", layout="wide")
st.title("⚙️ Administration de la Médiathèque")
try:
    if st.button("Ajouter un type de livre"):
        create_type()
    livre_types = load_types()
    df = pd.DataFrame(livre_types)
    event = st.dataframe(df,on_select='rerun',selection_mode='single-row',)
    row = event.selection.rows
    if row:
        record = df.iloc[row].to_dict(orient='records')[0]
        st.write(f"Type de livre sélectionné : {record}")
        update_type(record)
except Exception as e:
    st.error(f"Erreur: {e}")

