import os
import shutil
import definitions
from pathlib import Path


# ---
#
# FILE METHODS
#
# ---

# Method to get a file for the given path based on the root directory of the project
def get_file_name(rel_path):
    return str(Path(definitions.ROOT_DIR, rel_path).resolve())


# Method to get a file name from a full path
def get_file_name_from_path(full_path):
    return os.path.basename(full_path)


# Method to get just the suffix of a file.
def get_file_suffix(file_name):
    rtn = os.path.splitext(file_name)[1]
    rtn = rtn.replace(".", "", 1)
    return rtn


# Method to get the name of a file without the suffix.
def get_file_prefix(file_name):
    rtn = get_file_name_from_path(file_name)
    rtn = os.path.splitext(rtn)[0]
    return rtn


# ---
#
# DIRECTORY METHODS
#
# ---

# Method to get all of the directories for the given path.
def get_dirs(path):
    files = os.listdir(path)
    rtn = []
    for file in files:
        cur = os.path.join(str(path), file)
        if os.path.isdir(cur):
            rtn.append(cur)
    return rtn


# Method to get all of the files in the given path.
def get_files(path):
    files = os.listdir(path)
    rtn = []
    for file in files:
        cur = os.path.join(str(path), file)
        if os.path.isdir(cur) == False:
            rtn.append(cur)
    return rtn


# Method to create a directory if it does not exist
def mkdirs(path):
    os.mkdir(path)


# Delete a directory
def rmdir(path):
    if os.path.exists(path):
        shutil.rmtree(path)

