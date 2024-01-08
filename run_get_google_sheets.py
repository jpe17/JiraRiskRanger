from dotenv import load_dotenv
from google_sheets_fetch import GoogleSheetsFetch
from salesforce_connect import SalesforceConnect

# Load environment variables
load_dotenv()

"GETTING DATA FROM GOOGLE SHEETS"

sheet_id = '1k4qM9l0Ln9SQ4GvqkRJW_DVOD4S1OptjD9cl7PHeu3Y'
range_name = 'Jira Customer names & SFDC!A:B'
json_file_path = 'jira_sf_mapping.json'
GoogleSheetsFetch.save_name_mapping_as_json('google_sheets_credentials.json', sheet_id, range_name, json_file_path)

"GETTING ARR FROM SALESFORCE"

sf_instance = SalesforceConnect()
sf_instance.update_json_with_ARR('jira_sf_mapping.json')