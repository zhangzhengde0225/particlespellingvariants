import asyncio

from mcp import ClientSession
from mcp.client.sse import sse_client
# from mcp.client.streamable_http import streamablehttp_client

async def main(url: str):
    # Connect to a streamable HTTP server
    async with sse_client(url) as (
        read_stream,
        write_stream
    ):
        # Create a session using the client streams
        async with ClientSession(read_stream, write_stream) as session:
            # Initialize the connection
            await session.initialize()
            # List available tools
            tools = await session.list_tools()
            print(f"Available tools: {[tool.name for tool in tools.tools]}")

            tool_result = await session.call_tool(
                "add",
                arguments={"a": 5, "b": 3},
            )
            print(f"Tool result: {tool_result.content[0].text}")
            
            # tool_result = await session.call_tool(
            #     name="particle_name_to_properties",
            #     arguments={"name": "pi+"},
            # )
            # print(f"Tool result: {tool_result.content[0].text}")
            
            # List available prompts
            prompts = await session.list_prompts()
            print(f"Available prompts: {[p.name for p in prompts.prompts]}")

            # Get a prompt (greet_user prompt from fastmcp_quickstart)
            if prompts.prompts:
                prompt = await session.get_prompt("greet_user", arguments={"name": "Alice", "style": "friendly"})
                print(f"Prompt result: {prompt.messages[0].content}")

            # List available resources
            resources = await session.list_resources()
            print(f"Available resources: {[r.uri for r in resources.resources]}")


if __name__ == "__main__":
    url = "http://localhost:42996/sse"
    url = "http://localhost:42601/apiv2/mcp/sse"
    url = "http://localhost:42601/apiv2/mcp/md-648de797-3c7/sse"
    url = "https://aiapi.ihep.ac.cn/apiv2/mcp/md-648de797-3c7/sse"
    # url = "http://localhost:42600/mcp"
    asyncio.run(main(url=url))