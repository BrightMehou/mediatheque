import streamlit as st
from sqlalchemy import create_engine, text
import pandas as pd

DB_URL = "postgresql://postgres:postgres@localhost:5432/postgres"

@st.cache_resource 
def get_engine():
    return create_engine(DB_URL)

def load_genres():
    engine = get_engine()
    query = "SELECT id, genre FROM livre_genre ORDER BY genre;"
    
    with engine.connect() as connection:
        df = pd.read_sql(text(query), connection)
    return df

st.title("📚 Gestion de Bibliothèque")

try:
    df_genres = load_genres()

    genre_selectionne = st.selectbox(
        "Choisissez un genre littéraire :",
        options=df_genres['id'].tolist(),
        format_func=lambda x: df_genres[df_genres['id'] == x]['genre'].values[0]
    )

    st.write(f"Vous avez sélectionné l'ID : **{genre_selectionne}**")

except Exception as e:
    st.error(f"Erreur de connexion à la base de données : {e}")