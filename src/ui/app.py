import os

import requests
import streamlit as st

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")


@st.cache_data
def load_types() -> list[dict]:
    response = requests.get(f"{API_BASE_URL}/book_type", timeout=30)
    response.raise_for_status()
    return response.json()


def load_books(types: list[str] | None = None, user: str | None = None) -> list[dict]:
    params = {}
    if types:
        params["types"] = types
    if user:
        params["user"] = user

    response = requests.get(f"{API_BASE_URL}/book", params=params, timeout=30)
    response.raise_for_status()
    return response.json()


st.set_page_config(page_title="Médiathèque", page_icon="📚", layout="wide")
st.title("📚 Médiathèque")

try:
    types = load_types()

    type_selectionnes = st.multiselect(
        "Choisissez un type de livre :",
        options=[t["type"] for t in types],
    )

    user = st.text_input("Auteur (pseudonyme)")

    livres = load_books(types=type_selectionnes, user=user)
    st.dataframe(livres)

except Exception as e:
    st.error(f"Erreur: {e}")
