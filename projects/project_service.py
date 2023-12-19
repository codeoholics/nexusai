from aiclients import openai_client
from db.vector_utils import string_to_vector
from projects import project_repository, sourcecode_service
from projects.document_reader import extract_file_content_from_s3_url
from projects.project_repository import insert_project_into_db
from shared import logger

log = logger.get_logger(__name__)


def insert_project(obj):
    log.info("insert_project init")
    log.info(obj)
    current_response = insert_project_into_db(obj)
    log.info(obj)

    s3file = current_response["summary_file"]
    summary_contents = extract_file_content_from_s3_url(s3file)

    # now get the summary , create embedding and put it into vector

    # summary_contents
    log.info(current_response)
    # create embedding from summary
    project_id = current_response["id"]
    summary_embeddings = string_to_vector(summary_contents)
    summary_plagarismscore = None
    summary_plagarismscore = project_repository.find_similar_and_check_plagiarism("summary", summary_embeddings)
    summary_response = project_repository.insert_embeddings_to_project(project_id, "summary", summary_embeddings)
    sourcecode_response = None
    sourcecode_plagarismscore = None

    if current_response["prototype_sourcecode"]:
        log.info("Validating source code")
        sourcecode_embeddings = sourcecode_service.clone_and_vectorize(current_response["prototype_sourcecode"])
        sourcecode_response = project_repository.insert_embeddings_to_project(project_id, "sourcecode",
                                                                              sourcecode_embeddings)
        sourcecode_plagarismscore = project_repository.find_similar_and_check_plagiarism("sourcecode", summary_embeddings)
    plagiarism_details = []
    if summary_plagarismscore is not None:
        plagiarism_details.extend(summary_plagarismscore)
    if sourcecode_plagarismscore is not None:
        plagiarism_details.extend(sourcecode_plagarismscore)

    if plagiarism_details:
        project_repository.update_project_plagiarism_details(project_id, plagiarism_details)

    return {"project": current_response, "summary": summary_response, "summary_plagarismscore": summary_plagarismscore,
            "sourcecode": sourcecode_response, "sourcecode_plagarismscore": sourcecode_plagarismscore}
