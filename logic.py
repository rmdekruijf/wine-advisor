import pandas as pd
import bcrypt
from sqlalchemy import create_engine, Table, Column, String, MetaData, text
from openai import OpenAI

client = OpenAI()

def create_user_table(engine):
    meta = MetaData()
    users = Table(
        'users', meta,
        Column('username', String, primary_key=True),
        Column('password', String)
    )
    meta.create_all(engine)

def check_login(engine, username, password):
    with engine.connect() as conn:
        result = conn.execute(
            text("SELECT password FROM users WHERE username = :username"),
            {"username": username}
        ).fetchone()
        if result:
            return bcrypt.checkpw(password.encode(), result[0].encode())
        return False

def store_wines(engine, username, df):
    df.to_sql(f"{username}_wines", engine, if_exists="replace", index=False)

def load_user_wines(engine, username):
    try:
        return pd.read_sql_table(f"{username}_wines", engine)
    except Exception:
        return pd.DataFrame()

def log_question(engine, username, question, answer):
    table = f"{username}_history"
    df = pd.DataFrame([[question, answer]], columns=["question", "answer"])
    with engine.begin() as conn:
        df.to_sql(table, conn, if_exists="append", index=False)

def get_history(engine, username):
    try:
        return pd.read_sql_table(f"{username}_history", engine)
    except Exception:
        return pd.DataFrame()

def get_advice(question, df):
    wine_list = ""
    for _, row in df.iterrows():
        if pd.isna(row.iloc[0]):
            continue
        wine_list += (
            f"- {row.iloc[0]} van {row.iloc[1]} uit {row.iloc[2]} ({row.iloc[3]}), "
            f"druif: {row.iloc[4]}, jaar: {row.iloc[5]}, drinkvenster: {row.iloc[6]}. "
            f"Beschrijving: {row.iloc[7]}. Opengemaakt: {row.iloc[8]}, "
            f"Op voorraad: {row.iloc[9]}, Aankooplocatie: {row.iloc[10]}\n"
        )
    prompt = f"Wijncollectie:\n{wine_list}\n\nVraag: {question}\n\nAdvies:"
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content.strip()

def create_account(engine, username, password):
    with engine.begin() as conn:
        # Check if user exists
        result = conn.execute(
            text("SELECT * FROM users WHERE username = :u"),
            {"u": username}
        ).fetchone()
        if result:
            return False  # user already exists

        hashed_pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
        conn.execute(
            text("INSERT INTO users (username, password) VALUES (:u, :p)"),
            {"u": username, "p": hashed_pw}
        )
        return True

def add_vivino_links(df):
    def create_link(wine_name):
        if not wine_name or pd.isna(wine_name):
            return ""
        query = wine_name.replace(" ", "+")
        return f"https://www.vivino.com/search/wines?q={query}"
    
    df['Vivino Link'] = df.iloc[:, 0].apply(create_link)  # assuming first col is wine name
    return df
