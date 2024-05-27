from pymongo import MongoClient
from langchain.vectorstores import MongoDBAtlasVectorSearch
from langchain.embeddings import OpenAIEmbeddings
import data_managment 

class MongoDBVectorManager:
    def __init__(self, uri, db_name, collection_name, index_name, openai_api_key):
        self.client = MongoClient(uri)
        self.db = self.client[db_name]
        self.collection = self.db[collection_name]  # Corrected to properly reference the collection
        self.index_name = index_name
        self.openai_api_key = openai_api_key
    def clear_collection(self):
        """ Clears all documents from the collection. """
        self.collection.delete_many({})

    def setup_vector_search(self, documents, model='text-embedding-3-small'):
        """
        Sets up a MongoDB Atlas vector search with the provided documents and clears any existing records.
        """
        self.clear_collection()  # Clear existing documents in the collection
        embedding = OpenAIEmbeddings(model=model, openai_api_key= self.openai_api_key)
        
        vector_search = MongoDBAtlasVectorSearch.from_documents(
            documents=documents,
            embedding=embedding,
            collection=self.collection,
            index_name=self.index_name
        )
        return vector_search

    def get_retriever(self, vector_search, search_type="similarity", k=10, score_threshold=0.89):
        """
        Configures and returns a retriever from a vector search.
        """
        return vector_search.as_retriever(
            search_type=search_type,
            search_kwargs={"k": k, "score_threshold": score_threshold}
        )

# # Example usage
# if __name__ == "__main__":
#     db_manager = MongoDBVectorManager(MONGO_URI, 'db name', 'your collection name', 'vector index name for searching', openai_api_key)
#     documents = load_and_process_documents()  # Correct module reference
#     vector_search = db_manager.setup_vector_search(documents)
#     retriever = db_manager.get_retriever(vector_search)
#     print("Retriever is set up and ready to use.")
