"""Render the private EC2 dotenv file from two Secrets Manager payloads."""

import argparse
import json
import os
import re
from pathlib import Path
from urllib.parse import quote


def _compose_value(value: object) -> str:
    # Compose interpolates dollar signs even when they came from env_file.
    rendered = str(value).replace("$", "$$")
    if re.fullmatch(r"[A-Za-z0-9_./:@-]*", rendered):
        return rendered
    return json.dumps(rendered)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--application-secret", required=True, type=Path)
    parser.add_argument("--database-secret", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--image", required=True)
    args = parser.parse_args()

    application = json.loads(args.application_secret.read_text(encoding="utf-8"))
    database = json.loads(args.database_secret.read_text(encoding="utf-8"))

    postgres_host = "reflecta-demo-postgres.cmve4ymqytr2.us-east-1.rds.amazonaws.com"
    postgres_user = database["username"]
    postgres_password = database["password"]
    postgres_url = (
        "postgresql+psycopg2://"
        f"{quote(postgres_user, safe='')}:{quote(postgres_password, safe='')}"
        f"@{postgres_host}:5432/reflecta?sslmode=require"
    )

    values = {
        "ENV": "prod",
        "DEBUG": "false",
        "SQL_ECHO": "false",
        "LOG_LEVEL": "INFO",
        "POSTGRES_HOST": postgres_host,
        "POSTGRES_PORT": "5432",
        "POSTGRES_USER": postgres_user,
        "POSTGRES_PASSWORD": postgres_password,
        "POSTGRES_DB": "reflecta",
        "POSTGRES_POOL_SIZE": "3",
        "POSTGRES_MAX_OVERFLOW": "2",
        "POSTGRES_POOL_TIMEOUT_SECONDS": "15",
        "POSTGRES_POOL_RECYCLE_SECONDS": "600",
        "POSTGRES_COMMAND_TIMEOUT_SECONDS": "30",
        "ALEMBIC_CONNECTION_STRING": postgres_url,
        "ALEMBIC_MIGRATE": "false",
        "NEO4J_URI": "neo4j://neo4j:7687",
        "NEO4J_DATABASE": "neo4j",
        "NEO4J_USER": "neo4j",
        "NEO4J_PASSWORD": application["NEO4J_PASSWORD"],
        "NEO4J_ENCRYPTED": "false",
        "NEO4J_MAX_CONNECTION_POOL_SIZE": "10",
        "NEO4J_CONNECTION_ACQUISITION_TIMEOUT_SECONDS": "15",
        "NEO4J_CONNECTION_TIMEOUT_SECONDS": "10",
        "NEO4J_MAX_CONNECTION_LIFETIME_SECONDS": "600",
        "SMTP_HOST": "localhost",
        "SMTP_PORT": "2525",
        "SMTP_USER": "disabled",
        "SMTP_PASSWORD": "disabled",
        "AWS_S3_REGION": "us-east-1",
        "AWS_S3_WORKS_BUCKET": "reflecta-works-dev-553337000027-us-east-1-an",
        "AWS_S3_MEDIA_BUCKET": "reflecta-works-dev-553337000027-us-east-1-an",
        "AWS_S3_CATALOG_ASSETS_BUCKET": "reflecta-demo-catalog-assets-553337000027",
        "AWS_CLOUDFRONT_CATALOG_ASSETS_BASE_URL": "https://assets.reflectaapp.com.br",
        "AWS_SQS_REGION": "us-east-1",
        "AWS_SQS_EMAILS_QUEUE_URL": "https://sqs.us-east-1.amazonaws.com/553337000027/reflecta-emails-dev",
        "AWS_SQS_WORK_INGESTIONS_QUEUE_URL": "https://sqs.us-east-1.amazonaws.com/553337000027/reflecta-catalog-work-ingestions-dev",
        "AI_WORK_INGESTION_VISIBILITY_TIMEOUT_SECONDS": "300",
        "AI_WORK_INGESTION_HEARTBEAT_INTERVAL_SECONDS": "120",
        "AI_WORK_INGESTION_WAIT_TIME_SECONDS": "20",
        "AI_WORK_INGESTION_CHUNK_LEASE_SECONDS": "900",
        "BATCH_LIMIT": "10",
        "ATTEMPTS_LIMIT": "5",
        "JWT_SECRET": application["JWT_SECRET"],
        "RABBITMQ_URL": "amqp://unused:unused@127.0.0.1:5672/",
        "RABBITMQ_HOST": "127.0.0.1",
        "RABBITMQ_PORT": "5672",
        "RABBITMQ_USER": "unused",
        "RABBITMQ_PASSWORD": "unused",
        "RABBITMQ_VIRTUAL_HOST": "/",
        "RABBITMQ_USE_SSL": "false",
        "RABBITMQ_EMAIL_EXCHANGE": "unused",
        "RABBITMQ_EMAIL_DLX_EXCHANGE": "unused",
        "RABBITMQ_EMAIL_VERIFICATION_QUEUE": "unused",
        "RABBITMQ_EMAIL_VERIFICATION_RETRY_QUEUE": "unused",
        "RABBITMQ_EMAIL_VERIFICATION_DLX_QUEUE": "unused",
        "RABBITMQ_EMAIL_VERIFICATION_ROUTING_KEY": "unused",
        "RABBITMQ_EMAIL_VERIFICATION_RETRY_ROUTING_KEY": "unused",
        "RABBITMQ_EMAIL_VERIFICATION_DLX_ROUTING_KEY": "unused",
        "RABBITMQ_PASSWORD_RESET_QUEUE": "unused",
        "RABBITMQ_PASSWORD_RESET_RETRY_QUEUE": "unused",
        "RABBITMQ_PASSWORD_RESET_DLX_QUEUE": "unused",
        "RABBITMQ_PASSWORD_RESET_ROUTING_KEY": "unused",
        "RABBITMQ_PASSWORD_RESET_RETRY_ROUTING_KEY": "unused",
        "RABBITMQ_PASSWORD_RESET_DLX_ROUTING_KEY": "unused",
        "RABBITMQ_MAX_RETRIES": "5",
        "AWS_SNS_REGION": "us-east-1",
        "AWS_SNS_ARN": "arn:aws:sns:us-east-1:553337000027:reflecta-integration-events-dev",
        "FRONT_END_DOMAIN": "https://reflectaapp.com.br",
        "APP_NAME": "Reflecta",
        "OPENAI_API_KEY": application["OPENAI_API_KEY"],
        "OPENAI_MODEL": "gpt-6-luna",
        "OPENAI_TIMEOUT_SECONDS": "60",
        "OPENAI_MAX_OUTPUT_TOKENS": "12000",
        "OPENAI_PROVIDER_MAX_ATTEMPTS": "3",
        "OPENAI_PROVIDER_RETRY_BASE_SECONDS": "1.0",
        "OPENAI_REASONING_EFFORT": "low",
        "APP_IMAGE": args.image,
        "AWS_REGION": "us-east-1",
        "AWS_LOG_GROUP": "/reflecta/demo/application",
    }

    args.output.write_text(
        "".join(f"{key}={_compose_value(value)}\n" for key, value in values.items()),
        encoding="utf-8",
    )
    os.chmod(args.output, 0o600)


if __name__ == "__main__":
    main()
