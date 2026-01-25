import unittest
from fastapi.testclient import TestClient
from fastapi import Depends
from unittest.mock import AsyncMock
from app import app
from datetime import datetime
from helpers.api_paths import ApiPaths
from setup.dependecies.document_dependency import get_document_service
from helpers.auth_helper import AuthHelper
from service.presigned_service import PresignedService

class TestDocumentController(unittest.TestCase):
    
    @classmethod
    def setup_class(cls):
        cls.client = TestClient(app)

        cls.mock_document_service = AsyncMock()

        async def get_document_service_override():
            return cls.mock_document_service
        
        cls.mock_presigned_service = AsyncMock()

        async def presigned_service_override():
            return cls.mock_presigned_service
        
        async def verify_jwt_override(request):
             request.state.user = {
                "user_id":"user1",
                "role":"AUTHOR",
            }
             
        app.dependency_overrides[get_document_service] = get_document_service_override
        app.dependency_overrides[PresignedService] = presigned_service_override
        app.dependency_overrides[AuthHelper.verify_jwt] = verify_jwt_override


        def test_get_all_document_success(self):

            #Arrange 
            doc = AsyncMock()
            doc.id = "doc1"
            doc.status = "PENDING"
            doc.s3_path = "s3://my-doc-approval-bucket/documents/doc1/file.pdf"
            doc.created_at = datetime(2026, 1, 1, 10, 0, 0)
            doc.updated_at = datetime(2026, 1, 1, 10, 0, 0)
            doc.model_dump.return_value = {
            "id": "doc1",
            "status": "PENDING",
            }


            self.mock_document_service.get_all_document.return_value = [doc]
            self.mock_presigned_service.generate_presiged_url.return_value = (
                "https://signed/documents/doc1/file.pdf"
            )  


            #Act
            response = self.client.get(
                ApiPaths.GET_ALL_DOCUMENTS,
                params = {"status":"PENDING"}
            )

            #Assert
            self.assertEqual(response.status_code,200)

            body = response.json()
            self.assertEqual(len(body["data"]), 1) 

            self.mock_document_service.get_all_document.assert_awaited_once_with(
                {"user_id": "user1", "role": "AUTHOR"},
                status="PENDING",
            ) 

            self.mock_presigned_service.generate_presigned_get_url.assert_awaited_once_with(
                "documents/doc1/file.pdf"
            )

            
