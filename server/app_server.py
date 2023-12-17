import os

from flask import Flask, render_template, send_from_directory, request, jsonify, abort
from werkzeug.utils import secure_filename
import tempfile
import uuid

from flask_cors import CORS
import jwt
import datetime
import json

from awss3.contentmanager import uploadFile
from projects.document_reader import extract_text_from_file, identify_insights_from_filename
from projects.project_repository import insert_project_into_db
from shared import config
from awss3 import awsconfig
from shared import logger

log = logger.get_logger(__name__)

app = Flask(__name__, static_folder='static')



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


@app.route('/api/answer', methods=['GET'])
def answerchat():
    user_data = request.decoded_token
    print("user_data:", user_data)
    return jsonify({'result': f'Welcome {user_data["email"]}!'})





@app.route('/api/projects', methods=['POST'])
def add_project():
    user_data = request.decoded_token
    log.info("user %s", user_data)
    data = request.json
    if not data:
        return jsonify({"error": "No data provided"}), 400

    data['uploaded_by'] = user_data.get('email')
    current_time = datetime.datetime.now()
    data['date_created'] = current_time
    data['date_updated'] = current_time

    # Ensure members and categories are JSON arrays
    if 'members' in data and isinstance(data['members'], list):
        data['members'] = json.dumps(data['members'])
    if 'categories' in data and isinstance(data['categories'], list):
        data['categories'] = json.dumps(data['categories'])

    try:
        insert_project_into_db(data)
        return jsonify({"message": "Project added successfully"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


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
