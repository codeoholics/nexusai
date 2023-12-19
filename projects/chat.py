import json
import traceback
from datetime import datetime

from aiclients import openrouter_client
from projects.document_reader import extract_file_content_from_s3_url
from projects.project_repository import find_project_by_id
from shared import logger

log = logger.get_logger(__name__)

def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not serializable")

def get_answer(username,project_id,query):
    try:
        log.info("get_answer init")
        log.info(username)
        log.info(query)
        log.info(project_id)

        project_details = find_project_by_id(project_id)
        log.info(project_details)
        contents = extract_file_content_from_s3_url(project_details["summary_file"])
        log.info(contents)
        prompt = f"""Your name is {project_details['title']} , The question is asked by {username}, Here is a project details in json {json.dumps(project_details, default=json_serial)}. also some more details about project is {contents} please answer the following questions.{query}"""
        log.info(prompt)
        message_content = openrouter_client.fetch_first_from_ai(prompt)
        log.info(message_content)

        return message_content
    except Exception as e:
        traceback.print_exc()
        log.error("Error occurred during get_answer: %s", e)
        return "Unable to get answer"