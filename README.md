# NetSage AI

**AI-Assisted Network Troubleshooting with Human-in-the-Loop Review**

> Built by **Team depthlysis** — Applied AI + Network Troubleshooting Project

---

## Overview

NetSage AI is an intelligent troubleshooting assistant for Cisco-style lab networks. It combines **deterministic rule-based checks** with **LLM-powered diagnosis** (via OpenRouter) to help network engineers identify root causes of connectivity issues — while always keeping a **human reviewer** in the decision loop.

### Key Features

- **30 real-world troubleshooting cases** covering DHCP, DNS, NAT, ACLs, VLANs, OSPF, wireless, and gateway issues
- **Deterministic Rule Checker** — Python-based checks catch common config mistakes (duplicate IPs, missing VLANs, wrong masks, etc.) before involving the AI
- **AI Diagnosis via OpenRouter** — structured LLM analysis returning root cause, confidence, evidence, next command, and fix steps
- **Human-in-the-Loop Review** — every diagnosis must be Accepted, Edited, or Rejected by a human engineer
- **Responsible AI Logging** — documented cases where AI was wrong and corrected by humans
- **Interactive Streamlit Dashboard** — visual overview of issue types, severity, and AI vs. human agreement rates

---

## Architecture

```
+-----------------------------------------------------+
|                   Streamlit Dashboard                |
|  +----------+  +--------------+  +---------------+  |
|  | Overview  |  |Case Diagnosis|  |Responsible AI |  |
|  | Dashboard |  |    Page      |  |   Log Page    |  |
|  +----------+  +------+-------+  +---------------+  |
|                       |                              |
|            +----------+----------+                   |
|            |                     |                   |
|   +--------v--------+  +--------v--------+          |
|   |  Rule Checker   |  |  LLM Diagnosis  |          |
|   |  (Python/Regex) |  |  (OpenRouter)   |          |
|   +--------+--------+  +--------+--------+          |
|            |                     |                   |
|            +----------+----------+                   |
|                       v                              |
|              +----------------+                      |
|              | Human Review   |                      |
|              | Accept / Edit  |                      |
|              | Reject + Log   |                      |
|              +----------------+                      |
+-----------------------------------------------------+
```

**Data Flow:**
1. Engineer selects a case or enters symptoms + show-command outputs
2. Deterministic rule checker runs Python-based regex checks for obvious misconfigurations
3. AI diagnosis calls OpenRouter LLM with structured prompts for deeper analysis
4. Human engineer reviews AI output and Accepts / Edits / Rejects
5. All actions are logged to `human_review_log.csv` for accountability

---

## Project Structure

| File | Description |
|------|-------------|
| `dashboard.py` | Main Streamlit application with 3 pages: Dashboard, Case Diagnosis, Responsible AI Log |
| `rule_checker.py` | Deterministic Python checks for common Cisco config errors (10 checks) |
| `cases.csv` | 30 troubleshooting cases with symptoms, topology notes, realistic show-command outputs, expected faults, OSI layers, concepts, and severity levels |
| `diagnose_prompt.md` | System prompt for LLM diagnosis with 3 few-shot examples |
| `severity_prompt.md` | Helper prompt for severity/priority classification |
| `followup_prompt.md` | Helper prompt for follow-up verification commands |
| `responsible_ai_log.csv` | 8 documented cases where AI was corrected by a human |
| `human_review_log.csv` | Audit trail of all human review actions (Accept/Edit/Reject) |
| `demo_script.md` | 5-10 minute demo presentation guide |
| `requirements.txt` | Python package dependencies |

---

## Setup and Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Configure OpenRouter API Key

Get an API key at [https://openrouter.ai/keys](https://openrouter.ai/keys).

```bash
# Option 1: Environment variable
export OPENROUTER_API_KEY="sk-or-..."

# Option 2: Enter directly in the Streamlit sidebar when running the app
```

> **Note:** When no API key is configured, the app falls back to a local deterministic diagnosis engine that maps known fault signatures to structured output. This ensures the prototype remains functional for offline demos, but the full LLM-powered analysis requires a valid API key.

### Run the Dashboard

```bash
streamlit run dashboard.py
```

The app will open at `http://localhost:8501`.

---

## Usage Guide

### 1. Dashboard Page
- View case distribution by **issue type**, **severity**, and **OSI layer**
- See real-time **AI vs. Human agreement rate** computed from the review log
- Track total reviews, acceptances, edits, and rejections

### 2. Case Diagnosis Page
1. Select a case from the dropdown (or modify the inputs)
2. Click **Run Diagnostics**
3. Review the **deterministic rule checker** results (instant Python checks)
4. Review the **AI diagnosis** (LLM-powered via OpenRouter)
5. Add your notes and click **Accept**, **Edit**, or **Reject**
6. Your review action is logged automatically

### 3. Responsible AI Log Page
- View documented AI corrections (where AI was wrong)
- View the full human review audit trail
- Review statistics on acceptance/edit/rejection rates

---

## Running the Rule Checker Standalone

```bash
python rule_checker.py
```

This runs the deterministic checker against sample outputs and prints results.

---

## Responsible AI Principles

- **Human-in-the-Loop**: Every AI diagnosis requires human review before execution
- **Transparency**: AI provides confidence levels and evidence for every recommendation
- **Accountability**: All review actions are logged with timestamps and notes
- **Error Documentation**: AI mistakes are documented with human corrections and explanations
- **Safety First**: Deterministic checks catch obvious issues before AI is invoked

---

## Dataset Coverage

The 30 cases span **8 network concepts** across **4 OSI layers**:

| Concept | Cases | OSI Layer | Severity Range |
|---------|-------|-----------|----------------|
| DHCP | 5 | Layer 7 | Medium |
| DNS | 7 | Layer 7 | Medium |
| NAT | 4 | Layer 3 | High |
| Default Gateway | 4 | Layer 3 | High |
| Access Control Lists | 3 | Layer 3/4 | Critical |
| Inter-VLAN Routing | 2 | Layer 2 | High |
| Wireless Security | 3 | Layer 2 | Medium |
| OSPF Routing | 2 | Layer 3 | High |

---

## Team

**Team depthlysis**

---

## License

This project was developed as an academic assignment for Applied AI + Network Troubleshooting coursework.
