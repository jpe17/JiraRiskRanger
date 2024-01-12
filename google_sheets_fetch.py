import json
from google.oauth2 import service_account
from googleapiclient.discovery import build
from dotenv import load_dotenv
import os


class GoogleSheetsFetch:
    @staticmethod
    def read_cred():
        # Load environment variables
        load_dotenv()

        # Create a dictionary from the environment variables
        creds_dict = {
            "type": os.getenv("GOOGLE_SHEETS_TYPE"),
            "project_id": os.getenv("GOOGLE_SHEETS_PROJECT_ID"),
            "private_key_id": os.getenv("GOOGLE_SHEETS_PRIVATE_KEY_ID"),
            "private_key": os.getenv("GOOGLE_SHEETS_PRIVATE_KEY"),
            "client_email": os.getenv("GOOGLE_SHEETS_CLIENT_EMAIL"),
            "client_id": os.getenv("GOOGLE_SHEETS_CLIENT_ID"),
            "auth_uri": os.getenv("GOOGLE_SHEETS_AUTH_URI"),
            "token_uri": os.getenv("GOOGLE_SHEETS_TOKEN_URI"),
            "auth_provider_x509_cert_url": os.getenv("GOOGLE_SHEETS_AUTH_PROVIDER_X509_CERT_URL"),
            "client_x509_cert_url": os.getenv("GOOGLE_SHEETS_CLIENT_X509_CERT_URL")
        }

        return creds_dict

    @staticmethod
    def get_service():
        # Get the credentials dictionary
        creds_dict = GoogleSheetsFetch.read_cred()

        # Use the creds_dict to create credentials
        creds = service_account.Credentials.from_service_account_info(creds_dict)
        service = build('sheets', 'v4', credentials=creds)
        return service

    @staticmethod
    def get_name_mapping(sheet_id, range_name):
        service = GoogleSheetsFetch.get_service()
        sheet = service.spreadsheets()
        result = sheet.values().get(spreadsheetId=sheet_id, range=range_name).execute()
        values = result.get('values', [])

        name_mapping = {}
        for row in values:
            if len(row) >= 2:
                name_mapping[row[0]] = row[1]
        return name_mapping

    @staticmethod
    def save_name_mapping_as_json(sheet_id, range_name, json_file_path):
        name_mapping = GoogleSheetsFetch.get_name_mapping(sheet_id, range_name)

        # Transforming the name mapping to the required JSON structure
        transformed_mapping = [{"Jira": key, "SF": value} for key, value in name_mapping.items()]

        with open(json_file_path, 'w') as file:
            json.dump(transformed_mapping, file, indent=4)

