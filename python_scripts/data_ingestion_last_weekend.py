import os
import re
from datetime import datetime, timedelta

import pandas as pd
import requests
from bs4 import BeautifulSoup


def get_sunday_date(report_text):
    """Extracts the last date from the report text and formats it as YYYY_MM_DD."""
    # Replace " to " with " – "
    report_text = report_text.replace(" to ", " – ")
    # Pattern 1: "28 February – 2 March 2025 or 28 February to 2 March 2025"
    pattern1 = re.search(r"(\d{1,2})\s*(\w+)\s*–\s*(\d{1,2})\s*(\w+)\s*(\d{4})", report_text)
    # Pattern 2: "7-9 March 2025 or 7 to 9 March 2025"
    pattern2 = re.search(r"(\d{1,2})\s*–\s*(\d{1,2})\s*(\w+)\s*(\d{4})", report_text)

    if pattern1:
        end_day, end_month, year = pattern1.group(3), pattern1.group(4), pattern1.group(5)
    elif pattern2:
        end_day, end_month, year = pattern2.group(2), pattern2.group(3), pattern2.group(4)
    else:
        return None
    
    year = int(year)
    end_day = int(end_day)
    end_month = datetime.strptime(end_month, "%B").month
    
    # Construct the Sunday date
    sunday_date = datetime(year, end_month, end_day).strftime("%Y_%m_%d")
    return sunday_date


def main():

    # URL of the BFI Weekend Box Office Figures page with all the years and the current year reports
    URL = 'https://www.bfi.org.uk/industry-data-insights/weekend-box-office-figures'
    REPORTS_FOLDER = "wbo_reports"
    # Create a folder to store the reports
    os.makedirs(REPORTS_FOLDER, exist_ok=True)

    # Get current date and look for report for last Sunday
    today = datetime.now().date()
    idx = (today.weekday() + 1) % 7
    last_sunday = today - timedelta(idx)

    # Download the reports for last Sunday if it's available
    response = requests.get(URL)
    soup = BeautifulSoup(response.text, "html.parser")
    links = soup.find_all("a", href=True)
    links = [link for link in links if "Weekend box office report" in link.text]
    # Get the title of the latest weekend box office report
    report_title = links[0].text.strip()
    # Extract the date from the report title
    sunday_date = get_sunday_date(report_title)

    if sunday_date:
        print(f"Last Sunday report date: {sunday_date}")
        # If the date is the same last_sunday, then download the report
        if sunday_date == last_sunday.strftime("%Y_%m_%d"):
            report_url = links[0]["href"]
            filename = f"{REPORTS_FOLDER}/{sunday_date}.xlsx"
            
            # Download the report
            report_response = requests.get(report_url)
            with open(filename, "wb") as file:
                file.write(report_response.content)
                print(f"Downloaded last Sunday report: {filename}")

            # Load the data and keep only the first 15 rows
            df = pd.read_excel(filename, header=1).head(15)
            # Remove empty columns
            df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
            # Add a column with the report date
            df.insert(0, "report_date", sunday_date, True)

            # Write the data to a csv file
            df.to_csv(filename.replace(".xlsx", ".csv").replace(".xls", ".csv"), index=False)
            print(f"Converted: {filename} to csv")
            # Remove the xlsx file
            os.remove(filename)
        else:
            print(f"Last Sunday report is not available yet.")
            return
    else:
        print("The latest report date could not be extracted.")
        return 


if __name__ == '__main__':
    main()