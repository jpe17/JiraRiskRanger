import json
from google.oauth2 import service_account
from googleapiclient.discovery import build


class GoogleSheetsFetch:
    @staticmethod
    def get_service(credentials_json_path):
        with open(credentials_json_path, 'r') as file:
            creds_json = json.load(file)
        creds = service_account.Credentials.from_service_account_info(creds_json)
        service = build('sheets', 'v4', credentials=creds)
        return service

    @staticmethod
    def get_name_mapping(credentials_json_path, sheet_id, range_name):
        service = GoogleSheetsFetch.get_service(credentials_json_path)
        sheet = service.spreadsheets()
        result = sheet.values().get(spreadsheetId=sheet_id, range=range_name).execute()
        values = result.get('values', [])

        name_mapping = {}
        for row in values:
            if len(row) >= 2:
                name_mapping[row[0]] = row[1]
        return name_mapping

    @staticmethod
    def save_name_mapping_as_json(credentials_json_path, sheet_id, range_name, json_file_path):
        name_mapping = GoogleSheetsFetch.get_name_mapping(credentials_json_path, sheet_id, range_name)

        # Transforming the name mapping to the required JSON structure
        transformed_mapping = [{"Jira": key, "SF": value} for key, value in name_mapping.items()]

        with open(json_file_path, 'w') as file:
            json.dump(transformed_mapping, file, indent=4)

