
from boto3.dynamodb.types import TypeDeserializer, TypeSerializer
import asyncio
from src.setup.api_settings import AppSettings
from src.models.user import User
from src.enums.user_role import Role
from src.exceptions.app_exceptions import(
    NotFoundException, 
    InternalServerException,
      UserAlreadyExistsError
)
from datetime import datetime, timezone
from typing import Optional
import botocore
import logging

logger = logging.getLogger(__name__)
settings = AppSettings()

class UserRepo:
    def __init__(self, dynamodb):
        self.table_name = settings.DDB_TABLE_NAME
        if not self.table_name:
            raise RuntimeError("DDB_TABLE_NAME is not configured")
        self.dynamodb = dynamodb
        self.deserializer = TypeDeserializer()
        self.serializer = TypeSerializer()

    async def find_by_email(self, email: str) -> User:
        try:
            response = self.dynamodb.get_item(
                TableName=self.table_name,
                Key={"pk": {"S": "USER"}, "sk": {"S": f"EMAIL#{email}"}}
            )
        except Exception as e:
            logger.exception("DynamoDB get_item failed in find_by_email")
            raise InternalServerException("Failed to fetch user from database") from e

        if "Item" not in response:
            raise NotFoundException(f"User not found with email {email}")

        try:
            print("response==",response["Item"])
            raw = {k: self.deserializer.deserialize(v) for k, v in response["Item"].items()}
            raw.pop("pk", None)
            raw.pop("sk", None)
            return User(**raw)
        except Exception as e:
            logger.exception("Failed to deserialize user item from DynamoDB")
            raise InternalServerException("Corrupted user data in database") from e

    
    async def create_user(self, user: User) -> None:
        try:
            payload = user.model_dump()

            if isinstance(payload.get("role"), Role):
                payload["role"] = payload["role"].value

            created_at = payload.get("created_at")
            if isinstance(created_at, datetime):
                payload["created_at"] = created_at.replace(tzinfo=timezone.utc).isoformat().replace("+00:00", "Z")

            item_email = {
                "pk": "USER",
                "sk": f"EMAIL#{payload['email']}",
                **payload
            }
            item_email_ddb = {k: self.serializer.serialize(v) for k, v in item_email.items()}

            item_id = {
                "pk": "USER",
                "sk": f"ID#{payload['id']}",
                **payload
            }
            item_id_ddb = {k: self.serializer.serialize(v) for k, v in item_id.items()}

            self.dynamodb.transact_write_items(
                TransactItems=[
                    {
                        "Put": {
                            "TableName": self.table_name,
                            "Item": item_email_ddb,
                            "ConditionExpression": "attribute_not_exists(pk) AND attribute_not_exists(sk)"
                        }
                    },
                    {
                        "Put": {
                            "TableName": self.table_name,
                            "Item": item_id_ddb,
                            "ConditionExpression": "attribute_not_exists(pk) AND attribute_not_exists(sk)"
                        }
                    }
                ]
            )

        except botocore.exceptions.ClientError as e:
            code = e.response["Error"].get("Code")
            if code == "ConditionalCheckFailedException":
                raise UserAlreadyExistsError("User already exists") from e

            logger.exception("DynamoDB transaction failed in create_user")
            raise InternalServerException("Failed to create user in database") from e

        except Exception as e:
            logger.exception("Unexpected error during user creation")
            raise InternalServerException("Unexpected repository failure") from e


        
    async def find_by_id(self, user_id: int) -> Optional[User]:
        try:
            key = {
                "pk": {"S": "USER"},
                "sk": {"S": f"ID#{user_id}"}
            }

            response = await asyncio.to_thread(
                self.dynamodb.get_item,
                TableName=self.table_name,
                Key=key
            )

            item = response.get("Item")
            if not item:
                return None

            doc = {k: self.deserializer.deserialize(v) for k, v in item.items()}

            return User(
                id=str(doc.get("id")),
                name=doc.get("name"),
                email=doc.get("email"),
                password_hash=doc.get("password_hash"),
                role=Role(doc.get("role")),
                created_at=datetime.fromisoformat(doc.get("created_at").replace("Z", "+00:00"))
            )

        except botocore.exceptions.ClientError as e:
            logger.exception("failed to find user by id")
            raise InternalServerException(f"error from user repo : {e}") from e
        except Exception as e:
            logger.exception("unexpected error in find_by_id")
            raise InternalServerException(f"error from user repo : {e}") from e
