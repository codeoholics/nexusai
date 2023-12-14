from unittest import TestCase
from shared import app_loader
from openai import cc_analyser
from openai.cc_analyser import get_answer_for_question,  convert_to_sql_query

from db import query_executor

class Test(TestCase):
    @classmethod
    def setUpClass(cls):
        app_loader.init_app()

    def test_answer_my_question_for_how_many_people_called(self):
        response = get_answer_for_question("How many people called")
        print("=====================================")
        print(response)
    def test_answer_my_question_for_top_10_issues(self):
        response = get_answer_for_question("What are the top 10 issues that customers  with F150 called ")
        print("=====================================")
        print(response)
    def test_answer_my_question_for_top_10_issues_F250(self):
        response = get_answer_for_question("What are the top 10 issues that customers  with F250 called ")
        print("=====================================")
        print(response)

    def test_answer_my_question_for_top_10_issues_F250_last_week(self):
        response = get_answer_for_question("What are the top 10 issues that customers  with F250 called last week ")
        print("=====================================")
        print(response)


    def test_convert_to_sql_and_fetch_results(self):
        rows = convert_to_sql_query("what are the top 10 issues that customers  with F150 called last week")
        print(rows)
    def test_convert_to_sql(self):
        rows = convert_to_sql_query("what are the top 10 issues that customers  with F150 called last week")
        print(rows)
    def test_convert_to_sql_how_many_people_called(self):
        rows = convert_to_sql_query("How many people called")
        print(rows)



