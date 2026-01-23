from src.setup.api_settings import AppSettings 
from boto3.dynamodb.types import TypeDeserializer,TypeSerializer
from src.models.audit_log import AuditLog
from src.enums.document_status import DocumentStatus
from src.exceptions.app_exceptions import InternalServerException,NotFoundException
from typing import List,Optional
from datetime import datetime, timezone



settings = AppSettings()

class AuditRepo:
    def __init__(self,dynamodb):
        self.table_name =  settings.DDB_TABLE_NAME

        if not self.table_name:
            raise RuntimeError("DDB_TABLE_NAME is not configured")

        self.dynamodb = dynamodb
        self.deserializer = TypeDeserializer()
        self.serializer = TypeSerializer()

   
    async def get_all_logs(self, user_id: str = None) -> List[AuditLog]:
        try:
            
            params = {
                "TableName": self.table_name,
                "KeyConditionExpression": "pk = :pk",
                "ExpressionAttributeValues": {
                    ":pk": {"S": "AUDITLOG"},
                },
            }

            if user_id:
                sk_prefix = f"USER#{user_id}#EVENT"
                params["KeyConditionExpression"] += " AND begins_with(sk, :sk)"
                params["ExpressionAttributeValues"][":sk"] = {"S": sk_prefix}

            response = self.dynamodb.query(**params)

            items = response.get("Items", [])
            if not items:
                raise NotFoundException("items not found")

            logs = [
                {k: self.deserializer.deserialize(v) for k, v in it.items()}
                for it in items
            ]

            return [AuditLog(**i) for i in logs]

        except NotFoundException:
            raise
        except Exception as e:
            raise InternalServerException(f"audit repository failure = {e}")
