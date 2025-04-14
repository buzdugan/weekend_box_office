import os
import re
from datetime import datetime

import pandas as pd
import requests
from bs4 import BeautifulSoup



def get_sunday_date_from_report_title(report_text):
    """Extracts the last date from the report text and formats it as YYYY_MM_DD."""
    # Standardize separators
    report_text = report_text.replace(" to ", " - ")
    
    # Pattern 1: "28 February - 2 March 2025" (different months)
    pattern1 = re.search(r"(\d{1,2})\s*(\w+)\s*-\s*(\d{1,2})\s*(\w+)\s*(\d{4})", report_text)

    # Pattern 2: "7-9 March 2025" or "7 - 9 March 2025" (same month)
    pattern2 = re.search(r"(\d{1,2})\s*-\s*(\d{1,2})\s*(\w+)\s*(\d{4})", report_text)
    
    # Pattern 3: "24-26 January 2025" (no spaces around hyphen)
    pattern3 = re.search(r"(\d{1,2})-(\d{1,2})\s*(\w+)\s*(\d{4})", report_text)
    
    # Pattern 4: "24 December 2024 - 26 January 2025" (different months with years)
    pattern4 = re.search(r"(\d{1,2})\s*(\w+)\s*(\d{4})\s*-\s*(\d{1,2})\s*(\w+)\s*(\d{4})", report_text)
    
    if pattern1:
        end_day, end_month, year = pattern1.group(3), pattern1.group(4), pattern1.group(5)
    elif pattern2:
        end_day, end_month, year = pattern2.group(2), pattern2.group(3), pattern2.group(4)
    elif pattern3:
        end_day, end_month, year = pattern3.group(2), pattern3.group(3), pattern3.group(4)
    elif pattern4:
        end_day, end_month, year = pattern4.group(4), pattern4.group(5), pattern4.group(6)
    else:
        return None
    
    year = int(year)
    end_day = int(end_day)
    end_month = datetime.strptime(end_month, "%B").month
    # Construct the Sunday date
    sunday_date = datetime(year, end_month, end_day).strftime("%Y_%m_%d")
    return sunday_date


def clean_columns(df, last_sunday):
    # Remove empty columns
    df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
    # Add a column with the report date with - instead of _
    df.insert(0, "report_date", last_sunday.replace("_", "-"), True)

    # Convert to lowercase
    columns = [col.lower().replace(" ", "_") for col in df.columns]
    # Change the column with % to percent
    columns = [col.replace("%", "percent") for col in columns]

    # Rename columns
    df.columns = columns

    # Remove empty value substitute - from percent_change_on_last_week
    df['percent_change_on_last_week'] = df['percent_change_on_last_week'].replace("-", None).replace(" - ", None)

    # Change data types
    df['report_date'] = pd.to_datetime(df['report_date'], format='%Y-%m-%d')
    df['rank'] = df['rank'].astype('int')
    df['weekend_gross'] = df['weekend_gross'].astype('int')
    df['percent_change_on_last_week'] = df['percent_change_on_last_week'].astype('float')
    df['weeks_on_release'] = df['weeks_on_release'].astype('int')
    df['number_of_cinemas'] = df['number_of_cinemas'].astype('int')
    df['site_average'] = df['site_average'].astype('int')
    df['total_gross_to_date'] = df['total_gross_to_date'].astype('int')

    return df


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


def download_reports(url, REPORTS_FOLDER):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    # Find all report links 
    links = soup.find_all("a", href=True)
    links = [link for link in links if "Weekend box office report" in link.text]
    
    for link in links:
        report_title = link.text.strip()
        print(report_title)
        report_url = link["href"]
        
        sunday_date = get_sunday_date_from_report_title(report_title)
        if sunday_date:
            filename = f"{REPORTS_FOLDER}/{sunday_date}.xlsx"
            
            # Download the report as original Excel file
            report_response = requests.get(report_url)
            with open(filename, "wb") as file:
                file.write(report_response.content)
                print(f"Downloaded: {filename}")

            # Until 2025-04-14, 14 files formatted differently so we will skip them
            try:
                # Load the data and clean it
                df = pd.read_excel(filename, header=1).head(15)
                df = clean_columns(df, sunday_date)
                # Write the data to a csv file
                df.to_csv(filename.replace(".xlsx", ".csv").replace(".xls", ".csv"), index=False)
                print(f"Converted: {filename} to csv")
            except Exception as e:
                print(f"Error converting {filename}: {e}")
            # Remove the xlsx file
            os.remove(filename)
        else:
            print(f"Failed to extract the date from the report title: {report_title}")
            continue


def main():
    # URL of the BFI Weekend Box Office Figures page with all the years and the current year reports
    URL = 'https://www.bfi.org.uk/industry-data-insights/weekend-box-office-figures'
    REPORTS_FOLDER = "wbo_reports"
    # Create a folder to store the reports
    os.makedirs(REPORTS_FOLDER, exist_ok=True)

    years = extract_past_years(URL)
    print("Past years:", years)

    # Download the reports for the current year
    print(f'Downloading the reports for current year {datetime.now().year}...')
    download_reports(URL, REPORTS_FOLDER)
    print(f'Successfully downloaded the reports for {datetime.now().year}!')

    for year in years:
        YEAR_URL = f"{URL}/uk-weekend-box-office-reports-{year}"
        print(f'Downloading the reports for {year}...')
        download_reports(YEAR_URL, REPORTS_FOLDER)
        print(f'Successfully downloaded the reports for {year}!')


    # Load all the data from the csv files and combine them into one dataframe
    csv_files = os.listdir(REPORTS_FOLDER)
    csv_files = [filename for filename in csv_files if filename.endswith(".csv")]
    
    dataframes = []
    for filename in csv_files:
        df = pd.read_csv(f"{REPORTS_FOLDER}/{filename}")
        dataframes.append(df)

    # Concatenate all dataframes
    combined_df = pd.concat(dataframes, ignore_index=True)
    # Save the combined dataframe to a csv file
    combined_df.to_csv(f"{REPORTS_FOLDER}/historical_data.csv", index=False)
    print(f"Combined data saved to {REPORTS_FOLDER}/historical_data.csv")
    
    # Remove the csv files
    for filename in csv_files:
        os.remove(f"{REPORTS_FOLDER}/{filename}")


if __name__ == "__main__":
    main()

