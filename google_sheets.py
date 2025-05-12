#!/usr/bin/env python3

# pylint: disable=broad-exception-caught
# pylint: disable=broad-exception-raised
# pylint: disable=line-too-long
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=too-many-instance-attributes

import csv
import io
import re

import requests

def get_sheet_urls(spreadsheet_url, api_key):
    """
    Given a public Google Sheets URL and an API key, return a dict mapping sheet names to their URLs.
    """
    # Extract the spreadsheet ID from the URL
    match = re.search(r"/spreadsheets/d/([a-zA-Z0-9-_]+)", spreadsheet_url)
    if not match:
        raise ValueError("Invalid Google Sheets URL")
    spreadsheet_id = match.group(1)

    # Call the Sheets API to get metadata
    metadata_url = f"https://sheets.googleapis.com/v4/spreadsheets/{spreadsheet_id}?fields=sheets.properties&key={api_key}"
    response = requests.get(metadata_url) # pylint: disable=missing-timeout
    if response.status_code != 200:
        raise Exception(f"Error fetching sheet metadata: {response.status_code} - {response.text}")

    sheet_data = response.json()
    sheet_urls = {}

    for sheet in sheet_data["sheets"]:
        properties = sheet["properties"]
        title = properties["title"]
        gid = properties["sheetId"]
        sheet_urls[title] = f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/edit#gid={gid}"

    return sheet_urls

##
## Download the runlist from a Google Sheet
##

def extract_sheet_id_gid(url):
    """Extract Google Sheet ID from URL."""
    # Pattern for Google Sheets URLs
    pattern = r'https://docs\.google\.com/spreadsheets/d/([a-zA-Z0-9_-]+)'
    match = re.search(pattern, url)

    gidpatt = r'gid=([0-9]+)'
    gidmatch = re.search(gidpatt, url)
    if gidmatch:
        gid = gidmatch.group(1)
    else:
        gid = '0'

    if match:
        return match.group(1), gid

    raise ValueError("Invalid Google Sheets URL. Please provide a URL in the format: "
                     "https://docs.google.com/spreadsheets/d/YOUR_SHEET_ID/...")

def download_sheet(url):
    """
    Download a Google Sheet and return its contents as a list of rows.

    Args:
        url (str): Public URL of the Google Sheet

    Returns:
        list: A list of lists, where each inner list represents a row from the sheet

    Raises:
        ValueError: If the URL is not a valid Google Sheets URL
        Exception: If there's an error downloading the sheet
    """

    # Extract the Sheet ID from the URL
    sheet_id, sheet_gid = extract_sheet_id_gid(url)

    # Construct the export URL for the first sheet (as CSV)
    export_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={sheet_gid}"

    # Download the CSV content
    response = requests.get(export_url) # pylint: disable=missing-timeout

    # Check if the request was successful
    if response.status_code != 200:
        raise Exception(f"Failed to download the sheet. Status code: {response.status_code}")

    # Convert the content to a string
    csv_content = response.content.decode('utf-8')

    # Parse the CSV content
    csv_reader = csv.reader(io.StringIO(csv_content))

    # Convert to a list of rows
    data = list(csv_reader)

    return data


# Solution: Using the Google Sheets API with an API key (no OAuth needed for public sheets)
# 🔧 Step 1: Enable Sheets API and get your API key
# Go to: https://console.cloud.google.com/apis/library/sheets.googleapis.com
# Enable it, and create an API key under APIs & Services > Credentials

# spreadsheet_url = "https://docs.google.com/spreadsheets/d/1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms/edit#gid=0"
# api_key = "YOUR_API_KEY_HERE"

def main():
    spreadsheet_url = "https://docs.google.com/spreadsheets/d/1Te9oo6jeUPW_tof0Qr3y9-36qcnQWxsg_xJbFaSSuNM/edit?gid=0#gid=0"
    # pylint: disable=import-outside-toplevel
    from apikey import API_KEY

    sheet_links = get_sheet_urls(spreadsheet_url, API_KEY)
    print(sheet_links)

if __name__ == "__main__":
    main()
