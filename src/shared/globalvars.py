from dotenv import load_dotenv
import os


load_dotenv()


# LOCAL POSTGRESQL DATABASE VARIABLES
LOCAL_PG_USER = os.getenv("LOCAL_USER_DB")
LOCAL_PG_PASSWORD = os.getenv("LOCAL_USER_DB_PASSWORD")
LOCAL_PG_DATABASE = os.getenv("LOCAL_NAME_DB")
LOCAL_PG_HOST = os.getenv("LOCAL_HOST_DB")
LOCAL_PG_PORT = os.getenv("LOCAL_PORT_DB")
LOCAL_PG_CONNECTION_STRING = os.getenv("LOCAL_CONNECTION_STRING")


# DEV CONFIG
DEV = os.getenv("DEV_MODE") == "True"