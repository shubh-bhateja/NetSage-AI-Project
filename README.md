# NetSage AI 🧠

NetSage AI is an AI-assisted network troubleshooting helper designed for Cisco-style lab networks. It acts as an expert diagnostic assistant that reads network symptoms and `show` command outputs to suggest root causes and next steps. 

Crucially, NetSage AI is built around a **"Human in the Loop"** safety rule: it requires a human reviewer to approve or correct every diagnosis before a fix is accepted.

## Features

- **Deterministic Rule Checker**: A Python script runs instant regex and heuristic checks on `show` outputs to catch common deterministic errors (e.g., duplicate IPs, missing VLANs, interfaces down) before invoking the AI.
- **AI Diagnosis Prompting**: A carefully structured prompt forces the LLM to return strict JSON detailing the `root_cause`, `confidence`, `evidence`, `next_command`, and `fix_steps`.
- **Streamlit Dashboard UI**: An interactive dashboard with three main sections:
  1. **Overview Dashboard**: Visualizes the issue types, severities, and the AI vs Human agreement rate from our 30-case dataset.
  2. **Case Diagnosis**: An interactive interface to input a symptom and `show` output, run the deterministic checker, fetch the AI diagnosis, and accept/edit/reject the fix.
  3. **Responsible AI Log**: A ledger of cases where the AI's diagnosis was incorrect and corrected by a human, ensuring oversight.
- **30 Synthetic Network Cases**: A dataset (`cases.csv`) encompassing Layer 2 to Layer 7 network problems, including VLAN routing, DHCP, DNS, ACL, NAT, and wireless issues.

## Project Structure

- `dashboard.py`: The main Streamlit web application.
- `rule_checker.py`: The deterministic python logic that analyzes `show` commands.
- `diagnose_prompt.md`: The system prompt template for the AI model.
- `cases.csv`: The dataset containing 30 troubleshooting cases.
- `responsible_ai_log.csv`: The audit log tracking AI corrections made by human engineers.
- `full_demo_script.md`: The 7-minute script for presenting and demoing the project.
- `requirements.txt`: Python dependencies.

## Installation and Usage

To run this project locally, ensure you have Python 3 installed.

1. **Clone the repository:**
   ```bash
   git clone https://github.com/shubh-bhateja/NetSage-AI-Project.git
   cd NetSage-AI-Project
   ```

2. **Install the dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the Streamlit Dashboard:**
   ```bash
   streamlit run dashboard.py
   ```
   The dashboard will open automatically in your default web browser (typically at `http://localhost:8501`).

## Deployment
This project is configured to be easily deployed on [Streamlit Community Cloud](https://share.streamlit.io/). Simply link this GitHub repository and select `dashboard.py` as the main file path.

## Team
- Shubh Bhateja
- Somansh
