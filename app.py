import streamlit as st
import bcrypt
from sqlalchemy import create_engine
from logic import check_login, create_user_table, create_account
from datetime import datetime, timedelta

# SQLite setup
engine = create_engine("sqlite:///data/user_data.db")
create_user_table(engine)

st.set_page_config(page_title="Wine Advisor", layout="wide")

# --- Check for existing login session ---
if "username" in st.session_state and "login_time" in st.session_state:
    # If login is still valid (30 min)
    if datetime.now() - st.session_state["login_time"] < timedelta(minutes=30):
        st.switch_page("pages/1_My_Wines.py")
        st.stop()
    else:
        # Session expired
        st.session_state.clear()
        st.warning("⚠️ Je sessie is verlopen. Log opnieuw in.")

st.title("🍷 Wine Advisor - Login")
st.subheader("Log in op je account")

username = st.text_input("Gebruikersnaam")
password = st.text_input("Wachtwoord", type="password")

if st.button("Login"):
    if check_login(engine, username, password):
        st.session_state["username"] = username
        st.session_state["login_time"] = datetime.now()  # store login time
        st.success("✅ Ingelogd!")
        st.switch_page("pages/1_My_Wines.py")
    else:
        st.error("❌ Ongeldige gebruikersnaam of wachtwoord")

if st.button("Maak account aan"):
    if not username or not password:
        st.error("Vul zowel gebruikersnaam als wachtwoord in.")
    else:
        created = create_account(engine, username, password)
        if created:
            st.success("✅ Account aangemaakt! Log nu in.")
        else:
            st.error("❌ Gebruikersnaam bestaat al.")
