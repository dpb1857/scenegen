
import os

import apikey
import config
import google_sheets as gs

def can_get_sheetmap(url, filename):
    try:
        sheetmap = gs.get_sheet_urls(url, apikey.API_KEY)
    except Exception as e:
        return Exception(f"Cannot access sheet information for spreadsheet: {e}")

    if filename not in sheetmap:
        return Exception(f"Cannot find sheet named '{filename}' in spreadsheet")

def validate_config():
    def missing_path(msg, fname):
        return Exception(f"{msg}: {fname}")

    if not os.path.isdir(config.OBS_SCENES_DIRECTORY):
        return missing_path("missing scenes directory", config.OBS_SCENES_DIRECTORY)

    if not os.path.isdir(config.PDF_SLIDES_DIRECTORY):
        return missing_path("missing pdf slides directory", config.PDF_SLIDES_DIRECTORY)

    if not os.path.isfile(f"{config.OBS_SCENES_DIRECTORY}{config.TEMPLATES_FNAME}"):
        return missing_path("missing scene templates file", config.TEMPLATES_FNAME)
