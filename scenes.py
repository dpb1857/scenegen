#!/usr/bin/env python3

# pylint: disable=broad-exception-caught
# pylint: disable=broad-exception-raised
# pylint: disable=line-too-long
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=too-many-instance-attributes

import copy
import json
import uuid

import apikey
import config
import google_drive as gd
import google_sheets as gs


def generate_scene(scene_name, template_name, pagenum, templates, pdf_url):

    def create_custom_browser():
        name = f"Browser{scene_name}"
        for source in templates["sources"]:
            if source["id"] == "browser_source":
                b = copy.deepcopy(source)
                b.update({"name": name,
                          "uuid": str(uuid.uuid4())})
                b["settings"]["url"] = f"{pdf_url}&page={pagenum}"
                if name.endswith("->"):
                    b["settings"]["restart_when_active"] = True

                return b
        raise Exception("Could not find a browser object")

    def find_scene_browser(scene):
        for item in scene["settings"]["items"]:
            if item["name"].startswith("Browser"):
                return item
        return None

    def update_scene_browser(scene_browser_item, browser):
        scene_browser_item.update({"name": browser["name"],
                                   "source_uuid": browser["uuid"]})

    def create_scene_from_template(scene_name, template_name):
        for source in templates["sources"]:
            if source["id"] == "scene" and source["name"] == template_name:
                s = copy.deepcopy(source)
                s.update({"name": scene_name,
                          "uuid": str(uuid.uuid4())})
                return s
        raise Exception(f"Could not find scene template {template_name}")

    # print("Processing:", name, template, page)
    scene = create_scene_from_template(scene_name, template_name)
    b = None
    scene_browser_item = find_scene_browser(scene)
    if scene_browser_item:
        b = create_custom_browser()
        update_scene_browser(scene_browser_item, b)

    return b, scene

def _generate_scenes(runlist, templates, scenelist_name, pdf_url):

    new_scenes = [generate_scene(*scene_spec, templates, pdf_url) for scene_spec in runlist[1:]]

    # Attempt to set the current scene
    templates["current_scene"] = new_scenes[0][1]
    templates["current_program_scene"] = new_scenes[0][1]

    # Each new scene must be added to 'scene_order' and appended to 'sources'
    for scene_browser, scene in new_scenes:
        templates["scene_order"].append({"name": scene["name"]})
        templates["sources"].append(scene)
        if scene_browser:
            templates["sources"].append(scene_browser)

    templates["name"] = scenelist_name
    return templates

def generate_scenes(url, scenelist_name):

    obs_scenes_directory = config.OBS_SCENES_DIRECTORY
    pdf_slides_directory = config.PDF_SLIDES_DIRECTORY
    templates_fname = config.TEMPLATES_FNAME

    scenes_map = gs.get_sheet_urls(url, apikey.API_KEY)
    runlist_url = scenes_map[scenelist_name]
    runlist_data = gs.download_sheet(runlist_url)

    pdf_url = f"file:///{pdf_slides_directory}Slides-{scenelist_name}.pdf#toolbar=0"

    fname = f"{obs_scenes_directory}/{templates_fname}.json"
    with open(fname, "r", encoding="utf-8") as file:
        templates = json.load(file)

    scenes = _generate_scenes(runlist_data, templates, scenelist_name, pdf_url)

    with open(f"{obs_scenes_directory}/{scenelist_name}", "w", encoding="utf-8") as file:
        json.dump(scenes, file, indent=4, ensure_ascii=False)

def download_pdf(url, filename):
    pdf_slides_directory = config.PDF_SLIDES_DIRECTORY

    pdf_filename = f"{pdf_slides_directory}Slides-{filename}.pdf"

    pdf_url_data = gs.download_sheet(url)
    pdf_map = dict(pdf_url_data)
    if filename in pdf_map:
        pdf_url = pdf_map[filename]
        gd.download_to_local_filesystem(pdf_url, pdf_filename)
