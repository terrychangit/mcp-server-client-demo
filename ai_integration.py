"""
AI Model Integration with MCP Tools
====================================

This example shows how to use MCP tools with real AI models like OpenAI GPT-4.
The MCP server provides tools and context, while the AI model uses them to answer questions.
"""

import asyncio
import json
import os
import logging
from typing import List, Dict, Any
from client import MCPClient

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("python-dotenv not installed. Install with: pip install python-dotenv")
    print("Or set environment variables manually.")

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# AI Configuration - OpenAI Compatible API
try:
    from openai import OpenAI
except ImportError:
    print("Install OpenAI: pip install openai")
    exit(1)

# Configure your AI endpoint (update these values)
AI_ENDPOINT = os.getenv("AI_ENDPOINT", "https://ai-project-x.services.ai.azure.com/openai/v1/")
AI_MODEL_NAME = os.getenv("AI_MODEL_NAME", "DeepSeek-V3.1")
AI_DEPLOYMENT_NAME = os.getenv("AI_DEPLOYMENT_NAME", "DeepSeek-V3.1")
AI_API_KEY = os.getenv("AI_API_KEY")

if not AI_API_KEY:
    print("❌ Please set AI_API_KEY environment variable")
    print("Example: export AI_API_KEY='your-api-key-here'")
    exit(1)

# Initialize OpenAI-compatible client
client_ai = OpenAI(
    base_url=AI_ENDPOINT,
    api_key=AI_API_KEY
)


async def get_mcp_tools(mcp_client: MCPClient) -> List[Dict]:
    """Convert MCP tools to AI model tool format."""
    tools = await mcp_client.list_tools()
    # Note: In real implementation, you'd need to get tool schemas
    # For now, we'll define them manually based on our server
    return [
        {
            "type": "function",
            "function": {
                "name": "fetch_sales_data",
                "description": "Fetch sales data for a specific region and year",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "region": {"type": "string", "enum": ["APAC", "EMEA", "AMERICAS"]},
                        "year": {"type": "integer"}
                    },
                    "required": ["region", "year"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "calculate_metrics",
                "description": "Calculate profitability metrics from revenue and expenses",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "revenue": {"type": "number"},
                        "expenses": {"type": "number"}
                    },
                    "required": ["revenue", "expenses"]
                }
            }
        }
    ]


async def call_mcp_tool(mcp_client: MCPClient, tool_name: str, arguments: Dict) -> Dict:
    """Call an MCP tool and return the result."""
    result = await mcp_client.call_tool(tool_name, arguments)
    return json.loads(result.content[0].text)


async def ai_with_mcp_tools(query: str) -> str:
    """
    Use AI model with MCP tools to answer a query.
    This demonstrates the full MCP + AI integration.
    """
    print(f"\n🤖 Processing query: {query}")
    print("=" * 60)

    # Initialize MCP client
    mcp_client = MCPClient()

    try:
        # Connect to MCP server
        await mcp_client.connect_to_server("server.py")
        logger.info("✓ Connected to MCP server")

        # Get available tools
        tools = await get_mcp_tools(mcp_client)

        # Initial AI call with tools available
        messages = [
            {
                "role": "system",
                "content": "You are a helpful business analyst. Use the available tools to gather data and provide insights. When you need specific data, call the appropriate tools."
            },
            {
                "role": "user",
                "content": query
            }
        ]

        # Create chat completion with tools
        response = client_ai.chat.completions.create(
            model=AI_DEPLOYMENT_NAME,
            messages=messages,
            tools=tools,
            tool_choice="auto"
        )

        # Check if AI wants to use tools
        if response.choices[0].message.tool_calls:
            # Execute tool calls
            tool_results = []
            for tool_call in response.choices[0].message.tool_calls:
                tool_name = tool_call.function.name
                arguments = json.loads(tool_call.function.arguments)

                print(f"🔧 AI requested tool: {tool_name}")
                print(f"   Arguments: {arguments}")

                # Call the MCP tool
                result = await call_mcp_tool(mcp_client, tool_name, arguments)
                tool_results.append({
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": tool_name,
                    "content": json.dumps(result)
                })

                print(f"✓ Tool result: {result}")

            # Send tool results back to AI
            messages.append(response.choices[0].message)
            messages.extend(tool_results)

            # Get final response
            final_response = client_ai.chat.completions.create(
                model=AI_DEPLOYMENT_NAME,
                messages=messages
            )

            return final_response.choices[0].message.content

        else:
            return response.choices[0].message.content

    except Exception as e:
        logger.error(f"❌ Error: {e}")
        return f"Error: {e}"
    finally:
        await mcp_client.cleanup()


async def example_sales_analysis_ai():
    """Example: AI analyzing sales data using MCP tools."""
    print("\n" + "="*60)
    print("AI-POWERED SALES ANALYSIS WITH MCP TOOLS")
    print("="*60)

    query = "What is the sales performance for APAC in 2024? Calculate the profit margin and provide insights."

    result = await ai_with_mcp_tools(query)

    print(f"\n📊 AI Analysis Result:")
    print(result)


async def example_forecasting_ai():
    """Example: AI generating forecasts using MCP tools."""
    print("\n" + "="*60)
    print("AI-POWERED FORECASTING WITH MCP TOOLS")
    print("="*60)

    query = "Generate a 6-month sales forecast for APAC region. What growth rate should we expect?"

    result = await ai_with_mcp_tools(query)

    print(f"\n📈 AI Forecast Result:")
    print(result)


async def test_ai_connection():
    """Test basic AI connection without MCP."""
    print("\n🧪 Testing AI Connection...")
    try:
        response = client_ai.chat.completions.create(
            model=AI_DEPLOYMENT_NAME,
            messages=[
                {
                    "role": "user",
                    "content": "Hello! Please respond with a simple greeting.",
                }
            ],
        )
        print(f"✅ AI Connection Successful!")
        print(f"   Response: {response.choices[0].message.content}")
        return True
    except Exception as e:
        print(f"❌ AI Connection Failed: {e}")
        return False


async def main():
    """Run AI integration examples."""
    print("🤖 AI + MCP Integration Examples")
    print("Configuration loaded from .env file or environment variables:")
    print(f"  Endpoint: {AI_ENDPOINT}")
    print(f"  Model: {AI_MODEL_NAME}")
    print(f"  Deployment: {AI_DEPLOYMENT_NAME}")
    print(f"  API Key: {'Set' if AI_API_KEY else 'Not Set'}")
    print("\nTo configure:")
    print("1. Copy .env to .env.local and edit with your values")
    print("2. Or set environment variables manually")
    print("3. Or run: chmod +x setup_ai.sh && ./setup_ai.sh")

    # Test AI connection first
    if not await test_ai_connection():
        print("\n❌ Please check your AI configuration and try again.")
        return

    try:
        await example_sales_analysis_ai()
        await example_forecasting_ai()

        print("\n" + "="*60)
        print("✅ AI + MCP Integration Complete!")
        print("="*60)

    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    asyncio.run(main())