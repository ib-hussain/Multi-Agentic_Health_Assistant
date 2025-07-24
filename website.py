import streamlit as st
import streamlit.components.v1 as components
from data import database_handler as db

st.set_page_config(layout="wide")

# Inject custom CSS
st.markdown("""
    <style>
        body {
            background: linear-gradient(to bottom, #98db2e, #749244);
        }
        .nav-bar {
            background-color: #171a1f;
            padding: 1rem;
            display: flex;
            justify-content: center;
        }
        .nav-bar a {
            color: white;
            margin: 0 1.5rem;
            text-decoration: none;
            font-weight: bold;
        }
        .nav-bar a:hover {
            color: #98db2e;
        }
    </style>
""", unsafe_allow_html=True)

# Session state to persist login
if "user_id" not in st.session_state:
    st.session_state.user_id = None
if "page" not in st.session_state:
    st.session_state.page = "Login"

# Top navigation bar (visible only after login)
def navbar():
    st.markdown("""
        <div class="nav-bar">
            <a href="#" onclick="window.location.reload();">Chatbot</a>
            <a href="#" onclick="window.location.href='?page=Profile';">Profile Management</a>
        </div>
    """, unsafe_allow_html=True)

# Login Page
def login_page():
    st.title("Login")
    name = st.text_input("Name")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        user_id = db.get_id(name, password)
        if user_id:
            st.session_state.user_id = user_id
            st.session_state.page = "Chatbot"
            st.experimental_rerun()
        else:
            st.error("Invalid credentials")

# Signup Page
def signup_page():
    st.title("Signup")
    name = st.text_input("Name")
    password = st.text_input("Password", type="password")
    age = st.number_input("Age", min_value=1.0)
    gender = st.selectbox("Gender", ['Female', 'Male'])
    height = st.number_input("Height (m)", value=1.70)
    weight = st.number_input("Weight (kg)", value=66.4)
    goal = st.text_input("Fitness Goal", value="Get into better shape")
    diet = st.selectbox("Dietary Preference", ['vegan', 'carnivore', 'both', 'balanced', 'vegetarian', 'pescatarian', 'any'])
    times = st.multiselect("Available Start Times (HH:MM)", ['07:00', '09:00', '12:00', '15:00', '18:00'])
    deadline = st.number_input("Deadline (days)", value=90)
    mh_notes = st.text_area("Mental Health Notes")
    conditions = st.text_area("Medical Conditions")

    if st.button("Signup"):
        db.user_registration(name, age, gender, height, weight, goal, diet, times, mh_notes, conditions, deadline, password)
        st.success("Registration complete. Please login.")
        st.session_state.page = "Login"
        st.experimental_rerun()

# Chatbot Page
def chatbot_page():
    navbar()
    st.title("Chatbot")
    st.info("Chatbot interface coming soon...")

# Profile Management Page
def profile_page():
    navbar()
    st.title("Profile Management")
    profile = db.get_user_profile_by_id(st.session_state.user_id)
    if not profile:
        st.error("User not found.")
        return

    st.subheader("Update Profile Info")
    with st.form("profile_form"):
        new_name = st.text_input("Name", value=profile["name"])
        new_age = st.number_input("Age", value=profile["age"])
        new_weight = st.number_input("Weight (kg)", value=profile["weight"])
        new_height = st.number_input("Height (m)", value=profile["height"])
        new_gender = st.selectbox("Gender", ['Female', 'Male'], index=0 if profile["gender"] == "Female" else 1)
        new_goal = st.text_area("Fitness Goal", value=profile["fitness_goal"])
        new_diet = st.selectbox("Dietary Preference", ['vegan', 'carnivore', 'both', 'balanced', 'vegetarian', 'pescatarian', 'any'], index=6)
        new_deadline = st.number_input("Deadline (days)", value=profile["time_deadline"])
        new_mh = st.text_area("Mental Health Notes", value=profile["mental_health_background"] or "")
        new_cond = st.text_area("Medical Conditions", value=profile["medical_conditions"] or "")
        submitted = st.form_submit_button("Update")
        if submitted:
            db.change_name(profile["name"], new_name)
            db.change_age(new_name, new_age)
            db.change_weight(new_name, new_weight)
            db.change_height(new_name, new_height)
            db.change_gender(new_name, True if new_gender == 'Female' else False)
            db.change_fitness_goal(new_name, new_goal)
            db.change_dietary_pref(new_name, new_diet)
            db.change_time_deadline(new_name, int(new_deadline))
            db.change_mental_health_notes(new_name, new_mh)
            db.change_medical_conditions(new_name, new_cond)
            st.success("Profile updated.")

# Routing Logic
page = st.query_params.get("page")

if page == "Profile" and st.session_state.user_id:
    profile_page()
elif st.session_state.page == "Signup":
    signup_page()
elif st.session_state.page == "Chatbot" and st.session_state.user_id:
    chatbot_page()
elif st.session_state.page == "Login":
    login_page()
else:
    st.session_state.page = "Login"
    st.experimental_rerun()
