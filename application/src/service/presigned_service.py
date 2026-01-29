import logging
import uuid

import boto3
from dto.document import PresignRequest, PresignResponse
from exceptions.app_exceptions import InternalServerException

logger = logging.getLogger(__name__)


class PresignedService:

    def __init__(self):
        self.s3 = boto3.client("s3")
        self.bucket_name = "my-doc-approval-bucket"

    async def generate_presigned_url(self, presigned_request: PresignRequest):
        document_id = str(uuid.uuid4())
        file_key = f"documents/{document_id}/{presigned_request.filename}"

        try:
            upload_url = self.s3.generate_presigned_url(
                ClientMethod="put_object",
                Params={
                    "Bucket": self.bucket_name,
                    "Key": file_key,
                    "ContentType": presigned_request.content_type,
                },
                ExpiresIn=300,
            )
        except Exception as e:
            logger.exception("Failed to generate presigned url")
            raise InternalServerException("Failed to generate upload URL") from e

        presign_response = PresignResponse(
            document_id=document_id, upload_url=upload_url, file_key=file_key
        )
        return presign_response

    async def generate_presigned_get_url(self, file_key: str):
        try:
            get_url = self.s3.generate_presigned_url(
                ClientMethod="get_object",
                Params={"Bucket": self.bucket_name, "Key": file_key},
                ExpiresIn=1000,
            )
            return get_url

        except Exception as e:
            logger.exception("Failed to generate presigned get url")
            raise InternalServerException("Failed to generate download URL") from e
