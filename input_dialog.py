#!/usr/bin/env python3

# pylint: disable=broad-exception-caught
# pylint: disable=broad-exception-raised
# pylint: disable=line-too-long
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=too-many-instance-attributes

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

import config
import next_sunday
import scenes
import validation

class SimpleInputDialog:
    def __init__(self, master, default_url="", default_filename="output.csv"):
        self.master = master
        master.title("Download Scene")

        # Set window size and position it in center of screen
        window_width = 1200  # Doubled from 400 to 800; WIDTH
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
        # self.main_frame = ttk.Frame(master, padding=(20, 10))
        self.main_frame = ttk.Frame(master, padding=(40, 10))  # Increased horizontal padding from 20 to 40; WIDTH
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Add a title label
        self.title_label = ttk.Label(
            self.main_frame,
            text="Enter Scene Generation Information",
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
        self.url_entry = ttk.Entry(self.form_frame, width=110, textvariable=self.url_var)  # Doubled from 30 to 60; WIDTH
        self.url_entry.grid(row=0, column=1, sticky=tk.W, pady=5, padx=5)

        # Filename input
        self.filename_label = ttk.Label(self.form_frame, text="Filename:", font=("Segoe UI", 10))
        self.filename_label.grid(row=1, column=0, sticky=tk.W, pady=5)

        self.filename_var = tk.StringVar(value=default_filename)
        self.filename_entry = ttk.Entry(self.form_frame, width=110, textvariable=self.filename_var)  # Doubled from 30 to 60; WIDTH
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

        if (error := validation.can_get_sheetmap(url, filename)) is not None:
            messagebox.showerror("Error", f"Problems with URL: {error}")
            self.url_entry.focus_set()
            return

        if (error := validation.validate_config()) is not None:
            messagebox.showerror("Error", f"Problems with URL: {error}")
            self.url_entry.focus_set()
            return

        # Process the information
        try:
            self.process_runlist(url, filename)
            # Show a success message
            messagebox.showinfo(
                "Success",
                f"Scenelist generated in {filename}"
            )
        except Exception as e:  # pylint: disable=broad-exception-caught
            messagebox.showerror("Error", f"Something went wrong: {e}")

        # Close the dialog
        self.master.destroy()

    def process_runlist(self, url, filename):
        scenes.generate_scenes(url, filename)
        scenes.download_pdf(url, filename)

def main():
    root = tk.Tk()

    # You can specify default values here
    default_url = config.SCENES_URL
    default_filename = next_sunday.next_sunday_noon()

    app = SimpleInputDialog(root, default_url, default_filename)
    root.mainloop()

    # Return the values (useful if using this as a module)
    return app.url_var.get(), app.filename_var.get()

if __name__ == "__main__":
    main_url, main_filename = main()
    print(f"Selected URL: {main_url}")
    print(f"Selected filename: {main_filename}")
