import asyncio
import logging
from datetime import datetime, timezone
from typing import Optional
from helpers.common import Common

import botocore
from boto3.dynamodb.types import TypeDeserializer, TypeSerializer
from enums.user_role import Role
from exceptions.app_exceptions import InternalServerException, UserAlreadyExistsError
from models.user import User
from setup.api_settings import AppSettings

logger = logging.getLogger(__name__)
settings = AppSettings()


class UserRepo:
    def __init__(self, dynamodb):
        self.table_name = settings.DDB_TABLE_NAME
        if not self.table_name:
            raise RuntimeError(Common.DDB_TABLE_NAME_NOT_CONFIGURED)
        self.dynamodb = dynamodb
        self.deserializer = TypeDeserializer()
        self.serializer = TypeSerializer()

    async def find_by_email(self, email: str) -> User:
        try:
            response = self.dynamodb.get_item(
                TableName=self.table_name,
                Key={"pk": {"S": "USER"}, "sk": {"S": f"EMAIL#{email}"}},
            )
        except Exception as e:
            logger.exception(e)
            raise InternalServerException(
                Common.FAILED_FETCH_USER_FROM_DB
            ) from e

        item = response.get("Item")
        if not item:
            return None

        try:
            raw = {
                k: self.deserializer.deserialize(v) for k, v in response["Item"].items()
            }
            raw.pop("pk", None)
            raw.pop("sk", None)
            return User(**raw)
        except Exception as e:
            logger.exception(Common.FAILED_DESERIALIZE_USER_ITEM)
            raise InternalServerException(
                Common.CORRUPTED_USER_DATA_IN_DB
            ) from e

    async def create_user(self, user: User) -> None:
        try:
            payload = user.model_dump()

            if isinstance(payload.get("role"), Role):
                payload["role"] = payload["role"].value

            created_at = payload.get("created_at")
            if isinstance(created_at, datetime):
                payload["created_at"] = (
                    created_at.replace(tzinfo=timezone.utc)
                    .isoformat()
                    .replace("+00:00", "Z")
                )

            item_email = {"pk": "USER", "sk": f"EMAIL#{payload['email']}", **payload}
            item_email_ddb = {
                k: self.serializer.serialize(v) for k, v in item_email.items()
            }

            item_id = {"pk": "USER", "sk": f"ID#{payload['id']}", **payload}
            item_id_ddb = {k: self.serializer.serialize(v) for k, v in item_id.items()}

            self.dynamodb.transact_write_items(
                TransactItems=[
                    {
                        "Put": {
                            "TableName": self.table_name,
                            "Item": item_email_ddb,
                            "ConditionExpression": "attribute_not_exists(pk) AND attribute_not_exists(sk)",
                        }
                    },
                    {
                        "Put": {
                            "TableName": self.table_name,
                            "Item": item_id_ddb,
                            "ConditionExpression": "attribute_not_exists(pk) AND attribute_not_exists(sk)",
                        }
                    },
                ]
            )

        except botocore.exceptions.ClientError as e:
            code = e.response["Error"].get("Code")
            if code == "ConditionalCheckFailedException":
                raise UserAlreadyExistsError(Common.USER_ALREADY_EXISTS) from e

            logger.exception(Common.USER_REPO_DDB_TX_FAILED)
            raise InternalServerException(
                Common.FAILED_CREATE_USER_IN_DB
            ) from e

        except Exception as e:
            logger.exception(Common.UNEXPECTED_ERROR_DURING_USER_CREATION)
            raise InternalServerException(
                Common.DOCUMENT_SERVICE_FAILED
            ) from e

    async def find_by_id(self, user_id: int) -> Optional[User]:
        try:
            key = {"pk": {"S": "USER"}, "sk": {"S": f"ID#{user_id}"}}

            response = await asyncio.to_thread(
                self.dynamodb.get_item, TableName=self.table_name, Key=key
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
                created_at=datetime.fromisoformat(
                    doc.get("created_at").replace("Z", "+00:00")
                ),
            )

        except botocore.exceptions.ClientError as e:
            logger.exception(Common.FAILED_FIND_USER_BY_ID)
            raise InternalServerException(
                Common.ERROR_FROM_USER_REPO.format(error=e)
            ) from e
        except Exception as e:
            logger.exception(Common.UNEXPECTED_ERROR_FIND_BY_ID)
            raise InternalServerException(
                Common.ERROR_FROM_USER_REPO.format(error=e)
            ) from e
        
