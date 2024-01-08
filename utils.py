import json
from datetime import datetime
import pytz


def format_date(date_str):
    date_time = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S.%f%z")
    return date_time

def convert_date_in_israel_format(date):
    if date:
        # Get Israel timezone
        israel_tz = pytz.timezone('Israel')
        # Localize the date-time to Israel timezone
        date_in_israel_format = israel_tz.localize(date)
        return date_in_israel_format
    return None


def count_json_entries(file_path):
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
        return len(data)  # Counting the number of entries
    except FileNotFoundError:
        return "File not found. Please check the file path."
    except json.JSONDecodeError:
        return "Error decoding JSON. Please check the file content."
    except Exception as e:
        return f"An error occurred: {e}"
