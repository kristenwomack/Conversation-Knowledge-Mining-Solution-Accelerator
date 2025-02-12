import os

from dotenv import load_dotenv
load_dotenv()

class Config:
    SQLDB_DATABASE = os.getenv("SQLDB_DATABASE")
    SQLDB_PASSWORD: str = os.getenv("SQLDB_PASSWORD")
    SQLDB_SERVER: str = os.getenv("SQLDB_SERVER")
    SQLDB_USERNAME: str = os.getenv("SQLDB_USERNAME")

    AZURE_OPENAI_ENDPOINT: str = os.getenv("AZURE_OPEN_AI_ENDPOINT")
    AZURE_OPENAI_DEPLOYMENT_MODEL: str = os.getenv("AZURE_OPEN_AI_DEPLOYMENT_MODEL")
    AZURE_OPENAI_API_KEY: str = os.getenv("AZURE_OPEN_AI_API_KEY")
    AZURE_OPENAI_API_VERSION: str = os.getenv("OPEN_AI_API_VERSION")

    AZURE_AI_SEARCH_ENDPOINT: str = os.getenv("AZURE_AI_SEARCH_ENDPOINT")
    AZURE_AI_SEARCH_API_KEY: str = os.getenv("AZURE_AI_SEARCH_API_KEY")
    AZURE_AI_SEARCH_INDEX: str = os.getenv("AZURE_AI_SEARCH_INDEX")

config = Config()