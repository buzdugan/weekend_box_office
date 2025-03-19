import os
import re
import sys
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


def extract_past_years(URL):

    # Send a GET request to the URL
    response = requests.get(URL)

    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(response.content, 'html.parser')

    # Initialize a list to store the extracted years
    years = []

    # Find all sections that match the pattern 'UK weekend box office reports – year'
    headers = soup.find_all(['h2', 'h3'])
    headers = [header for header in headers if header.text.startswith('UK weekend box office reports')]
    for header in headers:
        year = header.get_text(strip=True)[-4:]
        years.append(year)

    return years


def main():

    # URL of the BFI Weekend Box Office Figures page with all the years and the current year reports
    URL = 'https://www.bfi.org.uk/industry-data-insights/weekend-box-office-figures'
    REPORTS_FOLDER = "wbo_reports"
    # Create a folder to store the reports
    os.makedirs(REPORTS_FOLDER, exist_ok=True)

    years = extract_past_years(URL)

    for year in years:
        # URL of the page with the reports
        YEAR_URL = f"{URL}/uk-weekend-box-office-reports-{year}"
        response = requests.get(YEAR_URL)
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

                # Load the data and keep only the first 15 rows
                df = pd.read_excel(filename, header=1).head(15)
                # Write the data to a csv file
                df.to_csv(filename.replace(".xlsx", ".csv"), index=False)
                print(f"Converted: {filename} to csv")
                # Remove the xlsx file
                os.remove(filename)

        print(f'Successfully downloaded the reports for {year}!')


if __name__ =='__main__':

    main()


# filename = "wbo_reports/2023_12_31.xlsx"
# filename = "wbo_reports/2024_12_29.xlsx"