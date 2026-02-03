import uuid
import logging
import boto3
from exceptions.app_exceptions import InternalServerException

logger = logging.getLogger(__name__)


class MultipartPresignedService:

    def __init__(self):
        self.s3 = boto3.client("s3")
        self.bucket_name = "my-doc-approval-bucket"

    # 1️⃣ Initiate multipart upload
    async def initiate_multipart_upload(self, filename: str, content_type: str):
        document_id = str(uuid.uuid4())
        file_key = f"documents/{document_id}/{filename}"

        try:
            response = self.s3.create_multipart_upload(
                Bucket=self.bucket_name,
                Key=file_key,
                ContentType=content_type
            )
        except Exception as e:
            logger.exception("Failed to initiate multipart upload")
            raise InternalServerException("Failed to initiate multipart upload") from e

        return {
            "document_id": document_id,
            "upload_id": response["UploadId"],
            "file_key": file_key
        }

    # 2️⃣ Generate presigned URL for ONE part
    async def generate_presigned_part_url(
        self, upload_id: str, file_key: str, part_number: int
    ):
        try:
            upload_url = self.s3.generate_presigned_url(
                ClientMethod="upload_part",
                Params={
                    "Bucket": self.bucket_name,
                    "Key": file_key,
                    "UploadId": upload_id,
                    "PartNumber": part_number,
                },
                ExpiresIn=900,
            )
            return upload_url

        except Exception as e:
            logger.exception("Failed to generate presigned part url")
            raise InternalServerException("Failed to generate part upload URL") from e

    # 3️⃣ Complete multipart upload
    async def complete_multipart_upload(self, upload_id: str, file_key: str, parts: list):
        try:
            self.s3.complete_multipart_upload(
                Bucket=self.bucket_name,
                Key=file_key,
                UploadId=upload_id,
                MultipartUpload={
                    "Parts": [
                        {
                            "PartNumber": p.part_number,
                            "ETag": p.etag
                        }
                        for p in parts
                    ]
                }
            )
        except Exception as e:
            logger.exception("Failed to complete multipart upload")
            raise InternalServerException("Failed to complete multipart upload") from e

    # 4️⃣ Abort multipart upload
    async def abort_multipart_upload(self, upload_id: str, file_key: str):
        try:
            self.s3.abort_multipart_upload(
                Bucket=self.bucket_name,
                Key=file_key,
                UploadId=upload_id
            )
        except Exception as e:
            logger.exception("Failed to abort multipart upload")
            raise InternalServerException("Failed to abort multipart upload") from e
