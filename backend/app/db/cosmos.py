import os

from azure.cosmos import CosmosClient
from azure.identity import DefaultAzureCredential
from dotenv import load_dotenv

load_dotenv()

COSMOS_URL = os.getenv("COSMOS_URL")
COSMOS_DATABASE = os.getenv("COSMOS_DATABASE")

credential = DefaultAzureCredential()

client = CosmosClient(
    url=COSMOS_URL,
    credential=credential,
)

database = client.get_database_client(COSMOS_DATABASE)

chat_sessions_container = database.get_container_client("chat_sessions")
messages_container = database.get_container_client("messages")