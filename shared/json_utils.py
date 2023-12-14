import json

def string_to_json(content):
    data = json.loads(content)
    formatted_json_str = json.dumps(data, indent=4)

    # Print the formatted JSON string
    print(formatted_json_str)
    return data
def save_json_to_file(data, filename):
    """
    Save dictionary data to a file in JSON format.

    Args:
    data (dict): The dictionary to save in JSON format.
    filename (str): The name of the file where the data will be saved.
    """
    try:
        with open(filename, 'w', encoding='utf-8') as file:
            # The `json.dump` function serializes the data to a JSON formatted
            # stream and outputs it to the file (represented by `file`).
            json.dump(data, file, ensure_ascii=False, indent=4)
        print(f"Data written to {filename}")
    except IOError as e:
        # Handle file writing errors here
        print(f"An error occurred while writing to the file: {e}")
    except TypeError as e:
        # Handle errors with the data format (if `data` is not serializable)
        print(f"Type error: {e}")
    except Exception as e:
        # Optionally, handle any other exceptions that may occur
        print(f"An unexpected error occurred: {e}")

