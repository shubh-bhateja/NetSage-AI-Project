import streamlit as st
import pandas as pd
import json
import random
from rule_checker import run_deterministic_checks

# Set page config
st.set_page_config(page_title="NetSage AI", layout="wide")
st.title("NetSage AI 🧠: Network Troubleshooting Assistant")

# Load data
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("cases.csv")
        return df
    except FileNotFoundError:
        return pd.DataFrame()

df = load_data()

# Sidebar for navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Dashboard", "Case Diagnosis", "Responsible AI Log"])

if page == "Dashboard":
    st.header("Overview Dashboard")
    if not df.empty:
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Issue Types (Concepts)")
            concept_counts = df['concept'].value_counts()
            st.bar_chart(concept_counts)
        with col2:
            st.subheader("Severity Levels")
            severity_counts = df['severity'].value_counts()
            st.bar_chart(severity_counts)
            
        st.subheader("AI vs Human Agreement rate")
        st.write("Current mock metric based on synthetic cases:")
        # Simulated metrics
        st.metric(label="Total Cases Reviewed", value="30")
        st.metric(label="Accepted without edit", value="83%", delta="2%")
        
    else:
        st.warning("cases.csv not found.")

elif page == "Case Diagnosis":
    st.header("Diagnose a Network Issue")
    
    if not df.empty:
        case_id = st.selectbox("Select a Sample Case to Diagnose", df['case_id'].tolist())
        selected_case = df[df['case_id'] == case_id].iloc[0]
        
        st.subheader("Engineer Input")
        symptom = st.text_area("Symptom", selected_case['symptom'])
        show_outputs = st.text_area("Show Outputs", selected_case['show_outputs'], height=150)
        
        if st.button("Run Diagnostics"):
            st.markdown("---")
            st.subheader("1. Deterministic Rule Checker")
            errors = run_deterministic_checks(show_outputs)
            if errors:
                for err in errors:
                    st.error(err)
            else:
                st.success("No basic deterministic errors found.")
                
            st.subheader("2. AI Diagnosis")
            with st.spinner("Analyzing with LLM..."):
                # Mocked AI Response for demo purposes
                mock_ai_response = {
                    "root_cause": selected_case['expected_fault'],
                    "confidence": "High",
                    "evidence": f"Derived from output: '{show_outputs}'",
                    "next_command": "show running-config",
                    "fix_steps": "Apply standard configuration fix based on the identified root cause."
                }
                
                st.json(mock_ai_response)
                
            st.subheader("3. Human Review")
            st.info("A human engineer must review and approve this fix before execution.")
            col1, col2, col3 = st.columns(3)
            col1.button("Accept (Execute Fix)", type="primary")
            col2.button("Edit Diagnosis")
            col3.button("Reject (Escalate)")
    else:
        st.warning("No cases found.")

elif page == "Responsible AI Log":
    st.header("Responsible AI: Corrected Diagnoses")
    try:
        log_df = pd.read_csv("responsible_ai_log.csv")
        st.dataframe(log_df, use_container_width=True)
    except FileNotFoundError:
        st.warning("Log not found.")
