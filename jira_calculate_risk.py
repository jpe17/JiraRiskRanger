import pandas as pd
from scipy.stats import norm
from jira_process import JiraProcess


class JiraCalculateRisk(JiraProcess):
    def __init__(self, file_path, json_mapping_path, csv_file_path):
        self.file_path = file_path
        self.json_mapping_path = json_mapping_path
        self.csv_file_path = csv_file_path
        self.tickets = self.load_json(self.file_path)
        self.mapping = self.load_json(self.json_mapping_path, True)
        self.estimated_times = self.load_csv(self.csv_file_path)

    def get_total_arr(self, ticket):
        total_arr = 0
        customers = self.get_customers(ticket)
        for customer in customers:
            customer_data = self.mapping.get(customer, {})
            arr_value = customer_data.get('ARR', 0)

            # Ensure arr_value is an integer
            arr_value = 0 if arr_value is None else arr_value
            total_arr += arr_value
        return total_arr

    def get_estimated_time_to_completion(self, ticket):
        mission_type = self.get_mission_type(ticket)
        if mission_type in self.estimated_times:
            return self.estimated_times[mission_type]['Mode']
        else:
            return None  # Or some default value

    def get_standard_deviation_to_completion(self, ticket):
        mission_type = self.get_mission_type(ticket)
        if mission_type in self.estimated_times:
            return self.estimated_times[mission_type]['Standard Deviation']

    def calculate_z_risk(self, ticket):
        if self.get_workdays_to_due(ticket) is not None and self.get_estimated_time_to_completion(
                ticket) is not None and self.get_standard_deviation_to_completion(
            ticket) is not None and self.get_standard_deviation_to_completion(ticket) != 0:
            return (self.get_workdays_to_due(ticket) - self.get_estimated_time_to_completion(
                ticket)) / self.get_standard_deviation_to_completion(ticket)
        else:
            return None

    def calculate_P_fail(self, ticket):
        return 100 - norm.cdf(self.calculate_z_risk(ticket)) * 100 if self.calculate_z_risk(
            ticket) is not None else None

    def calculate_P_fail_x_ARR(self, ticket):
        return self.calculate_P_fail(ticket) * self.get_total_arr(ticket) / 100 if self.calculate_P_fail(
            ticket) is not None else None

    def calculate_P_fail_x_ARR_x_ITC(self, ticket):
        return self.calculate_P_fail_x_ARR(ticket) * self.get_impact_to_customer(ticket) if (
                self.calculate_P_fail_x_ARR(ticket) is not None and self.get_impact_to_customer(
            ticket) is not None) else None
        return

    def generate_report(self):
        processed_data = []

        for ticket in self.tickets:
            processed_data.append({
                'ID': self.get_ticket_id(ticket),
                'Created': self.get_created_date(ticket).strftime("%Y-%m-%d") if self.get_created_date(
                    ticket) is not None else None,
                'Closed': self.get_closed_date(ticket).strftime("%Y-%m-%d") if self.get_closed_date(
                    ticket) is not None else None,
                'TIP': self.get_days_in_status(ticket, 'In Progress'),
                'Mission Type': self.get_mission_type(ticket),
                'Region': self.get_region(ticket),
                'Customer': self.get_customers(ticket),
                'Customer Phase': self.get_customer_phase(ticket),
                'Due Date': self.get_due_date(ticket).strftime("%Y-%m-%d") if self.get_due_date(
                    ticket) is not None else None,
                'ARR': self.get_total_arr(ticket),
                'ITC': self.get_impact_to_customer(ticket),
                'ETC': self.get_estimated_time_to_completion(ticket),
                'SD': self.get_standard_deviation_to_completion(ticket),
                'TTD': self.get_workdays_to_due(ticket),
                'Z': self.calculate_z_risk(ticket),
                'P': self.calculate_P_fail(ticket),
                '(P*ARR)': self.calculate_P_fail_x_ARR(ticket),
                '(P*ARR*ITC)': self.calculate_P_fail_x_ARR_x_ITC(ticket),
            })

        # Convert to DataFrame
        report_df = pd.DataFrame(processed_data)

        # Sort DataFrame by 'Calculated Risk (P*ARR)' in descending order
        report_df = report_df.sort_values(by='(P*ARR*ITC)', ascending=False)

        return report_df

    def get_report_df(self):
        return self.generate_report()

    @staticmethod
    def save_report_as_csv(report_df, filename):
        report_df.to_csv(filename, index=False)
