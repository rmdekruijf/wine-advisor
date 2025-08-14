import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
from logic import load_user_wines, store_wines

# Database connection
engine = create_engine("sqlite:///data/user_data.db")

if "username" not in st.session_state:
    st.warning("Log eerst in!")
    st.stop()

username = st.session_state["username"]

st.title("🍷 Mijn Wijnen")

# Your existing column names in Dutch
columns = [
    "Wijnnaam", "Producent", "Land", "Regio",
    "Druif", "Jaar", "Drinkvenster", "Korte omschrijving",
    "Geopend", "Op voorraad", "Aankooplocatie"
]

# Load wines from DB
wines_df = load_user_wines(engine, username)

# If empty, make new DataFrame with correct columns
if wines_df.empty:
    wines_df = pd.DataFrame(columns=columns)

# Add missing columns without duplicates
for col in columns:
    if col not in wines_df.columns:
        wines_df[col] = "" if col not in ["Geopend", "Op voorraad"] else False

# Keep only the defined columns (drop any extras)
wines_df = wines_df[columns]

# Convert booleans
wines_df["Geopend"] = wines_df["Geopend"].astype(bool)
wines_df["Op voorraad"] = wines_df["Op voorraad"].astype(bool)

# Editable table
st.markdown("**Beheer je wijncollectie**")
edited_df = st.data_editor(
    wines_df,
    num_rows="dynamic",
    use_container_width=True,
    column_config={
        "Geopend": st.column_config.CheckboxColumn("Geopend"),
        "Op voorraad": st.column_config.CheckboxColumn("Op voorraad")
    },
    key="wine_editor"
)

# Save button
if st.button("💾 Opslaan"):
    store_wines(engine, username, edited_df)
    st.success("✅ Wijnlijst opgeslagen!")
    st.rerun()

# CSV upload to replace list
st.markdown("---")
st.subheader("🔄 Vervang volledige wijnlijst")
replace_file = st.file_uploader("Upload CSV", type=["csv"])
if replace_file is not None:
    new_df = pd.read_csv(replace_file)
    for col in columns:
        if col not in new_df.columns:
            new_df[col] = "" if col not in ["Geopend", "Op voorraad"] else False
    new_df = new_df[columns]
    new_df["Geopend"] = new_df["Geopend"].astype(bool)
    new_df["Op voorraad"] = new_df["Op voorraad"].astype(bool)
    store_wines(engine, username, new_df)
    st.success("✅ Wijnlijst vervangen!")
    st.rerun()
    