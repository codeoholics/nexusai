from dotenv import load_dotenv
import os




def get(key,default=None):
    load_dotenv()
    return os.getenv(key,default)

