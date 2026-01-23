import os

class AppSettings:
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
    JWT_ALGORITHM = os.getenv("JWT_ALGORITHM")
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES = os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES")
    DDB_TABLE_NAME = os.getenv("DDB_TABLE_NAME")
    S3_BUCKET_NAME=os.getenv("S3_BUCKET_NAME")
    TOPIC_ARN=os.getenv("TOPIC_ARN")