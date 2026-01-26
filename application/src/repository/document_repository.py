from datetime import datetime
from typing import List, Optional

import botocore
from boto3.dynamodb.types import TypeDeserializer, TypeSerializer
from enums.document_status import DocumentStatus
from exceptions.app_exceptions import InternalServerException, NotFoundException
from models.document import Document
from setup.api_settings import AppSettings


class DocumentRepo:
    def __init__(self, dynamodb):
        self.ddb = dynamodb
        self.table = AppSettings().DDB_TABLE_NAME
        self.serializer = TypeSerializer()
        self.deserializer = TypeDeserializer()

    async def create_document(self, doc: Document):
        try:
            d = doc.model_dump()

            for k, v in d.items():
                if isinstance(v, datetime):
                    d[k] = v.isoformat()

            ddb_item = {k: self.serializer.serialize(v) for k, v in d.items()}

            tx = [
                {
                    "Put": {
                        "TableName": self.table,
                        "Item": {
                            "pk": {"S": f"AUTHOR#{doc.author_id}"},
                            "sk": {"S": f"DOC#{doc.id}"},
                            **ddb_item,
                        },
                    }
                },
                {
                    "Put": {
                        "TableName": self.table,
                        "Item": {
                            "pk": {
                                "S": f"AUTHOR#{doc.author_id}#STATUS#{doc.status.value}"
                            },
                            "sk": {"S": f"DOC#{doc.id}"},
                            **ddb_item,
                        },
                    }
                },
                {
                    "Put": {
                        "TableName": self.table,
                        "Item": {
                            "pk": {"S": "APPROVER#ALL"},
                            "sk": {"S": f"DOC#{doc.id}"},
                            **ddb_item,
                        },
                    }
                },
                {
                    "Put": {
                        "TableName": self.table,
                        "Item": {
                            "pk": {"S": f"APPROVER#STATUS#{doc.status.value}"},
                            "sk": {"S": f"DOC#{doc.id}"},
                            **ddb_item,
                        },
                    }
                },
            ]

            self.ddb.transact_write_items(TransactItems=tx)

        except botocore.exceptions.ClientError as e:
            raise InternalServerException("Failed to create document") from e

    async def get_documents(
        self, user_ctx: dict, status: Optional[str]
    ) -> List[Document]:
        user_id = user_ctx["user_id"]
        role = user_ctx["role"]

        if role == "AUTHOR":
            if status:
                pk = f"AUTHOR#{user_id}#STATUS#{status}"
            else:
                pk = f"AUTHOR#{user_id}"
        else:  # APPROVER
            if status:
                pk = f"APPROVER#STATUS#{status}"
            else:
                pk = "APPROVER#ALL"

        resp = self.ddb.query(
            TableName=self.table,
            KeyConditionExpression="pk = :pk",
            ExpressionAttributeValues={":pk": {"S": pk}},
        )
        items = resp.get("Items", [])
        if not items:
            raise NotFoundException("No documents found")

        documents = [
            {k: self.deserializer.deserialize(v) for k, v in it.items()} for it in items
        ]

        return [Document(**d) for d in documents]

    async def get_by_id(self, document_id: str) -> Document:
        key = {"pk": {"S": "APPROVER#ALL"}, "sk": {"S": f"DOC#{document_id}"}}
        try:
            resp = self.ddb.get_item(TableName=self.table, Key=key)
            item = resp.get("Item")
            if not item:
                raise NotFoundException("document not found")
            d = {k: self.deserializer.deserialize(v) for k, v in item.items()}

            d["status"] = DocumentStatus(d["status"])
            d["created_at"] = datetime.fromisoformat(
                d["created_at"].replace("Z", "+00:00")
            )
            d["updated_at"] = datetime.fromisoformat(
                d["updated_at"].replace("Z", "+00:00")
            )

            return Document(**d)
        except NotFoundException:
            raise
        except Exception as e:
            raise InternalServerException(f"failed to fetch document: {e}")

    async def update_status(
        self, doc: Document, new_status: DocumentStatus, comment: str, now: datetime
    ):

        updated_doc = Document(
            id=doc.id,
            author_id=doc.author_id,
            status=new_status,
            s3_path=doc.s3_path,
            comment=comment,
            created_at=doc.created_at,
            updated_at=now,
        )

        enc = updated_doc.model_dump()
        enc["status"] = new_status.value
        enc["created_at"] = updated_doc.created_at.isoformat().replace("+00:00", "Z")
        enc["updated_at"] = updated_doc.updated_at.isoformat().replace("+00:00", "Z")

        tx = []

        tx.append(
            {
                "Update": {
                    "TableName": self.table,
                    "Key": {
                        "pk": {"S": f"AUTHOR#{doc.author_id}"},
                        "sk": {"S": f"DOC#{doc.id}"},
                    },
                    "UpdateExpression": "SET #s = :s, #c = :c, #u = :u",
                    "ExpressionAttributeNames": {
                        "#s": "status",
                        "#c": "comment",
                        "#u": "updated_at",
                    },
                    "ExpressionAttributeValues": {
                        ":s": {"S": new_status.value},
                        ":c": self.serializer.serialize(comment),
                        ":u": {"S": enc["updated_at"]},
                    },
                }
            }
        )

        tx.append(
            {
                "Update": {
                    "TableName": self.table,
                    "Key": {"pk": {"S": "APPROVER#ALL"}, "sk": {"S": f"DOC#{doc.id}"}},
                    "UpdateExpression": "SET #s = :s, #c = :c, #u = :u",
                    "ExpressionAttributeNames": {
                        "#s": "status",
                        "#c": "comment",
                        "#u": "updated_at",
                    },
                    "ExpressionAttributeValues": {
                        ":s": {"S": new_status.value},
                        ":c": self.serializer.serialize(comment),
                        ":u": {"S": enc["updated_at"]},
                    },
                }
            }
        )

        try:
            self.ddb.transact_write_items(TransactItems=tx)
            return updated_doc

        except Exception:
            raise InternalServerException("transaction failed")
