# Test Conversations Documentation

This project uses manual conversation test evidence (screenshots) to validate
the agent behavior. Each screenshot represents a real conversation between
the chatbot and a user through the CLI interface.

The goal is to demonstrate that the agent:
- searches products correctly,
- handles multi-turn conversations,
- prevents invalid order creation,
- resolves ambiguous requests by asking clarification,
- and rejects unrelated or impossible queries.

## Test Coverage

The screenshot conversations cover at least eight scenarios required:

### 1. Product price request
The agent finds a product and returns price information correctly.

### 2. Ambiguous request → asks for clarification
When user intent is unclear, the agent requests additional information instead of guessing.

### 3. Context-aware parameter handling
After a product is discussed, the agent uses this context to fill function call parameters (e.g., quantity or product name).

### 4. Multiple matching results
When several products match the query, the agent presents options instead of choosing arbitrarily.

### 5. Non-existent product purchase attempt → clarification/denial
The agent refuses to create an order if the product does not exist and asks the user to reformulate the request.

### 6. Invalid quantity or tool error handling
The agent detects invalid input (e.g., non-numeric or negative quantity) and responds safely without crashing.



## Evidence

All evidence is included separately as screenshots. They show the input,
model response, and expected behavior aligned with the project rubric.
