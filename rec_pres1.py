import streamlit as st
import pandas as pd

# Dummy data: User credentials (student and educator)
users = {
    "1234": {"name": "Miles Dyson", "role": "student", "school": "Lincoln High School", "grade": "12"},
    "111": {"name": "Ms. Smith", "role": "educator", "school": "Lincoln High School", "position": "College Counselor"}
}

# Dummy data: University recommendations grouped into Foundation, Challenge, and Aspire
university_recommendations = {
    "Foundation": [
        {"name": "Arizona State University", "student_population": "74,795", "website": "https://www.asu.edu"},
        {"name": "Ohio State University", "student_population": "59,837", "website": "https://www.osu.edu"},
        {"name": "Penn State University", "student_population": "46,606", "website": "https://www.psu.edu"},
    ],
    "Challenge": [
        {"name": "University of Illinois Urbana-Champaign", "student_population": "52,331", "website": "https://www.illinois.edu"},
        {"name": "University of Wisconsin-Madison", "student_population": "47,932", "website": "https://www.wisc.edu"},
        {"name": "University of Florida", "student_population": "55,211", "website": "https://www.ufl.edu"},
    ],
    "Aspire": [
        {"name": "University of California, Berkeley", "student_population": "42,327", "website": "https://www.berkeley.edu"},
        {"name": "University of Michigan", "student_population": "48,090", "website": "https://www.umich.edu"},
        {"name": "University of North Carolina", "student_population": "30,092", "website": "https://www.unc.edu"},
    ],
}

# Initialize session state for login and button tracking
if "logged_in_user" not in st.session_state:
    st.session_state.logged_in_user = None
if "show_universities" not in st.session_state:
    st.session_state.show_universities = False
if "searched_student" not in st.session_state:
    st.session_state.searched_student = None


# Function to display categorized university list
def show_university_list():
    st.write("### Your Recommended Universities")

    for category, universities in university_recommendations.items():
        st.subheader(category)
        for uni in universities:
            st.write(f"- **{uni['name']}** (Student Population: {uni['student_population']}) [Website]({uni['website']})")


# Login Page
st.title("BrightPath")
st.write("Login to access personalized university recommendations.")

user_type = st.radio("Select User Type", ["Student", "Educator"])
user_id = st.text_input("Enter your User ID:")
login_button = st.button("Login")

if login_button:
    if user_id in users:
        st.session_state.logged_in_user = users[user_id]
    else:
        st.error("Invalid User ID. Please try again.")

# If logged in, display user-specific view
if st.session_state.logged_in_user:
    user = st.session_state.logged_in_user
    st.write(f"### Welcome, {user['name']}!")

    # **Student View**
    if user["role"] == "student":
        st.write(f"**School:** {user['school']}")
        st.write(f"**Grade:** {user['grade']}")
        st.write(
            "This platform helps you find universities that are a good fit for you based on your academic profile and background."
        )

        # Buttons for Student Actions
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Show University List"):
                st.session_state.show_universities = True
        with col2:
            st.write("👉 [Contact Counselor](mailto:counselor@school.edu)")

        # Show recommended universities
        if st.session_state.show_universities:
            show_university_list()

    # **Educator View**
    elif user["role"] == "educator":
        st.write(f"**School:** {user['school']}")
        st.write(f"**Role:** {user['position']}")
        st.write(
            "This platform allows educators to find students and view their university recommendations."
        )

        # Search for a student
        search_id = st.text_input("Enter Student ID to Search:")
        search_button = st.button("Search Student")

        if search_button:
            if search_id in users and users[search_id]["role"] == "student":
                st.session_state.searched_student = users[search_id]
            else:
                st.error("Student not found. Please check the ID.")

        # Show student details if found
        if st.session_state.searched_student:
            student = st.session_state.searched_student
            st.write(f"### Student Profile: {student['name']}")
            st.write(f"**School:** {student['school']}")
            st.write(f"**Grade:** {student['grade']}")

            # Show student's recommended universities
            show_university_list()

            # Contact student button
            st.write("📧 [Contact Student](mailto:student@email.com)")
