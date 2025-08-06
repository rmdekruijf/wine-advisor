import streamlit as st
import pandas as pd
import openai
import os

# --- Streamlit UI instellingen ---
st.set_page_config(page_title="Wine Advisor", page_icon="🍷", layout="wide")
st.title("🍷 Wine Advisor")
st.markdown("Vraag advies over welke wijn je het beste kunt drinken bij je maaltijd, humeur of gelegenheid.")

# --- OpenAI API key via Streamlit secrets ---
if "OPENAI_API_KEY" not in st.secrets:
    st.error("❌ OpenAI API key ontbreekt. Voeg deze toe in `.streamlit/secrets.toml`")
    st.stop()
else:
    openai.api_key = st.secrets["OPENAI_API_KEY"]

# --- Load wine data ---
@st.cache_data
def load_wines(uploaded_file=None):
    if uploaded_file is not None:
        df = pd.read_excel(uploaded_file)
        return df
    elif os.path.exists("wijnen.xlsx"):
        df = pd.read_excel("wijnen.xlsx")
        return df
    else:
        return pd.DataFrame()  # leeg dataframe als er geen bestand is

# --- Columns layout ---
col1, col2 = st.columns([1, 2])  # linker 1/3, rechter 2/3

# --- Linkerkolom: Upload + Prompt ---
with col1:
    st.header("Upload & Vraag")
    
    # Upload Excel
    if os.path.exists("wijnen.xlsx"):
        uploaded_file = None
        df = load_wines()
        st.success("✅ Bestand 'wijnen.xlsx' geladen.")
    else:
        uploaded_file = st.file_uploader("Upload je wijnen.xlsx bestand", type=["xlsx"])
        if uploaded_file is not None:
            df = load_wines(uploaded_file)
            st.success("✅ Bestand geüpload en geladen.")
        else:
            df = pd.DataFrame()
    
    # Prompt input
    if not df.empty:
        prompt = st.text_area(
            "Typ hier je vraag aan de AI",
            placeholder="Bijvoorbeeld: 'Welke wijn past bij stoofvlees?' of 'Ik heb een hangover, welke wijn kan ik nemen?'",
            height=100
        )
        st.info("Typ je vraag en klik op de knop rechts onder om advies te krijgen.")

# --- Rechterkolom: Tabel + AI advies ---
with col2:
    st.header("Mijn wijnen")
    if not df.empty:
        st.dataframe(df)
    else:
        st.info("Upload eerst je Excel-bestand in de linkerkolom om je wijnen te zien.")
    
    # AI advies
    if not df.empty and 'prompt' in locals() and prompt.strip() != "":
        if st.button("Vraag advies aan AI"):
            # Maak lijst van wijnen
            wijnLijst = ""
            for _, row in df.iterrows():
                if pd.isna(row.iloc[0]):
                    continue
                wijnLijst += (
                    f"- {row.iloc[0]} van {row.iloc[1]} uit {row.iloc[2]} ({row.iloc[3]}), druif: {row.iloc[4]}, "
                    f"jaar: {row.iloc[5]}, drinkvenster: {row.iloc[6]}. Beschrijving: {row.iloc[7]}. "
                    f"Opengemaakt: {row.iloc[8]}, Op voorraad: {row.iloc[9]}, Aankooplocatie: {row.iloc[10]}\n"
                )

            # Combineer prompt met wijnlijst
            volledigePrompt = f"{prompt}\n\nHier is de lijst met beschikbare wijnen:\n{wijnLijst}"

            # Verstuur naar OpenAI GPT-4o-mini
            try:
                with st.spinner("💬 AI is aan het nadenken..."):
                    response = openai.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[{"role": "user", "content": volledigePrompt}]
                    )
                    advies = response.choices[0].message.content
                    st.success("✅ Advies ontvangen!")
                    # Mooi jasje
                    st.markdown("### AI Advies")
                    st.markdown(f"<div style='border:1px solid #ccc; padding:15px; border-radius:8px; background:#f9f9f9;'>{advies}</div>", unsafe_allow_html=True)
            except Exception as e:
                st.error(f"❌ Er ging iets mis bij het ophalen van het advies: {e}")
