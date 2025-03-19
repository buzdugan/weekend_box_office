import os
import re
from datetime import datetime

import pandas as pd
import requests
from bs4 import BeautifulSoup


def get_sunday_date(report_text):
    """Extracts the last date from the report text and formats it as YYYY_MM_DD."""
    date_match = re.search(r'(\d{1,2})\s*-\s*(\d{1,2})\s*([A-Za-z]+)\s*(\d{4})', report_text)
    if not date_match:
        return None
    
    start_day, end_day, month, year = date_match.groups()
    year = int(year)
    end_day = int(end_day)
    month = datetime.strptime(month, "%B").month
    
    # Construct the Sunday date
    sunday_date = datetime(year, month, end_day).strftime("%Y_%m_%d")
    return sunday_date


def main():
    year = 2017
    # URL of the page with the reports
    BASE_URL = f"https://www.bfi.org.uk/industry-data-insights/weekend-box-office-figures/uk-weekend-box-office-reports-{year}"
    REPORTS_FOLDER = "wbo_reports" 

    # Create a folder to store the reports
    os.makedirs(REPORTS_FOLDER, exist_ok=True)

    # Fetch the webpage
    response = requests.get(BASE_URL)
    soup = BeautifulSoup(response.text, "html.parser")
    
    # Find all report links 
    links = soup.find_all("a", href=True)
    links = [link for link in links if "Weekend box office report" in link.text]
    
    for link in links[:3]:
        report_title = link.text.strip()
        report_url = link["href"]
        
        sunday_date = get_sunday_date(report_title)
        if sunday_date:
            filename = f"{REPORTS_FOLDER}/{sunday_date}.xlsx"
            
            # Download the report
            report_response = requests.get(report_url)
            with open(filename, "wb") as file:
                file.write(report_response.content)
                print(f"Downloaded: {filename}")

            # Load the data and keep only the first 15 rows:    
            df = pd.read_excel(filename, header=1).head(15)
            # Write the data to a csv file
            df.to_csv(filename.replace(".xlsx", ".csv"), index=False)
            print(f"Converted: {filename} to csv")
            # Remove the xlsx file
            os.remove(filename)

    print('Successfully downloaded the reports!')


if __name__ =='__main__':
    main()
