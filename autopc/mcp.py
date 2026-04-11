from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client
from mcp.client.stdio import stdio_client
import asyncio
import traceback
from functools import partial


class MCPManager:
    def __init__(self, autopc):
        self.autopc = autopc
        self.server_config = autopc.config["mcpServers"]
        self.sessions = {}

    async def start_all_mcp(self):
        print("[MCP] 连接MCP服务中")
        for name, cfg in self.server_config.items():
            try:
                if cfg.get("type") == "streamable-http":
                    async with streamable_http_client(cfg["url"]) as (
                        read_stream,
                        write_stream,
                        _,
                    ):
                        async with ClientSession(read_stream, write_stream) as session:
                            await session.initialize()
                            self.sessions[name] = session
                            print(f"[MCP] {name} 连接成功")
                            tools_result = await session.list_tools()

                            for tool in tools_result.tools:
                                tool_key = f"mcp_{name}_{tool.name}"
                                tool_arguments = tool.inputSchema
                                toolcall = {
                                    "type": "function",
                                    "function": {
                                        "name": f"mcp_{name}_{tool.name}",
                                        "description": tool.description or "",
                                        "parameters": tool_arguments,
                                    },
                                }
                                self.autopc.tools.append(toolcall)

                                async def _wrapper(control_arguments):
                                    return await self.use_mcp_tool(
                                        name, tool.name, control_arguments
                                    )

                                self.autopc.tool_map[tool_key] = _wrapper
                            print(f"[MCP] {name} 工具注册成功")
                else:
                    async with stdio_client(cfg["command"], cfg.get("args", [])) as (
                        r,
                        w,
                    ):
                        async with ClientSession(r, w) as session:
                            await session.initialize()
                            self.sessions[name] = session
                            print(f"[MCP] {name} 连接成功")
                            tools_result = await session.list_tools()

                            for tool in tools_result.tools:
                                tool_key = f"mcp_{name}_{tool.name}"
                                tool_arguments = tool.inputSchema
                                toolcall = {
                                    "type": "function",
                                    "function": {
                                        "name": f"mcp_{name}_{tool.name}",
                                        "description": tool.description or "",
                                    },
                                    "parameters": tool_arguments,
                                }
                                self.autopc.tools.append(toolcall)

                                async def _wrapper(control_arguments):
                                    return await self.use_mcp_tool(
                                        name, tool.name, control_arguments
                                    )

                                self.autopc.tool_map[tool_key] = _wrapper
                            print(f"[MCP] {name} 工具注册成功")
            except Exception as e:
                print(f"\n[MCP] {name} 连接失败：", e)
                traceback.print_exc()
        print("[MCP] 所有 MCP 服务连接完成")

    async def use_mcp_tool(self, session_name, tool_name, control_arguments):
        try:
            cfg = self.server_config.get(session_name)
            if cfg.get("type") == "streamable-http":
                async with streamable_http_client(cfg["url"]) as (
                    read_stream,
                    write_stream,
                    _,
                ):
                    async with ClientSession(read_stream, write_stream) as session:
                        await session.initialize()
                        self.sessions[session_name] = session
                        print(f"[MCP] {session_name} 连接成功")
                        result = await session.call_tool(
                            name=tool_name, arguments=control_arguments
                        )
                        return {"success": True, "result": result.content[0].text}
        except Exception as e:
            print(f"\n[MCP] {session_name} 操作失败：", e)
            return {"success": False, "error": str(e)}
