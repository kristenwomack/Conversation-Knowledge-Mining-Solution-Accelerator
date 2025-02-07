import os

from dotenv import load_dotenv
load_dotenv()

class Config:
    SQLDB_DATABASE = os.getenv("SQLDB_DATABASE")
    SQLDB_PASSWORD: str = os.getenv("SQLDB_PASSWORD")
    SQLDB_SERVER: str = os.getenv("SQLDB_SERVER")
    SQLDB_USERNAME: str = os.getenv("SQLDB_USERNAME")

config = Config()