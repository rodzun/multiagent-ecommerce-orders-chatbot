# 🛒 AI Product Delivery Chatbot – RAG + Autonomous Ordering

This project implements a production-grade e-commerce delivery chatbot capable of answering product questions using RAG retrieval and processing customer orders through natural conversation without forms. Customers can ask about product prices, availability, details, and then confirm purchases.  

The system uses OpenAI function calling for autonomous agent orchestration, Pydantic validation for strict data correctness, SQLite persistence for long-term order storage, and FAISS vector retrieval over 30+ product embeddings.

---

## 🚀 Project Objective

Modern e-commerce platforms lose revenue when customers must browse multiple pages to find information or place orders. This project solves that problem by implementing:

- Natural product Q&A using Vector search  
- Autonomous multi-turn order processing  
- Structured SQL persistence  
- Automatic detail extraction (quantity, product, name, price)  

The chatbot handles the entire journey in one conversation.

---

## 🧠 Architecture Overview

### Two-Agent Conversational System

User → (RAG Agent → Vector Store Search)
↓
Order Intent Detected
↓
(Order Agent → SQL Database)


### Components

1. **RAG Agent (search mode)**
   - Uses FAISS Vector Store
   - Retrieves price, stock status, descriptions
   - Context answers

2. **Order Agent (checkout mode)**
   - Detects purchase intent
   - Extracts product/quantity/history context
   - Calls database functions
   - Returns order confirmation

3. **Function Calling**
   - `tool_search_products`
   - `tool_create_order`

4. **Validation**
   - Pydantic models enforce integrity

5. **Persistent Database**
   - Orders stored permanently in SQLite

---

## 📂 Project Structure
```
data/
└── products.json → 30+ product entries

db/
└── orders.db → SQLite database

src/
├── models.py → Pydantic Product + Order models
├── database.py → SQL CRUD + export JSON utility
├── chatbot.py → Main conversation loop + function calling
└── initialize_vector_store.py → FAISS embedding builder

examples/
├── test_conversations.md → Evidence explanation
├── 1_...png
├── 2_...png
└── etc → Scenarios screenshots

.env → environment variables
.env.example → template
requirements.txt → dependencies
README.md → documentation

```

---

## 🛠 Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Environment Variables

Create .env:
```ini
OPENROUTER_API_KEY=YOUR_KEY
DATABASE_PATH=./db/orders.db
MODEL_NAME=openai/gpt-4o-mini
```

### 3. Build Vector Store
```bash
python src/initialize_vector_store.py
```

### 4. Run Chatbot
```bash
python src/chatbot.py
```

---
## 📦 Product Database
This repo contains 30 real products with:
- product_id
- name
- description
- price
- category
- stock_status

Stored inside:
```bash
data/products.json
```

FAISS embeddings are generated using:
```bash
OpenAI text-embedding-3-small via OpenRouter
```

---
## 🗃 Database Design
SQLite table:
```pgsql
orders (
    order_id      INTEGER PRIMARY KEY AUTOINCREMENT,
    product_name  TEXT NOT NULL,
    quantity      INTEGER NOT NULL,
    customer_name TEXT,
    price         FLOAT NOT NULL,
    total_price   FLOAT NOT NULL,
    timestamp     DATETIME DEFAULT CURRENT_TIMESTAMP
)
```
Data persists across program restarts.

The project includes:

- Create order
- Read order
- Export JSON
---
## 🧾 Pydantic Models
### ProductModel
Ensures:

- price > 0
- name ≥ 2 chars
- description ≥ 10 chars

### OrderModel
Ensures:

- quantity > 0
- total_price = price × quantity
- timestamp auto-generated
---
## 🔍 Why RAG?
Product data changes frequently.
Using a vector database enables:

- semantic retrieval
- free-text user queries
- flexible matching
- accurate pricing
- scalable product inventory

This avoids brittle keyword search.

---
## 🔗 Why Function Calling?
Function calling:

- reduces prompt complexity
- enforces typed schemas
- prevents hallucination
- enables true autonomous orchestration

LLMs choose tools automatically — no manual routing needed.

---
## 🤖 Agent Handoff Logic
LLM decides dynamically:

- If the user is exploring → use RAG tool

- If the user expresses intent → order tool

- No keywords, no routing trees

Examples:
```bash
"What is the price of Adidas shoes?" → search_products

"I'll buy 2 of those" → create_order
```

---
## 📦 Technical Decisions
### Database Choice: SQLite
Reasons:

- Portable

- Durable

- Zero-configuration

- ACID support

- Easy to inspect

### FAISS
- Fast

- Simple setup

- Low dependency footprint

---
## 🧪 Manual Test Scenarios
The following scenarios were manually verified:

- Product retrieval queries

- Ambiguous product queries

- Correct order creation

- Stock failure conditions

- Multiple turn order extraction

Located in:
```bash
examples/test_conversations.md
```

---

## 📝 Example Usage
```
User: Do you have iPhone?
Assistant: yes, price is 999...
User: I'll take 2 units
→ Order created
```

---

## 📜 License
MIT License.