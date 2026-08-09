import logging
import os

import requests
import streamlit as st

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")


@st.cache_data
def load_types() -> list[dict]:
    response = requests.get(f"{API_BASE_URL}/book_type", timeout=30)
    response.raise_for_status()
    return response.json()


@st.dialog("Ajouter un type de livre")
def create_type():
    new_type = st.text_input("Type de livre")
    if st.button("Ajouter"):
        response = requests.post(
            f"{API_BASE_URL}/book_type/", json={"type": new_type}, timeout=30
        )
        response.raise_for_status()
        logger.info("Création OK: %s", response.json())
        load_types.clear()
        st.rerun()


st.set_page_config(page_title="Médiathèque - Admin", page_icon="⚙️", layout="wide")
st.title("⚙️ Administration de la Médiathèque")

try:
    if st.button("Ajouter un type de livre"):
        create_type()

    livre_types = load_types()
    event = st.dataframe(
        livre_types,
        on_select="rerun",
        selection_mode="single-row",
        column_order=("type",),
    )

    row = event.selection.rows
    if row:
        selected_index = row[0]
        record = livre_types[selected_index]

        with st.form("Modifier le type de livre"):
            new_type = st.text_input("Type de livre", value=record["type"])
            submitted = st.form_submit_button("Modifier")

            if submitted:
                with st.spinner("Modification en cours..."):
                    response = requests.put(
                        f"{API_BASE_URL}/book_type/{record['id']}",
                        json={"type": new_type},
                        timeout=30,
                    )
                    response.raise_for_status()
                    logger.info("Modification du type %s réussie", record["id"])
                    load_types.clear()
                    st.rerun()

except Exception as e:
    logger.exception("Erreur: %s")
    st.error(f"Erreur: {e}")
