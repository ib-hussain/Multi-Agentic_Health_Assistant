import streamlit as st
from data.database_handler import (
    log_message,  # function to save chat history
    get_user_profile_by_id
)
from temp.audio import transcribe_audio as transcript
from agent_dispatcher import route_to_agent  # we'll implement this next

st.set_page_config(page_title="Virtual Health Assistant Chat", layout="wide")

st.title("🗨️ Virtual Health Assistant Chatbot")

# Sidebar: user session
user_id = st.session_state.get("user_id")
if not user_id:
    st.warning("Please log in to use the chatbot.")
    st.stop()

# Chat history container
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

chat_col, input_col = st.columns([4,1])
with chat_col:
    for entry in st.session_state.chat_history:
        if entry["sender"] == "user":
            st.markdown(f"**You:** {entry['text']}")
        else:
            st.markdown(f"**Bot:** {entry['text']}"    )

with input_col:
    st.markdown("---")
    # Text input
    text_input = st.text_area("Your message:", height=100)
    # Audio upload
    audio_file = st.file_uploader("Or upload audio (WAV/MP3):", type=["wav", "mp3"])
    # Image upload (if needed later)
    image_file = st.file_uploader("Or upload image:", type=["png", "jpg", "jpeg"])
    
    if st.button("Send"):
        if audio_file is not None:
            user_text = transcribe_audio(audio_file)
        else:
            user_text = text_input.strip()

        if not user_text:
            st.error("Please enter text or upload audio.")
        else:
            # Log user message
            st.session_state.chat_history.append({"sender": "user", "text": user_text})
            log_message(user_id, user_text, sender="user")

            # Route to the correct agent
            response = route_to_agent(user_id, user_text, image_file)

            # Log and display bot response
            st.session_state.chat_history.append({"sender": "bot", "text": response})
            log_message(user_id, response, sender="bot")
            
            # Clear input
            st.experimental_rerun()
