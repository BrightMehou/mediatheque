import streamlit as st
import requests
import os

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
    
@st.cache_data
def load_types() -> list[str]:
    response = requests.get(f"{API_BASE_URL}/types")
    response.raise_for_status()
    return response.json()

def load_livres(types: list[str] = None, auteur: str = None) -> list[dict]:
    params = {}
    if types:
        params["types"] = types
    if auteur:
        params["auteur"] = auteur
    response = requests.get(f"{API_BASE_URL}/livres", params=params)
    response.raise_for_status()
    return response.json()

st.set_page_config(page_title="Médiathèque", page_icon="📚", layout="wide")
st.title("📚 Médiathèque")

try:
    types = load_types()
    type_selectionnes = st.multiselect(
        "Choisissez un type de livre :",
        options=types,
    )
    auteur = st.text_input("Auteur (pseudonyme)")
    livres = load_livres(types=type_selectionnes, auteur=auteur)
    st.dataframe(livres)
except Exception as e:
    st.error(f"Erreur: {e}")