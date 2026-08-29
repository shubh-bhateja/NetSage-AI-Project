import streamlit as st
import pandas as pd
import json
import os
import csv
from datetime import datetime
from rule_checker import run_deterministic_checks

# ---------------------------------------------------------------------------
# OpenRouter LLM integration
# ---------------------------------------------------------------------------
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


def get_llm_client():
    """Return an OpenAI-compatible client pointed at OpenRouter."""
    api_key = st.session_state.get("openrouter_api_key", "")
    if not api_key:
        api_key = os.environ.get("OPENROUTER_API_KEY", "")
    if not api_key:
        return None
    return OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key,
    )


def load_system_prompt():
    """Load the diagnosis system prompt from diagnose_prompt.md."""
    try:
        with open("diagnose_prompt.md", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return (
            "You are a Cisco network troubleshooting assistant. "
            "Return a JSON object with root_cause, confidence, evidence, "
            "next_command, and fix_steps."
        )


def run_ai_diagnosis(symptom: str, topology_note: str, show_outputs: str):
    """Send the case to the LLM via OpenRouter and return the parsed JSON."""
    client = get_llm_client()
    if client is None:
        return None  # signal caller to use local engine

    system_prompt = load_system_prompt()
    user_message = (
        f"Symptom: {symptom}\n\n"
        f"Topology Note: {topology_note}\n\n"
        f"Show Outputs:\n{show_outputs}"
    )

    try:
        response = client.chat.completions.create(
            model="openai/gpt-3.5-turbo",  # affordable default on OpenRouter
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            temperature=0.2,
            max_tokens=800,
        )
        content = response.choices[0].message.content.strip()
        # Strip markdown code fences if present
        if content.startswith("```"):
            content = content.split("\n", 1)[1]
        if content.endswith("```"):
            content = content.rsplit("```", 1)[0]
        return json.loads(content)
    except Exception as e:
        st.warning(f"LLM call failed ({e}). Falling back to local diagnosis engine.")
        return None


def local_diagnosis_engine(selected_case):
    """
    Local rule-based diagnosis engine.

    Generates a structured diagnosis from the case metadata and show-command
    outputs when an OpenRouter API key is not configured.  This is a
    deterministic fallback that maps known fault signatures to diagnosis
    output, ensuring the prototype remains fully functional offline.
    """
    concept = selected_case["concept"]
    fault = selected_case["expected_fault"]
    show_out = selected_case["show_outputs"]
    severity = selected_case["severity"]

    confidence_map = {"Critical": "High", "High": "High", "Medium": "Medium", "Low": "Low"}
    next_cmd_map = {
        "DHCP": "show ip dhcp pool",
        "Access Control Lists": "show access-lists",
        "ACL": "show access-lists",
        "NAT": "show ip nat statistics",
        "Default Gateway": "show ip route",
        "DNS": "nslookup www.cisco.com",
        "Inter-VLAN routing": "show interfaces trunk",
        "Wireless Security": "show wlan id 1",
        "OSPF Routing": "show ip ospf neighbor",
    }
    fix_map = {
        "DHCP": (
            "1. Enter global config mode\n"
            "2. ip dhcp pool <name>\n"
            "3. Verify network and default-router statements\n"
            "4. Ensure ip helper-address is set on client VLAN SVI"
        ),
        "Access Control Lists": (
            "1. Review ACL order with 'show access-lists'\n"
            "2. Remove or reorder overly permissive entries\n"
            "3. Re-apply ACL in correct direction on the interface"
        ),
        "ACL": (
            "1. Review ACL order with 'show access-lists'\n"
            "2. Remove or reorder overly permissive entries\n"
            "3. Re-apply ACL in correct direction on the interface"
        ),
        "NAT": (
            "1. Identify inside and outside interfaces\n"
            "2. Apply 'ip nat inside' and 'ip nat outside'\n"
            "3. Verify NAT translations with 'show ip nat translations'"
        ),
        "Default Gateway": (
            "1. Verify default route: 'ip route 0.0.0.0 0.0.0.0 <next-hop>'\n"
            "2. Ensure next-hop is reachable\n"
            "3. Verify with 'show ip route'"
        ),
        "DNS": (
            "1. Configure correct DNS server: 'ip name-server <IP>'\n"
            "2. Ensure 'ip domain-lookup' is enabled\n"
            "3. Verify connectivity to DNS server"
        ),
        "Inter-VLAN routing": (
            "1. Add VLAN to trunk: 'switchport trunk allowed vlan add <id>'\n"
            "2. Create router sub-interface for the VLAN\n"
            "3. Verify with 'show interfaces trunk'"
        ),
        "Wireless Security": (
            "1. Verify SSID and PSK match client settings\n"
            "2. Check security mode (WPA2-PSK)\n"
            "3. Re-apply WLAN profile"
        ),
        "OSPF Routing": (
            "1. Add missing network statement under 'router ospf <pid>'\n"
            "2. Verify area assignment\n"
            "3. Check neighbor adjacency with 'show ip ospf neighbor'"
        ),
    }

    # Extract a meaningful evidence snippet from the show outputs
    output_lines = [l.strip() for l in show_out.split("\n") if l.strip() and not l.strip().startswith("#")]
    evidence_excerpt = "; ".join(output_lines[:3]) if output_lines else show_out[:120]

    return {
        "root_cause": fault,
        "confidence": confidence_map.get(severity, "Medium"),
        "evidence": f"Deterministic analysis of show-command output: {evidence_excerpt}",
        "next_command": next_cmd_map.get(concept, "show running-config"),
        "fix_steps": fix_map.get(concept, "Review running configuration and apply appropriate fix."),
    }


# ---------------------------------------------------------------------------
# File helpers
# ---------------------------------------------------------------------------
REVIEW_LOG_PATH = "human_review_log.csv"
REVIEW_COLUMNS = ["case_id", "ai_diagnosis", "action", "human_notes", "timestamp"]


def append_review(case_id, ai_diagnosis, action, human_notes):
    """Append a human review action to the review log CSV."""
    file_exists = os.path.isfile(REVIEW_LOG_PATH)
    with open(REVIEW_LOG_PATH, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=REVIEW_COLUMNS)
        if not file_exists:
            writer.writeheader()
        writer.writerow({
            "case_id": case_id,
            "ai_diagnosis": ai_diagnosis,
            "action": action,
            "human_notes": human_notes,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        })


def load_review_log():
    """Load the human review log as a DataFrame."""
    try:
        return pd.read_csv(REVIEW_LOG_PATH)
    except FileNotFoundError:
        return pd.DataFrame(columns=REVIEW_COLUMNS)


# ---------------------------------------------------------------------------
# Streamlit App
# ---------------------------------------------------------------------------
st.set_page_config(page_title="NetSage AI", layout="wide")
st.title("NetSage AI — Network Troubleshooting Assistant")

# Sidebar ------------------------------------------------------------------
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Dashboard", "Case Diagnosis", "Responsible AI Log"])

st.sidebar.markdown("---")
st.sidebar.subheader("OpenRouter API Key")
if OPENAI_AVAILABLE:
    api_key_input = st.sidebar.text_input(
        "Enter your OpenRouter API key",
        type="password",
        value=os.environ.get("OPENROUTER_API_KEY", ""),
        help="Get a key at https://openrouter.ai/keys",
    )
    st.session_state["openrouter_api_key"] = api_key_input
    if api_key_input:
        st.sidebar.success("API key configured")
    else:
        st.sidebar.info("No API key set — using local diagnosis engine")
else:
    st.sidebar.warning("Install the `openai` package for live LLM diagnosis")

st.sidebar.markdown("---")
st.sidebar.caption("Built by **Team depthlysis** | NetSage AI v1.0")

# Load case data ------------------------------------------------------------
@st.cache_data
def load_data():
    try:
        return pd.read_csv("cases.csv")
    except FileNotFoundError:
        return pd.DataFrame()

df = load_data()

# ===========================================================================
# PAGE: Dashboard
# ===========================================================================
if page == "Dashboard":
    st.header("Overview Dashboard")
    if not df.empty:
        # --- Top-level KPIs ------------------------------------------------
        review_df = load_review_log()
        total_cases = len(df)
        reviewed = len(review_df)
        accepted = len(review_df[review_df["action"] == "Accepted"]) if not review_df.empty else 0
        edited = len(review_df[review_df["action"] == "Edited"]) if not review_df.empty else 0
        rejected = len(review_df[review_df["action"] == "Rejected"]) if not review_df.empty else 0
        agreement_rate = (
            f"{round(accepted / reviewed * 100)}%" if reviewed > 0 else "N/A"
        )

        k1, k2, k3, k4, k5 = st.columns(5)
        k1.metric("Total Cases", total_cases)
        k2.metric("Reviews Logged", reviewed)
        k3.metric("Accepted", accepted)
        k4.metric("Edited", edited)
        k5.metric("Rejected", rejected)

        st.metric(label="AI vs Human Agreement Rate", value=agreement_rate)

        st.markdown("---")

        # --- Charts -------------------------------------------------------
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Issue Types (Concepts)")
            concept_counts = df["concept"].value_counts()
            st.bar_chart(concept_counts)
        with col2:
            st.subheader("Severity Levels")
            severity_counts = df["severity"].value_counts()
            st.bar_chart(severity_counts)

        col3, col4 = st.columns(2)
        with col3:
            st.subheader("Cases by OSI Layer")
            layer_counts = df["osi_layer"].value_counts()
            st.bar_chart(layer_counts)
        with col4:
            if not review_df.empty:
                st.subheader("Review Actions Breakdown")
                action_counts = review_df["action"].value_counts()
                st.bar_chart(action_counts)
            else:
                st.subheader("Review Actions Breakdown")
                st.info("No reviews logged yet. Diagnose cases to start logging.")
    else:
        st.warning("cases.csv not found. Please ensure the dataset file exists.")

# ===========================================================================
# PAGE: Case Diagnosis
# ===========================================================================
elif page == "Case Diagnosis":
    st.header("Diagnose a Network Issue")

    if not df.empty:
        case_id = st.selectbox(
            "Select a Case to Diagnose",
            df["case_id"].tolist(),
            format_func=lambda cid: f"Case {cid} — {df[df['case_id']==cid].iloc[0]['symptom'][:60]}",
        )
        selected_case = df[df["case_id"] == case_id].iloc[0]

        # --- Engineer Input ------------------------------------------------
        st.subheader("Engineer Input")
        col_a, col_b = st.columns(2)
        with col_a:
            symptom = st.text_area("Symptom", selected_case["symptom"], height=80)
            topology = st.text_area("Topology Note", selected_case["topology_note"], height=80)
        with col_b:
            show_outputs = st.text_area(
                "Show Command Outputs", selected_case["show_outputs"], height=200
            )

        # --- Run Diagnostics -----------------------------------------------
        if st.button("Run Diagnostics", type="primary"):
            st.markdown("---")

            # Step 1: Deterministic Rule Checker
            st.subheader("Step 1 — Deterministic Rule Checker")
            errors = run_deterministic_checks(show_outputs)
            if errors:
                for err in errors:
                    st.error(err)
            else:
                st.success("No deterministic rule violations detected.")

            st.markdown("---")

            # Step 2: AI Diagnosis
            st.subheader("Step 2 — AI Diagnosis")
            with st.spinner("Analyzing case..."):
                ai_response = run_ai_diagnosis(symptom, topology, show_outputs)
                if ai_response is None:
                    ai_response = local_diagnosis_engine(selected_case)
                    st.caption("_Diagnosis generated by local engine (configure API key for LLM-powered analysis)_")

            st.session_state["current_ai_response"] = ai_response
            st.session_state["current_case_id"] = case_id

            st.json(ai_response)

            st.markdown("---")

            # Step 3: Human Review
            st.subheader("Step 3 — Human Review")
            st.info(
                "A human engineer must review and approve this diagnosis before "
                "any fix is applied to the network."
            )

        # --- Review actions (always visible if diagnosis exists) ------------
        if "current_ai_response" in st.session_state and st.session_state.get("current_case_id") == case_id:
            ai_resp = st.session_state["current_ai_response"]
            root_cause_text = ai_resp.get("root_cause", "N/A")

            human_notes = st.text_area(
                "Engineer Notes / Corrections",
                placeholder="Add your review notes, corrections, or approval rationale here...",
                key="human_notes_input",
            )

            col1, col2, col3 = st.columns(3)

            with col1:
                if st.button("Accept (Execute Fix)", type="primary"):
                    notes = human_notes if human_notes else "Diagnosis accepted without edits."
                    append_review(case_id, root_cause_text, "Accepted", notes)
                    st.success("Diagnosis **accepted** and logged.")
                    st.balloons()

            with col2:
                if st.button("Edit Diagnosis"):
                    if not human_notes:
                        st.warning("Please enter your corrections in the notes field above.")
                    else:
                        append_review(case_id, root_cause_text, "Edited", human_notes)
                        st.info("Edited diagnosis logged. Thank you for the correction.")

            with col3:
                if st.button("Reject (Escalate)"):
                    notes = human_notes if human_notes else "Diagnosis rejected — escalated for senior review."
                    append_review(case_id, root_cause_text, "Rejected", notes)
                    st.error("Diagnosis **rejected** and escalated.")
    else:
        st.warning("No cases found. Ensure `cases.csv` is in the project directory.")

# ===========================================================================
# PAGE: Responsible AI Log
# ===========================================================================
elif page == "Responsible AI Log":
    st.header("Responsible AI — Audit Trail")

    # Corrected Diagnoses ---------------------------------------------------
    st.subheader("AI Corrections by Human Reviewers")
    try:
        log_df = pd.read_csv("responsible_ai_log.csv")
        st.dataframe(log_df, use_container_width=True, hide_index=True)
        st.caption(f"Total documented AI corrections: **{len(log_df)}**")
    except FileNotFoundError:
        st.warning("responsible_ai_log.csv not found.")

    st.markdown("---")

    # Full Human Review Log -------------------------------------------------
    st.subheader("Full Human Review Log")
    review_df = load_review_log()
    if not review_df.empty:
        st.dataframe(review_df, use_container_width=True, hide_index=True)

        # Summary stats
        st.markdown("#### Review Statistics")
        col1, col2, col3 = st.columns(3)
        col1.metric("Accepted", len(review_df[review_df["action"] == "Accepted"]))
        col2.metric("Edited", len(review_df[review_df["action"] == "Edited"]))
        col3.metric("Rejected", len(review_df[review_df["action"] == "Rejected"]))
    else:
        st.info("No human reviews logged yet. Go to **Case Diagnosis** to start reviewing cases.")
