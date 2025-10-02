

# MCP支持

该worker支持大模型上下文协议（MCP, Model Context Protocol），可以作为大模型的插件使用，提供粒子拼写变体查询等功能。


粒子拼写变体及物理性质工具

粒子物理中同一个粒子或共振态有不同的拼写方法，本工具适配了692种粒子的编程名、LaTex名、EvtGen名、HTML名、Unicode名以及其他别名，基本涵盖粒子名称。使用本工具，可根据粒子名称准确获取某个粒子的基本标识、多种拼写变体、物理属性、量子数、类型标识、衰变分支比等信息，为物理分析智能体提供支持。


### 部署方法：

```bash
bash run_psv_worker.sh
```
注意部署时生成的model id，例如：`md-648de797-3c7/sse`，后续配置MCP时需要用到。

### 通过MCP配置调用

```bash
{"mcpServers":{"particle_name_to_properties":{"url":"https://aiapi.ihep.ac.cn/apiv2/mcp/md-648de797-3c7/sse","transport":"sse",}}}
```

### 通过Python SDK调用：

```python
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
                name="particle_name_to_properties",
                arguments={"name": "pi+"},
            )
            print(f"Tool result: {tool_result.content[0].text}")
            
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
    url = "https://aiapi.ihep.ac.cn/apiv2/mcp/md-648de797-3c7/sse"
    asyncio.run(main(url=url))
```


