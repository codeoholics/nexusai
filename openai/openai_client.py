import json

import requests
from shared import config

url = config.get('OPENAI_URL')
# Request headers
token = config.get('OPENAI_TOKEN')
def init_openai():
    global url, token
    url = config.get('OPENAI_URL')
    token = config.get('OPENAI_TOKEN')



def query_openai_api(query):
    # Endpoint URL
    headers = {
        'authority': 'api.openai.com',
        'accept': 'application/json',
        'accept-language': 'en-US,en;q=0.9,ta;q=0.8',
        'authorization': ('Bearer %s' % token),
        'content-type': 'application/json',
           }

    # Request data
    data = {
        "messages": [{
            "role": "user",
            "content": (query)
        }],
        "temperature": 1,
        "max_tokens": 256,
        "top_p": 1,
        "frequency_penalty": 0,
        "presence_penalty": 0,
        "model": "gpt-3.5-turbo",
        "stream": False
    }

    # Make the POST request
    response = requests.post(url, headers=headers, json=data)

    # Parse and return the response (you can also add error handling here)
    return response.json()

# Call the function
def fetch_first_from_openai(prompt):
    # Endpoint URL
    headers = {
        'authority': 'api.openai.com',
        'accept': 'application/json',
        'accept-language': 'en-US,en;q=0.9,ta;q=0.8',
        'authorization': ('Bearer %s' % token),
        'content-type': 'application/json',
    }
    # Request data
    data = {
        "messages": [{
            "role": "user",
            "content": (prompt)
        }],
        "temperature": 1,
        "max_tokens": 256,
        "top_p": 1,
        "frequency_penalty": 0,
        "presence_penalty": 0,
        "model": "gpt-3.5-turbo",
        "stream": False
    }
    # Make the POST request
    response = requests.post(url, headers=headers, json=data)
    # Parse and return the response (you can also add error handling here)
    response_data = response.json()
    # print(json.dumps(response_data, indent=4))
    message_content = response_data['choices'][0]['message']['content']
    return message_content

def fetch_first_from_openai_with_context(context,prompt):
    # Endpoint URL
    headers = {
        'authority': 'api.openai.com',
        'accept': 'application/json',
        'accept-language': 'en-US,en;q=0.9,ta;q=0.8',
        'authorization': ('Bearer %s' % token),
        'content-type': 'application/json',
    }
    # Request data
    data = {
        "messages":
            [{
            "role": "system",
            "content": (context)
        },{
            "role": "user",
            "content": (prompt)
        }
            ],
        "temperature": 1,
        "max_tokens": 256,
        "top_p": 1,
        "frequency_penalty": 0,
        "presence_penalty": 0,
        "model": "gpt-3.5-turbo",
        "stream": False
    }
    # Make the POST request
    response = requests.post(url, headers=headers, json=data)
    # Parse and return the response (you can also add error handling here)
    response_data = response.json()
    print(json.dumps(response_data, indent=4))
    message_content = response_data['choices'][0]['message']['content']
    return message_content



