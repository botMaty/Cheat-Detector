import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'default-secret-key')
    DATA_FILE = 'data.json'
    DB_FILE = 'db.json'
    LOG_DIR = os.path.join(os.path.dirname(__file__), '..', 'logs')