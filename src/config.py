import os
from dotenv import load_dotenv
load_dotenv()  # Load environment variables from .env file

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
YOUTUBE_DATA_API = os.getenv('YOUTUBE_DATA_API')
MONGO_URI = os.getenv('MONGO_URI')
DESTINATION_FOLDER = os.getenv('DESTINATION_FOLDER') # path to processed data; or 'Betterchef-AI-Powered-Cooking-App/data/processed'


