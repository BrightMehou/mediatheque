import streamlit as st
import requests
import os

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")


@st.cache_data
def load_genres() -> list[str]:
    response = requests.get(f"{API_BASE_URL}/genres")
    response.raise_for_status()
    return response.json()
    
@st.cache_data
def load_types() -> list[str]:
    response = requests.get(f"{API_BASE_URL}/types")
    response.raise_for_status()
    return response.json()

st.title("📚 Gestion de Bibliothèque")

try:
    genres, types = load_genres(), load_types()
    genre_selectionne = st.selectbox(
        "Choisissez un genre littéraire :",
        options=genres,
    )
    type_selectionne = st.selectbox(
        "Choisissez un type de livre :",
        options=types,
    )
    st.write(f"Vous avez sélectionné le genre : **{genre_selectionne}**")
    st.write(f"Vous avez sélectionné le type : **{type_selectionne}**")

except Exception as e:
    st.error(f"Erreur de connexion à la base de données : {e}")