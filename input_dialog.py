#!/usr/bin/env python3

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import os

class SimpleInputDialog:
    def __init__(self, master, default_url="", default_filename="output.csv"):
        self.master = master
        master.title("Download Scene")

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
        except Exception as _e:
            pass

        # Create main frame with padding
        self.main_frame = ttk.Frame(master, padding=(20, 10))
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Add a title label
        self.title_label = ttk.Label(
            self.main_frame,
            text="Enter Download Information",
            font=("Segoe UI", 14)
        )
        self.title_label.pack(pady=(0, 20))

        # Create form frame
        self.form_frame = ttk.Frame(self.main_frame)
        self.form_frame.pack(fill=tk.X)

        # Scene URL input
        self.url_label = ttk.Label(self.form_frame, text="Scene URL:", font=("Segoe UI", 10))
        self.url_label.grid(row=0, column=0, sticky=tk.W, pady=5)

        self.url_var = tk.StringVar(value=default_url)
        self.url_entry = ttk.Entry(self.form_frame, width=30, textvariable=self.url_var)
        self.url_entry.grid(row=0, column=1, sticky=tk.W, pady=5, padx=5)

        # Filename input
        self.filename_label = ttk.Label(self.form_frame, text="Filename:", font=("Segoe UI", 10))
        self.filename_label.grid(row=1, column=0, sticky=tk.W, pady=5)

        self.filename_var = tk.StringVar(value=default_filename)
        self.filename_entry = ttk.Entry(self.form_frame, width=30, textvariable=self.filename_var)
        self.filename_entry.grid(row=1, column=1, sticky=tk.W, pady=5, padx=5)

        # Button frame
        self.button_frame = ttk.Frame(self.main_frame)
        self.button_frame.pack(fill=tk.X, pady=(20, 0))

        # Submit button
        self.submit_button = ttk.Button(
            self.button_frame,
            text="Download",
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

        # Show a success message
        messagebox.showinfo(
            "Success",
            f"Download request submitted!\n\nScene URL: {url}\nFilename: {filename}"
        )

        # Process the information
        self.process_download(url, filename)

        # Close the dialog
        self.master.destroy()

    def process_download(self, url, filename):
        # This is a placeholder function where you would implement the actual download logic
        print(f"Starting download from: {url}")
        print(f"Saving to: {filename}")

        # Example: You could write the information to a file for now
        with open("download_queue.txt", "a") as file:
            file.write(f"URL: {url}, Filename: {filename}\n")

        # Later you could replace this with actual download functionality

def main():
    root = tk.Tk()

    # You can specify default values here
    default_url = "https://docs.google.com/spreadsheets/d/"
    default_filename = "data.csv"

    app = SimpleInputDialog(root, default_url, default_filename)
    root.mainloop()

    # Return the values (useful if using this as a module)
    return app.url_var.get(), app.filename_var.get()

if __name__ == "__main__":
    url, filename = main()
    print(f"Selected URL: {url}")
    print(f"Selected filename: {filename}")
