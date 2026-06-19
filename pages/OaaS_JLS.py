import streamlit as st
import pandas as pd
import zipfile
import io
from jobspy import scrape_jobs
from concurrent.futures import ThreadPoolExecutor, as_completed

st.set_page_config(page_title="Job Listing Scraper", page_icon="💼", layout="wide")
st.title("Job Listing Scraper")
st.markdown("Note: Search for job listings targeting potential OaaS clients across multiple platforms using jobspy")

# ─────────────────────────────────────────────────────────────
# 🔹 Sidebar Filters
# ─────────────────────────────────────────────────────────────
st.sidebar.header("Search Parameters")
site_options = ["linkedin", "indeed", "glassdoor", "zip_recruiter", "dice"]
selected_sites = st.sidebar.multiselect("Select Job Sites", options=site_options, default=["linkedin", "indeed", "glassdoor"])

search_term = st.sidebar.text_input("Job Title or Keywords", "KYC Analyst")
location = st.sidebar.text_input("Target Location", "United States")

st.sidebar.markdown("---")
st.sidebar.subheader("Advanced Filters")

date_options = {
    "Any time": None,
    "Past 24 hours": 1,
    "Past 3 days": 3,
    "Past week": 7,
    "Past month": 30
}
date_posted = st.sidebar.selectbox("Date Posted", options=list(date_options.keys()))

experience_options = {
    "Any": None,
    "Entry level": "ENTRY_LEVEL",
    "Mid level": "MID_LEVEL",
    "Senior level": "SENIOR_LEVEL"
}
experience_level = st.sidebar.selectbox("Experience Level", options=list(experience_options.keys()))

job_type_options = {
    "Any": None,
    "Full-time": "FULLTIME",
    "Part-time": "PARTTIME",
    "Contract": "CONTRACT",
    "Internship": "INTERNSHIP"
}
job_type = st.sidebar.selectbox("Job Type", options=list(job_type_options.keys()))

remote_options = {
    "Any": None,
    "Remote only": "REMOTE"
}
remote = st.sidebar.selectbox("Remote Options", options=list(remote_options.keys()))

results_count = st.sidebar.slider("Maximum Results", min_value=10, max_value=200, value=50, step=10)

search_button = st.sidebar.button("Search Jobs", type="primary")

# ─────────────────────────────────────────────────────────────
# 🔹 Role-Location Maps
# ─────────────────────────────────────────────────────────────
CS_role_location_map = {
    "Compliance Specialist": ["USA", "UK", "Canada", "Australia"]
}

DDA_role_location_map = {
    "Due Diligence Analyst": ["UK", "Netherlands", "Germany", "United Arab Emirates"]
}

KYC_role_location_map = {
    "KYC Analyst": ["USA", "UK", "Ireland", "Luxembourg", "Netherlands", "United Arab Emirates"]
}

FCA_role_location_map = {
    "Financial Crime Analyst": ["USA", "UK", "Germany", "France", "United Arab Emirates", "Saudi Arabia"]
}

CA_role_location_map = {
    "BSA/AML Compliance Analyst": ["USA"]
}

MLRO_role_location_map = {
    "Money Laundering Reporting Officer": ["UK", "Ireland", "Germany", "France", "UAE", "Saudi Arabia"]
}

HVOR_role_location_map = {
    "AML Analyst": ["USA", "UK", "Germany", "United Arab Emirates", "Netherlands", "Ireland"],
    "Transaction Monitoring Analyst": ["USA", "UK", "Ireland", "United Arab Emirates", "Netherlands"],
    "Sanctions Analyst": ["USA", "UK", "France", "Germany", "Switzerland", "United Arab Emirates"],
    "Customer Due Diligence Analyst": ["UK", "Germany", "France", "Luxembourg", "United Arab Emirates"],
    "Enhanced Due Diligence Analyst": ["USA", "UK", "Ireland", "Netherlands"],
    "OFAC Analyst": ["USA"],
    "Compliance Associate": ["USA", "UK", "Ireland", "France"],
    "KYC/CDD/EDD Specialist": ["UK", "Germany", "Ireland", "Netherlands"],
    "Customer Onboarding Analyst": ["UK", "Luxembourg", "Ireland", "United Arab Emirates"],
    "Due Diligence Analyst": ["UK", "Netherlands", "Germany", "United Arab Emirates"],
    "Sanctions & Embargoes Analyst": ["Germany", "Switzerland", "France"],
    "Legal & Compliance Analyst": ["France", "Germany", "United Arab Emirates"],
    "Fraud Investigator": ["USA", "UK", "Ireland", "United Arab Emirates"]
}

LSAML_role_location_map = {
    "AML Compliance Officer": ["USA", "UK", "Germany", "France", "United Arab Emirates", "Saudi Arabia"],
    "Risk & Compliance Analyst - AML": ["USA", "UK", "Germany", "France", "United Arab Emirates"],
    "Deputy MLRO": ["UK", "Germany", "Luxembourg", "UAE"],
    "Compliance Monitoring Officer (AML-focused)": ["UK", "Germany", "Ireland", "United Arab Emirates"],
    "Anti-Financial Crime Officer": ["Germany", "Switzerland", "Netherlands", "France"],
    "Financial Crime Compliance Manager": ["UK", "Germany", "UAE", "Saudi Arabia"],
    "Head of Financial Crime Compliance": ["UK", "Germany", "UAE", "Switzerland"],
    "Compliance Business Partner (AML)": ["UK", "Germany", "France"],
    "Financial Crime Risk Officer": ["UK", "Germany", "United Arab Emirates"],
    "CAMS-Certified Compliance Professional": ["UK", "USA", "Switzerland", "United Arab Emirates"]
}

# Selectable role groupings
role_groups_available = {
    "Compliance Specialist (CS)": CS_role_location_map,
    "Due Diligence Analyst (DDA)": DDA_role_location_map,
    "KYC Analyst (KYC)": KYC_role_location_map,
    "Financial Crime Analyst (FCA)": FCA_role_location_map,
    "BSA/AML Compliance Analyst (CA)": CA_role_location_map,
    "MLRO Roles (MLRO)": MLRO_role_location_map,
    "High-Volume OaaS Roles (HVOR)": HVOR_role_location_map,
    "Large Scale AML Roles (LSAML)": LSAML_role_location_map
}

st.sidebar.markdown("---")
st.sidebar.subheader("Batch Role Group Selection")
selected_role_groups = st.sidebar.multiselect(
    "Select Role Groups to Run in Batch Search",
    options=list(role_groups_available.keys()),
    default=["High-Volume OaaS Roles (HVOR)"]
)
batch_button = st.sidebar.button("Run Batch Search", type="secondary")
# ─────────────────────────────────────────────────────────────
# 🔹 Job Search Functions
# ─────────────────────────────────────────────────────────────
def search_jobs():
    with st.spinner("Searching for jobs..."):
        try:
            jobs = scrape_jobs(
                site_name=selected_sites,
                search_term=search_term,
                location=location,
                results_wanted=results_count,
                days_ago=date_options[date_posted],
                job_type=job_type_options[job_type],
                experience_level=experience_options[experience_level],
                country_indeed=location,
                linkedin_fetch_description=True,
                remote_only=(remote_options[remote] == "REMOTE")
            )
            return jobs
        except Exception as e:
            st.error(f"Error searching jobs: {str(e)}")
            return None

def batch_search_jobs():
    # Combine selected mappings
    role_location_map = {}
    for group in selected_role_groups:
        role_location_map.update(role_groups_available[group])

    search_tasks = [(role, loc) for role, locs in role_location_map.items() for loc in locs]
    total = len(search_tasks)
    progress = st.progress(0, text="Starting batch search...")
    results = []
    csv_files = []
    grouped = {}

    def fetch(role, loc):
        try:
            jobs = scrape_jobs(
                site_name=selected_sites,
                search_term=role,
                location=loc,
                results_wanted=results_count,
                days_ago=date_options[date_posted],
                job_type=job_type_options[job_type],
                experience_level=experience_options[experience_level],
                country_indeed=loc,
                linkedin_fetch_description=True,
                remote_only=(remote_options[remote] == "REMOTE")
            )
            if not jobs.empty:
                jobs["Search Job Title"] = role
                jobs["Search Location"] = loc
                return (role, jobs)
        except Exception as e:
            st.error(f"❌ {role} in {loc} failed: {e}")
        return None

    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {executor.submit(fetch, r, l): (r, l) for r, l in search_tasks}
        for i, future in enumerate(as_completed(futures)):
            progress.progress((i + 1) / total, text=f"{i + 1} of {total} searches complete")
            result = future.result()
            if result:
                role, jobs = result
                results.append(jobs)
                grouped.setdefault(role, []).append(jobs)

    progress.empty()

    for role, dfs in grouped.items():
        df = pd.concat(dfs, ignore_index=True)
        csv_files.append((f"{role.replace(' ', '_')}.csv", df.to_csv(index=False).encode("utf-8")))

    if csv_files:
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w") as zf:
            for name, content in csv_files:
                zf.writestr(name, content)
        return pd.concat(results, ignore_index=True), zip_buffer.getvalue()
    return pd.DataFrame(), None

# ─────────────────────────────────────────────────────────────
# 🔹 Run
# ─────────────────────────────────────────────────────────────
if search_button or batch_button or 'jobs_data' in st.session_state:
    if search_button or batch_button or st.session_state.get('refresh_data', False):
        if batch_button:
            jobs_df, zip_data = batch_search_jobs()
        else:
            jobs_df = search_jobs()
            zip_data = None

        if jobs_df is not None and not jobs_df.empty:
            st.session_state['jobs_data'] = jobs_df
            st.session_state['zip_data'] = zip_data
            st.session_state['refresh_data'] = False
        elif 'jobs_data' not in st.session_state:
            st.warning("No jobs found with the selected criteria.")
            st.stop()

    if 'jobs_data' in st.session_state:
        jobs_df = st.session_state['jobs_data']
        st.subheader("Search Results")

        search_filter = st.text_input("Filter results (search in all fields)", "")
        column_order = [
            "id", "title", "company", "location", "description", "date_posted",
            "site", "For Priority", "job_url", "job_url_direct",
            "job_type", "salary_source", "interval", "min_amount", "max_amount", "currency",
            "is_remote", "job_level", "job_function", "listing_type", "emails",
            "company_industry", "company_url", "company_logo", "company_url_direct",
            "company_addresses", "company_num_employees", "company_revenue", "company_description", "Current Week", "To Approach", "Search Job Title", "Search Location"
        ]
        jobs_df["Search Job Title"] = jobs_df.get("Search Job Title", "")
        jobs_df["Search Location"] = jobs_df.get("Search Location", "")
        filtered_df = jobs_df[[col for col in column_order if col in jobs_df.columns]]

        if search_filter:
            mask = pd.Series(False, index=filtered_df.index)
            for col in filtered_df.columns:
                if filtered_df[col].dtype == 'object':
                    mask |= filtered_df[col].astype(str).str.contains(search_filter, case=False, na=False)
            filtered_df = filtered_df[mask]

        st.download_button("Download Combined Results (CSV)", filtered_df.to_csv(index=False), "job_search_results.csv", "text/csv")

        if batch_button and st.session_state.get("zip_data"):
            st.download_button("Download All Roles as ZIP", st.session_state["zip_data"], "batch_job_results.zip", "application/zip")

        st.dataframe(filtered_df, use_container_width=True, hide_index=True, height=600)
else:
    st.info("👈 Set search parameters or choose a batch role group to get started.")
