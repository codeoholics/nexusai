import os
from docx import Document
import fitz  # PyMuPDF
import json
import requests
import tempfile

from striprtf.striprtf import rtf_to_text

from io import BytesIO

from aiclients import openrouter_client
from shared import logger

log = logger.get_logger(__name__)


def extract_text_from_file(file_path):
    text = ""
    file_extension = os.path.splitext(file_path)[1].lower()
    try:
        if file_extension == '.docx':
            doc = Document(file_path)
            text = '\n'.join(para.text for para in doc.paragraphs)

        elif file_extension == '.pdf':
            with fitz.open(file_path) as doc:
                text = ''.join(page.get_text() for page in doc)

        elif file_extension in ('.txt', '.md'):  # Treat .md files as plain text
            with open(file_path, 'r', encoding='utf-8') as file:
                text = file.read()

        elif file_extension == '.rtf':
            with open(file_path, 'rb') as file:
                rtf_text = file.read()
                text = rtf_to_text(rtf_text)

    except Exception as e:
        log.error("Error occurred during text extraction: %s", e)
        return None

    return text


def format_insights(json_string):
    """
    Attempts to parse a JSON-like string.
    If parsing fails, returns a JSON object with all fields empty.
    """
    try:
        # Try to parse the JSON string
        parsed_json = json.loads(json_string)
    except json.JSONDecodeError:
        # If parsing fails, create an empty JSON object
        parsed_json = {
            "title": "",
            "description": "",
            "institute": "",
            "categories": "",
            "theme": "",
            "domain": ""
        }
    return parsed_json


def identify_insights_from_filename(filename):
    try:
        contents = extract_text_from_file(filename)
        return identify_insights_from_text(contents)
    except Exception as e:
        log.error("Error occurred during text extraction: %s", e)
        return {
            "title": "",
            "description": "",
            "institute": "",
            "categories": "",
            "theme": "",
            "domain": ""
        }


def identify_insights_from_text(summary):
    try:

        # if question is more than 500 words then we will take first 500 words
        if len(summary) > 500:
            summary = summary[:500]

        prompt = f"""Here is a project summary: {summary}. Please extract the following information in JSON format: title, description, institute, categories (topics separated by commas), theme (such as science or arts or engineering,it), and domain (like disaster management)."""
        log.info(prompt)
        message_content = openrouter_client.fetch_first_from_ai(prompt)

        return format_insights(message_content)
    except Exception as e:
        log.error("Error occurred during text extraction: %s", e)
        return {
            "title": "",
            "description": "",
            "institute": "",
            "categories": "",
            "theme": "",
            "domain": ""
        }

def download_public_s3_file(url):
    try:
        # Download the file
        response = requests.get(url)
        response.raise_for_status()
        summary = None

        # Write the content to a temporary file
        with tempfile.NamedTemporaryFile(delete=True) as temp_file:
            temp_file.write(response.content)
            temp_file.flush()
            filename = temp_file.name  # Get the name of the temporary file
            summary = extract_text_from_file(filename)
            return summary

    except requests.RequestException as e:
        log.error(f"Failed to download the file: {e}")
        return None
    except Exception as e:
        log.error(f"Error processing the file: {e}")
        return None
