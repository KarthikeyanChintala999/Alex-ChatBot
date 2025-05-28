# 🛍️ Alex - Your E-Commerce Assistant

Welcome to **Alex**, your personalized E-Commerce assistant built with [Streamlit](https://streamlit.io/), [LangChain](https://www.langchain.com/),
and interactive visual analytics using [Plotly](https://plotly.com/). Alex helps customers with their orders, products, loyalty points, and personalized
shopping tips — all with conversational ease.

---

##  Features

###  Conversational Chatbot
- Ask about order status, product suggestions, loyalty points, and more.
- Human-like responses powered by a LangChain agent.
- Retains chat history for contextual conversation.

### Real-time Analytics Dashboard
- See metrics like:
  - Total user queries
  - Success rate
  - Average response time
  - Multi-tool usage rate
- Tool usage visualized with dynamic bar charts.
- Interaction timeline and success/failure pie charts with Plotly.

### Quick Start Options
- Sample buttons to trigger queries like:
  - Greeting the bot
  - Checking order status
  - Asking about loyalty points
  - Weather-based shopping recommendations

###  Reset Functionality
- Reset the chat history to start fresh anytime.

---

## Behind the Scenes

###  Components
- **`main.py`**: Streamlit UI that powers the chat, sidebar metrics, quick start, and dynamic feedback.
- **`agent.py`**: Implements the `EcommerceAgent`, which handles all intelligent interactions.
- **LangChain Messages**: Uses `HumanMessage` and `AIMessage` for structured multi-turn conversations.
- **Caching**: Streamlit's `@st.cache_resource` optimizes agent loading.

---

## Installation

1. Clone this repository:

   bash
   git clone https://github.com/your-username/alex-ecommerce-assistant.git
   cd alex-ecommerce-assistant

2. (Recommended) Create a virtual environment:

bash
python -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate

3. Install the dependencies

pip install -r requirements.txt

4. Run the app

streamlit run main.py

5. File Structure

├── main.py               # Streamlit UI and logic
├── agent.py              # LangChain-powered EcommerceAgent
├── requirements.txt      # Project dependencies
├── README.md             # Project documentation

