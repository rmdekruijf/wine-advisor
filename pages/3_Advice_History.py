import streamlit as st
from sqlalchemy import create_engine
import pandas as pd
from logic import get_history

# DB setup
engine = create_engine("sqlite:///data/user_data.db")

st.title("🧠 Mijn Adviezen")

if "username" not in st.session_state:
    st.warning("Log eerst in!")
    st.stop()

username = st.session_state["username"]

# Load history
history = get_history(engine, username)

if history.empty:
    st.info("Je hebt nog geen vragen gesteld.")
else:
    st.write("Klik op een vraag om het advies te bekijken of te verwijderen.")
    for idx, row in history.iterrows():
        col1, col2 = st.columns([8, 1])
        with col1:
            with st.expander(f"❓ {row['question']}"):
                st.markdown(f"**Antwoord:** {row['answer']}")
        with col2:
            if st.button("🗑️", key=f"delete_{idx}"):
                with engine.begin() as conn:
                    conn.execute(
                        f"DELETE FROM {username}_history WHERE question = :q AND answer = :a",
                        {"q": row['question'], "a": row['answer']}
                    )
                st.success("Advies verwijderd.")
                st.experimental_rerun()
