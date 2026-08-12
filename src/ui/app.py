import os

import requests
import streamlit as st

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")


@st.cache_data
def load_topics() -> list[dict]:
    response = requests.get(f"{API_BASE_URL}/topic", timeout=30)
    response.raise_for_status()
    return response.json()


def load_pages(topics: list[str] | None = None, user: str | None = None) -> list[dict]:
    params = {}
    if topics:
        params["topics"] = topics
    if user:
        params["user"] = user

    response = requests.get(f"{API_BASE_URL}/page", params=params, timeout=30)
    response.raise_for_status()
    return response.json()


st.set_page_config(page_title="Wiki", page_icon="📚", layout="wide")
st.title("📚 Wiki")

try:
    topics = load_topics()

    topic_selectionnes = st.multiselect(
        "Choisissez un thème :",
        options=[t["topic"] for t in topics],
    )

    user = st.text_input("Auteur (pseudoe)")

    pages = load_pages(topics=topic_selectionnes, user=user)
    st.dataframe(pages)

except Exception as e:
    st.error(f"Erreur: {e}")
