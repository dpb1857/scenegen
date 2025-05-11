#!/usr/bin/env python3

# pylint: disable=broad-exception-caught
# pylint: disable=broad-exception-raised
# pylint: disable=line-too-long
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=too-many-instance-attributes

import re

import requests

def download_to_local_filesystem(url, filename):
    """
    Downloads a file from Google Drive and saves it locally.

    Parameters:
    url (str): The Google Drive URL with "anyone can view" permissions
    filename (str): The local path where the file should be saved

    Returns:
    bool: True if successful, False otherwise
    """
    # Extract the file ID from the URL
    file_id_match = re.search(r"(?:/d/|id=|/file/d/|open\?id=)([a-zA-Z0-9_-]+)", url)
    if not file_id_match:
        print(f"Could not extract file ID from URL: {url}")
        return False

    file_id = file_id_match.group(1)

    # Direct download link for Google Drive files
    download_url = f"https://drive.google.com/uc?id={file_id}&export=download"

    # For larger files, Google Drive might show a confirmation page
    # This session approach helps handle that
    session = requests.Session()

    # Get the initial response
    response = session.get(download_url, stream=True)

    # Check if there's a download warning (for larger files)
    for key, value in response.cookies.items():
        if key.startswith('download_warning'):
            # Add the confirmation token to the URL
            download_url = f"{download_url}&confirm={value}"
            response = session.get(download_url, stream=True)
            break

    # Check if the request was successful
    if response.status_code != 200:
        print(f"Failed to download file. Status code: {response.status_code}")
        return False

    # Save the file
    try:
        with open(filename, 'wb') as f:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
        print(f"File successfully downloaded to {filename}")
        return True
    except Exception as e:
        print(f"Error saving file: {e}")
        return False



# # Example usage
def main():
    # url = "https://drive.google.com/file/d/1ABC123XYZ/view?usp=sharing"
    url = "https://drive.google.com/file/d/1Rudg-LOEM-Mv0RXuDkdPMIwmX8sqzIkvmEftkjaTdYzxbh8DkEpwf_uw0HBH_7Er4XWfuX5bs-_Yl5-X/view?usp=sharing"
    download_to_local_filesystem(url, "/tmp/downloaded_file.pdf")

if __name__ == "__main__":
    main()
