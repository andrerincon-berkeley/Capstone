import streamlit as st
import pandas as pd
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt

# Load and display logo
logo = Image.open("logo.png")
st.sidebar.image(logo, width=250)

# Dummy data
users = {
    "1234": {"name": "Miles Dyson", "role": "student", "school": "Lincoln High School", "grade": "12"},
    "111": {"name": "Ms. Smith", "role": "educator", "school": "Lincoln High School", "position": "College Counselor"}
}

university_recommendations = {
    "Foundation": [
        {"University": "Arizona State University", "Population": "74,795", "Website": "https://www.asu.edu"},
        {"University": "Ohio State University", "Population": "59,837", "Website": "https://www.osu.edu"},
        {"University": "Penn State University", "Population": "46,606", "Website": "https://www.psu.edu"},
    ],
    "Challenge": [
        {"University": "University of Illinois Urbana-Champaign", "Population": "52,331", "Website": "https://www.illinois.edu"},
        {"University": "University of Wisconsin-Madison", "Population": "47,932", "Website": "https://www.wisc.edu"},
        {"University": "University of Florida", "Population": "55,211", "Website": "https://www.ufl.edu"},
    ],
    "Aspire": [
        {"University": "University of California, Berkeley", "Population": "42,327", "Website": "https://www.berkeley.edu"},
        {"University": "University of Michigan", "Population": "48,090", "Website": "https://www.umich.edu"},
        {"University": "University of North Carolina", "Population": "30,092", "Website": "https://www.unc.edu"},
    ],
}

# Initialize session states
for key in ["logged_in_user", "searched_student"]:
    if key not in st.session_state:
        st.session_state[key] = None

# Sidebar Login Form
st.sidebar.title("Login")
with st.sidebar.form("login_form"):
    user_type = st.radio("User Type", ["Student", "Educator"])
    user_id = st.text_input("User ID")
    submitted = st.form_submit_button("Login")

    if submitted:
        if user_id in users and users[user_id]["role"] == user_type.lower():
            st.session_state.logged_in_user = users[user_id]
        else:
            st.sidebar.error("Invalid credentials.")

# Logout
if st.session_state.logged_in_user:
    if st.sidebar.button("Logout"):
        st.session_state.clear()
        st.experimental_rerun()

# Main App
if st.session_state.logged_in_user:
    user = st.session_state.logged_in_user
    st.write(f"### Welcome, {user['name']} 👋")

    if user["role"] == "student":
        st.info(f"**School:** {user['school']} | **Grade:** {user['grade']}")
        st.write("Discover universities tailored to your academic profile.")

        tab1, tab2 = st.tabs(["University Recommendations", "Undermatch Risk"])

        with tab1:
            st.subheader("🎯 Your Recommended Universities")
            for category, universities in university_recommendations.items():
                with st.container():
                    st.markdown(f"### {category} Schools")
                    for uni in universities:
                        st.markdown(f"- **{uni['University']}** (Student Population: {uni['Population']}) - [Website]({uni['Website']})")
            st.markdown("📧 [Contact Counselor](mailto:counselor@school.edu)")

        with tab2:
            st.subheader("📊 Your Undermatch Risk")
            risk_data = np.random.normal(50, 15, 200)
            student_risk_score = np.random.randint(20, 80)

            risk_level = "Low" if student_risk_score < 40 else "Medium" if student_risk_score < 60 else "High"
            st.write(f"Your undermatch risk is **{risk_level}** (Score: {student_risk_score}).")

            fig, ax = plt.subplots(figsize=(8, 3))
            ax.boxplot(risk_data, vert=False, patch_artist=True,
                       boxprops=dict(facecolor="lightblue"), medianprops=dict(color="blue"))
            ax.scatter(student_risk_score, 1, color='red', s=100, label='Your Score', zorder=5)
            ax.set_yticks([])
            ax.set_xlabel("Undermatch Risk Score")
            ax.set_title("Distribution of Undermatch Risk Scores")
            ax.legend()
            ax.grid(axis='x', linestyle='--', alpha=0.7)
            st.pyplot(fig)

    elif user["role"] == "educator":
        st.info(f"**School:** {user['school']} | **Position:** {user['position']}")
        st.write("Search students to view their university recommendations.")

        with st.form("student_search"):
            search_id = st.text_input("Enter Student ID")
            search_btn = st.form_submit_button("Search")

            if search_btn:
                if search_id in users and users[search_id]["role"] == "student":
                    st.session_state.searched_student = users[search_id]
                else:
                    st.error("Student ID not found.")

        if st.session_state.searched_student:
            student = st.session_state.searched_student
            st.subheader(f"📚 Student: {student['name']}")
            st.write(f"**School:** {student['school']} | **Grade:** {student['grade']}")

            for category in university_recommendations:
                with st.expander(f"{category} Schools"):
                    for uni in university_recommendations[category]:
                        st.markdown(f"- **{uni['University']}** (Student Population: {uni['Population']}) - [Website]({uni['Website']})")

            st.markdown("📧 [Contact Student](mailto:student@email.com)")

else:
    st.write("Welcome to BrightPath, a platform designed to empower students by connecting them with universities that match their potential, avoiding undermatching and ensuring they reach their academic and career goals.")
    st.write("👈 Please log in via the sidebar to access personalized content.")
