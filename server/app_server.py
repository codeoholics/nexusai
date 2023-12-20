import csv
import os
import threading
import traceback

from flask import Flask, render_template, send_from_directory, request, jsonify, abort
from werkzeug.utils import secure_filename
import tempfile
import uuid

from flask_cors import CORS
import jwt
import datetime
import json

from awss3.contentmanager import uploadFile
from projects import project_repository, project_api, chat
from projects.document_reader import extract_text_from_file, identify_insights_from_filename
from projects.project_repository import insert_project_into_db
from shared import config
from awss3 import awsconfig
from shared import logger

log = logger.get_logger(__name__)

app = Flask(__name__, static_folder='static')
app.register_blueprint(project_api.project_api, url_prefix='/api/projects')


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    full_path = os.path.join(app.static_folder, path)
    print("Attempting to serve:", full_path)  # Debug print
    if path != "" and os.path.exists(app.static_folder + '/' + path):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')


@app.before_request
def check_token():
    if request.method == 'OPTIONS':
        return None  # Allows default Flask handling for OPTIONS

    JWT_SECRET = config.get('JWT_SECRET')

    # List of routes that don't need authentication, not using now ,as everything should be authorized to get all
    open_routes = ['/login', '/signup']
    print("request path:", request.path)

    # If request is to an open route, we don't need to check for a token
    if request.path in open_routes:
        return None

    auth_header = request.headers.get('Authorization')

    if auth_header and auth_header.startswith('Bearer '):
        token = auth_header.split(" ")[1]  # Take the token part of the header
        try:
            # Decode the token
            decoded_token = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
            # You can now store the decoded token in the request context
            # to make it available to the view functions if needed
            request.decoded_token = decoded_token
        except jwt.ExpiredSignatureError:

            abort(401, description='Token has expired')
        except jwt.InvalidTokenError:
            abort(401, description='Invalid token')
    else:
        abort(401, description='Missing token')

def getChatResponse(email,projectId,message):
    # return message
    # return "I don't know what to say to that" + message + " " + email + " " + projectId
    return chat.get_answer(email,projectId,message)

@app.route('/api/answer', methods=['GET'])
def answerchat():
    user_data = request.decoded_token
    print("user_data:", user_data)
    return jsonify({'result': getChatResponse(user_data["email"],request.args.get('projectid'),request.args.get('question'))})
    # return jsonify({'result': f'Welcome {user_data["email"]}!'})







@app.route('/api/allprojects', methods=['GET'])
def get_all_projects():
    try:
        projects = project_repository.find_all_projects()
        return jsonify(projects), 200
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route('/api/projects/uploaded_by/<uploaded_by>', methods=['GET'])
def get_projects_by_uploaded_by(uploaded_by):
    try:
        projects = project_repository.find_projects_by_uploaded_by(uploaded_by)
        return jsonify(projects), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/projects/categories', methods=['GET'])
def get_projects_by_categories():
    categories = request.args.get('categories')  # Expected as a comma-separated string
    if categories:
        categories_list = categories.split(',')
    else:
        return jsonify({"error": "No categories provided"}), 400

    try:
        projects = project_repository.find_projects_by_categories(categories_list)
        return jsonify(projects), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/projects/domain/<domain>', methods=['GET'])
def get_projects_by_domain(domain):
    try:
        projects = project_repository.find_projects_by_domain(domain)
        return jsonify(projects), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/projects/search', methods=['GET'])
def search_projects():
    # Extract search filters from query parameters
    filters = {
        'title': request.args.get('title'),
        'project_type': request.args.get('project_type'),
        'theme': request.args.get('theme'),
        'categories': request.args.get('categories'),  # JSON array as a string
        # Add other filters as needed
    }

    # Sorting parameters
    sort_by = request.args.get('sort_by', 'title')
    sort_type = request.args.get('sort_type', 'asc')

    # Pagination parameters
    try:
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
    except ValueError:
        return jsonify({"error": "Invalid pagination parameters"}), 400

    try:
        search_results = project_repository.search_projects_with_pagination(filters, page, per_page, sort_by, sort_type)
        return jsonify(search_results), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# import csv
# import threading
# from flask import Flask, request, jsonify
#
# app = Flask(__name__)


def process_data(data,user_data):
    log.info("Processing data...")
    log.info("Data: %s", data)
    log.info("User data: %s", user_data)
    # Implement the logic to process your data
    pass


@app.route('/api/projects/uploadmultipleprojecttemplate', methods=['POST'])
def uploadmultipleprojecttemplate():
    user_data = request.decoded_token
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400  # Bad Request

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400  # Bad Request

    if file:
        temp_dir = tempfile.mkdtemp()
        temp_path = os.path.join(temp_dir, secure_filename(file.filename))
        file.save(temp_path)

        try:
            with open(temp_path, newline='') as csvfile:
                reader = csv.DictReader(csvfile)
                required_fields = {'fileurl', 'title', 'member', 'domain', 'categories', 'sourcecode_url', 'demo_url'}

                if not required_fields.issubset(reader.fieldnames):
                    return jsonify({'error': 'CSV does not have the required fields'}), 400  # Bad Request

                data = [row for row in reader]
                threading.Thread(target=process_data, args=(data,user_data,)).start()

                return jsonify({'message': 'File uploaded and processing started'}), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500  # Internal Server Error
        finally:
            os.remove(temp_path)
            os.rmdir(temp_dir)

    return jsonify({'error': 'An unexpected error occurred'}), 500  # Internal Server Error






@app.route('/api/projects/createtemplate', methods=['POST'])
def createtemplate():
    user_data = request.decoded_token
    log.info("user %s", user_data)
    log.info("request %s", request)
    log.info(request.files)

    if 'files' not in request.files:
        return jsonify({'error': 'No files part'}), 400

    files = request.files.getlist('files')

    # if 'files' not in request.files:
    #     return jsonify({'error': 'No files part'}), 400  # Bad Request
    #
    # files = request.files.getlist('files')
    file_urls = []

    try:
            # If the user does not select a file, the browser submits an
            # empty file without a filename.
            for file in files:
                log.info("file %s", file)
                if file.filename == '':
                    return jsonify({'error': 'No selected file'}), 400  # Bad Request

                if file:

                    filename = secure_filename(file.filename)
                    temp_dir = tempfile.mkdtemp()
                    temp_path = os.path.join(temp_dir, filename)
                    file.save(temp_path)

                    # Upload the file to S3

                    try:
                        log.info("Uploading filename: %s", filename)

                        userid = user_data["userId"]

                        # Todo , use this once its in production
                        random_uuid = uuid.uuid4().hex
                        filename = f"{userid}-{random_uuid}-{filename}"
                        #filename = f"{userid}-{filename}"
                        url = uploadFile(temp_path, filename)
                        file_urls.append(url)

                    except Exception as e:
                        traceback.print_exc()
                        log.error("An error occurred: %s", e)


                    finally:
                        # Clean up the temporary file

                        os.remove(temp_path)
                        os.rmdir(temp_dir)
            with tempfile.NamedTemporaryFile(mode='w+', delete=False) as temp_csv:
                fieldnames = ['fileurl', 'title', 'member', 'domain', 'categories','sourcecode_url','demo_url']
                writer = csv.DictWriter(temp_csv, fieldnames=fieldnames)
                writer.writeheader()
                for url in file_urls:
                    writer.writerow({'fileurl': url, 'title': '', 'member': '', 'domain': '', 'categories': '', 'sourcecode_url': '','demo_url': ''})

                temp_csv.flush()
                temp_csv.close()  # Close the file to ensure all data is written

                random_uuid = uuid.uuid4().hex
                filename = f"template-{random_uuid}-projects.csv"
                temp_file_path = temp_csv.name  # Get the path of the temporary file

                try:
                    url = uploadFile(temp_file_path, filename)  # Pass the file path instead of the file object
                finally:
                    os.unlink(temp_file_path)  # Delete the temporary file after uploading

                return jsonify({"url": url,
                                'result': f'Template created Successfully for files'})


    except Exception as e:
        traceback.print_exc()
        log.error("An error occurred: %s", e)
        return jsonify({'error': str(e)}), 500  # Internal Server Error




@app.route('/api/projects/uploaddocument', methods=['POST'])
def uploaddocument():
    user_data = request.decoded_token
    log.info("user %s", user_data)
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400  # Bad Request

    file = request.files['file']

    # If the user does not select a file, the browser submits an
    # empty file without a filename.
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400  # Bad Request

    if file:

        filename = secure_filename(file.filename)
        temp_dir = tempfile.mkdtemp()
        temp_path = os.path.join(temp_dir, filename)
        file.save(temp_path)

        # Upload the file to S3

        try:
            log.info("Uploading filename: %s", filename)

            userid = user_data["userId"]

            # Todo , use this once its in production
            random_uuid = uuid.uuid4().hex
            # filename = f"{userid}-{random_uuid}-{filename}"
            filename = f"{userid}-{filename}"
            url = uploadFile(temp_path, filename)
            content = identify_insights_from_filename(temp_path)
            return jsonify({"url": url, "content": content,
                            'result': f'File uploaded successfully to S3. Welcome {user_data["email"]}!'})
        except Exception as e:
            log.error("An error occurred: %s", e)
            return jsonify({'error': str(e)}), 500  # Internal Server Error

        finally:
            # Clean up the temporary file
            os.remove(temp_path)
            os.rmdir(temp_dir)

    return jsonify({'error': 'An unexpected error occurred'}), 500  # Internal Server Error



def start_server():
    CORS(app, resources={r"/api/*": {"origins": "*"}}, allow_headers=["Authorization", "Content-Type"])
    app.run(use_reloader=True, debug=True, port=5000, threaded=True)

#
# @app.route('/api/answer', methods=['POST'])  # Changed to POST
# def answer_chat_via_post():
#     # Parse the JSON data from the request body
#     data = request.get_json()  # or you can use request.json
#
#     # Validate and extract the 'question' property from the JSON body
#     if data and 'question' in data:
#         question = data['question']
#         answer = getChatResponse(question)
#         return jsonify({'result': answer})
#     else:
#         # Bad request: the client did not provide the necessary 'question' property
#         return jsonify({'error': 'Missing "question" in the request body'}), 400
