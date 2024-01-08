import json
import os
from simple_salesforce import Salesforce as SF


class SalesforceConnect:
    def __init__(self):
        self.sf = SF(
            username=os.getenv('SALESFORCE_USERNAME'),
            password=os.getenv('SALESFORCE_PASSWORD'),
            security_token=os.getenv('SALESFORCE_SECURITY_TOKEN'),
        )

    def get_ARR(self, customer_name):
        # Escaping single quotes in the customer name
        safe_customer_name = customer_name.replace("'", "\\'")
        query = f"SELECT Direct_Account_ARR__c FROM Account WHERE Name = '{safe_customer_name}'"
        try:
            records = self.sf.query(query)
            return records['records'][0]['Direct_Account_ARR__c'] if records['records'] else 0
        except Exception as e:
            print(f"Error: {e}")
            return 0

    def update_json_with_ARR(self, json_file_path):
        with open(json_file_path, 'r') as file:
            data = json.load(file)

        for entry in data:
            customer_name = entry['SF']
            entry['ARR'] = self.get_ARR(customer_name)

        with open(json_file_path, 'w') as file:
            json.dump(data, file, indent=4)


