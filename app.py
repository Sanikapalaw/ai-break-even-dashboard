import streamlit as st
import requests

st.set_page_config(page_title="SCM AI Assistant", page_icon="🚚")

st.title("🚚 SCM AI Assistant")

# -------- API KEY --------
api_key = st.secrets.get("GEMINI_API_KEY", "")

if not api_key:
    st.error("API Key Missing")
    st.stop()

url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"

# -------- CHAT MEMORY --------
if "chat_history" not in st.session_state:
    st.session_state.chat_history = ""

if "messages" not in st.session_state:
    st.session_state.messages = []

# -------- SHOW CHAT --------
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# -------- GEMINI FUNCTION --------
def ask_gemini(question):

    # build prompt like CFO project
    prompt = f"""
    You are a Supply Chain Management assistant.

    Previous Conversation:
    {st.session_state.chat_history}

    User Question:
    {question}
    """

    res = requests.post(
        url,
        json={"contents":[{"parts":[{"text":prompt}]}]}
    )

    data = res.json()

    answer = data["candidates"][0]["content"]["parts"][0]["text"]

    # save history
    st.session_state.chat_history += f"\nUser: {question}\nAssistant: {answer}"

    return answer


# -------- USER INPUT --------
user_input = st.chat_input("Ask SCM question...")

if user_input:
    st.session_state.messages.append(
        {"role":"user","content":user_input}
    )

    with st.chat_message("user"):
        st.write(user_input)

    reply = ask_gemini(user_input)

    st.session_state.messages.append(
        {"role":"assistant","content":reply}
    )

    with st.chat_message("assistant"):
        st.write(reply)


# -------- SUGGESTED QUESTIONS --------
st.divider()
st.subheader("Suggested Questions")

suggestions = [
    "What causes delivery delays?",
    "How to reduce logistics cost?",
    "What are SCM KPIs?",
    "Explain demand forecasting"
]

cols = st.columns(2)

for i, q in enumerate(suggestions):
    if cols[i % 2].button(q):

        st.session_state.messages.append(
            {"role":"user","content":q}
        )

        with st.chat_message("user"):
            st.write(q)

        reply = ask_gemini(q)

        st.session_state.messages.append(
            {"role":"assistant","content":reply}
        )

        with st.chat_message("assistant"):
            st.write(reply)
