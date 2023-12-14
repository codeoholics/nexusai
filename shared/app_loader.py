
from dotenv import load_dotenv

from db import db_client

from db.projects_service import ensure_projects_exists

from openai import openai_client
from  shared import config
from shared.resourcereader import get_absolute_path_from_resources


def setup_database():
    db_client.initdb()
    ensure_projects_exists()




def init_app():
    load_dotenv()
    print("Loaded environment variables from .env file")
    print(f"DB_HOST: {config.get('PG_HOST')}")
    setup_database()
    openai_client.init_openai()
    print("App initialized successfully!")