import streamlit as st
import pandas as pd
from jobspy import scrape_jobs

st.set_page_config(page_title="Job Listing Scraper", page_icon="💼", layout="wide")

st.title("Job Listing Scraper")
st.markdown("Note: Search for jobs listings targeting potential OaaS clients across multiple platforms using jobspy")

# Sidebar for search parameters
st.sidebar.header("Search Parameters")
site_options = ["linkedin", "indeed", "glassdoor", "zip_recruiter", "dice"]
selected_sites = st.sidebar.multiselect(
    "Select Job Sites", 
    options=site_options,
    default=["linkedin", "indeed", "glassdoor"]
)

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

def search_jobs():
    with st.spinner("Searching for jobs... This may take a moment."):
        try:
            days_ago = date_options[date_posted]
            experience_level_param = experience_options[experience_level]
            job_type_param = job_type_options[job_type]
            remote_param = remote_options[remote]
            
            jobs = scrape_jobs(
                site_name=selected_sites,
                search_term=search_term,
                location=location,
                results_wanted=results_count,
                days_ago=days_ago,
                job_type=job_type_param,
                experience_level=experience_level_param,
                country_indeed=location,
                linkedin_fetch_description=True,
                remote_only=(remote_param == "REMOTE")
            )
            
            return jobs
        except Exception as e:
            st.error(f"Error searching jobs: {str(e)}")
            return None

if search_button or 'jobs_data' in st.session_state:
    if search_button or st.session_state.get('refresh_data', False):
        jobs_df = search_jobs()
        if jobs_df is not None and not jobs_df.empty:
            st.session_state['jobs_data'] = jobs_df
            st.session_state['refresh_data'] = False
        elif 'jobs_data' not in st.session_state:
            st.warning("No jobs found with the selected criteria. Try adjusting your search parameters.")
            st.stop()
    
    if 'jobs_data' in st.session_state:
        jobs_df = st.session_state['jobs_data']
        
        # Simple DataFrame display
        st.subheader("Search Results")
        
        # Allow user to filter results
        search_filter = st.text_input("Filter results (search in all fields)", "")
        
        # Filter the dataframe
        column_order = [
            "id", "title", "company", "location", "description", "date_posted",
            "site", "For Priority", "job_url", "job_url_direct", "job_type", "salary_source",
            "interval", "min_amount", "max_amount", "currency", "is_remote",
            "job_level", "job_function", "listing_type", "emails",
            "company_industry", "company_url", "company_logo", "company_url_direct",
            "company_addresses", "company_num_employees", "company_revenue", "company_description"
        ]
        filtered_df = jobs_df
        filtered_df["For Priority"] = ""
        filtered_df = filtered_df[[col for col in column_order if col in filtered_df.columns]]
        if search_filter:
            mask = pd.Series(False, index=filtered_df.index)
            for column in filtered_df.columns:
                if filtered_df[column].dtype == 'object':
                    column_mask = filtered_df[column].astype(str).str.contains(search_filter, case=False, na=False)
                    mask = mask | column_mask
            filtered_df = filtered_df[mask]
        
        # Show download button
        csv = filtered_df.to_csv(index=False)
        st.download_button(
            label="Download results as CSV",
            data=csv,
            file_name=f"job_search_results.csv",
            mime="text/csv",
        )
        
        # Display the filtered dataframe
        st.dataframe(
            filtered_df, 
            use_container_width=True,
            hide_index=True,
            height=600,
            column_config={
                "link": st.column_config.LinkColumn("Apply Link")
            }
        )
        
else:
    st.info("👈 Set your job search parameters in the sidebar and click 'Search Jobs' to get started!")