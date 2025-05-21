
SCENES_URL = "https://docs.google.com/spreadsheets/d/1Te9oo6jeUPW_tof0Qr3y9-36qcnQWxsg_xJbFaSSuNM/edit?gid=0#gid=0"

MODE = "windows"
# MODE = "linux"

if MODE == "linux":
    OBS_SCENES_DIRECTORY = "./scenes/"
    PDF_SLIDES_DIRECTORY = "./slides/"
elif MODE == "don-windows":
    OBS_SCENES_DIRECTORY = "c:/Users/dpb/AppData/Roaming/obs-studio/basic/scenes/"
    PDF_SLIDES_DIRECTORY = "c:/Users/dpb/Slides/"
else:
    OBS_SCENES_DIRECTORY = "c:/Users/SaintMarks/AppData/Roaming/obs-studio/basic/scenes/"
    PDF_SLIDES_DIRECTORY = "c:/Users/SaintMarks/Slides/"

TEMPLATES_FNAME = "templates.json"
