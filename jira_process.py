import json
import pandas as pd
from datetime import datetime, timedelta
from utils import format_date, convert_date_in_israel_format


class JiraProcess:
    @staticmethod
    def load_json(path, is_mapping=False):
        with open(path) as f:
            data = json.load(f)
        if is_mapping:
            return {item['Jira']: {'SF': item['SF'], 'ARR': item.get('ARR', 0)} for item in data}
        return data

    @staticmethod
    def load_csv(path):
        return pd.read_csv(path).set_index('Mission Type').to_dict('index')

    @staticmethod
    def get_ticket_id(ticket):
        return ticket.get("Key")

    @staticmethod
    def get_created_date(ticket):
        created_date = format_date(ticket["Created"])
        return created_date

    @staticmethod
    def get_closed_date(ticket):
        transitions = ticket["Status Transitions"]
        for transition in transitions:
            if transition['to'] == 'Closed' and ticket["Status"] == 'Closed':
                return format_date(transition['date'])
        return None

    @staticmethod
    def get_days_in_status(ticket, status):
        transitions = ticket["Status Transitions"]
        sorted_transitions = sorted(transitions, key=lambda x: format_date(x['date']))
        time_in_status = 0
        status_start = None

        for transition in sorted_transitions:
            if transition['to'] == status and status_start is None:
                status_start = format_date(transition['date'])
            elif transition['from'] == status and status_start:
                end_time = format_date(transition['date'])
                time_in_status += (end_time - status_start).total_seconds()
                status_start = None

        return time_in_status / (24 * 3600) if time_in_status > 0 else 0

    @staticmethod
    def get_mission_type(ticket):
        return ticket.get("Mission type")

    @staticmethod
    def get_region(ticket):
        return [ticket.get("Region")] or []

    @staticmethod
    def get_customers(ticket):
        return ticket.get("Customers") or []

    @staticmethod
    def get_customer_phase(ticket):
        return ticket.get("Customer Phase") or []

    @staticmethod
    def get_impact_to_customer(ticket):
        impact_to_customer = ticket.get("Priority")
        if impact_to_customer == "Highest":
            impact_to_customer_percent = 1.2
        elif impact_to_customer == "High":
            impact_to_customer_percent = 1.1
        elif impact_to_customer == "Medium":
            impact_to_customer_percent = 1.05
        elif impact_to_customer == "Low":
            impact_to_customer_percent = 1.0
        else:
            impact_to_customer_percent = 0.0
        return impact_to_customer_percent

    @staticmethod
    def get_due_date(ticket):
        due_date_str = ticket.get("Due date")
        if due_date_str:
            due_date = datetime.strptime(due_date_str, "%Y-%m-%d")
            due_date = convert_date_in_israel_format(due_date)
            return due_date
        return None

    def get_workdays_to_due(self, ticket, excluded=(6, 7)):
        due_date = self.get_due_date(ticket)
        if due_date is None:
            return None

        # Ensure due_date is a date object
        due_date = due_date.date() if isinstance(due_date, datetime) else due_date

        # Start from today's date
        today = datetime.now().date()
        # Initialize counter for workdays
        workdays = 0

        # Determine the increment or decrement step
        step = timedelta(days=1 if due_date >= today else -1)

        while today != due_date:
            if today.isoweekday() not in excluded:
                workdays += 1 if due_date >= today else -1
            today += step

        return workdays