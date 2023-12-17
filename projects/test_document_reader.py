import os
from unittest import TestCase

from projects.document_reader import extract_text_from_file, identify_insights_from_filename, extract_file_content_from_s3_url
from projects.project_seeder import get_resource_folder_path
from shared import logger
log = logger.get_logger(__name__)
import app_loader


class Test(TestCase):
    @classmethod
    def setUpClass(cls):
        app_loader.init_app()

    def test_identify_insights_should_work_well_for_avalid_file(self):
        response = identify_insights_from_filename("../resources/summary1.docx")
        print("=====================================")
        print(response)
        # assert response is a map with all the keys title description institute categories theme domain
        self.assertTrue("title" in response)
        # title should contain home automation lower case
        self.assertTrue("Home Automation" in response["title"])
        self.assertTrue("description" in response)
    def test_identify_insights_for_all__documents_should_work_well(self):
        resources_dir = get_resource_folder_path()
        print("Path to 'resources' folder:", resources_dir)

        files = os.listdir(resources_dir)
        docx_and_pdf_files = [f for f in files if f.endswith('.docx') or f.endswith('.pdf')]
        for filename in docx_and_pdf_files:
            full_path = os.path.join(resources_dir, filename)
            print("=====================================" + full_path)
            response = identify_insights_from_filename(full_path)
            log.info(response)
            self.assertTrue("title" in response)
            # title should not be empty string
            self.assertTrue(len(response["title"]) > 0)





    def test_extract_text_from_file_should__return_properly(self):
        response = extract_text_from_file("../resources/summary1.docx")
        log.info(response)

        self.assertTrue("The rapid advancement in Internet of Things" in response)

    def test_download_public_s3_file_should_work_properly(self):
        response = extract_file_content_from_s3_url("../resources/summary1.docx")
        self.assertTrue("The rapid advancement in Internet of Things" in response)
