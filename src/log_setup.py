import logging
import os
from logging import FileHandler, Formatter, getLogger

from dotenv import find_dotenv, load_dotenv


load_dotenv(find_dotenv())

# directoryを変更
os.chdir(os.path.dirname(os.path.abspath(__file__)))


common_logger = getLogger(__name__)
common_logger.setLevel(logging.INFO)

stream_handler = FileHandler(filename="logs/common.log")
stream_handler.setLevel(logging.INFO)
stream_handler.setFormatter(Formatter("[%(levelname)s] %(asctime)s %(message)s"))
common_logger.addHandler(stream_handler)


# Azure Application InsightsにLogを送信するときは下記を追加

# pip install opencensus-ext-azure

# from opencensus.ext.azure.log_exporter import AzureLogHandler
# from opencensus.trace import config_integration

# config_integration.trace_integrations(["logging"])

# logging.basicConfig(handlers=[AzureLogHandler()])

# azure_handler = AzureLogHandler()
# azure_handler.setLevel(logging.INFO)
# common_logger.addHandler(azure_handler)
