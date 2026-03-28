import os
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document
from .mock_data import MOCK_PLACES

CHROMA_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "data", "chroma")

def get_embeddings():
    return OpenAIEmbeddings()

def init_vector_db():
    embeddings = get_embeddings()
    vector_store = Chroma(
        collection_name="travel_places", 
        embedding_function=embeddings, 
        persist_directory=CHROMA_PATH
    )
    
    # Check if already initialized by trying to get the collection count
    # Catch any error if collection is completely fresh
    try:
        existing_count = len(vector_store.get()["ids"])
    except:
        existing_count = 0

    if existing_count == 0:
        print("Initializing ChromaDB with mock data...")
        docs = []
        for place in MOCK_PLACES:
            content = f"Name: {place['name']}\nType: {place['type']}\nLocation: {place['location']}\nDescription: {place['description']}\nCost: ${place['cost']}"
            metadata = {
                "id": place["id"],
                "name": place["name"],
                "type": place["type"],
                "location": place["location"],
                "cost": place["cost"],
                "rating": place["rating"]
            }
            docs.append(Document(page_content=content, metadata=metadata))
        vector_store.add_documents(docs)
        print(f"Added {len(docs)} documents to ChromaDB.")
    else:
        print(f"ChromaDB already contains {existing_count} documents.")
        
    return vector_store

def retrieve_places(query: str, k: int = 3):
    vector_store = Chroma(
        collection_name="travel_places",
        embedding_function=get_embeddings(),
        persist_directory=CHROMA_PATH
    )
    results = vector_store.similarity_search(query, k=k)
    return [res.metadata for res in results]
