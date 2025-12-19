"""
MCP Client
Uses official MCP SDK with proper StdioServerParameters pattern
"""

import asyncio
import sys
import logging
from contextlib import AsyncExitStack
from typing import Optional
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MCPClient:
    """MCP client to interact with MCP servers using official SDK pattern."""
    
    def __init__(self):
        """Initialize the MCP client."""
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()
    
    async def connect_to_server(self, server_script_path: str) -> None:
        """
        Connect to an MCP server.
        
        Args:
            server_script_path: Path to the server script (must be .py file)
            
        Raises:
            ValueError: If server script is not a .py file
            RuntimeError: If connection fails
        """
        try:
            # Validate server path
            if not server_script_path.endswith('.py'):
                raise ValueError("Server script must be a .py file")
            
            logger.info(f"Connecting to server: {server_script_path}")
            
            # Create server parameters
            server_params = StdioServerParameters(
                command="python",
                args=[server_script_path],
                env=None
            )
            
            # Create and enter stdio client
            stdio_transport = await self.exit_stack.enter_async_context(
                stdio_client(server_params)
            )
            
            # Create client session
            self.session = await self.exit_stack.enter_async_context(
                ClientSession(*stdio_transport)
            )
            
            # Initialize the session
            await self.session.initialize()
            logger.info("✓ Connected to server successfully!")
            
        except Exception as e:
            logger.error(f"✗ Failed to connect: {e}")
            raise
    
    async def list_tools(self) -> None:
        """List all available tools from the server."""
        if not self.session:
            logger.error("Not connected to server")
            return
        
        try:
            tools = await self.session.list_tools()
            logger.info("\n📋 Available Tools:")
            if tools.tools:
                for tool in tools.tools:
                    logger.info(f"  • {tool.name}")
                    if hasattr(tool, 'description') and tool.description:
                        logger.info(f"    └─ {tool.description}")
            else:
                logger.info("  (No tools available)")
        except Exception as e:
            logger.error(f"Error listing tools: {e}")
    
    async def list_resources(self) -> None:
        """List all available resources from the server."""
        if not self.session:
            logger.error("Not connected to server")
            return
        
        try:
            resources = await self.session.list_resources()
            logger.info("\n📁 Available Resources:")
            if resources.resources:
                for resource in resources.resources:
                    logger.info(f"  • {resource.uri}")
                    if hasattr(resource, 'name') and resource.name:
                        logger.info(f"    └─ {resource.name}")
            else:
                logger.info("  (No resources available)")
        except Exception as e:
            logger.error(f"Error listing resources: {e}")
    
    async def list_prompts(self) -> None:
        """List all available prompts from the server."""
        if not self.session:
            logger.error("Not connected to server")
            return
        
        try:
            prompts = await self.session.list_prompts()
            logger.info("\n📝 Available Prompts:")
            if prompts.prompts:
                for prompt in prompts.prompts:
                    logger.info(f"  • {prompt.name}")
                    if hasattr(prompt, 'description') and prompt.description:
                        logger.info(f"    └─ {prompt.description}")
            else:
                logger.info("  (No prompts available)")
        except Exception as e:
            logger.error(f"Error listing prompts: {e}")
    
    async def call_tool(self, tool_name: str, arguments: dict) -> Optional[object]:
        """
        Call a specific tool on the server.
        
        Args:
            tool_name: Name of the tool to call
            arguments: Dictionary of arguments for the tool
            
        Returns:
            The tool result or None if error
        """
        if not self.session:
            logger.error("Not connected to server")
            return None
        
        try:
            logger.info(f"\n🔧 Calling tool: {tool_name}")
            logger.info(f"   Arguments: {arguments}")
            
            result = await self.session.call_tool(tool_name, arguments)
            
            logger.info(f"✓ Tool result:")
            for content in result.content:
                if hasattr(content, 'text'):
                    logger.info(f"   {content.text}")
                else:
                    logger.info(f"   {content}")
            
            return result
            
        except Exception as e:
            logger.error(f"✗ Error calling tool: {e}")
            return None
    
    async def get_resource(self, uri: str) -> Optional[object]:
        """
        Get a specific resource from the server.
        
        Args:
            uri: URI of the resource to retrieve
            
        Returns:
            The resource content or None if error
        """
        if not self.session:
            logger.error("Not connected to server")
            return None
        
        try:
            logger.info(f"\n📂 Reading resource: {uri}")
            
            result = await self.session.read_resource(uri)
            
            logger.info(f"✓ Resource content:")
            for content in result.contents:
                if hasattr(content, 'text'):
                    logger.info(f"   {content.text}")
                else:
                    logger.info(f"   {content}")
            
            return result
            
        except Exception as e:
            logger.error(f"✗ Error reading resource: {e}")
            return None
    
    async def get_prompt(self, prompt_name: str, arguments: dict) -> Optional[object]:
        """
        Get a specific prompt from the server.

        Args:
            prompt_name: Name of the prompt to retrieve
            arguments: Dictionary of arguments for the prompt

        Returns:
            The prompt result or None if error
        """
        if not self.session:
            logger.error("Not connected to server")
            return None

        try:
            logger.info(f"\n📝 Getting prompt: {prompt_name}")
            logger.info(f"   Arguments: {arguments}")

            result = await self.session.get_prompt(prompt_name, arguments)

            logger.info(f"✓ Prompt result:")
            for message in result.messages:
                logger.info(f"   {message}")

            return result.messages

        except Exception as e:
            logger.error(f"✗ Error getting prompt: {e}")
            return None

    async def cleanup(self) -> None:
        """Clean up resources and close connections."""
        try:
            await self.exit_stack.aclose()
            logger.info("✓ Cleanup complete")
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")


async def main() -> None:
    """Main entry point."""
    # Check command line arguments
    if len(sys.argv) < 2:
        print("\n" + "="*60)
        print("MCP Client - Official SDK Implementation")
        print("="*60)
        print("\nUsage: python client.py <path_to_server_script>")
        print("\nExample:")
        print("  Terminal 1: python server.py")
        print("  Terminal 2: python client.py server.py")
        print("\n" + "="*60 + "\n")
        sys.exit(1)
    
    server_script_path = sys.argv[1]
    
    client = MCPClient()
    
    try:
        # Connect to server
        await client.connect_to_server(server_script_path)
        
        # List all capabilities
        await client.list_tools()
        await client.list_resources()
        await client.list_prompts()
        
        # Example: Call a tool (uncomment to test)
        # result = await client.call_tool("fetch_sales_data", {
        #     "region": "APAC",
        #     "year": 2024
        # })
        
        # Example: Read a resource (uncomment to test)
        # resource = await client.get_resource("resource://company/config")
        
        logger.info("\n✅ Client ready for use!")
        
    except Exception as e:
        logger.error(f"\n❌ Fatal error: {e}")
        sys.exit(1)
    finally:
        await client.cleanup()


if __name__ == "__main__":
    asyncio.run(main())