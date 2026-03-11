import streamlit as st
import anthropic
import json
import time
import pandas as pd
import os

st.set_page_config(
    page_title="AI Ticket Triage Agent",
    page_icon="🎫",
    layout="wide"
)

# ── Styling ──────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=DM+Sans:wght@300;400;500;600;700&display=swap');

* { font-family: 'DM Sans', sans-serif; }

.stApp {
    background: #0A0A0F;
    color: #E8E8F0;
}

.main-title {
    font-family: 'DM Mono', monospace;
    font-size: 13px;
    letter-spacing: 0.2em;
    color: #666680;
    text-transform: uppercase;
    margin-bottom: 4px;
}

.main-heading {
    font-size: 42px;
    font-weight: 700;
    color: #F0F0FF;
    line-height: 1.1;
    margin-bottom: 8px;
}

.main-heading span {
    color: #6C63FF;
}

.sub-heading {
    font-size: 15px;
    color: #888899;
    font-weight: 400;
    margin-bottom: 40px;
}

.kpi-card {
    background: #13131F;
    border: 1px solid #1E1E30;
    border-radius: 12px;
    padding: 20px 24px;
    text-align: center;
}

.kpi-value {
    font-size: 32px;
    font-weight: 700;
    margin-bottom: 4px;
}

.kpi-label {
    font-size: 12px;
    color: #666680;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    font-family: 'DM Mono', monospace;
}

.ticket-input-box {
    background: #13131F;
    border: 1px solid #1E1E30;
    border-radius: 12px;
    padding: 24px;
    margin-bottom: 20px;
}

.result-card {
    background: #13131F;
    border: 1px solid #1E1E30;
    border-radius: 12px;
    padding: 24px;
    margin-top: 20px;
    animation: fadeIn 0.4s ease;
}

@keyframes fadeIn {
    from { opacity: 0; transform: translateY(8px); }
    to   { opacity: 1; transform: translateY(0); }
}

.tag {
    display: inline-block;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 600;
    font-family: 'DM Mono', monospace;
    letter-spacing: 0.05em;
    margin-right: 6px;
}

.tag-critical  { background: #3D1515; color: #FF6B6B; border: 1px solid #FF6B6B40; }
.tag-high      { background: #3D2A10; color: #FFB347; border: 1px solid #FFB34740; }
.tag-medium    { background: #2A2A10; color: #FFD700; border: 1px solid #FFD70040; }
.tag-low       { background: #0F2A1A; color: #4ADE80; border: 1px solid #4ADE8040; }
.tag-auto-yes  { background: #0F2A1A; color: #4ADE80; border: 1px solid #4ADE8040; }
.tag-auto-no   { background: #2A1515; color: #FF6B6B; border: 1px solid #FF6B6B40; }
.tag-blue      { background: #101830; color: #818CF8; border: 1px solid #818CF840; }
.tag-purple    { background: #1A1030; color: #C084FC; border: 1px solid #C084FC40; }

.result-label {
    font-size: 11px;
    color: #555570;
    text-transform: uppercase;
    letter-spacing: 0.15em;
    font-family: 'DM Mono', monospace;
    margin-bottom: 6px;
}

.result-value {
    font-size: 18px;
    font-weight: 600;
    color: #E8E8F0;
    margin-bottom: 16px;
}

.macro-box {
    background: #0D0D1A;
    border: 1px solid #6C63FF40;
    border-left: 3px solid #6C63FF;
    border-radius: 8px;
    padding: 14px 18px;
    font-family: 'DM Mono', monospace;
    font-size: 14px;
    color: #A5A5FF;
    margin-top: 8px;
}

.summary-box {
    background: #0D1A0D;
    border: 1px solid #4ADE8040;
    border-left: 3px solid #4ADE80;
    border-radius: 8px;
    padding: 14px 18px;
    font-size: 14px;
    color: #B0FFB0;
    margin-top: 8px;
    line-height: 1.6;
}

.divider {
    border: none;
    border-top: 1px solid #1E1E30;
    margin: 24px 0;
}

.batch-row {
    background: #13131F;
    border: 1px solid #1E1E30;
    border-radius: 8px;
    padding: 12px 16px;
    margin-bottom: 8px;
    display: flex;
    align-items: center;
    gap: 12px;
}

.stTextArea textarea {
    background: #0D0D1A !important;
    border: 1px solid #2A2A40 !important;
    border-radius: 8px !important;
    color: #E8E8F0 !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 14px !important;
}

.stTextArea textarea:focus {
    border-color: #6C63FF !important;
    box-shadow: 0 0 0 2px #6C63FF20 !important;
}

.stTextInput input {
    background: #0D0D1A !important;
    border: 1px solid #2A2A40 !important;
    color: #E8E8F0 !important;
    border-radius: 8px !important;
}

.stButton button {
    background: #6C63FF !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    font-size: 14px !important;
    padding: 10px 24px !important;
    transition: all 0.2s !important;
    width: 100%;
}

.stButton button:hover {
    background: #5B52EE !important;
    transform: translateY(-1px) !important;
}

.stSelectbox select, div[data-baseweb="select"] {
    background: #0D0D1A !important;
    border: 1px solid #2A2A40 !important;
    color: #E8E8F0 !important;
}

div[data-baseweb="tab-list"] {
    background: #13131F !important;
    border-radius: 10px !important;
    padding: 4px !important;
    border: 1px solid #1E1E30 !important;
}

div[data-baseweb="tab"] {
    color: #666680 !important;
    font-weight: 500 !important;
}

div[aria-selected="true"][data-baseweb="tab"] {
    background: #6C63FF !important;
    color: white !important;
    border-radius: 8px !important;
}

.stSpinner > div { border-top-color: #6C63FF !important; }

footer { display: none; }
#MainMenu { display: none; }
header { display: none; }
</style>
""", unsafe_allow_html=True)

# ── Classifier ───────────────────────────────────────────────────────────────
SYSTEM_PROMPT = """You are a support operations analyst for Wealthsimple, a Canadian fintech company.
Classify each support ticket and return ONLY a valid JSON object with these exact keys:
{
  "issue_type": one of ["Account Access", "Billing & Payments", "Technical Bug", "KYC & Compliance", "Portfolio & Trading", "Product Education", "Feature Request", "Security"],
  "urgency": one of ["Low", "Medium", "High", "Critical"],
  "sentiment": one of ["Positive", "Neutral", "Frustrated", "Angry"],
  "can_be_automated": true or false,
  "recommended_macro": a short macro name like "Reset Password Flow",
  "one_line_summary": a single sentence describing the ticket for an agent dashboard,
  "estimated_handle_time_mins": integer between 2 and 20
}
Return ONLY the JSON. No explanation, no markdown."""


def classify_ticket(api_key, subject, description, channel="web"):
    client = anthropic.Anthropic(api_key=api_key)
    msg = f"Subject: {subject}\nDescription: {description}\nChannel: {channel}"
    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=300,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": msg}]
    )
    return json.loads(response.content[0].text.strip())


# ── Header ───────────────────────────────────────────────────────────────────
col_title, col_badge = st.columns([3, 1])
with col_title:
    st.markdown('<div class="main-title">Wealthsimple Support Operations</div>', unsafe_allow_html=True)
    st.markdown('<div class="main-heading">AI Ticket <span>Triage</span> Agent</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-heading">Classifies support tickets by urgency, sentiment, issue type, and automation potential in real time.</div>', unsafe_allow_html=True)

# ── API Key ───────────────────────────────────────────────────────────────────
# Read from Streamlit secrets first, then env var, then manual input
api_key = ""
try:
    api_key = st.secrets["ANTHROPIC_API_KEY"]
except Exception:
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")

if not api_key:
    with st.expander("🔑 Enter your Anthropic API Key", expanded=True):
        api_key = st.text_input("API Key", type="password", placeholder="sk-ant-...", label_visibility="collapsed")
        st.caption("Get a free key at console.anthropic.com — this demo costs under $0.01")

st.markdown('<hr class="divider">', unsafe_allow_html=True)

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs(["  Single Ticket  ", "  Batch Demo  ", "  How It Works  "])

# ── TAB 1: Single Ticket ──────────────────────────────────────────────────────
with tab1:
    # Process any pending example load before widgets render
    if st.session_state.get("_pending_example"):
        ex = st.session_state.pop("_pending_example")
        st.session_state["_subject"] = ex["subject"]
        st.session_state["_description"] = ex["description"]
        st.session_state["_channel"] = ex["channel"]

    col_form, col_result = st.columns([1, 1], gap="large")

    with col_form:
        st.markdown("#### Paste a support ticket")

        subject = st.text_input("Subject line", key="_subject", placeholder="e.g. Can't log into my account")

        description = st.text_area(
            "Ticket description",
            key="_description",
            placeholder="e.g. I've been trying to log in for the past hour and keep getting an invalid credentials error...",
            height=160
        )

        channel = st.selectbox("Channel", ["email", "web", "chat", "phone"], key="_channel")

        # Example tickets
        st.markdown('<div class="result-label" style="margin-top:16px">Try an example</div>', unsafe_allow_html=True)
        ex_col1, ex_col2, ex_col3 = st.columns(3)

        examples = {
            "🔴 Security breach": {
                "subject": "Account hacked — change password",
                "description": "Someone accessed my account and changed my email address. I am locked out. This is a SECURITY BREACH.",
                "channel": "phone"
            },
            "🟡 Billing issue": {
                "subject": "Wrong amount withdrawn from bank",
                "description": "A $500 withdrawal appeared on my bank statement that I did not authorize. Please investigate immediately.",
                "channel": "email"
            },
            "🟢 Simple FAQ": {
                "subject": "How do I open an FHSA?",
                "description": "Hi, I'm interested in opening a First Home Savings Account. Can you walk me through the steps?",
                "channel": "web"
            }
        }

        with ex_col1:
            if st.button("🔴 Security", use_container_width=True):
                st.session_state["_pending_example"] = examples["🔴 Security breach"]
                st.rerun()
        with ex_col2:
            if st.button("🟡 Billing", use_container_width=True):
                st.session_state["_pending_example"] = examples["🟡 Billing issue"]
                st.rerun()
        with ex_col3:
            if st.button("🟢 FAQ", use_container_width=True):
                st.session_state["_pending_example"] = examples["🟢 Simple FAQ"]
                st.rerun()

        st.markdown("")
        run_btn = st.button("⚡ Triage this ticket", use_container_width=True)

    with col_result:
        st.markdown("#### Classification result")

        if run_btn:
            if not api_key:
                st.error("Add your API key above first.")
            elif not subject or not description:
                st.warning("Fill in both the subject and description.")
            else:
                with st.spinner("Classifying..."):
                    try:
                        result = classify_ticket(api_key, subject, description, channel)

                        urgency = result.get("urgency", "Medium")
                        urg_class = urgency.lower()
                        auto = result.get("can_be_automated", False)
                        mins = result.get("estimated_handle_time_mins", 5)

                        # Tags row
                        st.markdown(f"""
                        <div style="margin-bottom:20px">
                            <span class="tag tag-{urg_class}">{urgency}</span>
                            <span class="tag tag-{'auto-yes' if auto else 'auto-no'}">{'✓ Automatable' if auto else '✗ Needs human'}</span>
                            <span class="tag tag-blue">{result.get('issue_type','')}</span>
                            <span class="tag tag-purple">{result.get('sentiment','')}</span>
                        </div>
                        """, unsafe_allow_html=True)

                        # Summary
                        st.markdown('<div class="result-label">Agent summary</div>', unsafe_allow_html=True)
                        st.markdown(f'<div class="summary-box">{result.get("one_line_summary","")}</div>', unsafe_allow_html=True)

                        # Macro
                        st.markdown('<div class="result-label" style="margin-top:16px">Recommended next step</div>', unsafe_allow_html=True)
                        st.markdown(f'<div class="macro-box">→ {result.get("recommended_macro","")}</div>', unsafe_allow_html=True)

                        # Stats
                        st.markdown('<div style="margin-top:20px">', unsafe_allow_html=True)
                        m1, m2 = st.columns(2)
                        with m1:
                            st.markdown(f"""
                            <div class="kpi-card">
                                <div class="kpi-value" style="color:#818CF8">{mins} min</div>
                                <div class="kpi-label">Handle time</div>
                            </div>""", unsafe_allow_html=True)
                        with m2:
                            saving = mins if auto else 0
                            st.markdown(f"""
                            <div class="kpi-card">
                                <div class="kpi-value" style="color:#4ADE80">{saving} min</div>
                                <div class="kpi-label">Time saved if automated</div>
                            </div>""", unsafe_allow_html=True)

                    except Exception as e:
                        st.error(f"Classification failed: {str(e)}")
        else:
            st.markdown("""
            <div style="background:#13131F; border:1px dashed #2A2A40; border-radius:12px; padding:48px 24px; text-align:center; color:#444460">
                <div style="font-size:32px; margin-bottom:12px">🎫</div>
                <div style="font-size:14px">Enter a ticket and click Triage<br>or try one of the examples</div>
            </div>
            """, unsafe_allow_html=True)

# ── TAB 2: Batch Demo ─────────────────────────────────────────────────────────
with tab2:
    st.markdown("#### Run the 10-ticket batch demo")
    st.markdown('<div style="color:#888899; font-size:14px; margin-bottom:24px">Watch the agent classify 10 real Wealthsimple-style tickets in real time. Shows variety: Critical to Low urgency, automatable and not.</div>', unsafe_allow_html=True)

    BATCH_TICKETS = [
        {"subject": "Account hacked — change password immediately", "description": "Someone accessed my account and changed my email address. I am locked out. This is a SECURITY BREACH.", "channel": "phone"},
        {"subject": "Wrong amount withdrawn from bank", "description": "A $500 withdrawal appeared on my bank statement that I did not authorize. Please investigate immediately.", "channel": "email"},
        {"subject": "Incorrect capital gains report", "description": "My capital gains summary shows a $2,400 gain on a stock I sold at a loss. This is wrong and will mess up my taxes.", "channel": "email"},
        {"subject": "App keeps crashing on iPhone", "description": "Every time I open the Wealthsimple app it crashes within 30 seconds. iPhone 14, iOS 17.2.", "channel": "email"},
        {"subject": "Bank linking keeps failing", "description": "I've tried to link my RBC chequing account 6 times. It keeps saying connection failed at the final step.", "channel": "email"},
        {"subject": "TFSA contribution room question", "description": "I contributed $6,500 this year but my dashboard shows I'm over my limit. Is there a system error?", "channel": "email"},
        {"subject": "Verification email never arrived", "description": "I signed up 3 days ago and still haven't received my verification email. Checked spam folder too.", "channel": "web"},
        {"subject": "How do I open an FHSA?", "description": "Hi, I'm interested in opening a First Home Savings Account. Can you walk me through the steps?", "channel": "web"},
        {"subject": "Round-up investing feature request", "description": "Would love a feature to choose which account my spare change goes into. Any plans for this?", "channel": "web"},
        {"subject": "What are Wealthsimple's MER fees?", "description": "Can you tell me the management expense ratios for your ETF portfolios? Comparing to other robo-advisors.", "channel": "web"},
    ]

    if st.button("▶ Run batch demo", use_container_width=False):
        if not api_key:
            st.error("Add your API key above first.")
        else:
            results = []
            progress = st.progress(0)
            status_text = st.empty()
            results_container = st.container()

            for i, ticket in enumerate(BATCH_TICKETS):
                status_text.markdown(f'<div style="color:#888899; font-size:13px; font-family:DM Mono">Classifying ticket {i+1}/10: {ticket["subject"][:50]}...</div>', unsafe_allow_html=True)

                try:
                    result = classify_ticket(api_key, ticket["subject"], ticket["description"], ticket["channel"])
                    results.append({**ticket, **result})

                    urgency = result.get("urgency", "Medium")
                    urg_class = urgency.lower()
                    auto = result.get("can_be_automated", False)

                    with results_container:
                        st.markdown(f"""
                        <div style="background:#13131F; border:1px solid #1E1E30; border-radius:8px; padding:12px 16px; margin-bottom:6px; display:flex; align-items:center; gap:12px">
                            <span class="tag tag-{urg_class}" style="min-width:72px; text-align:center">{urgency}</span>
                            <span style="font-size:13px; color:#C0C0D0; flex:1">{ticket['subject']}</span>
                            <span class="tag tag-{'auto-yes' if auto else 'auto-no'}">{'✓ Auto' if auto else '✗ Manual'}</span>
                        </div>
                        """, unsafe_allow_html=True)

                except Exception as e:
                    st.warning(f"Ticket {i+1} failed: {str(e)}")

                progress.progress((i + 1) / len(BATCH_TICKETS))
                time.sleep(0.2)

            status_text.empty()
            progress.empty()

            if results:
                total = len(results)
                auto_count = sum(1 for r in results if r.get("can_be_automated"))
                time_saved = sum(r.get("estimated_handle_time_mins", 0) for r in results if r.get("can_be_automated"))
                critical = sum(1 for r in results if r.get("urgency") == "Critical")
                containment = auto_count / total * 100

                st.markdown('<hr class="divider">', unsafe_allow_html=True)
                st.markdown("#### Batch summary")
                k1, k2, k3, k4 = st.columns(4)
                metrics = [
                    (k1, str(total), "Tickets classified", "#818CF8"),
                    (k2, f"{containment:.0f}%", "Containment rate", "#4ADE80"),
                    (k3, f"{time_saved} min", "Time saved", "#C084FC"),
                    (k4, str(critical), "Critical tickets", "#FF6B6B"),
                ]
                for col, val, label, color in metrics:
                    with col:
                        st.markdown(f"""
                        <div class="kpi-card">
                            <div class="kpi-value" style="color:{color}">{val}</div>
                            <div class="kpi-label">{label}</div>
                        </div>""", unsafe_allow_html=True)

# ── TAB 3: How It Works ───────────────────────────────────────────────────────
with tab3:
    st.markdown("#### How the pipeline works")

    steps = [
        ("01", "Input", "A CSV of Zendesk-format tickets comes in — ticket ID, subject, description, channel, and user-reported priority."),
        ("02", "Classify", "Each ticket is sent to Claude Haiku with a structured system prompt. The model returns a JSON object with issue type, urgency, sentiment, automation flag, recommended macro, and handle time estimate."),
        ("03", "Validate", "If the API returns malformed JSON, the agent catches the error and writes a fallback classification — no ticket is silently skipped."),
        ("04", "Output", "Results are written to a formatted Excel dashboard with 4 tabs: Executive Summary, All Tickets, Critical Queue, and Automation Candidates."),
        ("05", "Scale", "60 tickets classified in under 90 seconds for under $0.50. The same pipeline runs on 10,000 tickets with no changes to the code."),
    ]

    for num, title, desc in steps:
        st.markdown(f"""
        <div style="display:flex; gap:20px; margin-bottom:20px; align-items:flex-start">
            <div style="font-family:DM Mono; font-size:11px; color:#6C63FF; background:#101025; border:1px solid #6C63FF40; border-radius:6px; padding:4px 10px; min-width:36px; text-align:center; margin-top:2px">{num}</div>
            <div>
                <div style="font-weight:600; color:#E8E8F0; margin-bottom:4px">{title}</div>
                <div style="font-size:14px; color:#888899; line-height:1.6">{desc}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<hr class="divider">', unsafe_allow_html=True)
    st.markdown("#### Tech stack")
    cols = st.columns(4)
    stack = [
        ("Python", "Orchestration"),
        ("Claude Haiku", "Classification"),
        ("pandas + openpyxl", "Data & Excel output"),
        ("Streamlit", "This interface"),
    ]
    for col, (tool, role) in zip(cols, stack):
        with col:
            st.markdown(f"""
            <div class="kpi-card">
                <div style="font-weight:600; color:#E8E8F0; font-size:14px; margin-bottom:4px">{tool}</div>
                <div class="kpi-label">{role}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown('<hr class="divider">', unsafe_allow_html=True)
    st.markdown("""
    <div style="font-size:13px; color:#555570; font-family:DM Mono; text-align:center">
        Built by Mahin · Wealthsimple Workflow Optimization Portfolio · 2024
    </div>
    """, unsafe_allow_html=True)
