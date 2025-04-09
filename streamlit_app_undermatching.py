import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# Dummy data
users = {
    "1234": {"name": "Miles Dyson", "role": "student", "school": "Lincoln High School", "grade": "12"},
    "5678": {"name": "Sarah Connor", "role": "student", "school": "Lincoln High School", "grade": "11"},
    "9012": {"name": "John Connor", "role": "student", "school": "Lincoln High School", "grade": "12"},
    "3141": {"name": "Kyle Reese", "role": "student", "school": "Lincoln High School", "grade": "11"},
    "2718": {"name": "Catherine Weaver", "role": "student", "school": "Lincoln High School", "grade": "12"},
    "111": {"name": "Ms. Smith", "role": "educator", "school": "Lincoln High School", "position": "College Counselor"}
}

university_recommendations = {
    "Foundation": [
        {"University": "Arizona State University", "Population": "74,795", "Website": "https://www.asu.edu", "Description": "Large, diverse campus ideal for students seeking a wide variety of academic options."},
        {"University": "Ohio State University", "Population": "59,837", "Website": "https://www.osu.edu", "Description": "Strong athletics and broad academic programs with great community engagement."},
        {"University": "Penn State University", "Population": "46,606", "Website": "https://www.psu.edu", "Description": "Robust alumni network with excellent career placement resources."},
    ],
    "Thrive": [
        {"University": "University of Illinois Urbana-Champaign", "Population": "52,331", "Website": "https://www.illinois.edu", "Description": "Outstanding STEM programs and research opportunities."},
        {"University": "University of Wisconsin-Madison", "Population": "47,932", "Website": "https://www.wisc.edu", "Description": "Exceptional academic rigor with vibrant student life."},
        {"University": "University of Florida", "Population": "55,211", "Website": "https://www.ufl.edu", "Description": "Highly ranked with excellent programs across disciplines."},
    ],
    "Aspire": [
        {"University": "University of California, Berkeley", "Population": "42,327", "Website": "https://www.berkeley.edu", "Description": "Top-tier university emphasizing research and intellectual growth."},
        {"University": "University of Michigan", "Population": "48,090", "Website": "https://www.umich.edu", "Description": "Academic excellence, extensive resources, strong school spirit."},
        {"University": "University of North Carolina", "Population": "30,092", "Website": "https://www.unc.edu", "Description": "Strong academics combined with rich traditions and community."},
    ],
}

# Generate risk data once
risk_data = np.random.normal(50, 15, 200)

# Initialize session states
if "logged_in_user" not in st.session_state:
    st.session_state["logged_in_user"] = None

# Sidebar Logo and Login
sidebar_logo = """
<h1 style='text-align:left; font-size:60px;'>🎓<br>
<span style='color:#FDB515;'>Bright</span><span style='color:#003262;'>Path</span></h1>
"""
st.sidebar.markdown(sidebar_logo, unsafe_allow_html=True)
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
main_logo = """
<div style='text-align:center;'>
    <h1 style='font-size:70px;'>🎓</h1>
    <h1><span style='color:#FDB515;'>Bright</span><span style='color:#003262;'>Path</span></h1>
    <h3 style='color:#666;'>Empowering Students Towards Academic Excellence</h3>
    <hr style='margin:20px;'>
</div>
"""
st.markdown(main_logo, unsafe_allow_html=True)

if st.session_state.logged_in_user:
    user = st.session_state.logged_in_user
    st.write(f"### Welcome, {user['name']} 👋")

    if user["role"] == "student":
        st.info(f"**School:** {user['school']} | **Grade:** {user['grade']}")
        st.write("Discover universities tailored to your academic profile.")

        st.subheader("🎯 Your Recommended Universities")
        for category, universities in university_recommendations.items():
            with st.expander(f"{category} Schools"):
                for uni in universities:
                    st.markdown(f"- **{uni['University']}** (Population: {uni['Population']}) - {uni['Description']} [Website]({uni['Website']})")

        st.markdown("📧 [Contact Counselor](mailto:counselor@school.edu)")

    elif user["role"] == "educator":
        st.info(f"**School:** {user['school']} | **Position:** {user['position']}")
        st.write("Use the insights below to guide discussions and support student academic planning.")

        grade_filter = st.sidebar.multiselect("Filter by Grade", options=["11", "12"], default=["11", "12"])
        risk_filter = st.sidebar.multiselect("Filter by Risk Level", options=["Low", "Medium", "High"], default=["Low", "Medium", "High"])

        for uid, student in users.items():
            if student["role"] == "student" and student["grade"] in grade_filter:
                if student["name"] == "Miles Dyson":
                    student_risk_score = 75  # Always High
                elif student["name"] == "Sarah Connor":
                    student_risk_score = 30  # Always Low
                elif student["name"] == "John Connor":
                    student_risk_score = 50  # Always Medium
                else:
                    student_risk_score = np.random.randint(20, 80)

                risk_level = "Low" if student_risk_score < 40 else "Medium" if student_risk_score < 60 else "High"

                if risk_level in risk_filter:
                    st.markdown(f"---\n### 🎓 {student['name']} (Grade: {student['grade']}, Risk: {risk_level})")

                    with st.expander("📘 University Recommendations", expanded=False):
                        st.markdown("Encourage exploration of these universities and discuss how they align with the student's academic goals.")
                        for category, universities in university_recommendations.items():
                            st.markdown(f"**{category} Schools**")
                            for uni in universities:
                                st.markdown(f"- **{uni['University']}** (Population: {uni['Population']}) - {uni['Description']} [Website]({uni['Website']})")

                    fig = px.box(x=risk_data, points="all", title="Undermatch Risk", labels={"x": "Risk Score"})
                    fig.add_scatter(x=[student_risk_score], y=[0], mode='markers', marker=dict(color='red', size=10), name="Student Score")
                    fig.update_layout(height=150, margin=dict(l=10, r=10, t=30, b=10), font=dict(size=10))
                    st.plotly_chart(fig, use_container_width=True)

else:
    st.markdown("<div style='text-align:center;color:#555;'>Welcome to BrightPath. Please log in via the sidebar to access personalized content and recommendations tailored for academic success.</div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    with st.expander("📖 About Us"):
        st.write("BrightPath is dedicated to closing the college opportunity gap by helping students find and apply to universities that match their academic potential. We partner with educators to ensure that no student undermatches.")

    with st.expander("🛠️ Product"):
        st.write("Our platform offers personalized university recommendations, visual risk insights, and tools for both students and educators to support effective college planning.")

    with st.expander("🤖 Model"):
        st.write("We use advanced data science techniques to estimate student undermatch risk and align academic profiles with university characteristics. Our models are transparent, fair, and regularly validated.")
