import os
from langchain.document_loaders import TextLoader
from config import DESTINATION_FOLDER

def load_and_process_documents(destination_folder= DESTINATION_FOLDER):
    """
    Loads text files from a specified folder, reads their content, and merges them into a single list.

    Args:
        destination_folder (str): The path to the folder containing text files.

    Returns:
        list: A list of merged document contents.
    """
    # List all text files in the destination folder
    my_txt_files = [file for file in os.listdir(destination_folder) if file.endswith('.txt')]

    # Initialize an empty list to hold the loaders
    loaders = []
    for my_txt in my_txt_files:
        my_txt_path = os.path.join(destination_folder, my_txt)
        loaders.append(TextLoader(my_txt_path))

    # Load data from each file
    data = []
    for loader in loaders:
        data.append(loader.load())

    # Merge the documents
    merged_documents = []
    for doc in data:
        merged_documents.extend(doc)

    # Optional: Print the merged list of all the documents to double check
    print("len(merged_documents) =", len(merged_documents))
    # print(merged_documents)

    return merged_documents

