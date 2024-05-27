from pymongo import MongoClient
from dotenv import load_dotenv
import os

def test_mongodb_connection():
    load_dotenv()  # Load environment variables from .env file
    # Fetch MongoDB URI securely from environment variables
    mongo_uri = os.getenv('MONGO_URI')
    if not mongo_uri:
        print("MongoDB URI not found. Please set the MONGO_URI environment variable.")
        return

    try:
        client = MongoClient(mongo_uri)

        # Connect to the MongoDB server and retrieve its version to test the connection
        server_info = client.server_info() 
        print("Successfully connected to MongoDB.")
        print("MongoDB Server Version:", server_info['version'])

        # Optionally, list databases to show a successful connection
        databases = client.list_database_names()
        print("Databases:", databases)

    except Exception as e:
        print("An error occurred while trying to connect to MongoDB:", str(e))

if __name__ == "__main__":
    test_mongodb_connection()
