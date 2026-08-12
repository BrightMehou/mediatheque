import logging
import os

import requests
import streamlit as st

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")


@st.cache_data
def load_topics() -> list[dict]:
    response = requests.get(f"{API_BASE_URL}/topic", timeout=30)
    response.raise_for_status()
    return response.json()


def load_users() -> list[dict]:
    response = requests.get(f"{API_BASE_URL}/user", timeout=30)
    response.raise_for_status()
    return response.json()


@st.dialog("Ajouter un thème")
def create_topic() -> None:
    new_topic = st.text_input("Thème")
    if st.button("Ajouter"):
        response = requests.post(
            f"{API_BASE_URL}/topic/",
            json={"topic": new_topic},
            timeout=30,
        )
        response.raise_for_status()
        logger.info("Création OK: %s", response.json())
        load_topics.clear()
        st.rerun()


@st.dialog("Ajouter un utilisateur")
def create_user() -> None:
    new_first_name = st.text_input("Prénom")
    new_last_name = st.text_input("Nom")
    new_pseudo = st.text_input("pseudoe")
    new_email = st.text_input("Email")
    if st.button("Ajouter"):
        response = requests.post(
            f"{API_BASE_URL}/user/",
            json={
                "first_name": new_first_name,
                "last_name": new_last_name,
                "pseudo": new_pseudo,
                "email": new_email,
            },
            timeout=30,
        )
        response.raise_for_status()
        logger.info("Création OK: %s", response.json())
        load_users.clear()
        st.rerun()


st.set_page_config(page_title="Wiki - Admin", page_icon="⚙️", layout="wide")
st.title("⚙️ Administration du Wiki")

topic, user = st.tabs(["Thèmes", "Utilisateurs"])
with topic:
    st.subheader("Gestion des thèmes")
    try:
        if st.button("Ajouter un thème"):
            create_topic()

        topics = load_topics()
        event = st.dataframe(
            topics,
            on_select="rerun",
            selection_mode="single-row",
            column_order=("topic",),
        )

        row = event.selection.rows
        if row:
            selected_index = row[0]
            record = topics[selected_index]

            with st.form("Modifier le thème"):
                new_topic = st.text_input("Thème", value=record["topic"])
                submitted = st.form_submit_button("Modifier")

                if submitted:
                    with st.spinner("Modification en cours..."):
                        response = requests.put(
                            f"{API_BASE_URL}/topic/{record['id']}",
                            json={"topic": new_topic},
                            timeout=30,
                        )
                        response.raise_for_status()
                        logger.info("Modification du thème %s réussie", record["id"])
                        load_topics.clear()
                        st.rerun()

    except Exception as e:
        logger.exception("Erreur: %s")
        st.error(f"Erreur: {e}")

with user:
    st.subheader("Gestion des utilisateurs")
    try:
        if st.button("Ajouter un utilisateur"):
            create_user()

        users = load_users()
        event = st.dataframe(
            users,
            on_select="rerun",
            selection_mode="single-row",
            column_order=("first_name", "last_name", "pseudo", "email"),
        )

        row = event.selection.rows
        if row:
            selected_index = row[0]
            record = users[selected_index]

            with st.form("Modifier l'utilisateur"):
                new_first_name = st.text_input("Prénom", value=record["first_name"])
                new_last_name = st.text_input("Nom", value=record["last_name"])
                new_pseudo = st.text_input("pseudoe", value=record["pseudo"])
                new_email = st.text_input("Email", value=record["email"])
                submitted = st.form_submit_button("Modifier")

                if submitted:
                    with st.spinner("Modification en cours..."):
                        response = requests.put(
                            f"{API_BASE_URL}/user/{record['id']}",
                            json={
                                "first_name": new_first_name,
                                "last_name": new_last_name,
                                "pseudo": new_pseudo,
                                "email": new_email,
                            },
                            timeout=30,
                        )
                        response.raise_for_status()
                        logger.info(
                            "Modification de l'utilisateur %s réussie", record["id"]
                        )
                        st.rerun()
    except Exception as e:
        logger.exception("Erreur: %s")
        st.error(f"Erreur: {e}")
