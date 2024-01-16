
# JIRA Risk Calculator

## Description

This project is a Python application that fetches data from JIRA based on a user-provided JQL query, calculates risk, and provides a downloadable report. The application utilizes several libraries including `jira`, `numpy`, `pandas`, `plotly`, `pytz`, and `streamlit`.

## Installation

To install the necessary dependencies for this project, clone the repository and run the following command in your terminal:

pip install -r requirements.txt

This will install the necessary Python libraries listed in the `requirements.txt` file.

## Usage

To use the application, run the `run_get_priority.py` script. The script will prompt you to enter a JQL query. After entering the query, you can fetch data from JIRA by clicking the 'Fetch Data from JIRA' button. Once the data is fetched, you can calculate the risk by clicking the 'Calculate Risk' button. The calculated risk will be displayed in a table, and you can download the report as a CSV file by clicking the 'Download report as CSV' button.

python run_get_priority.py

## Contributing

Contributions to this project are welcome. Please feel free to fork the project, make your changes, and submit a pull request.