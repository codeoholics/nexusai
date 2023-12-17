from unittest import TestCase

import app_loader
from projects.project_seeder import seed_projects_data


class Test(TestCase):
    @classmethod
    def setUpClass(cls):
        app_loader.init_app()

    def test_generate_mock_data(self):
        print("===============test_generate_mock_data======================")
        response = seed_projects_data()
        print("=====================================")
        print(response)
        # # assert response is a map with all the keys title description institute categories theme domain
        # self.assertTrue("title" in response)
        # # title should contain home automation lower case
        # self.assertTrue("Home Automation" in response["title"])
        # self.assertTrue("description" in response)
