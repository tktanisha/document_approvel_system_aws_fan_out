import unittest
from unittest.mock import MagicMock, patch

from service.presigned_service import PresignedService
from dto.document import PresignRequest
from exceptions.app_exceptions import InternalServerException


class TestPresignedService(unittest.IsolatedAsyncioTestCase):

    @patch("service.presigned_service.boto3.client")
    async def test_generate_presigned_url_success(self, mock_boto_client):
        mock_s3_client = MagicMock()
        mock_s3_client.generate_presigned_url.return_value = "upload-url"

        mock_boto_client.return_value = mock_s3_client

        service = PresignedService()

        presign_request = PresignRequest(
            filename="test.pdf",
            content_type="application/pdf"
        )

        response = await service.generate_presigned_url(presign_request)

        self.assertIsNotNone(response.document_id)
        self.assertEqual(response.upload_url, "upload-url")
        self.assertTrue(response.file_key.startswith("documents/"))

        mock_s3_client.generate_presigned_url.assert_called_once()

    @patch("service.presigned_service.boto3.client")
    async def test_generate_presigned_url_exception(self, mock_boto_client):
        mock_s3_client = MagicMock()
        mock_s3_client.generate_presigned_url.side_effect = Exception("s3 error")

        mock_boto_client.return_value = mock_s3_client

        service = PresignedService()

        presign_request = PresignRequest(
            filename="test.pdf",
            content_type="application/pdf"
        )

        with self.assertRaises(InternalServerException):
            await service.generate_presigned_url(presign_request)

    @patch("service.presigned_service.boto3.client")
    async def test_generate_presigned_get_url_success(self, mock_boto_client):
        mock_s3_client = MagicMock()
        mock_s3_client.generate_presigned_url.return_value = "get-url"

        mock_boto_client.return_value = mock_s3_client

        service = PresignedService()

        result = await service.generate_presigned_get_url(
            "documents/123/test.pdf"
        )

        self.assertEqual(result, "get-url")
        mock_s3_client.generate_presigned_url.assert_called_once()

    @patch("service.presigned_service.boto3.client")
    async def test_generate_presigned_get_url_exception(self, mock_boto_client):
        mock_s3_client = MagicMock()
        mock_s3_client.generate_presigned_url.side_effect = Exception("s3 error")

        mock_boto_client.return_value = mock_s3_client

        service = PresignedService()

        with self.assertRaises(InternalServerException):
            await service.generate_presigned_get_url(
                "documents/123/test.pdf"
            )
