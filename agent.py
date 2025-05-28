from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_groq import ChatGroq
from tools import tools
from dotenv import load_dotenv
import os
import time
from datetime import datetime

load_dotenv()

class EcommerceAgent:
    def __init__(self):
        self.llm = ChatGroq(
            temperature=0.8,
            model_name="llama3-70b-8192",
            groq_api_key=os.getenv("GROQ_API_KEY")
        )
        
        # Initialize metrics
        self.metrics = {
            'total_queries': 0,
            'successful_resolutions': 0,
            'tool_usage': {tool.name: 0 for tool in tools},
            'fallback_responses': 0,
            'multi_tool_episodes': 0,
            'context_retention_score': 0,
            'avg_response_time': 0,
            'total_tokens': 0,
            'session_start': datetime.now().isoformat(),
            'interactions': []
        }
        
        system_prompt = """You're Alex, a friendly and knowledgeable e-commerce assistant. 
        
Your personality:
- Warm and conversational (use emojis occasionally 😊)
- Ask follow-up questions when needed
- Admit when you don't know something
- Guide users to relevant tools naturally

How to help:
1. Greetings: Respond warmly to casual chat
2. General questions: Answer conversationally if you know
3. Specific requests: Use tools when appropriate
4. Uncertainty: Say "I don't know" or ask clarifying questions

Tools available: {tool_names}"""
        
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad")
        ])
        
        self.agent = create_tool_calling_agent(self.llm, tools, self.prompt)
        
        self.agent_executor = AgentExecutor(
            agent=self.agent,
            tools=tools,
            verbose=True,
            handle_parsing_errors="Oops! I got a bit confused there. Could you rephrase that?",
            max_iterations=5,
            return_intermediate_steps=True
        )

    def run_agent(self, query, chat_history=None):
        start_time = time.time()
        self.metrics['total_queries'] += 1
        interaction = {
            'timestamp': datetime.now().isoformat(),
            'query': query,
            'success': False,
            'tools_used': [],
            'response_time': 0,
            'error': None
        }
        
        try:
            input_dict = {
                "input": query,
                "tool_names": ", ".join([tool.name for tool in tools]),
                "chat_history": chat_history or []
            }
            
            result = self.agent_executor.invoke(input_dict)
            
            # Track tool usage
            if 'intermediate_steps' in result:
                interaction['tools_used'] = [step[0].tool for step in result['intermediate_steps']]
                for tool_name in interaction['tools_used']:
                    self.metrics['tool_usage'][tool_name] += 1
                
                if len(interaction['tools_used']) > 1:
                    self.metrics['multi_tool_episodes'] += 1
            
            # Track context awareness
            if chat_history and any(h.content in query for h in chat_history[-3:]):
                self.metrics['context_retention_score'] += 1
            
            response = self._humanize_response(result["output"], query)
            
            if "error" not in response.lower():
                self.metrics['successful_resolutions'] += 1
                interaction['success'] = True
            
            # Track token usage (if available)
            if hasattr(self.llm, 'last_token_usage'):
                self.metrics['total_tokens'] += self.llm.last_token_usage
                interaction['tokens_used'] = self.llm.last_token_usage
            
            interaction['response_time'] = time.time() - start_time
            self.metrics['avg_response_time'] = (
                (self.metrics['avg_response_time'] * (self.metrics['total_queries'] - 1) + 
                 interaction['response_time']) / self.metrics['total_queries']
            )
            
            self.metrics['interactions'].append(interaction)
            return response
        
        except Exception as e:
            self.metrics['fallback_responses'] += 1
            interaction['error'] = str(e)
            self.metrics['interactions'].append(interaction)
            return "😅 Oops! I'm having trouble understanding. Could you try asking differently?"

    def _humanize_response(self, response, original_query):
        """Make responses more conversational and friendly"""
        if not response or response.strip() == "":
            return "🤔 I'm not sure how to respond to that. Could you give me more details?"
        
        if "error" in response.lower():
            if "loyalty" in original_query.lower():
                return "🔍 To check loyalty points, I'll need your customer ID. Could you share that? (Example: 'My ID is C001')"
            return "🛠️ I need a bit more info to help with that. " + response.replace("error:", "").capitalize()
        
        follow_ups = {
            "order status": "\n\nIs there anything else you'd like to know about this order?",
            "product": "\n\nWould you like me to suggest similar products?",
            "loyalty": "\n\nWould you like to know how to earn more points?"
        }
        
        for key, follow_up in follow_ups.items():
            if key in original_query.lower() and "?" not in response:
                response += follow_up
        
        conversational_replacements = {
            "The status is": "I see your order status is",
            "The product details are": "Here's what I found about this product:",
            "Your loyalty points are": "You've got"
        }
        
        for formal, friendly in conversational_replacements.items():
            if response.startswith(formal):
                response = response.replace(formal, friendly)
        
        return response

    def get_metrics(self):
        """Return calculated metrics"""
        metrics = self.metrics.copy()
        metrics['success_rate'] = (
            metrics['successful_resolutions'] / metrics['total_queries'] * 100 
            if metrics['total_queries'] > 0 else 0
        )
        metrics['multi_tool_rate'] = (
            metrics['multi_tool_episodes'] / metrics['total_queries'] * 100 
            if metrics['total_queries'] > 0 else 0
        )
        metrics['context_retention_rate'] = (
            metrics['context_retention_score'] / metrics['total_queries'] * 100 
            if metrics['total_queries'] > 0 else 0
        )
        return metrics
