import importlib.resources as resources

import resources as my_resources
import assets as my_assets
import csv

def get_absolute_path_from_resources(filename):
    file_path = resources.files(my_resources) / str(filename)
    return str(file_path)

def get_absolute_path_from_assets(filename):
    file_path = resources.files(my_assets) / str(filename)
    return str(file_path)

def read_file_content_as_string_from_assets(filename):
    file_path = get_absolute_path_from_assets(filename)
    context = ""
    with open(file_path, "r") as file:
        context = file.read()

    return context

def read_prompt_from(filename):
    return read_file_content_as_string_from_assets("prompts/"+filename)

