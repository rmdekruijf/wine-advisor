# pages/4_Ask_Advice.py
import streamlit as st
from sqlalchemy import create_engine
from logic import load_user_wines, get_advice, log_question

engine = create_engine("sqlite:///data/user_data.db")

if "username" not in st.session_state:
    st.error("Je bent niet ingelogd.")
    st.stop()

username = st.session_state["username"]

st.title("🍷 Vraag advies")

# Load wines silently just to pass into the advice logic
wines_df = load_user_wines(engine, username)

if wines_df.empty:
    st.warning("Je hebt nog geen wijnen toegevoegd.")
    st.stop()

# Bigger text box for the question
question = st.text_area("Vraag me iets over je wijncollectie..", height=150)

# Get advice with a loading spinner
if st.button("💡 Vraag advies", use_container_width=True):
    if not question.strip():
        st.warning("Stel een vraag!")
    else:
        with st.spinner("Nadenken... 🍇"):
            advice = get_advice(question, wines_df)
            log_question(engine, username, question, advice)

        st.markdown("### Advies")
        st.write(advice)
