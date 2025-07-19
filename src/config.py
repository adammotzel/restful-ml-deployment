"""
Initialize / instantiate all supporting objects for the app.

    1. ModelWrapper (using the fitted model object)
    2. LoggingClient
    3. DataCollectionClient
    4. Environment Variables
        a. API Credentials
        b. Server and Port for serving
    5. ThreadPoolExecutor for handling all data collection tasks in a 
       single, separate thread
"""

import os
from concurrent.futures import ThreadPoolExecutor

from dotenv import load_dotenv

from src.model import ModelWrapper
from src.clients import DataCollectionClient, LoggingClient


_logging_client = LoggingClient(
    name=__file__,
    storage_dir="data/logs",
    console_logs=True
)
logger = _logging_client.logger

model = ModelWrapper(path="models/model.pkl")

data_client = DataCollectionClient(
    columns=model.feature_names + [
        "prediction", 
        "identifier", 
        "request_time",
    ],
    storage_dir="data/monitoring",
    logger=logger
)

data_collection_executor = ThreadPoolExecutor(max_workers=1)

load_dotenv()

CORRECT_USERNAME = os.environ["AUTH_UN"]
CORRECT_PASSWORD = os.environ["AUTH_PW"]

HOST = os.getenv("SERVER_IP", "127.0.0.1")
PORT = os.getenv("SERVER_PORT", 8000)
