#!/usr/bin/env python3

# pylint: disable=broad-exception-caught
# pylint: disable=broad-exception-raised
# pylint: disable=line-too-long
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=too-many-instance-attributes

import logging
import os
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

        # Create main frame with padding
        self.main_frame = ttk.Frame(master, padding=(40, 20))
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Add a title label
        self.title_label = ttk.Label(
            self.main_frame,
            text="Enter Scene Generation Information",
            font="TkHeadingFont"
        )
        self.title_label.pack(pady=(0, 20))

        # Create form frame
        self.form_frame = ttk.Frame(self.main_frame)
        self.form_frame.pack(fill=tk.X)

        # Scene URL input
        self.url_label = ttk.Label(self.form_frame, text="Scene URL:")
        self.url_label.grid(row=0, column=0, sticky=tk.W, pady=5)

        self.url_var = tk.StringVar(value=default_url)
        self.url_entry = ttk.Entry(self.form_frame, width=100, textvariable=self.url_var)
        self.url_entry.grid(row=0, column=1, sticky=tk.W, pady=5, padx=5)

        # Filename input
        self.filename_label = ttk.Label(self.form_frame, text="Filename:")
        self.filename_label.grid(row=1, column=0, sticky=tk.W, pady=5)

        self.filename_var = tk.StringVar(value=default_filename)
        self.filename_entry = ttk.Entry(self.form_frame, width=100, textvariable=self.filename_var)
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

        # Let the window size itself to its contents, then center it
        master.update_idletasks()
        width = master.winfo_reqwidth()
        height = master.winfo_reqheight()
        x = (master.winfo_screenwidth() - width) // 2
        y = (master.winfo_screenheight() - height) // 3
        master.geometry(f"+{x}+{y}")
        master.resizable(False, False)

        # When started from the Dock the window may open behind other apps
        master.lift()
        master.attributes('-topmost', True)
        master.after(500, lambda: master.attributes('-topmost', False))

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
            messagebox.showerror("Error", f"Problems with configuration: {error}")
            return

        # Process the information
        try:
            self.process_runlist(url, filename)
            logging.info("Generated scenes for %s", filename)
            # Show a success message
            messagebox.showinfo(
                "Success",
                f"Scenelist generated in {filename}"
            )
        except Exception as e:  # pylint: disable=broad-exception-caught
            logging.exception("Scene generation failed for %s", filename)
            messagebox.showerror("Error", f"Something went wrong: {e}")

        # Close the dialog
        self.master.destroy()

    def process_runlist(self, url, filename):
        scenes.generate_scenes(url, filename)
        scenes.download_pdf(url, filename)

def setup_logging():
    # There is no terminal when started from the Dock, so keep a log
    logfile = os.path.expanduser("~/Library/Logs/scenegen.log")
    try:
        os.makedirs(os.path.dirname(logfile), exist_ok=True)
        logging.basicConfig(filename=logfile, level=logging.INFO,
                            format="%(asctime)s %(levelname)s %(message)s")
    except OSError:
        logging.basicConfig(level=logging.INFO)

def main():
    setup_logging()
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
