import streamlit as st
import pandas as pd
import openai

# ----------------------------
# Page settings
# ----------------------------
st.set_page_config(page_title="🍷 Wijn Advies", layout="centered")
st.title("🍷 Wijn Advies Assistent")
st.markdown(
    "Upload je wijninventaris (Excel), stel een vraag, en ontvang een gepersonaliseerd wijnadvies."
)

# ----------------------------
# OpenAI client
# ----------------------------
client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# ----------------------------
# Upload Excel
# ----------------------------
uploaded_file = st.file_uploader("📄 Upload je wijn Excel-bestand", type="xlsx")

if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file, sheet_name="Wijn")
        st.success("✅ Bestand geladen. Hieronder zie je een preview van je wijninventaris:")
        st.dataframe(df)

        # ----------------------------
        # Ask question
        # ----------------------------
        vraag = st.text_input(
            "🗣️ Stel je vraag (bv: 'Wat past goed bij pasta?' of 'Ik ben moe maar wil één glas.')"
        )

        if st.button("Vraag advies"):
            if not vraag:
                st.warning("❗ Voer een vraag in voordat je advies opvraagt.")
            else:
                # ----------------------------
                # Build wine list text safely
                # ----------------------------
                wijnLijst = ""
                for index, row in df.iterrows():
                    if pd.isna(row.iloc[0]):  # stop at first empty wine name
                        break

                    # convert all columns to string
                    cols = [str(row.iloc[i]) if not pd.isna(row.iloc[i]) else "" for i in range(11)]

                    wijnLijst += (
                        f"- {cols[0]} van {cols[1]} uit {cols[2]} ({cols[3]}), druif: {cols[4]}, jaar: {cols[5]}, "
                        f"drinkvenster: {cols[6]}. Beschrijving: {cols[7]}. "
                        f"Opengemaakt: {cols[8]}, Op voorraad: {cols[9]}, Aankooplocatie: {cols[10]}\n"
                    )

                volledige_prompt = f"{vraag}\n\nHier is de lijst met beschikbare wijnen:\n{wijnLijst}"

                # ----------------------------
                # Call OpenAI GPT
                # ----------------------------
                with st.spinner("🍇 Wijnadvies wordt opgehaald..."):
                    response = client.chat.completions.create(
                        model="gpt-4o",
                        messages=[
                            {
                                "role": "system",
                                "content": "Je bent een sommelier AI. Je helpt mensen om de beste wijn uit hun collectie te kiezen op basis van hun vraag en voorkeuren."
                            },
                            {"role": "user", "content": volledige_prompt}
                        ]
                    )

                    antwoord = response.choices[0].message.content
                    st.success("✅ Advies ontvangen:")
                    st.markdown(antwoord)

    except Exception as e:
        st.error(f"❌ Fout bij het verwerken van het Excel-bestand: {e}")

else:
    st.info("📥 Upload een Excel-bestand met een werkblad 'Wijn'.")
