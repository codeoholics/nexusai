import os
import tempfile

import requests
from docx import Document
import fitz  # PyMuPDF
import json

from striprtf.striprtf import rtf_to_text

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
        if 'categories' in parsed_json and parsed_json['categories'].strip():
            parsed_json['categories'] = [category.strip() for category in parsed_json['categories'].split(',')]
        else:
            parsed_json['categories'] = []

        return parsed_json
    except json.JSONDecodeError:
        log.error("Error occurred during JSON parsing: %s", json_string)
        raise ValueError("Error occurred during JSON parsing: %s", json_string)


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
            "categories": [],
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

def extract_file_content_from_s3_url(url):
    try:
        # Download the file
        response = requests.get(url)
        response.raise_for_status()

        # Check if the response is empty
        if not response.content:
            log.error("The response content is empty.")
            return None

        # Log the response status and content length
        log.info(f"Response Status: {response.status_code}, Content Length: {len(response.content)}")

        # Extract filename from URL
        filename = url.split('/')[-1]
        temp_dir = tempfile.gettempdir()
        temp_file_path = os.path.join(temp_dir, filename)

        # Write the content to a temporary file with the same name
        with open(temp_file_path, 'wb') as temp_file:
            temp_file.write(response.content)

        log.info(f"Downloaded the file to {temp_file_path}")

        # Extract text from the file
        summary = extract_text_from_file(temp_file_path)
        log.info(f"Extracted the following text from the file: {len(summary)}")

        # Clean up: Delete the temporary file after use
        os.remove(temp_file_path)

        return summary

    except requests.RequestException as e:
        log.error(f"Failed to download the file: {e}")
        return None
    except Exception as e:
        log.error(f"Error processing the file: {e}")
        return None