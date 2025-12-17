import os
import json
import dotenv
from openai import OpenAI
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from database import create_order, init_db, export_orders_to_json
from models import OrderModel

dotenv.load_dotenv()
api_key = os.getenv("OPENROUTER_API_KEY")
model_chat = os.getenv("MODEL_NAME", "openai/gpt-4o-mini")

if not api_key:
    raise ValueError("❌ OPENROUTER_API_KEY not found in .env")

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=api_key,
)

def load_rag_system():
    print("🧠 Loading RAG System with OpenRouter Embeddings...")
    embeddings = OpenAIEmbeddings(
        model="text-embedding-3-small",
        openai_api_key=api_key,
        openai_api_base="https://openrouter.ai/api/v1"
    )
    return FAISS.load_local("faiss_index_openrouter", embeddings, allow_dangerous_deserialization=True)

vector_db = load_rag_system()

def tool_search_products(query: str):
    """Busca productos en el Vector Store."""
    print(f"🔍 [RAG Agent] Searching for: {query}")
    docs = vector_db.similarity_search(query, k=3)
    
    results = []
    for d in docs:
        m = d.metadata
        results.append(f"- {m['name']} (${m['price']}). ID: {m['id']}. Status: {m['stock']}. Description: {d.page_content}")
    
    return "\n".join(results) if results else "No products found."

def tool_create_order(product_name: str, quantity: int, customer_name: str):
    """Procesa y persiste la orden en la DB SQL."""
    print(f"📦 [Order Agent] Processing order for: {product_name}")
    
    init_db()
    search_res = vector_db.similarity_search(product_name, k=1)
    if not search_res:
        return "Error: Product not found to verify price."
    
    p_data = search_res[0].metadata
    
    if p_data['stock'].lower() == "out of stock":
        return f"Sorry, {p_data['name']} is currently out of stock. Order cancelled."

    try:
        total = float(p_data['price']) * quantity
        order_data = OrderModel(
            price=p_data['price'],
            product_name=product_name,
            quantity=quantity,
            total_price=total,
            customer_name=customer_name
        )
        order_id = create_order(order_data)
        export_orders_to_json()
        return f"SUCCESS! Order #{order_id} created for {quantity}x {p_data['name']}. Total: ${total}. Customer: {customer_name}"
    
    except Exception as e:
        return f"Validation error: {str(e)}"

tools_schema = [
    {
        "type": "function",
        "function": {
            "name": "tool_search_products",
            "description": "Search for products in the vector store based on a query to retrieve details like price, availability.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "The search query for products."}
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "tool_create_order",
            "description": "Create and persist an order based on extracted details from conversation. Extract product_name, quantity, price, customer_name from context.",
            "parameters": {
                "type": "object",
                "properties": {
                    "product_name": {"type": "string"},
                    "quantity": {"type": "integer"},
                    "price": {"type": "number"},
                    "customer_name": {"type": "string"}
                },
                "required": ["product_name", "quantity", "price", "customer_name"]
            }
        }
    }
]


def main():
    chat_history = [
        {"role": "system", "content": "You are an e-commerce chatbot. Use tools to search products or create orders based on conversation. Detect purchase intent (e.g., 'buy', 'order') and call create_order autonomously. Extract details from full history without re-asking if possible. Be conversational."}
    ]
    print("Chatbot ready. Type 'exit' to quit.")

    while True:
        user_text = input("\n👤 User: ")
        if user_text.lower() in ["exit", "quit"]: break

        chat_history.append({"role": "user", "content": user_text})

        response = client.chat.completions.create(
            model=model_chat,
            messages=chat_history,
            tools=tools_schema
        )

        resp_msg = response.choices[0].message
        
        if resp_msg.tool_calls:
            chat_history.append(resp_msg)
            
            for call in resp_msg.tool_calls:
                fn_name = call.function.name
                fn_args = json.loads(call.function.arguments)
                
                if fn_name == "tool_search_products":
                    obs = tool_search_products(fn_args['query'])
                elif fn_name == "tool_create_order":
                    obs = tool_create_order(fn_args['product_name'], fn_args.get('quantity', 1), fn_args['customer_name'])
                
                chat_history.append({
                    "tool_call_id": call.id,
                    "role": "tool",
                    "name": fn_name,
                    "content": obs
                })

            second_resp = client.chat.completions.create(
                model=model_chat,
                messages=chat_history
            )
            final_text = second_resp.choices[0].message.content
        else:
            final_text = resp_msg.content

        print(f"🤖 Assistant: {final_text}")
        chat_history.append({"role": "assistant", "content": final_text})

if __name__ == "__main__":
    main()