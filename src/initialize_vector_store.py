import os
import json
import dotenv
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document
from models import ProductModel

dotenv.load_dotenv()

DATA_PATH = "data/products.json"
VECTOR_STORE_PATH = "faiss_index_openrouter"

def initialize_vector_store():
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise ValueError("❌ OPENROUTER_API_KEY not found in .env")

    print("🔄 Loading products...")
    with open(DATA_PATH, 'r', encoding='utf-8') as f:
        products = json.load(f)

    documents = []
    for p in products:
        validated_p = ProductModel(**p)
        content = f"Product: {validated_p.name}. Category: {validated_p.category}. Description: {validated_p.description}. Price: {validated_p.price}"
        metadata = {
            "id": validated_p.product_id,
            "name": validated_p.name,
            "price": validated_p.price,
            "stock": validated_p.stock_status
        }
        documents.append(Document(page_content=content, metadata=metadata))

    print("🧠 Generating Embeddings via OpenRouter (text-embedding-3-small)...")
    
    embeddings = OpenAIEmbeddings(
        model="text-embedding-3-small",
        openai_api_key=api_key,
        openai_api_base="https://openrouter.ai/api/v1"
    )

    vector_store = FAISS.from_documents(documents, embeddings)
    vector_store.save_local(VECTOR_STORE_PATH)
    print(f"✅ FAISS Index created successfully at {VECTOR_STORE_PATH}")

if __name__ == "__main__":
    initialize_vector_store()