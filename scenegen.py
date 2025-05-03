#!/usr/bin/env python3

# pylint: disable=broad-exception-raised
# pylint: disable=line-too-long
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=too-many-instance-attributes

import copy
import csv
from io import StringIO
import json
import os
import re
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import uuid
import requests

##
## Globals
##

if False:
    SLIDES_DIRECTORY = "/tmp/sldes.pdf"
    TEMPLATES_FILE = "templates.json"
    SCENES_DIRECTORY = "/tmp/"
else:
    SLIDES_DIRECTORY = "s:/Slides/"
    TEMPLATES_FILE = "c:/Users/dpb/AppData/Roaming/obs-studio/basic/scenes/templates.json"
    SCENES_DIRECTORY = "c:/Users/dpb/AppData/Roaming/obs-studio/basic/scenes/"

##
## Download the runlist from a Google Sheet
##

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
    csv_reader = csv.reader(StringIO(csv_content))

    # Convert to a list of rows
    data = list(csv_reader)

    return data

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

##
## Two functions to load and save json files
##

def load_json_file(filename):
    """
    Load and deserialize a JSON file into Python data structures.

    Args:
        filename (str): Path to the JSON file to load

    Returns:
        dict/list: The deserialized JSON data as Python data structures

    Raises:
        FileNotFoundError: If the specified file doesn't exist
        json.JSONDecodeError: If the file contains invalid JSON
        PermissionError: If the file cannot be accessed due to permission issues
    """
    try:
        # Check if file exists
        if not os.path.isfile(filename):
            raise FileNotFoundError(f"The file '{filename}' does not exist")

        # Open and read the JSON file
        with open(filename, 'r', encoding='utf-8') as file:
            data = json.load(file)

        return data

    except FileNotFoundError as e:
        # Re-raise with a clear message
        raise FileNotFoundError(f"File not found: filename:{filename} error: {e}") from e

    except json.JSONDecodeError as e:
        # Provide more helpful information about JSON parsing errors
        raise json.JSONDecodeError(
            f"Invalid JSON in {filename}: {str(e)}",
            e.doc,
            e.pos
        )

    except PermissionError as e:
        # Handle permission issues
        raise PermissionError(f"Permission denied when trying to read {filename}") from e

    except Exception as e:
        # Catch any other unexpected errors
        raise Exception(f"Error loading JSON file {filename}: {str(e)}") from e


def save_to_json_file(data, filename, indent=4, ensure_directory=True):
    """
    Serialize Python data structures to JSON and save to a file.

    Args:
        data (dict/list): The Python data structure to serialize to JSON
        filename (str): Path to the output JSON file
        indent (int, optional): Number of spaces for indentation. Defaults to 4.
            Set to None for the most compact representation.
        ensure_directory (bool, optional): If True, create parent directories
            if they don't exist. Defaults to True.

    Returns:
        bool: True if the operation was successful

    Raises:
        TypeError: If the data cannot be serialized to JSON
        PermissionError: If the file cannot be written due to permission issues
        OSError: If there's an error creating directories or writing the file
    """
    try:
        # Create directory if it doesn't exist and ensure_directory is True
        if ensure_directory:
            directory = os.path.dirname(filename)
            if directory and not os.path.exists(directory):
                os.makedirs(directory)

        # Open the file in write mode
        with open(filename, 'w', encoding='utf-8') as file:
            # Serialize the data to JSON and write to the file
            json.dump(data, file, indent=indent, ensure_ascii=False)

        return True

    except TypeError as e:
        # This happens when the data contains types that can't be serialized to JSON
        raise TypeError(f"Cannot serialize to JSON: {str(e)}") from e

    except PermissionError as e:
        # Handle permission issues
        raise PermissionError(f"Permission denied when trying to write to {filename}") from e

    except OSError as e:
        # Handle file system errors
        raise OSError(f"Error writing to file {filename}: {str(e)}") from e

    except Exception as e:
        # Catch any other unexpected errors
        raise Exception(f"Unexpected error saving JSON to {filename}: {str(e)}") from e

##
## Dialog to get the spreadsheet and the scenes filename;
##

class SimpleInputDialog:
    def __init__(self, master):
        self.master = master
        master.title("Create Scenes")

        # Set window size and position it in center of screen
        window_width = 400
        window_height = 200
        screen_width = master.winfo_screenwidth()
        screen_height = master.winfo_screenheight()
        center_x = int(screen_width/2 - window_width/2)
        center_y = int(screen_height/2 - window_height/2)
        master.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')

        # Modern Windows 11 styling
        try:
            self.style = ttk.Style()
            self.style.theme_use('vista')  # Use vista theme which looks similar to Windows 11
        except Exception: # pylint: disable=broad-exception-caught
            pass

        # Create main frame with padding
        self.main_frame = ttk.Frame(master, padding=(20, 10))
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Add a title label
        self.title_label = ttk.Label(
            self.main_frame,
            text="Enter Scene Creation Info",
            font=("Segoe UI", 14)
        )
        self.title_label.pack(pady=(0, 20))

        # Create form frame
        self.form_frame = ttk.Frame(self.main_frame)
        self.form_frame.pack(fill=tk.X)

        # Scene URL input
        self.url_label = ttk.Label(self.form_frame, text="Scene URL:", font=("Segoe UI", 10))
        self.url_label.grid(row=0, column=0, sticky=tk.W, pady=5)

        self.url_var = tk.StringVar()
        self.url_entry = ttk.Entry(self.form_frame, width=30, textvariable=self.url_var)
        self.url_entry.grid(row=0, column=1, sticky=tk.W, pady=5, padx=5)

        # Filename input
        self.filename_label = ttk.Label(self.form_frame, text="Filename:", font=("Segoe UI", 10))
        self.filename_label.grid(row=1, column=0, sticky=tk.W, pady=5)

        self.filename_var = tk.StringVar()
        self.filename_entry = ttk.Entry(self.form_frame, width=30, textvariable=self.filename_var)
        self.filename_entry.grid(row=1, column=1, sticky=tk.W, pady=5, padx=5)

        # Button frame
        self.button_frame = ttk.Frame(self.main_frame)
        self.button_frame.pack(fill=tk.X, pady=(20, 0))

        # Submit button
        self.submit_button = ttk.Button(
            self.button_frame,
            text="Generate Scenes",
            command=self.submit
        )
        self.submit_button.pack(side=tk.RIGHT, padx=5)

        # Cancel button
        self.cancel_button = ttk.Button(
            self.button_frame,
            text="Cancel",
            command=self.master.destroy
        )
        self.cancel_button.pack(side=tk.RIGHT, padx=5)

        # Set focus to the first entry field
        self.url_entry.focus_set()

        # Bind Enter key to submit
        master.bind('<Return>', lambda event: self.submit())

    def submit(self):
        # Validate inputs
        url = self.url_var.get().strip()
        filename = self.filename_var.get().strip()

        if not url:
            messagebox.showerror("Error", "Please enter a Scene URL")
            self.url_entry.focus_set()
            return

        if not filename:
            messagebox.showerror("Error", "Please enter a filename")
            self.filename_entry.focus_set()
            return

        # # Show a success message
        # messagebox.showinfo(
        #     "Success",
        #     f"Download request submitted!\n\nScene URL: {url}\nFilename: {filename}"
        # )

        try:
            # Process the information
            self.process_runlist(url, filename)
            messagebox.showinfo(
                "Success",
                f"Scenelist processed, saved in {filename}"
                )
        except Exception as e: # pylint: disable=broad-exception-caught
            messagebox.showinfo(
                "Sad face",
                f"Something went wrong: {e}"
                )

        # Close the dialog
        self.master.destroy()

    def process_runlist(self, url, filename):
        # print(f"Starting download from: {url}")
        # print(f"Saving to: {filename}")

        # # Example: You could write the information to a file for now
        # with open("download_queue.txt", "a") as file:
        #     file.write(f"URL: {url}, Filename: {filename}\n")

        # # Later you could replace this with actual download functionality

        data = download_sheet(url)
        templatecollection = load_json_file(TEMPLATES_FILE)

        def create_custom_browser(name, page):
            for source in templatecollection["sources"]:
                if source["id"] == "browser_source":
                    b = copy.deepcopy(source)
                    b.update({"name": name,
                              "uuid": str(uuid.uuid4())})
                    b["settings"]["url"] = f"file:///{SLIDES_DIRECTORY}Slides-{filename}.pdf#toolbar=0&page={page}"
                    if name.endswith("->"):
                        b["settings"]["restart_when_active"] = True

                    return b
            raise Exception("Could not find a browser object")

        def create_scene_from_template(template, name):
            for source in templatecollection["sources"]:
                if source["id"] == "scene" and source["name"] == template:
                    s = copy.deepcopy(source)
                    s.update({"name": name,
                              "uuid": str(uuid.uuid4())})
                    return s
            raise Exception(f"Could not find scene template {template}")

        def find_scene_browser(scene):
            for item in scene["settings"]["items"]:
                if item["name"].startswith("Browser"):
                    return item
            return None

        def update_scene_browser(scene_browser_item, browser):
            scene_browser_item.update({"name": browser["name"],
                                       "source_uuid": browser["uuid"]})

        def gen_scene(newscene):
            name, template, page = newscene
            # print("Processing:", name, template, page)
            scene = create_scene_from_template(template, name)
            b = None
            scene_browser_item = find_scene_browser(scene)
            if scene_browser_item:
                b = create_custom_browser(f"Browser{name}", page)
                update_scene_browser(scene_browser_item, b)

            return b, scene

        newobjects = [gen_scene(newscene) for newscene in data[1:]]
        templatecollection["current_scene"] = newobjects[0][1]
        templatecollection["current_program_scene"] = newobjects[0][1]
        for b, scene in newobjects:
            templatecollection["scene_order"].append({"name": scene["name"]})
            templatecollection["sources"].append(scene)
            if b:
                templatecollection["sources"].append(b)

        templatecollection["name"] = filename

        save_to_json_file(templatecollection, f"{SCENES_DIRECTORY}{filename}.json")

def main1():
    root = tk.Tk()
    _app = SimpleInputDialog(root)
    root.mainloop()

# Example usage:
def main2():
    # Example: Replace with your actual Google Sheet URL
    # sample_url = "https://docs.google.com/spreadsheets/d/1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms/edit"
    sample_url = "https://docs.google.com/spreadsheets/d/1Te9oo6jeUPW_tof0Qr3y9-36qcnQWxsg_xJbFaSSuNM/edit?usp=sharing"

    try:
        data = download_sheet(sample_url)

        # Print the first few rows as a sample
        print("First 3 rows of the sheet:")
        for row in data[1:]:
            print(f"{row}")

        print(f"\nTotal rows: {len(data)}")

    except Exception as e:
        print(f"Error: {e}")

# Example usage:
def main3():
    try:
        # Replace with your actual JSON file path
        # data = load_json_file("example.json")
        data = load_json_file("SceneTestCollection1.json")

        # Print the type of the loaded data
        print(f"Data type: {type(data)}")

        # If it's a dictionary, print the keys
        if isinstance(data, dict):
            print(f"Keys: {list(data.keys())}")

        # If it's a list, print its length
        elif isinstance(data, list):
            print(f"List length: {len(data)}")

            # Print first item if list is not empty
            if data:
                print(f"First item type: {type(data[0])}")
                if isinstance(data[0], dict):
                    print(f"First item keys: {list(data[0].keys())}")

    except Exception as e:
        print(f"Error: {e}")

# Example usage:
def main4():
    try:
        # Example data to save
        sample_data = {
            "name": "John Doe",
            "age": 30,
            "is_active": True,
            "skills": ["Python", "JSON", "Data Analysis"],
            "address": {
                "street": "123 Main St",
                "city": "Anytown",
                "zip": "12345"
            }
        }

        # Save the data to a JSON file
        success = save_to_json_file(sample_data, "output.json")

        if success:
            print("Data successfully saved to output.json")

            # Display file size
            file_size = os.path.getsize("output.json")
            print(f"File size: {file_size} bytes")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main1()
    # main2()
    # main3()
    # main4()
    # sheet = "https://docs.google.com/spreadsheets/d/1Te9oo6jeUPW_tof0Qr3y9-36qcnQWxsg_xJbFaSSuNM/edit?gid=1071203818"
    # sheet = "https://docs.google.com/spreadsheets/d/1Te9oo6jeUPW_tof0Qr3y9-36qcnQWxsg_xJbFaSSuNM/edit?gid=0"
    # print(download_sheet(sheet))
