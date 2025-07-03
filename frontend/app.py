import streamlit as st
import requests
from streamlit_js_eval import streamlit_js_eval

if "msgs" not in st.session_state:
    st.session_state.msgs = []
if "slots" not in st.session_state:
    st.session_state.slots = {}
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
    
tz = streamlit_js_eval(js_expressions="Intl.DateTimeFormat().resolvedOptions().timeZone")
if tz and "timezone" not in st.session_state.slots:
    st.session_state.slots["timezone"] = tz

st.title("📅 AI Calendar Booking Assistant")

user = st.chat_input("Say something…")

if user:
    st.session_state.msgs.append({"role": "user", "content": user})
    with st.spinner("Thinking…"):
        try:
            response = requests.post(
                "https://chat-n-schedule.onrender.com/chat",
                json={
                    "prompt": user,
                    "slots": st.session_state.slots,
                },
            )
            
            data = response.json()
            bot = data.get("response", "Sorry, no response")

            # Update slot memory
            updated = data.get("updated_slots", {})
            st.session_state.slots.update(updated)

        except requests.exceptions.RequestException as e:
            bot = f"Request failed: {e}"
        except ValueError as e:
            bot = f"Invalid JSON response: {e}"

        st.session_state.msgs.append({"role": "assistant", "content": bot})

# Display chat history
for m in st.session_state.msgs:
    st.chat_message(m["role"]).write(m["content"])
