#!/usr/bin/env python3

# pylint: disable=broad-exception-caught
# pylint: disable=broad-exception-raised
# pylint: disable=line-too-long
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=too-many-instance-attributes

import psutil

def get_running_programs():
    """
    Returns a list of names of currently running programs on Windows 11.

    Returns:
        list: A list of program names (without file extensions)
    """
    running_programs = []

    try:
        # Get all running processes
        for process in psutil.process_iter(['pid', 'name']):
            try:
                # Get process name and remove .exe extension if present
                process_name = process.info['name']
                if process_name.endswith('.exe'):
                    process_name = process_name[:-4]

                # Add to list if not already present (avoid duplicates)
                if process_name not in running_programs:
                    running_programs.append(process_name)

            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                # Skip processes that can't be accessed
                continue

    except Exception as e:
        print(f"Error getting running programs: {e}")
        return []

    # Sort the list for better readability
    return sorted(running_programs)

def get_running_programs_detailed():
    """
    Returns a list of dictionaries with detailed information about running programs.

    Returns:
        list: A list of dictionaries containing name, pid, and memory usage
    """
    running_programs = []

    try:
        for process in psutil.process_iter(['pid', 'name', 'memory_info']):
            try:
                process_info = {
                    'name': process.info['name'],
                    'pid': process.info['pid'],
                    'memory_mb': round(process.info['memory_info'].rss / 1024 / 1024, 2)
                }
                running_programs.append(process_info)

            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue

    except Exception as e:
        print(f"Error getting detailed program info: {e}")
        return []

    # Sort by memory usage (highest first)
    return sorted(running_programs, key=lambda x: x['memory_mb'], reverse=True)

def obs_is_running():
    process_list = get_running_programs()
    return "obs64" in process_list

# Example usage
if __name__ == "__main__":
    print("Running Programs (Simple List):")
    programs = get_running_programs()
    for program in programs[:20]:  # Show first 20 programs
        print(f"- {program}")

    print(f"\nTotal running programs: {len(programs)}")

    print("\n" + "="*50)
    print("Running Programs (Detailed - Top 10 by Memory):")
    detailed_programs = get_running_programs_detailed()
    for program in detailed_programs[:10]:
        print(f"- {program['name']} (PID: {program['pid']}, Memory: {program['memory_mb']} MB)")
