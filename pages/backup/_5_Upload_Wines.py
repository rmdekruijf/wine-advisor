import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
from logic import store_wines, load_user_wines

st.set_page_config(page_title="Upload Wijnen", layout="wide")
st.title("📤 Upload je wijncollectie")

if "username" not in st.session_state:
    st.warning("Log eerst in via de hoofdpagina.")
    st.stop()

engine = create_engine("sqlite:///data/user_data.db")

st.markdown("### Upload je Excel-bestand met wijnen (bijv. `wijnen.xlsx`)")

uploaded_file = st.file_uploader("Kies je Excel-bestand", type=["xlsx"])

if uploaded_file is not None:
    try:
        df = pd.read_excel(uploaded_file)
        st.session_state["uploaded_df"] = df

        # Preview
        st.success("Voorbeeld van geüploade wijnen:")
        st.dataframe(df.head(), use_container_width=True)

        if st.button("✅ Wijnen opslaan"):
            store_wines(engine, st.session_state["username"], df)
            st.success("Wijnen succesvol opgeslagen!")
    except Exception as e:
        st.error(f"Fout bij het inlezen van het bestand: {e}")

# Optional: show current wines
if st.checkbox("Toon eerder opgeslagen wijnen"):
    saved_df = load_user_wines(engine, st.session_state["username"])
    if not saved_df.empty:
        st.markdown("### Eerder opgeslagen wijnen")
        st.dataframe(saved_df, use_container_width=True)
    else:
        st.info("Nog geen wijnen opgeslagen.")
