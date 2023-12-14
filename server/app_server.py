import os

from flask import Flask, render_template,send_from_directory, request,jsonify,abort
from flask_cors import CORS
import jwt
from shared import config



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


def start_server():
    CORS(app,   resources={r"/api/*": {"origins": "*"}}, allow_headers=["Authorization", "Content-Type"])
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
