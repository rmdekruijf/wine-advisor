import streamlit as st
import pandas as pd
import openai

# Set page config
st.set_page_config(page_title="Wine Advisor", page_icon="🍷", layout="centered")

# Load secrets
openai.api_key = st.secrets["OPENAI_API_KEY"]

# Title and intro
st.title("🍷 Wine Advisor")
st.markdown(
    "Ask for a wine recommendation based on your meal, mood, or occasion. "
    "We'll check your personal wine collection and give you the best match!"
)

# Question input
prompt = st.text_input(
    "What would you like advice on?",
    placeholder="e.g. I'm eating spicy pasta, what should I drink?",
    help="Ask any question like: 'What's a good wine for sushi?' or 'What to drink when hungover?'"
)

# Load wine list
@st.cache_data
def load_wines():
    df = pd.read_excel("wijnen.xlsx")
    df = df.fillna("")  # avoid NaN issues
    return df

df = load_wines()

# Format wine list into text
def format_wines(df):
    wine_list = ""
    for _, row in df.iterrows():
        if pd.isna(row.iloc[0]) or row.iloc[0] == "":
            continue
        wine_list += (
            f"- {str(row.iloc[0])} van {str(row.iloc[1])} uit {str(row.iloc[2])} ({str(row.iloc[3])}), "
            f"druif: {str(row.iloc[4])}, jaar: {str(row.iloc[5])}, "
            f"drinkvenster: {str(row.iloc[6])}. Beschrijving: {str(row.iloc[7])}. "
            f"Opengemaakt: {str(row.iloc[8])}, Op voorraad: {str(row.iloc[9])}, "
            f"Aankooplocatie: {str(row.iloc[10])}\n"
        )
    return wine_list

# Button to get advice
if prompt:
    with st.spinner("Thinking... 🍇"):
        wijnlijst = format_wines(df)
        full_prompt = (
            f"{prompt}\n\nHier is de lijst met beschikbare wijnen:\n{wijnlijst}"
        )

        try:
            response = openai.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": full_prompt}],
                temperature=0.7
            )
            antwoord = response.choices[0].message.content
            st.markdown("### 🍷 AI Wine Recommendation")
            st.success(antwoord)
        except Exception as e:
            st.error(f"Something went wrong: {e}")
