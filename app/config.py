import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')
    SQLALCHEMY_DATABASE_URI = 'mysql://flaskuser:flaskpass@127.0.0.1/apple_db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False