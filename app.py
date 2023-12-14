# This is a sample Python script.
import dotenv

from server.app_server import start_server
from shared import app_loader



# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    app_loader.init_app()
    start_server()

