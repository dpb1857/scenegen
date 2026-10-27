# scenegen

Reads a service's run list from the Google Sheet in `config.SCENES_URL` and
writes an OBS scene collection for it, built from the scenes in
`templates.json`. It also downloads the service's slides PDF, which the
generated browser sources display page by page.

It uses the shared OBS setup on this Mac (see `/Users/Shared/OBS/README.md`):

- scene collections: `/Users/Shared/OBS/obs-studio/basic/scenes/`
- slides: `/Users/Shared/OBS/slides/`

so it works the same for every user, whether or not they have run `link-obs.sh`.

## Installing

Put `apikey.py` (a Google API key with the Sheets API enabled, as
`API_KEY = "..."`) in this directory; it is not kept in git. Then:

```sh
make deps            # Homebrew Python and Tk; run as yourself, not root
sudo make install
make check
```

This installs:

| Path | What |
|---|---|
| `/usr/local/lib/scenegen/` | the code, `apikey.py`, and a private Python venv |
| `/usr/local/bin/scenegen` | command-line launcher |
| `/Applications/Scenegen.app` | the same launcher as an app; drag it to the Dock |

It also creates `/Users/Shared/OBS/slides` if it's missing. Rerun
`sudo make install` after changing the code. `sudo make uninstall` removes
everything except the slides directory.

The app icon is `macos/Scenegen.icns`, drawn by `macos/make_icon.py`
(needs Pillow) if you want to change it.

## Using it

Quit OBS (as every user), start Scenegen, and check the sheet name it
offers; it defaults to the coming Sunday. If OBS is running and the scene
collection already exists, it refuses to write it, since OBS would overwrite
the changes.

Errors are shown in a dialog and logged to `~/Library/Logs/scenegen.log`.
