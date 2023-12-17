import csv
import ast
import json
import os

from aiclients import openai_client
from awss3.contentmanager import uploadFile
from db import db_client
from projects import project_repository, sourcecode_service

from projects.document_reader import identify_insights_from_filename, identify_insights_from_text, \
    extract_text_from_file
from projects.project_repository import insert_project_into_db
from shared.resourcereader import get_absolute_path_from_resources

from shared import logger

log = logger.get_logger(__name__)


def get_row_as_json(row, keys):
    master_list = []
    for key in keys:
        raw_value = row.get(key, None)
        if raw_value:
            tags_list = ast.literal_eval(raw_value)
            normalized_tags = []  ## [normalize_tag(tag) for tag in tags_list]
            master_list.extend(normalized_tags)

    return master_list

def remove_bom(key):
    return key.encode('utf-8-sig').decode('utf-8-sig')

def seed_projects_data():
    names = []
    log.info("seed_projects_data")

    # Read and insert data from CSV
    resources_dir = get_resource_folder_path()
    print("Path to 'resources' folder:", resources_dir)
    responses = []
    csv_file_path = os.path.join(resources_dir, 'mockprojects.csv')
    with open(csv_file_path, mode='r', encoding='utf-8-sig') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            log.info(row)
            email = row['name'].lower() + "@student.com"
            filename = row['file']
            full_path = os.path.join(resources_dir, filename)
            # full_path = os.path.join(resources_dir, "summary5.pdf")
            summary_contents = extract_text_from_file(full_path)
            obj = identify_insights_from_text(summary_contents)
            # categories  , split by comma , if empty set empty list
            if obj['categories'] == "":
                obj['categories'] = []
            else:
                obj['categories'] = obj['categories'].split(",")

            obj['categories'] = json.dumps(obj['categories'])
            obj['uploaded_by'] = email
            obj['project_type'] = 'student'
          #  row['githuburl'] = "https://github.com/muthuishere/declarative-optional.git"
            if row['githuburl'] != "":
                obj['prototype_sourcecode'] = row['githuburl']



            obj['institute'] = 'panimalar institute of technology'
            obj['members'] = json.dumps([email])
            log.info(f"Uploading to s3")
            url = uploadFile(full_path, filename)
            obj['summary_file'] = url
            log.info(f"Inserting to db")

            # now get summary conetnt
            current_response = insert_project_into_db(obj)
            log.info(obj)


            #now get the summary , create embedding and put it into vector

            # summary_contents
            log.info(current_response)
            #create embedding from summary
            project_id = current_response["id"]
            summary_embeddings = openai_client.create_openai_embedding(summary_contents)
            summary_response = project_repository.insert_embeddings_to_project(project_id, "summary", summary_embeddings)
            sourcecode_response = None


            if current_response["prototype_sourcecode"]:
                log.info("Validating source code")
                sourcecode_embeddings = sourcecode_service.clone_and_vectorize(current_response["prototype_sourcecode"])
                sourcecode_response = project_repository.insert_embeddings_to_project(project_id, "sourcecode",sourcecode_embeddings)

            responses.append({"project": current_response, "summary": summary_response, "sourcecode": sourcecode_response})
            # break

    log.info(f"Responses: {responses}")
    return responses



def get_resource_folder_path():
    current_script_dir = os.path.dirname(os.path.abspath(__file__))
    resources_dir = os.path.join(current_script_dir, '..', 'resources')
    resources_dir = os.path.abspath(resources_dir)
    return resources_dir



def seed_projects():
    log.info("seed_projects init")
    if db_client.table_has_records("projects"):
        return



