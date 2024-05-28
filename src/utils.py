# utils.py

# Import libraries.
from io import BytesIO
from PIL import Image
import base64
from openai import OpenAI
import requests
from googleapiclient.discovery import build
from database import *
import getpass
import gradio as gr
import os
import pprint
import sys
from gradio.themes.base import Base
from icecream import ic
from langchain.callbacks.tracers import ConsoleCallbackHandler
from langchain_core.messages import HumanMessage, SystemMessage
from langchain.document_loaders import PyPDFLoader
from langchain.embeddings import OpenAIEmbeddings
from langchain.prompts import PromptTemplate
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import MongoDBAtlasVectorSearch
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI
from pymongo import MongoClient
from langchain.document_loaders import TextLoader
from data_managment import load_and_process_documents
import os
from config import OPENAI_API_KEY, YOUTUBE_DATA_API, MONGO_URI
from policy import policy


client = OpenAI(api_key=OPENAI_API_KEY)
db_manager = MongoDBVectorManager(MONGO_URI, 'recipe_database', 'recipes_collection', 'vector_index', OPENAI_API_KEY)
documents = load_and_process_documents()  
vector_search = db_manager.setup_vector_search(documents)
retriever = db_manager.get_retriever(vector_search)


def check_incoming_query(query, policy=policy):
    """
    Checks if the requested query falls under any unsafe content categories according to the defined policy.
    """
    task_description = f"Task: Determine whether the following query complies with our safety policy. "\
                       "If the query is about food, culinary items or related (while cooking or process) then it is SAFE. "\
                       f"Query to assess:\n---\n{query}\n---"
    
    output_instructions = """
    Instructions for safety assessment:
    - Begin with 'SAFE' or 'UNSAFE'. Use 'UNSAFE' only if the query definitely falls into any of the unsafe content categories.
    - If 'UNSAFE', list the violated category names on a new line, separated by commas.
    """
    
    prompt = f"{task_description}\n{policy}\n{output_instructions}"
    
    response = client.completions.create(
        model="gpt-3.5-turbo-instruct",
        prompt=prompt,
        max_tokens=3000,
        user="user_123456"
    )
    return response

def parse_safety_response(llm_response):
    """
    Parses the safety response from the LLM and returns the safety status and reason.
    """
    response_text = llm_response.choices[0].text
    if 'UNSAFE' in response_text:
        return {'safety_status': 'UNSAFE', 'reason': response_text}
    return {'safety_status': 'SAFE', 'reason': 'None, it is safe.'}


def encode_image_to_base64(image):
    if image is None:
        raise ValueError("No image provided")
    buffered = BytesIO()
    image.save(buffered, format="JPEG")
    return base64.b64encode(buffered.getvalue()).decode('utf-8')

def get_dish_suggestions(image):
    """Analyze uploaded image and suggest dishes based on detailed instructions."""
    base64_image = encode_image_to_base64(image)
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "gpt-4-vision-preview",
        "messages": [{
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": """
                        Instructions:

                        1. Analyze the provided image or list of ingredients.
                        2. Generate possible dishes based on the context.
                        3. If ingredients are provided separately, suggest dishes that can be made using those ingredients.
                        Output Format:
                        - Provide the list of possible dishes.
                        - For each dish, include a brief description or recipe.
                        - Use bullet points or paragraphs for readability.
                    """
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{base64_image}"
                    }
                }
            ]
        }],
        "max_tokens": 700
    }
    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=data)
    if response.status_code == 200:
        return response.json()['choices'][0]['message']['content']
    else:
        return f"Error: {response.status_code} - {response.text}"


def search_youtube_videos(dish_name): #FIXME: when user type in unvalid dish_name
    """Search for YouTube cooking videos."""
    # Safety check of the incoming question
    llm_response = check_incoming_query(f"{dish_name} (food recipe)?")
    safety_response = parse_safety_response(llm_response)
    if safety_response['safety_status'] == 'UNSAFE':
        return [f"https://www.youtube.com/embed/{404}"] # default unvalid link

    youtube = build('youtube', 'v3', developerKey=YOUTUBE_DATA_API)
    search_params = {'q': dish_name + " food recipe", 'part': 'snippet', 'maxResults': 1, 'type': 'video'}
    search_response = youtube.search().list(**search_params).execute()
    video_ids = [item['id']['videoId'] for item in search_response['items']]
    return [f"https://www.youtube.com/embed/{video_id}" for video_id in video_ids]


def generate_embed_html(video_ids):
    """Generate HTML embed code for YouTube videos, displayed two per row."""
    html_content = "<div style='display: flex; flex-wrap: wrap;'>"
    for video_id in video_ids:
        html_content += f'''
        <div style="flex: 1 1 50%; padding: 2px;">
            <iframe width="100%" height="315" src="{video_id}" frameborder="0"
                allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                allowfullscreen></iframe>
        </div>
        '''

    html_content += "</div>"
    return html_content



def get_recipe(dish_name):
    """Fetch a recipe for a selected dish."""

    # Safety check of the incoming question
    llm_response = check_incoming_query(dish_name)
    safety_response = parse_safety_response(llm_response)
    if safety_response['safety_status'] == 'UNSAFE':
        return f"Your dish name query cannot be processed as it violates safety guidelines: {safety_response['reason']}"


    template = """
    Use the following context to generate a detailed recipe for the specified dish or food. Your role is as a cuisine expert, and your job is to create recipes.

    Context:
    {context}

    Dish or Food Name:
    {question}

    Instructions:
    1. Provide a brief overview of the dish, including its origin and key ingredients.
    2. List all necessary ingredients with precise measurements.
    3. Detail each step of the cooking process, ensuring clarity and ease of understanding.
    4. Mention any special cooking techniques or equipment needed.
    5. Include tips for serving and possible variations of the recipe.

    Please ensure your response is:
    - Accurate and based on reliable cooking practices.
    - Clear and easy to understand, avoiding technical jargon unless necessary.
    - Respectful and considerate, recognizing diverse culinary traditions and practices.
    - Helpful and constructed to empower the user to cook successfully and safely.
    - Do not allow any unsafe or unethical response according to the OpenAI guidelines.

    """


    custom_rag_prompt = PromptTemplate.from_template(template)

    llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0.2)

    def format_docs(docs):
      return "\n\n".join(doc.page_content for doc in docs)


    rag_chain = (
      { "context": retriever | format_docs, "question": RunnablePassthrough()}
      | custom_rag_prompt
      | llm
      | StrOutputParser()
    )
    query = dish_name

    answer = rag_chain.invoke(query)

    # Source; generented Reciepe along with embeddings and metadata
    # documents = retriever.get_relevant_documents(query)

    return answer



def ai_assistant_interaction(dish_name, question, chat_log):
    """AI assistant to help with cooking questions using an AI model and a custom template.
    This function emphasizes responsible AI interactions by ensuring accuracy, respectfulness,
    and privacy in its responses."""

    if not question:
        return "Please ask a question to continue."

    # Safety check of the incoming question
    llm_response = check_incoming_query(f"While Cooking {dish_name} (or by accident): {question}")
    safety_response = parse_safety_response(llm_response)
    if safety_response['safety_status'] == 'UNSAFE':
        return f"Your question cannot be processed as it violates safety guidelines: {safety_response['reason']}"





    # Define the template for AI Chef interactions with a focus on responsible AI practices
    template = f"""
    You are an AI chef assistant ready to help with making {dish_name}. Below is the context you can use to provide a thoughtful and accurate response. Remember to be clear and considerate in your guidance.

    Context:
    {{context}}

    Question on dish:
    For cooking {dish_name}: {question}

    Please ensure your response is:
    - Accurate and based on reliable cooking practices.
    - Clear and easy to understand, avoiding technical jargon unless necessary.
    - Respectful and considerate, recognizing diverse culinary traditions and practices.
    - Helpful and constructed to empower the user to cook successfully and safely.
    - Do not allow any unsafe or unethical response according to the OpenAI guidelines.
    """

    # Assuming retriever and formatting functions are correctly set up
    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)

    # Instantiate your model and configure the RAG process
    llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0.2)  # Moderate temperature for predictable responses

    # Setting up the RAG chain
    rag_chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}  # Ensure 'retriever' is properly defined
        | PromptTemplate.from_template(template)  # Use the template dynamically
        | llm
        | StrOutputParser()
    )

    # Invoke the RAG chain with the dish name as a context query
    answer = rag_chain.invoke(dish_name)

    return answer

def clear_all():
    # Return `None` for each component that needs to be cleared
    return None, None, None, None, None, []  # Added an extra `None` for `suggestions_output`

