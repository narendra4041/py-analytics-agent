import os
import base64
from uuid import uuid4

from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient, ContentSettings
from dotenv import load_dotenv

load_dotenv()

STORAGE_ACCOUNT_URL = os.getenv("AZURE_STORAGE_ACCOUNT_URL")
BLOB_CONTAINER = os.getenv("AZURE_BLOB_CONTAINER")

credential = DefaultAzureCredential()

blob_service_client = BlobServiceClient(
    account_url=STORAGE_ACCOUNT_URL,
    credential=credential,
)

container_client = blob_service_client.get_container_client(
    BLOB_CONTAINER
)


def upload_chart_base64(chart_base64: str, chat_id: str) -> str:
    image_bytes = base64.b64decode(chart_base64)

    blob_name = f"charts/{chat_id}/{uuid4()}.png"

    blob_client = container_client.get_blob_client(blob_name)

    blob_client.upload_blob(
        image_bytes,
        overwrite=True,
        content_settings=ContentSettings(
            content_type="image/png"
        ),
    )

    return blob_client.url