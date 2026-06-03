import os
import base64
from uuid import uuid4
from datetime import datetime, timedelta, timezone

from azure.identity import DefaultAzureCredential
from azure.storage.blob import (
    BlobServiceClient,
    ContentSettings,
    BlobSasPermissions,
    generate_blob_sas,
)
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

    start_time = datetime.now(timezone.utc) - timedelta(minutes=5)
    expiry_time = datetime.now(timezone.utc) + timedelta(hours=1)

    user_delegation_key = blob_service_client.get_user_delegation_key(
        key_start_time=start_time,
        key_expiry_time=expiry_time,
    )

    sas_token = generate_blob_sas(
        account_name=blob_service_client.account_name,
        container_name=BLOB_CONTAINER,
        blob_name=blob_name,
        user_delegation_key=user_delegation_key,
        permission=BlobSasPermissions(read=True),
        start=start_time,
        expiry=expiry_time,
    )

    return {
        "blob_name": blob_name,
        "chart_url": f"{blob_client.url}?{sas_token}",
    }

def generate_chart_sas_url(blob_name: str) -> str:
    blob_client = container_client.get_blob_client(blob_name)

    start_time = datetime.now(timezone.utc) - timedelta(minutes=5)
    expiry_time = datetime.now(timezone.utc) + timedelta(hours=1)

    user_delegation_key = blob_service_client.get_user_delegation_key(
        key_start_time=start_time,
        key_expiry_time=expiry_time,
    )

    sas_token = generate_blob_sas(
        account_name=blob_service_client.account_name,
        container_name=BLOB_CONTAINER,
        blob_name=blob_name,
        user_delegation_key=user_delegation_key,
        permission=BlobSasPermissions(read=True),
        start=start_time,
        expiry=expiry_time,
    )

    return f"{blob_client.url}?{sas_token}"