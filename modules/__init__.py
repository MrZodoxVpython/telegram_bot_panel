import importlib
import os
import glob
from os.path import basename, dirname, isfile

def __list_all_modules():
    mod_paths = glob.glob(dirname(__file__) + "/*.py")
    all_modules = [
        basename(f)[:-3]
        for f in mod_paths
        if isfile(f) and f.endswith(".py") and not f.endswith("__init__.py")
    ]
    return all_modules

ALL_MODULES = sorted(__list_all_modules())

def __import_all_modules():
    base_dir = os.path.dirname(__file__)
    for root, dirs, files in os.walk(base_dir):
        for file in files:
            if file.endswith(".py") and not file.startswith("__"):
                rel_path = os.path.relpath(os.path.join(root, file), base_dir)
                module_path = rel_path[:-3].replace(os.path.sep, ".")
                importlib.import_module(f"xolpanel.modules.{module_path}")

__import_all_modules()

