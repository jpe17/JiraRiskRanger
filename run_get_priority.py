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
st.title('JIRA RISK CALCULATOR')

# Streamlit input for JQL query
jql_query = st.text_input('Enter your JQL query',
                          'project = OS AND statusCategory = 2 AND status != "Blocked By Dev" AND "Module[Dropdown]" '
                          '= SA AND "Priority Rank[Number]" is not EMPTY AND "Region[Dropdown]" in (EMEA) ORDER BY '
                          'cf[10169] ASC')

# Section for fetching data from JIRA
if st.button('Fetch Data from JIRA'):
    jira = JiraFetch()
    fields = ['*all']
    tickets = jira.search_issues(jql_query, fields=fields, expand='changelog')
    jira.write_issues_to_json(tickets, file_name='To_Do_jira_tickets.json')
    entry_count = count_json_entries('To_Do_jira_tickets.json')
    st.write(f"Imported {entry_count} issues successfully!")

# Section for calculating risk
if st.button('Calculate Risk'):
    jira_calc = JiraCalculateRisk('To_Do_jira_tickets.json', 'jira_sf_mapping.json', 'estimated_times.csv')
    report_df = jira_calc.get_prio_report_df()

    # Set pandas options to display all columns
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
