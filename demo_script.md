# NetSage AI Demo Script

This script outlines the required 5-10 minute video demonstration for the final project submission.

## Setup (Before Recording)
1. Ensure the Streamlit app is running locally (`streamlit run dashboard.py`) or on your deployed URL.
2. Open the "Dashboard" view.
3. Have your Packet Tracer lab file open in the background (if required for visual context).
4. (Optional) Set your OpenRouter API key in the sidebar for live AI diagnosis.

## Scene 1: Introduction & Dashboard Overview (1-2 minutes)
1. **Introduction**: "Hello, we are team **depthlysis**, and this is our presentation for the NetSage AI network troubleshooting assistant."
2. **Dashboard Review**: 
   - Show the Overview Dashboard with the 5 KPI metrics at the top (Total Cases, Reviews Logged, Accepted, Edited, Rejected).
   - Highlight that the dataset contains 30 distinct cases across 8 different network concepts and 4 OSI layers.
   - Show the bar charts for Issue Types, Severity Levels, OSI Layers, and Review Actions breakdown.
   - Point out the AI vs Human Agreement Rate — explain that this is computed dynamically from actual review data.

## Scene 2: Diagnosing a Broken Case (2-3 minutes)
1. **Navigate**: Go to the "Case Diagnosis" page.
2. **Select Issue**: Pick a complex issue from the dropdown (e.g., Case 8 — VLAN trunk issue, or Case 2 — ACL problem).
3. **Show the Input**: Point out the realistic show-command outputs that look like actual Cisco IOS CLI text.
4. **Run Rule Checker**: Click "Run Diagnostics". Emphasize:
   - The deterministic Python checks run instantly
   - They catch basic errors (duplicate IPs, missing VLANs, interface down) before the AI is involved
   - Show any warnings that appear
5. **AI Output**: Walk through the AI JSON output. Point out the:
   - Root Cause — the AI's best guess at the problem
   - Confidence Level — how sure the AI is
   - Evidence cited — specific references to the show-command output
   - Suggested Next Command — for further verification
   - Step-by-step Fix — actionable IOS commands

## Scene 3: Human Oversight & Verification (1-2 minutes)
1. **Explain**: The AI acts as a junior assistant. The human engineer is the ultimate decision-maker. No fix is applied without human approval.
2. **Accept**: Add a note like "Verified in lab — diagnosis is correct" and click "Accept (Execute Fix)". Show the success confirmation.
3. **Edit Example**: Select another case, run diagnostics, then enter a correction in the notes field and click "Edit Diagnosis". Explain that this logs the human's correction for responsible AI tracking.
4. **Reject Example**: (Optional) Show a case where the AI is wrong and click "Reject (Escalate)".
5. **Verification**: (Optional) Switch to Packet Tracer, apply the AI's suggested configuration, and show that ping now succeeds.

## Scene 4: Responsible AI Logging (1 minute)
1. **Navigate**: Go to the "Responsible AI Log" page.
2. **AI Corrections Table**: Show the table containing 8 documented instances where the AI made a mistake and was corrected by a human engineer.
   - Point out specific examples: e.g., "The AI diagnosed a missing VLAN but the real issue was port security err-disabled."
   - Explain why this matters for building trust in AI systems.
3. **Full Review Log**: Scroll down to the Human Review Log showing all Accept/Edit/Reject actions with timestamps.
4. **Review Statistics**: Show the metrics at the bottom — total Accepted, Edited, and Rejected counts.
5. **Conclusion**: "NetSage AI demonstrates responsible AI by keeping humans in the loop, logging all decisions, and documenting AI mistakes. Thank you for watching."

## Tips for Recording
- Use a clear microphone and speak at a moderate pace.
- Zoom in on important UI elements for visibility.
- Keep the demo between 5-10 minutes total.
- If using live AI (OpenRouter), have your API key pre-entered in the sidebar.
- If internet is unavailable, the app falls back to the local diagnosis engine.
