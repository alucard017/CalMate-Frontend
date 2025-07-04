import streamlit as st
import requests
import re
from datetime import timedelta
from dateparser import parse

FASTAPI_API_URL = "http://backend:8000/book"

st.set_page_config(page_title="CalMate - Booking Assistant", layout="centered")
st.title("📅 CalMate – Smart Calendar Assistant")

# Sidebar
st.sidebar.title("ℹ️ About CalMate")
st.sidebar.markdown("""
**CalMate** is your friendly assistant to schedule Google Calendar meetings using natural language.

🔹 Just say things like:
- "Schedule a call tomorrow at 3 PM"
- "Book a meeting next Friday 10 AM"

Built with ❤️ using FastAPI, LangGraph, and Streamlit.\n\n
👨‍💻 Developed by Apurba
""")

# Optional user info inputs
st.subheader("👤 Who is booking this?")
name = st.text_input("Name", placeholder="e.g., Apurba")
email = st.text_input("Email", placeholder="e.g., user@example.com")

# Chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Previous chat messages
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).markdown(msg["content"])

# Input
user_input = st.chat_input("💬 When would you like to book a meeting?")

if user_input:
    st.chat_message("user").write(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})

    if not name or not email:
        reply = "⚠️ Please provide your name and email before booking."
        st.chat_message("assistant").write(reply)
        st.session_state.messages.append({"role": "assistant", "content": reply})
    else:
        with st.spinner("🔍 Checking availability and booking..."):
            try:
                response = requests.post(FASTAPI_API_URL, json={"user_input": user_input})

                if response.status_code == 200:
                    data = response.json()
                    reply = (
                        f"✅ **Booking confirmed!**\n\n"
                        f"🔗 [Click to view event details]({data['calendar_link']})\n\n"
                    )
                else:
                    reply = f"❌ Error: {response.json()['detail']}"

            except requests.exceptions.RequestException as e:
                reply = f"⚠️ Server error: {e}"

        st.chat_message("assistant").markdown(reply)
        st.session_state.messages.append({"role": "assistant", "content": reply})

