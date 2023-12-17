from unittest import TestCase

from projects import sourcecode_service
from projects.document_reader import extract_text_from_file, identify_insights_from_filename, extract_file_content_from_s3_url
import app_loader
from projects.project_seeder import seed_projects_data


class Test(TestCase):
    @classmethod
    def setUpClass(cls):
        app_loader.init_app()

    def test_vectorize_source_code(self):
        response = sourcecode_service.clone_and_vectorize("https://github.com/muthuishere/declarative-optional.git")
        print("=====================================")
        print(response)
        # # assert response is a map with all the keys title description institute categories theme domain
        # self.assertTrue("title" in response)
        # # title should contain home automation lower case
        # self.assertTrue("Home Automation" in response["title"])
        # self.assertTrue("description" in response)
