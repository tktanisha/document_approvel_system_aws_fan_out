# Document Approval System

## Overview

A backend service for uploading documents, managing approval workflows, tracking audit logs and sending notifications to users.

This system allows users to upload documents, approvers to review and update document status, and the platform to maintain audit logs.

It is designed for scalability, low latency, and event-driven processing.

## Architecture Design
- Client → ALB → ECS Service for core API handling
- Presigned URLs for direct document upload to S3
- DynamoDB for document metadata, status, and audit logs
- SNS + SQS fan-out for asynchronous processing
- Lambda for notifications and audit log processing
- AWS SES for email notifications

## Api Endpoints
Swagger: http://document-approval-system-1672613019.ap-south-1.elb.amazonaws.com/docs

#### Health

- GET /health

#### Authentication

- POST /auth/register
- POST /auth/login

#### Documents

- POST /documents/presign – Generate presigned S3 upload URL
- POST /documents – Create document metadata
- GET /documents – Fetch documents (author / approver view)
- PATCH /documents/{document_id} – Update document status

#### Audit Logs

- GET /auditlogs – Fetch audit history

## DynamoDB Schema

| Access Pattern                | Partition Key                       | Sort Key                              |
| ----------------------------- | ----------------------------------- | ------------------------------------- |
| Get User by email             | `USER`                              | `EMAIL#{email}`                       |
| Get User by id                | `USER`                              | `ID#{user_id}`                        |
| Get Author docs by id         | `AUTHOR#{author_id}`                | `DOC#{doc_id}`                        |
| Get Author docs by status     | `AUTHOR#{author_id}#STATUS#{status}`| `DOC#{doc_id}`                        |
| Get all docs - Approver       | `APPROVER#ALL`                      | `DOC#{doc_id}`                        |
| Get docs by status - Approver | `APPROVER#STATUS#{status}`          | `DOC#{doc_id}`                        |
| Get Audit logs                | `AUDITLOG`                          | `USER#{user_id}#Event#{event_id}`     |

## Data Storage

- S3 – Stores uploaded documents
- DynamoDB – Stores:
    - User details
    - Document metadata
    - Approval status
    - Audit logs
