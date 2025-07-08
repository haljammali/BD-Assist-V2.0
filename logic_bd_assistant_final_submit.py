
import streamlit as st
import datetime
import re
import base64

# ------------------ Page Setup ------------------
st.set_page_config(page_title="LOGIC BD Assistant", layout="wide")

# ------------------ LOGIC Styling ------------------
st.markdown("""
    <style>
        body {
            background-color: #F7F7F7;
        }
        .stApp {
            font-family: 'Segoe UI', sans-serif;
        }
        .block-container {
            padding: 2rem 3rem;
        }
        h1, h2, h3, h4 {
            color: #004236;
        }
        .stButton>button {
            background-color: #004236;
            color: white;
            border-radius: 6px;
            padding: 0.4em 1.2em;
        }
        .stDownloadButton>button {
            background-color: #C4A35A;
            color: white;
        }
        img.logo {
            width: 200px;
            margin-bottom: 1rem;
        }
    </style>
""", unsafe_allow_html=True)

# ------------------ LOGO ------------------
st.markdown('<img src="https://logic-consulting.com/wp-content/uploads/2021/03/logo-header.png" class="logo">', unsafe_allow_html=True)

# ------------------ App Title ------------------
st.title("LOGIC Business Development Assistant")
st.markdown("Analyze RFPs, generate timelines, estimate fees, and outline project roadmaps.")

# ------------------ Input Section ------------------
st.header("RFP Input")

rfp_text = st.text_area("Paste RFP content here", height=200)
uploaded_file = st.file_uploader("Or upload a .txt file", type=["txt"])
if uploaded_file:
    rfp_text = uploaded_file.read().decode("utf-8")

submit_clicked = st.button("Submit")

if not submit_clicked:
    st.stop()

if not rfp_text:
    st.warning("Please provide RFP content above and click Submit.")
    st.stop()

# ------------------ Auto-Detection Logic ------------------
st.header("Auto-Detected Client Profile")

# Deadline
deadline_match = re.search(r"(?:submit.*?on or before|deadline(?: for)? submission).*?(\b\w+day\b.*?\d{4})", rfp_text, re.IGNORECASE)
deadline_str = deadline_match.group(1).strip() if deadline_match else None
try:
    detected_deadline = datetime.datetime.strptime(deadline_str, "%A %B %d, %Y").date()
except:
    detected_deadline = datetime.date.today()

# Company Name
company_match = re.search(r"to\s+(.*?)\s+in conformity with the requirements", rfp_text, re.IGNORECASE)
company_name = company_match.group(1).strip() if company_match else "Unknown Company"

# Industry
industry_keywords = ["textile", "energy", "agriculture", "construction", "banking", "technology", "transport", "local development", "governance"]
industry_found = next((word for word in industry_keywords if word.lower() in rfp_text.lower()), "General")

# Employees
employee_match = re.search(r"(\d{2,5})\s+employee", rfp_text, re.IGNORECASE)
employee_count_detected = int(employee_match.group(1)) if employee_match else None
if employee_count_detected:
    if employee_count_detected < 50:
        emp_size = "< 50"
    elif employee_count_detected <= 100:
        emp_size = "50–100"
    elif employee_count_detected <= 250:
        emp_size = "101–250"
    elif employee_count_detected <= 500:
        emp_size = "251–500"
    elif employee_count_detected <= 1000:
        emp_size = "501–1000"
    else:
        emp_size = "> 1000"
else:
    emp_size = "Unknown"

# ------------------ Show Detected Info ------------------
st.markdown(f"**Proposal Deadline:** {detected_deadline.strftime('%Y-%m-%d')}")
st.markdown(f"**Company Name:** {company_name}")
st.markdown(f"**Industry (Detected):** {industry_found}")
st.markdown(f"**Estimated Employee Count:** {emp_size}")

proposal_deadline = st.date_input("Edit Proposal Deadline", value=detected_deadline)

# ------------------ Editable Fields ------------------
st.header("Client Profile")

location = st.selectbox("Location", ["EGYPT", "UAE", "KSA"])
revenue = st.selectbox("Client Top Line Revenue", ["< $5M", "$5M–$50M", "$50M–$500M", "> $500M"])
industry = st.selectbox("Industry", ["Non-Profit", "Government/Public", "Manufacturing", "Financial Services", "Tech/Startup", "Other"], index=5)
employees = st.selectbox("Employee Count", ["< 50", "50–100", "101–250", "251–500", "501–1000", "> 1000"])

# ------------------ Pricing Logic ------------------
currency_map = {"EGYPT": "USD", "UAE": "AED", "KSA": "SAR"}
daily_rate_map = {"EGYPT": 1100, "UAE": 10000, "KSA": 12500}
currency = currency_map[location]
base_daily_rate = daily_rate_map[location]

revenue_multiplier = {"< $5M": 0.8, "$5M–$50M": 1.0, "$50M–$500M": 1.2, "> $500M": 1.5}[revenue]
industry_multiplier = {
    "Non-Profit": 0.9,
    "Government/Public": 1.0,
    "Manufacturing": 1.1,
    "Financial Services": 1.3,
    "Tech/Startup": 1.2,
    "Other": 1.0
}[industry]

adjusted_daily_rate = base_daily_rate * revenue_multiplier * industry_multiplier

# ------------------ Timeline Estimate ------------------
st.header("Timeline & Fees")

word_count = len(rfp_text.split())
base_weeks = max(10, min(16, word_count // 300))  # Enforce minimum 10 weeks

employee_timeline_add = {
    "< 50": 0,
    "50–100": 1,
    "101–250": 2,
    "251–500": 3,
    "501–1000": 4,
    "> 1000": 5
}.get(employees, 0)

estimated_weeks = base_weeks + employee_timeline_add
estimated_days = estimated_weeks * 5
total_fees = adjusted_daily_rate * estimated_days

st.markdown(f"**Estimated Duration:** {estimated_weeks} weeks")
st.markdown(f"**Estimated Total Fees:** {currency} {total_fees:,.0f}")

# ------------------ Roadmap ------------------
st.header("Project Roadmap")

phases = ["Kickoff & Research", "Stakeholder Interviews", "Analysis & Insights", "Draft Report", "Final Presentation"]
phase_weeks = estimated_weeks // len(phases)
roadmap = ""
for i, phase in enumerate(phases):
    start = i * phase_weeks + 1
    end = start + phase_weeks - 1
    roadmap += f"- {phase} ({start}–{end} week)\n"

st.text_area("Suggested Roadmap", roadmap, height=150)

# ------------------ Download Summary ------------------
st.header("Download Summary")

summary = f"""PROJECT ASSESSMENT SUMMARY

Proposal Deadline: {proposal_deadline.strftime('%Y-%m-%d')}
Detected Company Name: {company_name}
Detected Industry: {industry_found}
Detected Employee Count Estimate: {emp_size}

Location: {location}
Currency: {currency}
Base Daily Rate: {base_daily_rate:,}
Adjusted Daily Rate: {adjusted_daily_rate:,.2f}
Revenue Tier: {revenue}
Industry: {industry}
Employee Count: {employees}
Estimated Duration: {estimated_weeks} weeks
Estimated Total Fees: {currency} {total_fees:,.0f}

ROADMAP:
{roadmap}
"""

b64 = base64.b64encode(summary.encode()).decode()
href = f'<a href="data:file/txt;base64,{b64}" download="project_summary.txt">Download Project Summary</a>'
st.markdown(href, unsafe_allow_html=True)
