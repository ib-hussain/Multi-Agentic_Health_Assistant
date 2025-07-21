import streamlit as st
from data import database_handler as db
st.title("Virtual Health Assistant")

with st.form("user_form"):
    name = st.text_input("Name")
    age = st.number_input("Age", min_value=1, max_value=120, step=1)
    weight = st.number_input("Weight (kg)", min_value=1.0, max_value=500.0, step=0.1)
    submitted = st.form_submit_button("Add User")
    if submitted:
        db.user_registration(name=name, Age=age, Weight_kg=weight)
        st.success(f"User '{name}' added successfully!")

