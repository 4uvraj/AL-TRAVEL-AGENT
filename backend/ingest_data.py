from app.rag.vector_store import init_vector_db
from dotenv import load_dotenv

load_dotenv()

if __name__ == "__main__":
    print("Initiating Vector DB ingestion...")
    try:
        init_vector_db()
        print("Ingestion complete.")
    except Exception as e:
        print(f"Error during ingestion: {e}")
        print("Hint: Ensure OPENAI_API_KEY is correctly set in the .env file.")
