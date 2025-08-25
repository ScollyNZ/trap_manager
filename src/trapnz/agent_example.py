"""
Example of using Trap.NZ Agent Tools with OpenAI Function Calling
"""
import asyncio
import json
from openai import OpenAI
from .database import TrapNZDatabase
from .agent_tools import create_agent_tools
from .logging_config import setup_default_logging, get_logger

# Set up logging
setup_default_logging()
logger = get_logger(__name__)

class TrapNZOpenAIAgent:
    """Example OpenAI agent that uses Trap.NZ tools"""
    
    def __init__(self, openai_api_key: str, db: TrapNZDatabase):
        self.client = OpenAI(api_key=openai_api_key)
        self.agent_tools = create_agent_tools(db)
        self.tool_functions = self.agent_tools.get_tool_functions()
        self.tool_schemas = self.agent_tools.get_tool_schemas()
    
    def chat_with_tools(self, user_message: str) -> str:
        """Chat with the agent using function calling"""
        try:
            # First, get the response from OpenAI with potential function calls
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": """You are a helpful Trap.NZ data analyst assistant. You have access to trap line data, 
                        trap information, and trap records. You can help users understand their trap network, analyze 
                        performance, and find specific information. Always be helpful and provide clear explanations."""
                    },
                    {
                        "role": "user",
                        "content": user_message
                    }
                ],
                tools=self.tool_schemas,
                tool_choice="auto"
            )
            
            response_message = response.choices[0].message
            
            # Check if the model wants to call a function
            if response_message.tool_calls:
                # Process each tool call
                for tool_call in response_message.tool_calls:
                    function_name = tool_call.function.name
                    function_args = json.loads(tool_call.function.arguments)
                    
                    logger.info(f"Calling function: {function_name} with args: {function_args}")
                    
                    # Execute the function
                    if function_name in self.tool_functions:
                        function_result = self.tool_functions[function_name](**function_args)
                        
                        # Add the function result to the conversation
                        response_message.content += f"\n\nFunction {function_name} result: {json.dumps(function_result, indent=2)}"
                    else:
                        logger.warning(f"Unknown function: {function_name}")
                
                # Get a final response from the model
                final_response = self.client.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {
                            "role": "system",
                            "content": """You are a helpful Trap.NZ data analyst assistant. Analyze the function results 
                            and provide a clear, helpful response to the user's question."""
                        },
                        {
                            "role": "user",
                            "content": user_message
                        },
                        {
                            "role": "assistant",
                            "content": response_message.content
                        }
                    ]
                )
                
                return final_response.choices[0].message.content
            
            return response_message.content
            
        except Exception as e:
            logger.error(f"Error in chat_with_tools: {e}")
            return f"Sorry, I encountered an error: {str(e)}"

async def example_usage():
    """Example of using the Trap.NZ OpenAI agent"""
    
    # Initialize database (this would use your actual database)
    db = TrapNZDatabase(db_path="example_trapnz.db")
    
    # Initialize agent (you'll need to provide your OpenAI API key)
    # agent = TrapNZOpenAIAgent("your-openai-api-key-here", db)
    
    # Example queries you could ask the agent:
    example_queries = [
        "How many trap lines do I have?",
        "Show me all traps with red health status",
        "What's the performance summary for trap test-trap-1?",
        "How many DOC200 traps do I have?",
        "Give me a summary of line test-line-1",
        "What are the latest records for all my traps?",
        "Find all traps with low battery voltage",
        "Show me traps that haven't been checked recently"
    ]
    
    print("🧪 Example Trap.NZ Agent Queries:")
    for i, query in enumerate(example_queries, 1):
        print(f"{i}. {query}")
    
    print("\n💡 To use this agent:")
    print("1. Set your OpenAI API key")
    print("2. Initialize the agent with your database")
    print("3. Ask questions about your trap network!")
    
    # Example of how the agent would respond:
    print("\n📊 Example Agent Response Structure:")
    print("""
    The agent can:
    - Retrieve all trap lines and provide summaries
    - Search traps by health status, type, or other criteria
    - Get detailed performance metrics for specific traps
    - Analyze trap records and provide insights
    - Generate line summaries with trap counts and health statistics
    """)

def standalone_tool_example():
    """Example of using the tools directly without OpenAI"""
    
    print("🔧 Standalone Tool Usage Example:")
    
    # Initialize database
    db = TrapNZDatabase(db_path="example_trapnz.db")
    agent_tools = create_agent_tools(db)
    
    # Example: Get all lines
    print("\n📋 Getting all lines:")
    result = agent_tools.get_all_lines()
    print(json.dumps(result, indent=2))
    
    # Example: Search traps by status
    print("\n🔍 Searching traps by status:")
    result = agent_tools.search_traps_by_status("green")
    print(json.dumps(result, indent=2))
    
    # Example: Get trap performance summary
    print("\n📊 Getting trap performance summary:")
    result = agent_tools.get_trap_performance_summary("test-trap-1")
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    # Run the standalone example
    standalone_tool_example()
    
    # Run the async example
    asyncio.run(example_usage())
