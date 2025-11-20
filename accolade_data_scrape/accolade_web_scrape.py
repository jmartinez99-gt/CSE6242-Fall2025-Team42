import pandas as pd
import numpy as np
import requests
import re
from utils import matching

# Grab accolade URL data
accolade_urls = pd.read_csv('refdocs/ncaa_accolade_urls.csv', index_col=False)

# Set the proper User-Agent Header for the Python Request based on Mac OS
headers = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )
}

# Iterate over all rows to match NCAA accolade data with IPEDS data based on each URL identified
for index, row in accolade_urls.iterrows():

    # Obtain sport, gender, and division information from accolade_urls
    # Remove ampersand and whitespace in Sport values to form filename consistency
    sport = row['sport'].replace(" ", "").replace("&", "")
    gender = row['gender']
    division = row['division']
    csv_filename = 'output/{}_{}_{}_accolades.csv'.format(division, gender, sport)
    print("Importing table for {}...".format(csv_filename))

    # Define URL to scrape accolade data
    URL = row['url']

    # Fetch HTML page contents 
    response = requests.get(URL, headers=headers)
    response.raise_for_status()
    html = response.text

    # Obtain NCAA accolade tables from HTML page and convert into single pandas DataFrame
    # NOTE: Each row identied appears as one singular table, so all tables identified must be concatenated into one table
    html_raw_data = pd.read_html(html)
    accolade_raw_df = pd.concat(html_raw_data, ignore_index=True)

    # Based on the School column name of the table identified in the URL, 
    # Create 'Champion' column with respect to that column name
    if 'Champion (Record)' in accolade_raw_df.columns:
        accolade_raw_df['Champion'] = accolade_raw_df['Champion (Record)'] \
            .str.split(r"\(\d") \
            .str[0] \
            .str.strip()
    elif 'Team (Record)' in accolade_raw_df.columns:
        accolade_raw_df['Champion'] = accolade_raw_df['Team (Record)'] \
            .str.split(r"\(\d") \
            .str[0] \
            .str.strip()
    elif 'School' in accolade_raw_df.columns:
        accolade_raw_df['Champion'] = accolade_raw_df['School'] \
            .str.split(r"\(\d") \
            .str[0] \
            .str.strip()
    
    # Year column may appear as the name "Season", so rename accordingly
    if 'Year' not in accolade_raw_df.columns:
        accolade_raw_df.rename(columns={'Season': 'Year'}, inplace=True)

    # Filter out data where a given year appears as NaN
    accolade_raw_df = accolade_raw_df[accolade_raw_df['Year'].notna()]

    # Run data transformations on the Year column if the column data type does not appear as an int or float
    # Remove extraneous characters and only keep numerical characters
    if ((accolade_raw_df['Year'].dtype != 'int64') | (accolade_raw_df['Year'].dtype != np.float64)):
        accolade_raw_df['Year'] = accolade_raw_df['Year'].astype(str) \
            .str.replace(".0", "") \
            .str.replace(r"[^0-9]", "", regex=True) \
            .astype(float).astype(int)

    # Ensure the Year column is of data type int
    accolade_raw_df['Year'] = accolade_raw_df['Year'].astype(int)
    
    # Combine NCAA accolade data with IPEDS directory data to obtain the UNITID of each university identified
    matching_df = matching.find_ipeds_match(accolade_raw_df[['Year', 'Champion']])
    matching_df['Sport'] = row['sport']
    matching_df['Gender'] = row['gender']
    matching_df['Division'] = row['division']

    # Reorder columns into readable format
    final_df = matching_df[['Division', 'Gender', 'Sport', 'Year', 'UNITID', 'Champion', 'INSTNM', 'Champion_NORM', 'INSTNM_NORM', 'type_of_match']]
    final_df.to_csv(csv_filename, index=False)

'''
    Cited Sources
        https://www.geeksforgeeks.org/python/user-agent-in-python-request/
        https://pandas.pydata.org/docs/reference/api/pandas.Series.str.split.html
        https://pandas.pydata.org/docs/reference/api/pandas.Series.str.strip.html
        https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.astype.html
        https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.notna.html
        https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.iterrows.html#pandas-dataframe-iterrows
        https://stackoverflow.com/questions/16476924/how-can-i-iterate-over-rows-in-a-pandas-dataframe
        https://pandas.pydata.org/docs/reference/api/pandas.read_csv.html
        https://pandas.pydata.org/docs/reference/api/pandas.read_html.html
        https://www.w3schools.com/python/ref_string_format.asp
'''