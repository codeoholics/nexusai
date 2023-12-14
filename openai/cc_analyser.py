from db.cache_service import insert_item_to_cache, get_answer_from_cache
from shared import json_utils

import requests

from db.query_executor import analyze_rows, RowColumnType
from db.tag_service import normalize_tag
from openai import openai_client
from db import query_executor
import re

from shared.resourcereader import read_file_content_as_string_from_assets, read_prompt_from
from shared.string_utils import case_insensitive_replace, extract_field_names_within_curly_braces




def convert_to_sql_query(prompt):


    context = read_prompt_from("sqlqueryprompt.txt")

    print(context)
    message_content = openai_client.fetch_first_from_openai_with_context(context,prompt)
    print(message_content)

    data = json_utils.string_to_json(message_content)

    data["parsedsql"]=  parse_json_to_sql(message_content)
    return  data





def parse_json_to_sql(json_input):



    data = json_utils.string_to_json(json_input)
    # print(data)

    if 1 == 1:
        return data['query']

    query = data['query']

    if data.get('params') is None:
        return query

    for param in data['params']:
        if param['columnname'] == 'tags':
            # Extracting the tags from the string representation of the list
            tags = param['value']
            tags = case_insensitive_replace(str(tags), "ARRAY", "")
            tags = tags.strip("[]").replace("'", "").split(',')

            for tag in tags:
                # Normalizing and replacing in the original query
                updated_tag = normalize_tag(tag)
                print(f"""Replacing {tag} with {updated_tag}""")
                query = query.replace(tag, updated_tag)

    return query



def convert_to_response_old(question, rows):
    prompt = f"""I have asked a question: "{question} " , I looked upon a table for the answer
               id, short_summary, issue, resolution, next_steps, sentiment, agent_performance,date_created, tags, product_names
               where id is primary key , date_created is of type timestamp , tags & product_names is of type JSONB , while all other columns are of type TEXT.
               All columns  are self-explanatory. to search with JSONB use sql ```WHERE tags ? 'repair'```   ``` product_names ? 'F150'```
               I have received the following answer from the table for the question: {rows}
               I would like you to build a response for me based on the answer No need to mention table or the question, but it should appear as a human is answering question on his own. strictly avoid table rather use data.
               """
    print(prompt)
    message_content = openai_client.fetch_first_from_openai(prompt)
    return message_content

def parse_response_based_on_data(data):
    rows = data['rows']
    question = data['query']
    answer_template = data['answer_template']
    response = convert_to_response(question, rows)
    return response


def extract_first_value(dict_list):
    """
    Extract the first value from a list of dictionaries. It extracts the value of
    the first key-value pair from the first dictionary in the list.

    :param dict_list: List of dictionaries.
    :return: The value from the first key-value pair in the first dictionary.
    """
    if not dict_list or not isinstance(dict_list, list):
        # If the input is not a list or is an empty list, return None
        print("Input is not a non-empty list.")
        return None

    if not isinstance(dict_list[0], dict) or not dict_list[0]:
        # If the first item in the list is not a dictionary or is an empty dictionary, return None
        print("First item is not a non-empty dictionary.")
        return None

    # Get the first dictionary in the list
    first_dict = dict_list[0]

    # Get the first key in the dictionary
    first_key = next(iter(first_dict))

    # Return the value corresponding to the first key
    return first_dict[first_key]


# def handle_one_row_one_column(data):
#
#     field_names = extract_field_names_within_curly_braces(answer_template)
#     rows = data['rows']
#     print("handle_one_row_one_column" )
#     print(rows)
#     value = extract_first_value(rows)
#     print(value)
#     if len(field_names) == 1:
#         return answer_template.replace("{" + field_names[0] + "}", str(value))
#     else:
#         print("Error: Answer template is wrong" + answer_template)
#         return f"""Your answer is {str(value)}"""

# def handle_more_than_10_rows(data):
#
#
#     answer_template = data['answer_template']
#     field_names = extract_field_names_within_curly_braces(answer_template)
#     rows = data['rows']
#
#     print("Error: Handle 10 rows not implemented" + answer_template)
#
#     return f"""Your answer is {str(rows[0][0])}"""


def convert_to_response_from_openai(question,data):
    content = read_prompt_from("convert_to_response_prompt.txt")
    # replace {question} with question
    content = content.replace("{question}", question)
    # replace {sqlquery} with data['parsedsql']
    content = content.replace("{sqlquery}", data['parsedsql'])
    # replace {answer_template} with data['answer_template']
    # content = content.replace("{answer_template}", data['answer_template'])
    # replace {rows} with data['rows']
    content = content.replace("{rows}", str(data['rows']))
    print(content)
    message_content = openai_client.fetch_first_from_openai(content)
    return message_content


def convert_to_response(question,result_type,data):
    rows = data['rows']


    # if result_type is RowColumnType.ONE_ROW_ONE_COLUMN:
    #     return handle_one_row_one_column(data)


    if(len(rows) > 10):
        rows = data['rows']
        rows = rows[0:10]
        data['rows'] = rows


    return convert_to_response_from_openai(question,data)




def get_answer_for_question(question):

    #Uncomment after things started working
    cached_item = get_answer_from_cache(question)
    if cached_item is not None:
        print("Found in cache")
        return cached_item

    data = convert_to_sql_query(question)
    sqlquery = data['parsedsql']
    print(sqlquery)
    rows = query_executor.execute_fetch_query(sqlquery)
    data["rows"]=rows
    print(rows)
    result_type = analyze_rows(rows)
    if result_type is RowColumnType.NO_DATA:
        return "Unable to find any data for the query"

    answer = convert_to_response(question,result_type,data)

    insert_item_to_cache(question,sqlquery,answer)
    return answer


