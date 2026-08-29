# NetSage AI Demo Script

This script outlines the required 5-10 minute video demonstration for the final project submission.

## Setup (Before Recording)
1. Ensure the Streamlit app is running locally (`streamlit run dashboard.py`) or on your deployed URL.
2. Open the "Dashboard" view.
3. Have your Packet Tracer lab file open in the background (if required for visual context).

## Scene 1: Introduction & Dashboard Overview (1-2 minutes)
1. **Introduction**: "Hello, we are team [Name], and this is our presentation for the NetSage AI network troubleshooting assistant."
2. **Dashboard Review**: 
   - Show the Overview Dashboard.
   - Highlight that the dataset contains 30 distinct cases across different OSI layers and network concepts.
   - Briefly explain the "AI vs Human Agreement rate" to show human oversight is active.

## Scene 2: Diagnosing a Broken Case (2-3 minutes)
1. **Navigate**: Go to the "Case Diagnosis" page.
2. **Select Issue**: Pick a complex issue from the dropdown (e.g., VLAN mismatch or ACL drop).
3. **Run Rule Checker**: Click "Run Diagnostics". Emphasize the deterministic Python checks that run instantly to catch simple errors (like duplicate IPs) before involving the AI.
4. **AI Output**: Walk through the AI JSON output. Point out the:
   - Root Cause
   - Confidence Level
   - Evidence cited
   - Suggested Next Command
   - Step-by-step fix

## Scene 3: Human Oversight & Verification (1-2 minutes)
1. **Review**: Explain that the AI acts as a junior assistant, and the human engineer is the ultimate decision-maker.
2. **Action**: Click on "Accept (Execute Fix)" or "Edit Diagnosis" depending on whether you want to show a correction.
3. **Verification**: (Optional) Switch to Packet Tracer, apply the AI's suggested configuration, and show that ping now succeeds.

## Scene 4: Responsible AI Logging (1 minute)
1. **Navigate**: Go to the "Responsible AI Log" page.
2. **Explain**: Show the table containing at least 5 instances where the AI made a mistake (e.g., wrong subnet mask assumption) and was corrected by a human engineer, highlighting the importance of the human-in-the-loop safety rule.
3. **Conclusion**: Wrap up the demo.
