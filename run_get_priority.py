import pandas as pd
import streamlit as st
from jira_fetch import JiraFetch
from jira_calculate_risk import JiraCalculateRisk
from utils import count_json_entries
from dotenv import load_dotenv
import io

# Load environment variables
load_dotenv()

# Streamlit app title
st.title('JIRA PRIORITY RANK')

# Define JQL queries for each region
jql_queries = {
    "EMEA": 'project = OS AND statusCategory = 2 AND status != "Blocked By Dev" AND "Module[Dropdown]" = SA AND "Priority Rank[Number]" is not EMPTY AND "Region[Dropdown]" in (EMEA) ORDER BY cf[10169] ASC',
    "APAC": 'project = OS AND statusCategory = 2 AND "Module[Dropdown]" = SA AND "Region[Dropdown]" in ("APAC++") AND "Priority Rank[Number]" is not EMPTY ORDER BY cf[10169] ASC',
    "NA": 'project = OS AND statusCategory = 2 AND "Module[Dropdown]" = SA AND "Priority Rank[Number]" is not EMPTY AND "Region[Dropdown]" in ("North America") AND "Customer Phase[Dropdown]" in (Ongoing, Onboarding, Prospect) ORDER BY cf[10169] ASC',
    "LATAM": 'project = OS AND statusCategory = 2 AND "Module[Dropdown]" = SA AND "Priority Rank[Number]" is not EMPTY AND "Region[Dropdown]" in (latam) ORDER BY cf[10169] ASC',
    "Global": 'project = OS AND (labels != backlog OR labels is EMPTY) AND statusCategory = "To Do" AND (Module=SA OR type=Mission) AND "Priority Rank[Number]"!=EMPTY ORDER BY cf[10169] ASC, priority DESC, due ASC, updated ASC, created DESC'
}

# Initialize session state for selected JQL query and region name
if 'selected_jql' not in st.session_state:
    st.session_state.selected_jql = None
if 'selected_region' not in st.session_state:
    st.session_state.selected_region = None

# Horizontal layout for region buttons
cols = st.columns(5)
regions = list(jql_queries.keys())
for i, col in enumerate(cols):
    if col.button(regions[i]):
        st.session_state.selected_jql = jql_queries[regions[i]]
        st.session_state.selected_region = regions[i]

# Check if a region is selected
if st.session_state.selected_jql and st.session_state.selected_region:
    st.write(f"You have selected the region: {st.session_state.selected_region}")

    # Section for fetching data from JIRA
    if st.button('Fetch Data from JIRA'):
        jira = JiraFetch()
        fields = ['*all']
        tickets = jira.search_issues(st.session_state.selected_jql, fields=fields, expand='changelog')
        jira.write_issues_to_json(tickets, file_name='To_Do_jira_tickets.json')
        entry_count = count_json_entries('To_Do_jira_tickets.json')
        st.write(f"Imported {entry_count} issues successfully!")

    # Section for calculating risk
    if st.button('Calculate Risk'):
        jira_calc = JiraCalculateRisk('To_Do_jira_tickets.json', 'jira_sf_mapping.json', 'estimated_times.csv')
        report_df = jira_calc.get_prio_report_df()
        pd.set_option('display.max_columns', None)
        pd.set_option('display.float_format', '{:.1f}'.format)

        # Display the DataFrame in Streamlit
        st.dataframe(report_df)

        # Convert DataFrame to CSV
        csv = report_df.to_csv(index=False)
        # To convert to a CSV file in memory
        b = io.BytesIO()
        b.write(csv.encode())
        b.seek(0)

        # Create a download button and make the CSV file downloadable
        st.download_button(
            label="Download report as CSV",
            data=b,
            file_name='report.csv',
            mime='text/csv',
        )
