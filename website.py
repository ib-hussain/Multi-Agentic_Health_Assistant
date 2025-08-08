import streamlit as st
import os
from pathlib import Path
import tempfile
from data.database_postgres import (
    get_id, user_registration, 
    get_user_profile_by_id, change_name, insert_daily_stats_entry, get_daily_stats_by_id, 
    change_everything
                                    )
from temp.audio import transcribe_audio as transcript
from chatbots.diet import get_image_description as diet

debug = st.secrets["DEBUGGING_MODE"]
NULLstring =str(st.secrets["NULL_STRING"])

st.set_page_config(
    page_title="Virtual Health Assistant", 
    layout="wide",
    initial_sidebar_state="collapsed"
)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Manrope:wght@300;400;600&family=Anaheim&display=swap');   
    .stApp {
        background: radial-gradient(
        circle at 20% 20%,
        rgba(255, 212, 196, 1) 0%, rgba(255, 237, 188, 1) 30%, rgba(236, 217, 255, 1) 55%, rgba(202, 224, 255, 1) 80% );
    background-blend-mode: screen; background-size: cover;
        /*
        background: radial-gradient( circle at 20% 20%, rgba(255, 212, 196, 1) 0%,    /* peach/coral */ rgba(255, 237, 188, 1) 30%,   /* pale yellow */ rgba(236, 217, 255, 1) 55%,   /* lavender purple */ rgba(202, 224, 255, 1) 80%    /* pastel sky blue */ ), radial-gradient( circle at 80% 30%, rgba(240, 210, 255, 0.8) 0%,  /* soft violet */ transparent 70% ), radial-gradient( circle at 50% 80%, rgba(200, 230, 255, 0.8) 0%,  /* light blue glow */ transparent 70% ); background-blend-mode: screen; background-size: cover;    
        */
        font-family: 'Manrope', sans-serif;
    } 
    /* Hide Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    /* Custom navbar */
    .navbar-brand {
        background-color: transparent; 
        /*padding: 0px 20px;  Vertical and horizontal padding */
        margin: -1rem -1rem 1rem -1rem; /* Adjust margins */
        display: flex; /* Add this to enable align-items and justify-content */
        align-items: left;
        justify-content: left;
        border-radius: 14px; /* Rounded corners */
        color: #171a1f; /* Text color */
        font-family: 'Anaheim', sans-serif; /* Font family */
        font-size: 28px; /* Font size */
        font-weight: bolder; /* Bold text 
        text-decoration: none;*/ /* Remove underline 
            opacity: 0.81;*/
    }
    .navbar-logo {
        height: 36px; /* adjust size to match text */
        vertical-align: middle;
        margin-left: 5px; /* space between text and image */
    }
    /* Login/Signup containers */
    .auth-container {
        background-color: #171a1f;
        color: white;
        padding: 40px;
        border-radius: 10px;
        max-width: 500px;
        margin: 5% auto;
        box-shadow: 0 4px 20px rgba(0,0,0,0.3);}
    .auth-title {
        font-family: 'Anaheim', sans-serif;
        font-size: 32px;
        color: white;
        text-align: center;
        margin-bottom: 10px; }
    .auth-subtitle {
        font-size: 16px;
        color: white;
        text-align: center;
        margin-bottom: 30px;}
    /* Custom button styling */
    .stButton > button {
        background-color: #1d88cf !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 5px !important;
        padding: 10px 20px !important;
        font-weight: bold !important;
        font-family: 'Manrope', sans-serif !important;
        width: 100% !important;
        margin-top: 10px !important;
    }
    .stButton > button:hover {
        background-color: #174666!important;
        color: #ffffff !important;
    }
    /* Input styling */
    .stTextInput > div > div > input {
        background-color: white !important;
        color: black !important;
        border-radius: 5px !important;
        border: none !important;
        padding: 10px !important;
        font-family: 'Manrope', sans-serif !important;
    }
    .stSelectbox > div > div > select {
        background-color: white !important;
        color: black !important;
        border-radius: 5px !important;
        border: none !important;
        font-family: 'Manrope', sans-serif !important;
    }
    .stNumberInput > div > div > input {
        background-color: white !important;
        color: black !important;
        border-radius: 5px !important;
        border: none !important;
        font-family: 'Manrope', sans-serif !important;
    }
    .stTextArea > div > div > textarea {
        background-color: white !important;
        color: black !important;
        border-radius: 5px !important;
        border: none !important;
        font-family: 'Manrope', sans-serif !important;
    }
    /* Profile container */
    .profile-container {
        background-color: rgba(23, 26, 31, 0.9);
        color: white;
        padding: 30px;
        border-radius: 15px;
        margin: 20px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.3);
    }
    .profile-title {
        font-family: 'Anaheim', sans-serif;
        font-size: 28px;
        color: #98db2e;
        margin-bottom: 20px;
    }
    /* Stats cards */
    .stats-card {
        background-color: rgba(255, 255, 255, 0.1);
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
        border-left: 4px solid #98db2e;
    }
    
    .stats-value {
        font-size: 24px;
        font-weight: bold;
        color: #98db2e;
    }
    
    .stats-label {
        font-size: 14px;
        color: white;
        margin-top: 5px;
    }
    
    /* Footer links */
    .footer-link {
        color: #98db2e !important;
        text-decoration: none !important;
        font-size: 18px;
    }
    
    .footer-text {
        color: white;
        font-size: 16px;
        text-align: center;
        margin-top: 20px;
    }
    
    /* Chatbot container */
    .chatbot-container {
        background-color: rgba(23, 26, 31, 0.9);
        color: white;
        padding: 30px;
        border-radius: 15px;
        margin: 20px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.3);
        min-height: 400px;
    }
</style>
""", unsafe_allow_html=True)

# Session State Initialization
if "user_id" not in st.session_state:
    st.session_state.user_id = None
if "current_page" not in st.session_state:
    st.session_state.current_page = "login"
if "user_profile" not in st.session_state:
    st.session_state.user_profile = None
# Navigation Functions
def set_page(page_name):
    st.session_state.current_page = page_name
    st.rerun()
#perfect ----------------------------------------------------------------------------------------------------------------------------
def logout():
    st.session_state.user_id = None
    st.session_state.user_profile = None
    st.session_state.current_page = "login"
    st.rerun()
# Navbar for authenticated pages
def render_navbar():
    if st.session_state.user_id:
        current_page = st.session_state.current_page
        # Create active class for current page
        chatbot_class = "active" if current_page == "chatbot" else ""
        daily_class = "active" if current_page == "daily_progress" else ""
        profile_class = "active" if current_page == "profile" else ""
        st.markdown(f"""<div class="navbar-brand">
                            Virtual Health Assistant
                            <img src="https://raw.githubusercontent.com/ib-hussain/Cinemago/refs/heads/main/favicon.png" alt="Rose Logo" class="navbar-logo">
                        </div>""", unsafe_allow_html=True)
        # Navigation buttons (invisible but functional)
        col1, col2, col3, col4, col5,col6,col7, col8, col9  = st.columns([1,1,1,1,1,1,1,1,1])
        with col1:st.empty()  # Spacer
        with col2:st.empty()  # Spacer
        with col3:
            if st.button("Chatbot", key="nav_chatbot"):
                set_page("chatbot")
        with col4:
            st.empty()  # Spacer
        with col5:
            if st.button("Progress", key="nav_daily"):
                set_page("daily_progress")
        with col6:st.empty()  # Spacer
        with col7:
            if st.button("Profile", key="nav_profile"):
                set_page("profile")
        with col8:st.empty()  # Spacer
        with col9:
            if st.button("Logout", key="nav_logout"):
                logout()
        st.markdown("---")
# Login Page
def login_page():
    st.markdown('<h1 class="auth-title">Virtual Health Assistant🥀</h1>', unsafe_allow_html=True)
    st.markdown('<p class="auth-subtitle">Welcome back! Log in to continue your health journey</p>', unsafe_allow_html=True)
    
    with st.form("login_form", clear_on_submit=False):
        name = st.text_input("Full Name", placeholder="Enter your full name")
        password = st.text_input("Password", type="password", placeholder="Enter your password")
        
        col1, col2 = st.columns(2)
        with col1:
            login_submitted = st.form_submit_button("Log In")
        with col2:
            if st.form_submit_button("Sign Up"):
                set_page("signup")
        
        if login_submitted:
            if name and password:
                user_id = get_id(name, password)
                if user_id:
                    st.session_state.user_id = user_id
                    st.session_state.user_profile = get_user_profile_by_id(user_id)
                    st.success("Login successful!")
                    set_page("chatbot")
                else:
                    st.error("Invalid credentials. Please try again.")
            else:
                st.error("Please fill in all fields.")
    st.markdown('</div>', unsafe_allow_html=True)
# Signup Page
def signup_page():
    st.markdown('<h1 class="auth-title">Create Your Account</h1>', unsafe_allow_html=True)
    st.markdown('<p class="auth-subtitle">Join us and start your health journey!</p>', unsafe_allow_html=True)
    
    with st.form("signup_form", clear_on_submit=True):
        # Basic Information
        st.subheader("Basic Information")
        name = str(st.text_input("Full Name", placeholder="Enter your full name"))
        if debug: print("name entered:", name, "------------------------------------------------------------------------------------------")
        password = str(st.text_input("Password", type="password", placeholder="Create a password", max_chars=10))
        if debug: print("password entered:", password)
        age = float(st.number_input("Age", min_value=1.0, max_value=150.0, value=25.0, step=0.1))
        if debug: print("age entered:", age)

        col1, col2 = st.columns(2)
        with col1:
            gender = str(st.selectbox("Gender", ['Female', 'Male']))
            if debug: print("gender entered:", gender)
        with col2:
            height = float(st.number_input("Height (meters)", min_value=0.5, max_value=3.0, value=1.70, step=0.01))
            if debug: print("height entered:", height)

        weight = float(st.number_input("Weight (kg)", min_value=20.0, max_value=500.0, value=70.0, step=0.1))
        if debug: print("weight entered:", weight)

        # Fitness Information
        st.subheader("Fitness Goals")
        fitness_goal = str(st.text_area("Fitness Goal", value="Get into better shape", placeholder="Describe your fitness goals..."))
        if debug: print("fitness_goal entered:", fitness_goal)
        diet_pref = str(st.selectbox("Dietary Preference", 
                                ['any', 'vegan', 'vegetarian', 'pescatarian', 'carnivore', 'balanced', 'both']))
        if debug: print("diet_pref entered:", diet_pref)

        # Time and Schedule
        st.subheader("Schedule")
        time_deadline = st.number_input("Goal Deadline (days)", min_value=1, max_value=365, value=90)
        
        # Available times (simplified)
        available_times = st.multiselect("Preferred Workout Times", 
                                       ['06:00', '07:00', '08:00', '09:00', '10:00', '11:00', 
                                        '12:00', '13:00', '14:00', '15:00', '16:00', '17:00', 
                                        '18:00', '19:00', '20:00', '21:00'], max_selections=3)
        # Health Information
        st.subheader("Health Information")
        mental_health_notes = str(st.text_area("Mental Health Notes (Optional)", 
                                         placeholder="Any mental health conditions from past or present that you may have..."))
        if debug: print("mental_health_notes entered:", mental_health_notes)
        medical_conditions = str(st.text_area("Medical Conditions (Optional)", 
                                        placeholder="Any medical conditions you may have..."))
        if debug: print("medical_conditions entered:", medical_conditions)

        # Terms checkbox
        terms_agreed = st.checkbox("I agree with Terms & Conditions")
        if debug: print("terms_agreed:", terms_agreed)
        
        col1, col2 = st.columns(2)
        with col1:
            signup_submitted = st.form_submit_button("Sign Up")
        with col2:
            if st.form_submit_button("Login"):
                set_page("login")
        
        if signup_submitted:
            if not terms_agreed:
                st.error("Please agree to Terms & Conditions")
            elif not name or not password:
                st.error("Name and password are required")
            else:
                try:
                    user_registration(
                        name=name,
                        Age=age,
                        gender=gender,
                        height_m=height,
                        Weight_kg=weight,
                        fitness_goal=fitness_goal,
                        dietary_pref=diet_pref,
                        time_available=available_times[:3],  # Limit to 3 times
                        mental_health_notes=mental_health_notes if mental_health_notes else None,
                        medical_conditions=medical_conditions if medical_conditions else None,
                        time_deadline=time_deadline,
                        password=password
                    )
                    st.success("Account created successfully! Please log in.")
                    if debug:
                        print(f"User {name} registered successfully----------------------------------------------------------------------------")
                    st.balloons()
                    set_page("login")
                except Exception as e:
                    st.error(f"Registration failed: {str(e)}")
    
    st.markdown('</div>', unsafe_allow_html=True)
#perfect ----------------------------------------------------------------------------------------------------------------------------
# issues:
# we are fucked and this shit is full of issues 
# daily progress page doesnot work in any way whatsoever
# supabase genrates horsehit and doesnot make rows properly
# time functionality is a nightmare
# ui is very bad and very badly made      
# profile management page needs a change password and change timings functionality                          
# Chatbot Page (Home Page)
def chatbot_page():
    """
    Chatbot page with centered white chat card, text/image/audio inputs,
    proper file saving (temp/download.<ext>, temp/temp_audio.mp3), and diet() call.
    """
    render_navbar()
    if not st.session_state.user_profile:
        st.session_state.user_profile = get_user_profile_by_id(st.session_state.user_id)
    profile = st.session_state.user_profile
    # ---- Styles for centered chat card ----
    st.markdown(
        """
        <style>
        .chat-wrapper { display:flex; justify-content:center; }
        .chat-input-row { display:flex; gap:10px; flex-wrap:wrap; }
        .chat-hint { color:#666; font-size:13px; margin: 6px 2px 8px 2px; }
        .upload-row { display:flex; gap:12px; flex-wrap:wrap; margin-top:6px; }
        .send-row { display:flex; gap:10px; margin-top:10px; flex-wrap:wrap; }
        .pill { padding:8px 12px; border-radius:10px; background:#f6f7f8; border:1px solid #eee; font-size:13px; color:#333; }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # ---- Chat history state ----
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": f"Hi {profile['name']}. You can type, upload a food image, or upload a short mp3 audio. I'll analyze the meal and give nutrition insights."}
        ]

    # Render message history
    for m in st.session_state.messages:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])  # already markdown-friendly
    # ---- Inputs ----
    # A) Text input
    user_text = st.chat_input("Type a message or add a caption for your image…")

    # B) Uploaders (inline under the messages)
    col_u1, col_u2 = st.columns(2)
    with col_u1:
        img_file = st.file_uploader( "Upload a food image (png/jpg/jpeg/ico)", type=["png", "jpg", "jpeg", "ico"], key="diet_image_upl")
    with col_u2:
        audio_file = st.file_uploader( "Upload audio (mp3) to transcribe & send", type=["mp3"], key="diet_audio_upl" )
    # C) Action buttons
    c1, c2, c3 = st.columns([1,1,1])
    with c1:
        send_text = st.button("Send Text", use_container_width=True)
    with c2:
        analyze_image = st.button("Analyze Image", use_container_width=True)
    with c3:
        transcribe_audio_and_send = st.button("Transcribe & Send", use_container_width=True)

    # Helpers
    def _save_image_to_temp(upload) -> str | None:
        """Save uploaded image to temp/download.<ext> and return path."""
        if not upload:
            return None
        from pathlib import Path
        ext = Path(upload.name).suffix.lower()
        if ext not in {".png", ".jpg", ".jpeg", ".ico"}:
            st.error("Unsupported image type.")
            return None
        dest = f"temp/download{ext}"
        with open(dest, "wb") as f:
            f.write(upload.getbuffer())
        return dest
    def _append_and_render(role: str, content: str):
        st.session_state.messages.append({"role": role, "content": content})
        with st.chat_message(role):
            st.markdown(content)

    # ---- Handlers ----
    # 1) If the user typed text and clicked send
    if user_text and not send_text:
        # Streamlit's chat_input sends on Enter automatically; mimic a send button feel
        send_text = True
    if send_text and (user_text or "" ):
        _append_and_render("user", user_text or "")
        # For now, if no image attached, just acknowledge. You can wire mental-health/exercise later.
        _append_and_render(
            "assistant",
            "Got it. If you also upload a meal photo, I'll do a full nutrition analysis."
        )

    # 2) Image analysis path
    if analyze_image:
        if img_file is None:

            st.warning(f"Please upload an image first.")
        else:
            img_path = _save_image_to_temp(img_file)
            if img_path:
                # If there's a text caption in chat_input, echo it in the chat first
                if user_text:
                    _append_and_render("user", user_text)
                _append_and_render("user", "(Uploaded a meal photo)")
                st.image(img_file, caption="Your upload", use_column_width=True)
                # Call diet() with prompt + image path
                with st.chat_message("assistant"):
                    with st.spinner("Analyzing your meal…"):
                        try:
                            prompt = user_text or ""
                            res = diet(image_path=img_path, prompt=prompt, user_id=st.session_state.user_id)
                            if res.get("status") == "success":
                                st.markdown(res["description"])
                                st.session_state.messages.append({"role": "assistant", "content": res["description"]})
                            else:
                                msg = f"Error: {res.get('message','Unknown error')}"
                                st.error(msg)
                                st.session_state.messages.append({"role": "assistant", "content": msg})
                        except Exception as e:
                            msg = f"Image analysis failed: {e}"
                            st.error(msg)
                            st.session_state.messages.append({"role": "assistant", "content": msg})

    # 3) Audio transcription path -> auto send as user message, then respond
    if transcribe_audio_and_send:
        if audio_file is None:
            st.warning("Please upload an mp3 first.")
        else:
            # Save as temp/temp_audio.mp3
            audio_dest = "temp/temp_audio.mp3"
            with open(audio_dest, "wb") as f:
                f.write(audio_file.getbuffer())
            # Get transcript
            try:
                with st.spinner("Transcribing…"):
                    text = transcript("temp/")
                text = text.strip() if text else ""
            except Exception as e:
                text = ""
                st.error(f"Transcription failed: {e}")
            if text:
                # Display transcript as a user message and auto-send it
                _append_and_render("user", text)
                # If there is also an image uploaded, analyze with that transcript as caption
                if img_file is not None:
                    img_path = _save_image_to_temp(img_file)
                else:
                    img_path = None
                if img_path:
                    with st.chat_message("assistant"):
                        with st.spinner("Analyzing your meal…"):
                            try:
                                res = diet(image_path=img_path, prompt=text, user_id=st.session_state.user_id)
                                if res.get("status") == "success":
                                    st.markdown(res["description"])
                                    st.session_state.messages.append({"role": "assistant", "content": res["description"]})
                                else:
                                    msg = f"Error: {res.get('message','Unknown error')}"
                                    st.error(msg)
                                    st.session_state.messages.append({"role": "assistant", "content": msg})
                            except Exception as e:
                                msg = f"Image analysis failed: {e}"
                                st.error(msg)
                                st.session_state.messages.append({"role": "assistant", "content": msg})
                else:
                    _append_and_render(
                        "assistant",
                        "Transcript received. Upload a meal photo as well if you want a full nutrition breakdown."
                    )
    # Close the chat card
    st.markdown('</div></div>', unsafe_allow_html=True)

# Daily Progress Page (Combined viewing and logging)
def daily_progress_page():
    render_navbar()
    st.markdown('<h1 class="profile-title">Daily Progress</h1>', unsafe_allow_html=True)
    # Current Stats Display
    daily_stats = get_daily_stats_by_id(st.session_state.user_id)
    if daily_stats:
        st.subheader("Current Progress")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"""
            <div class="stats-card">
                <div class="stats-value">{daily_stats[1]}</div>
                <div class="stats-label">Last Update</div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div class="stats-card">
                <div class="stats-value">{daily_stats[2].title()}</div>
                <div class="stats-label">Activity Level</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="stats-card">
                <div class="stats-value">{daily_stats[5]}</div>
                <div class="stats-label">Days Completed</div>
            </div>
            """, unsafe_allow_html=True)
            
            progress_emoji = "📈" if daily_stats[4] == "positive" else "📉" if daily_stats[4] == "negative" else "➡️"
            st.markdown(f"""
            <div class="stats-card">
                <div class="stats-value">{progress_emoji} {daily_stats[4].title()}</div>
                <div class="stats-label">Progress Feeling</div>
            </div>
            """, unsafe_allow_html=True)
        
        if daily_stats[6]:
            st.markdown(f"""
            <div class="stats-card">
                <div class="stats-value">{daily_stats[6]}</div>
                <div class="stats-label">Days Remaining</div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No daily stats recorded yet. Log your first entry below!")
    
    # Daily Stats Logging
    st.subheader("Log Today's Progress")
    col1, col2 = st.columns(2)
    with col1:
        activity_level = st.selectbox("Activity Level Today", 
                                    ['not active', 'lightly active', 'active', 'very active'])
    with col2:
        progress_condition = st.selectbox("How do you feel about your progress?", 
                                        ['positive', 'neutral', 'negative'])
    if st.button("Log Today's Stats"):
        try:
            insert_daily_stats_entry(st.session_state.user_id, activity_level, progress_condition)
            st.success("Daily stats logged successfully!")
            st.rerun()
        except Exception as e:
            st.error(f"Error logging stats: {str(e)}")
    
    st.markdown('</div>', unsafe_allow_html=True)
# Profile Management Page
def profile_page():
    render_navbar()
    if not st.session_state.user_profile:
        st.session_state.user_profile = get_user_profile_by_id(st.session_state.user_id)
    profile = st.session_state.user_profile
    st.markdown('<h1 class="profile-title">Profile Management</h1>', unsafe_allow_html=True)
    # Display current profile info
    st.subheader("Current Profile Information")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
        <div class="stats-card">
            <div class="stats-value">{profile["name"]}</div>
            <div class="stats-label">Name</div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown(f"""
        <div class="stats-card">
            <div class="stats-value">{profile["age"]} years</div>
            <div class="stats-label">Age</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="stats-card">
            <div class="stats-value">{profile["weight"]} kg</div>
            <div class="stats-label">Weight</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="stats-card">
            <div class="stats-value">{profile["height"]} m</div>
            <div class="stats-label">Height</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class="stats-card">
            <div class="stats-value">{profile["gender"]}</div>
            <div class="stats-label">Gender</div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown(f"""
        <div class="stats-card">
            <div class="stats-value">{profile["diet_pref"].title()}</div>
            <div class="stats-label">Diet Preference</div>
        </div>
        """, unsafe_allow_html=True)
    st.markdown("---")
    # Edit profile form
    st.subheader("Edit Profile")
    with st.form("profile_form"):
        st.subheader("Basic Information")

        col1, col2 = st.columns(2)
        with col1:
            new_name = st.text_input("Name", value=profile["name"])
            new_age = st.number_input("Age", value=float(profile["age"]), min_value=1.0, step=0.1)
            new_weight = st.number_input("Weight (kg)", value=float(profile["weight"]), min_value=20.0, step=0.1)
        with col2:
            new_height = st.number_input("Height (m)", value=float(profile["height"]), min_value=0.5, step=0.01)
            new_gender = st.selectbox("Gender", ['Female', 'Male'], 
                                    index=0 if profile["gender"] == "Female" else 1)
            new_deadline = st.number_input("Goal Deadline (days)", value=profile["time_deadline"], min_value=1)
        st.subheader("Fitness & Diet")
        new_goal = st.text_area("Fitness Goal", value=profile["fitness_goal"] or "")
        new_diet = st.selectbox("Dietary Preference", 
                              ['any', 'vegan', 'vegetarian', 'pescatarian', 'carnivore', 'balanced', 'both'],
                              index=['any', 'vegan', 'vegetarian', 'pescatarian', 'carnivore', 'balanced', 'both'].index(profile["diet_pref"]))
        st.subheader("Health Information")
        new_mh = st.text_area("Mental Health Notes", value=profile["mental_health_background"] or "")
        new_cond = st.text_area("Medical Conditions", value=profile["medical_conditions"] or "")
        submitted = st.form_submit_button("Update Profile")
        if submitted:
            try:
                # Update all fields
                if new_name != profile["name"]:
                    change_name(profile["name"], new_name)
                    profile["name"] = new_name  # Update local profile
                change_everything(
                    profile["name"], 
                    new_age,
                    new_gender == 'Female',
                    new_weight,
                    new_height,
                    new_diet,
                    int(new_deadline),
                    new_goal,
                    new_mh,
                    new_cond
                )
                st.success("Profile updated successfully!")
                # Refresh profile data
                st.session_state.user_profile = get_user_profile_by_id(st.session_state.user_id)
                st.rerun()
            except Exception as e:
                st.error(f"Error updating profile: {str(e)}")
    st.markdown('</div>', unsafe_allow_html=True)
# Main App Router
def main():
    # Route to appropriate page based on authentication and current page
    if st.session_state.user_id is None:
        if st.session_state.current_page == "signup":
            signup_page()
        else:
            login_page()
    else:
        if st.session_state.current_page == "profile":
            profile_page()
        elif st.session_state.current_page == "daily_progress":
            daily_progress_page()
        else:
            chatbot_page()  # Default to chatbot (home page)
if __name__ == "__main__":
    main()