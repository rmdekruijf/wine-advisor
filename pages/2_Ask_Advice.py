import streamlit as st
from sqlalchemy import create_engine
from logic import load_user_wines, get_advice
import time

# ----------------------
# Setup
# ----------------------
engine = create_engine("sqlite:///data/user_data.db")

if "username" not in st.session_state:
    st.error("Please log in first!")
    st.stop()

username = st.session_state["username"]
wines_df = load_user_wines(engine, username)

st.title("🍷 Wine Advisor Chat")

# ----------------------
# Initialize session state
# ----------------------
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []

if "is_typing" not in st.session_state:
    st.session_state["is_typing"] = False

# ----------------------
# CSS for premium bubbles
# ----------------------
st.markdown("""
<style>
.chat-container {
    max-height: 600px;
    overflow-y: auto;
    padding: 10px;
    border-radius: 15px;
    background-color: #f5f5f7;
    width: 100%;
}
.user-bubble, .ai-bubble {
    padding: 12px;
    border-radius: 20px;
    margin: 5px 0;
    max-width: 70%;
    animation: fadeIn 0.3s ease-in-out;
}
.user-bubble {
    background: linear-gradient(135deg, #a8edea, #fed6e3);
    text-align: left;
}
.ai-bubble {
    background: linear-gradient(135deg, #fdfbfb, #ebedee);
    text-align: left;
    margin-left: auto;
}
.sender-label {
    font-weight: bold;
    margin-bottom: 4px;
}
.typing {
    font-style: italic;
    color: gray;
}
.dot {
    display: inline-block;
    margin: 0 2px;
    width: 6px;
    height: 6px;
    background-color: gray;
    border-radius: 50%;
    animation: bounce 0.6s infinite;
}
.dot:nth-child(1) { animation-delay: 0s; }
.dot:nth-child(2) { animation-delay: 0.2s; }
.dot:nth-child(3) { animation-delay: 0.4s; }

@keyframes bounce {
    0%, 80%, 100% { transform: scale(0); }
    40% { transform: scale(1); }
}

@keyframes fadeIn {
    from { opacity: 0; transform: translateY(10px);}
    to { opacity: 1; transform: translateY(0);}
}
</style>
""", unsafe_allow_html=True)


# ----------------------
# Chat input
# ----------------------
question = st.text_area(
    "Type your question here...",
    height=100,
    key="question_input",
    placeholder="Ask about food pairings, styles, vintages..."
)

def send_question():
    question_text = st.session_state["question_input"].strip()
    if question_text:
        st.session_state["question_input"] = ""  # clear input
        st.session_state["is_typing"] = True
        # Get advice
        advice = get_advice(question_text, wines_df)
        st.session_state["chat_history"].append({"user": question_text, "ai": advice})
        st.session_state["is_typing"] = False

st.button("Send", on_click=send_question)

# ----------------------
# Chat display
# ----------------------
def render_chat():
    st.markdown('<div class="chat-container" id="chat">', unsafe_allow_html=True)
    
    for entry in st.session_state["chat_history"]:
        if entry.get("user"):
            st.markdown(f'''
                <div class="sender-label">You</div>
                <div class="user-bubble">{entry["user"]}</div>
            ''', unsafe_allow_html=True)
        if entry.get("ai"):
            st.markdown(f'''
                <div class="sender-label" style="text-align:right;">Advisor</div>
                <div class="ai-bubble">{entry["ai"]}</div>
            ''', unsafe_allow_html=True)
    
    if st.session_state["is_typing"]:
        st.markdown('''
            <div class="sender-label" style="text-align:right;">Advisor</div>
            <div class="ai-bubble typing">
                Advisor is typing
                <span class="dot"></span><span class="dot"></span><span class="dot"></span>
            </div>
        ''', unsafe_allow_html=True)
        
    st.markdown('</div>', unsafe_allow_html=True)
    # Auto scroll
    st.markdown("""
    <script>
    var chatDiv = window.parent.document.querySelector('.chat-container');
    if(chatDiv){ chatDiv.scrollTop = chatDiv.scrollHeight; }
    </script>
    """, unsafe_allow_html=True)

# ----------------------
# Render chat only once
# ----------------------
render_chat()
