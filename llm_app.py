import streamlit as st
import requests

FASTAPI_API_URL = "https://calmate-backend.onrender.com"  

st.set_page_config(page_title="CalMate – AI Calendar Assistant", layout="centered")
st.title("📅 CalMate – AI Calendar Assistant")

# Sidebar
st.sidebar.title("ℹ️ About CalMate")
st.sidebar.markdown("""
**CalMate** is your friendly assistant to schedule Google Calendar meetings using natural language.

✅ Book using plain English  
📅 Find open slots  
🤖 Friendly conversation with smart LLM  
🔗 Get Google Calendar links directly 

Built with ❤️ using FastAPI, LangGraph, and Streamlit.\n\n
👨‍💻 Developed by Apurba
""")

# Chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).markdown(msg["content"])

# User input
user_input = st.chat_input("💬 Ask anything like: 'Book a 30 min meeting tomorrow at 2 PM'")

if user_input:
    st.chat_message("user").markdown(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})

    # /chat endpoint
    with st.spinner("🤖 Thinking..."):
        try:
            response = requests.post(f"{FASTAPI_API_URL}/chat", json={"messages": st.session_state.messages})
            response.raise_for_status()
            data = response.json()

            # If tool call occurred
            if "tool_results" in data:
                reply = ""
                for tool in data["tool_results"]:
                    func = tool["tool"]
                    result = tool["result"]

                    if func == "findOpenSlots":
                        slots = result.get("open_slots", [])
                        if not slots:
                            reply += "❌ No free slots found.\n"
                        else:
                            reply += "🕒 **Available slots:**\n\n"
                            for slot in slots:
                                reply += f"• {slot['start_time']} → {slot['end_time']}\n"

                    elif func == "checkAvailability":
                        reply += "✅ Slot is available!\n" if result.get("available") else "❌ That slot is already booked.\n"

                    elif func == "bookEvent":
                        link = result.get("calendar_link")
                        if link:
                            reply += f"✅ **Meeting booked!** [📅 View on Google Calendar]({link})\n"
                        else:
                            reply += "❌ Booking failed. Try again.\n"

                    else:
                        reply += f"⚠️ Unknown tool: {func}\n"

            else:
                # Just a regular reply
                reply = data.get("response", "🤖 Hmm, I didn’t quite get that.")

        except requests.exceptions.RequestException as e:
            reply = f"❌ API Error: {e}"

       
        st.chat_message("assistant").markdown(reply)
        st.session_state.messages.append({"role": "assistant", "content": reply})
