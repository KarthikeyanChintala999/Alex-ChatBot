import streamlit as st
from agent import EcommerceAgent
from langchain_core.messages import AIMessage, HumanMessage
import pandas as pd
import plotly.express as px

# Initialize agent with caching
@st.cache_resource(show_spinner=False)
def load_agent():
    return EcommerceAgent()

agent = load_agent()

# Streamlit UI
st.title("🛍️ Alex - Your E-Commerce Assistant")
st.caption("Hi there! I'm Alex, here to help with orders, products, and more 😊")

# Metrics dashboard
with st.sidebar:
    st.header("📊 Performance Metrics")
    metrics = agent.get_metrics()
    
    col1, col2 = st.columns(2)
    col1.metric("Total Queries", metrics['total_queries'])
    col2.metric("Success Rate", f"{metrics['success_rate']:.1f}%")
    
    col3, col4 = st.columns(2)
    col3.metric("Avg Response Time", f"{metrics['avg_response_time']:.2f}s")
    col4.metric("Multi-Tool Rate", f"{metrics['multi_tool_rate']:.1f}%")
    
    st.progress(metrics['success_rate']/100, text="Overall Success")
    
    # Tool usage visualization
    if metrics['total_queries'] > 0:
        tool_df = pd.DataFrame.from_dict(metrics['tool_usage'], orient='index', columns=['count'])
        tool_df = tool_df.sort_values('count', ascending=False)
        st.subheader("🔧 Tool Usage")
        st.bar_chart(tool_df)
    
    # Feedback buttons
    st.subheader("💬 Feedback")
    feedback_col1, feedback_col2 = st.columns(2)
    if feedback_col1.button("👍"):
        st.session_state.feedback = "positive"
    if feedback_col2.button("👎"):
        st.session_state.feedback = "negative"

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = [{
        "role": "assistant", 
        "content": "Hi there! 👋 I'm Alex, your e-commerce assistant. How can I help you today?"
    }]
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Enhanced sample queries
def handle_sample_query(query):
    st.session_state.messages.append({"role": "user", "content": query})
    with st.chat_message("user"):
        st.markdown(query)
    return query

# Sidebar with personality
with st.sidebar:
    st.header("💡 Quick Start")
    st.markdown("Try these examples:")
    
    if st.button("👋 Just say hello"):
        handle_sample_query("Hi Alex!")
    
    if st.button("📦 Order status"):
        handle_sample_query("Can you check order #123 for me?")
    
    if st.button("🏆 Loyalty points"):
        handle_sample_query("What are my points for customer C001?")
    
    if st.button("☔ Weather recommendation"):
        handle_sample_query("What should I buy for rainy weather in London?")
    
    st.markdown("---")
    if st.button("🧹 Reset chat", type="secondary"):
        st.session_state.messages = [{
            "role": "assistant", 
            "content": "Hi again! What would you like help with today?"
        }]
        st.session_state.chat_history = []
        st.rerun()

# User input
if user_input := st.chat_input("Type your message here..."):
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Get agent response with typing animation
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = agent.run_agent(
                user_input,
                chat_history=st.session_state.chat_history
            )
        
        # Display response progressively
        message_placeholder = st.empty()
        full_response = ""
        for chunk in response.split():
            full_response += chunk + " "
            message_placeholder.markdown(full_response + "▌")
        message_placeholder.markdown(full_response)
        
        st.session_state.messages.append({"role": "assistant", "content": response})
        
        # Update LangChain message history
        st.session_state.chat_history.extend([
            HumanMessage(content=user_input),
            AIMessage(content=response)
        ])

# Detailed metrics view
with st.expander("📈 Detailed Metrics"):
    metrics = agent.get_metrics()
    
    st.subheader("Performance Overview")
    st.json(metrics)
    
    if metrics['total_queries'] > 0:
        # Create interaction timeline
        interactions_df = pd.DataFrame(metrics['interactions'])
        if not interactions_df.empty:
            interactions_df['timestamp'] = pd.to_datetime(interactions_df['timestamp'])
            interactions_df = interactions_df.set_index('timestamp')
            
            st.subheader("Interaction Timeline")
            st.line_chart(interactions_df['response_time'])
            
            # Success/failure pie chart
            st.subheader("Success vs. Failure")
            fig = px.pie(
                names=['Success', 'Failure'],
                values=[metrics['successful_resolutions'], 
                       metrics['total_queries'] - metrics['successful_resolutions']]
            )
            st.plotly_chart(fig)
