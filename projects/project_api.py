import datetime
import json

from flask import Blueprint, jsonify, request

from projects import project_repository
from projects.project_service import insert_project

project_api = Blueprint('project_api', __name__)

from shared import logger

log = logger.get_logger(__name__)


# string: This is the default type. It accepts any text without a slash. For example, in @app.route('/items/<string:item_id>'), the item_id will capture a string like abc123.

# int: Accepts positive integers. For example, @app.route('/items/<int:item_id>') will match URLs like /items/123 but not /items/abc.
#
# float: Like int but for floating point values. Useful for numerical values that may have a fractional part.
#
# path: Similar to string, but it also accepts slashes. This is useful when you expect part of the URL to include forward slashes. For example, @app.route('/path/<path:subpath>') can match /path/some/text/here.
#
# uuid: Accepts UUID strings. If you're using UUIDs as identifiers in your application, this can automatically validate that the URL parameter is a valid UUID. For instance, @app.route('/users/<uuid:user_id>') will only match valid UUID strings.

@project_api.route('/<string:project_id>', methods=['GET'])
def get_project_by_id(project_id):
    try:
        project = project_repository.find_project_by_id(project_id)
        if project:
            return jsonify(project), 200
        else:
            return jsonify({"error": "Project not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@project_api.route('', methods=['POST'])
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
        result = insert_project(data)

        return jsonify({"message": "Project added successfully", "result": result}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500
