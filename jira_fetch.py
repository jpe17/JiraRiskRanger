from jira import JIRA as JIRA_Client
import os
import json


class JiraFetch:
    def __init__(self):
        self.jira = JIRA_Client(
            basic_auth=(os.getenv('JIRA_USERNAME'), os.getenv('JIRA_TOKEN')),
            server=os.getenv('JIRA_SERVER')
        )

    def search_issues(self, jql_query, maxResults=100, fields=None, expand=None):
        startAt = 0
        all_issues = []

        while True:
            issues = self.jira.search_issues(jql_query, startAt=startAt, maxResults=maxResults, fields=fields,
                                             expand=expand)
            all_issues.extend(issues)

            # Check if we have fetched all issues
            if len(issues) < maxResults:
                break
            startAt += len(issues)

        return all_issues

    def extract_status_transitions(self, issue):
        transitions = []
        if hasattr(issue, 'changelog'):
            for history in issue.changelog.histories:
                for item in history.items:
                    if item.field == 'status':
                        transitions.append({
                            'date': history.created,
                            'from': item.fromString,
                            'to': item.toString
                        })
        return transitions

    def format_issue_data(self, issue):
        # Extracting component names
        components = [c.name for c in issue.fields.components] if issue.fields.components else None

        # Handling CustomFieldOption for customers
        customer_field = getattr(issue.fields, 'customfield_10071', None)
        if customer_field:
            customers = [c.value for c in customer_field] if isinstance(customer_field, list) else customer_field.value
        else:
            customers = None

        # Handling CustomFieldOption for customers
        if issue.fields.priority:
            priority_field = str(issue.fields.priority)
        else:
            priority_field = None

        return {
            "Issue Type": issue.fields.issuetype.name if issue.fields.issuetype else None,
            "Key": issue.key,
            "Summary": issue.fields.summary,
            "Assignee": issue.fields.assignee.displayName if issue.fields.assignee else None,
            "Status": issue.fields.status.name if issue.fields.status else None,
            "Created": issue.fields.created,
            "Due date": issue.fields.duedate,
            "Priority Rank": getattr(issue.fields, 'customfield_10169', None),
            "Region": str(getattr(issue.fields, 'customfield_10173', None)),
            "Labels": issue.fields.labels,
            "Reporter": issue.fields.reporter.displayName if issue.fields.reporter else None,
            "Mission type": str(getattr(issue.fields, 'customfield_10175', None)),
            "Module": str(getattr(issue.fields, 'customfield_10074', None)),
            "Component": components,
            "Σ Time Spent": issue.fields.aggregatetimespent,
            "Σ Original Estimate": issue.fields.aggregatetimeoriginalestimate,
            "Status Transitions": self.extract_status_transitions(issue),
            "Customers": customers,
            "Customer Phase": str(getattr(issue.fields, 'customfield_10174', None)),
            "Priority": priority_field
        }

    def write_issues_to_json(self, issues, file_name):
        # Formats the issue data and writes it to a JSON file
        formatted_data = [self.format_issue_data(issue) for issue in issues]
        with open(file_name, 'w') as file:
            json.dump(formatted_data, file, indent=4)
        print(f"Data written to {file_name}")
