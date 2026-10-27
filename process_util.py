#!/usr/bin/env python3

# pylint: disable=missing-function-docstring

import psutil

import config

def obs_is_running():
    """
    True if OBS is running as any user. The scenes directory is shared,
    so another user's OBS can overwrite our changes just like our own.
    """
    name = config.OBS_PROCESS_NAME.lower()
    for process in psutil.process_iter(['name']):
        try:
            if (process.info['name'] or "").lower() == name:
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue
    return False

if __name__ == "__main__":
    print(f"OBS running: {obs_is_running()}")
