import os
import json
from typing import Any
from openai import OpenAI
from termcolor import colored
import inspect
import asyncio
from types import SimpleNamespace
import sys

from .prompts import TOOLS_PROMPT, RECAP_PROMPT
from .tools import TOOLS
from .config import ConfigManager
from .skills import SkillsManager
from .utils import (
    terminal_input,
    image_to_base64,
    screenshot,
    image_add_lim,
    download_file,
    mouse_action,
    click_action,
    double_click_action,
    write_action,
    press_action,
    terminal_action,
    return_terminal_action,
    get_request,
    post_request,
    read_autopc_config,
    serialize_messages,
    read_file,
    read_dir_list,
    insert_file,
    delete_file,
    new_task,
    set_task_state,
    get_tasks_list,
    delete_task,
    remove_folder,
    remove_file,
    new_file,
    copy_file,
    create_dir,
    move_dir,
    copy_folder,
)
from .plugins import PluginsManager
from .mcp import MCPManager


class AutoPC:
    # 类常量定义
    BASE_DIR = os.getcwd()

    # 设置单例
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        # Logo输出
        logoASCII = r""" 
_______       ________      ________      ___  ___      _________    ________      ________    ________     
|\  ___ \     |\_____  \    |\   __  \    |\  \|\  \    |\___   ___\ |\   __  \    |\   __  \  |\   ____\    
\ \   __/|     \|___/  /|   \ \  \|\  \   \ \  \\\  \   \|___ \  \_| \ \  \|\  \   \ \  \|\  \ \ \  \___|    
 \ \  \_|/__       /  / /    \ \   __  \   \ \  \\\  \       \ \  \   \ \  \\\  \   \ \   ____\ \ \  \       
  \ \  \_|\ \     /  /_/__    \ \  \ \  \   \ \  \\\  \       \ \  \   \ \  \\\  \   \ \  \___|  \ \  \____  
   \ \_______\   |\________\   \ \__\ \__\   \ \_______\       \ \__\   \ \_______\   \ \__\      \ \_______\
    \|_______|    \|_______|    \|__|\|__|    \|_______|        \|__|    \|_______|    \|__|       \|_______|

    """
        print(colored(logoASCII, "blue"))

        # 初始化实例变量
        self.skills = {}
        self.config = {}
        self.client = OpenAI(api_key="")
        self.tools: list = TOOLS
        self.on_ai_send_message = []
        self.on_tool_use = []
        self.allow_tools = []
        self.commands = {}

        # 工具映射
        self.tool_map = {
            "mouse": mouse_action,
            "click": lambda _: click_action(),
            "doubleClick": lambda _: double_click_action(),
            "write": write_action,
            "press": press_action,
            "terminal": terminal_action,
            "returnTerminal": return_terminal_action,
            "readSkillMd": self._wrap_read_skill_md,
            "download": download_file,
            "getRequest": get_request,
            "postRequest": post_request,
            "readAutoPCConfig": lambda _: read_autopc_config(),
            "childAgentChat": self.child_agent_chat,
            "deleteFileLine": delete_file,
            "insertFile": insert_file,
            "readDirList": read_dir_list,
            "readFile": read_file,
            "newTask": new_task,
            "setTaskState": set_task_state,
            "getTasksList": lambda _: get_tasks_list(),
            "deleteTask": delete_task,
            "removeFile": remove_file,
            "removeFolder": remove_folder,
            "newFile": new_file,
            "copyFile": copy_file,
            "createFolder": create_dir,
            "moveDir": move_dir,
            "copyFolder": copy_folder,
        }

        # 初始化
        self.read_config()

    def _init_prompts(self):
        """根据配置初始化提示词"""
        self.recap_prompt = RECAP_PROMPT
        self.all_tools_prompt = (
            TOOLS_PROMPT
            + f"""
{
                [
                    {
                        "arguments": {
                            "is_multimodal": self.config.setdefault(
                                "is_multimodal", False
                            ),
                            "prompt": self.config.setdefault("lines_prompt", ""),
                            "skills": self.skills,
                        },
                    }
                ]
            }
"""
        )
        self.begin_prompt = {"role": "system", "content": self.all_tools_prompt}
        self.messages = [self.begin_prompt]
        self.full_messages = self.messages.copy()

    def on_ai_send_message_handler(self):
        for handler in self.on_ai_send_message:
            handler()

    def _count_token(self, text: str) -> int:
        if not text:
            return 0
        return int(len(text) * 1.3) + 1

    def get_messages_token(self):
        total = 0
        for msg in self.messages:
            total += 3
            role: Any = msg.get("role") if isinstance(msg, dict) else msg.role
            content: Any = msg.get("content") if isinstance(msg, dict) else msg.content
            reasoning_content: Any = (
                msg.get("reasoning_content")
                if isinstance(msg, dict)
                else getattr(msg, "reasoning_content", "")
            )

            total += self._count_token(role)
            total += self._count_token(content)
            total += self._count_token(reasoning_content)

        total += 3
        print(f"[Token] 当前上下文token:{total}")
        return {"token": total}

    def recap_messages(self):
        try:
            text_parts = []
            for msg in self.messages[1:]:
                role = msg.get("role") if isinstance(msg, dict) else msg.role
                content: Any = (
                    msg.get("content") if isinstance(msg, dict) else msg.content
                )
                if role == "user":
                    text_parts.append(f"{role}:{content[0]}")
                else:
                    text_parts.append(f"{role}:{content}")
            raw_text = "\n".join(text_parts)

            recap_messages = [
                {"role": "system", "content": self.recap_prompt},
                {"role": "user", "content": [{"type": "text", "text": raw_text}]},
            ]

            completion = self.client.chat.completions.create(
                model=self.config.setdefault("model", ""),
                temperature=0.6,
                messages=recap_messages,
                tools=self.tools,
                extra_body={"thinking": {"type": "disabled"}},
            )
            summary_content = completion.choices[0].message.content
            self.messages = [
                self.messages[0],
                {"role": "user", "content": f"【历史对话】\n{summary_content}"},
            ]
            print(f"[Token] 总结后内容: {summary_content}")
            print("[Token] 总结完成")
            return True
        except Exception as e:
            print(f"[Token] {e}")
            print("[Token] 总结失败")
            return False

    def try_recap_messages(self):
        token = self.get_messages_token()
        if token["token"] >= (
            int(self.config.setdefault("context_window", "128000")) * 0.75
        ):
            self.push_messages(
                {
                    "role": "assistant",
                    "name": "system_notice",
                    "content": f"当前Token({token['token']})过多,尝试压缩中",
                }
            )
            self.on_ai_send_message_handler()
            print("[压缩Token] 达到Token上限,开始总结")
            recap_success = self.recap_messages()
            current_token = self.get_messages_token()
            self.push_messages(
                {
                    "role": "assistant",
                    "name": "system_notice",
                    "content": f"Token压缩{recap_success if '成功' else '失败'},总结前Token:{token['token']},当前Token:{current_token['token']}",
                }
            )
            self.on_ai_send_message_handler()
            print(
                f"[压缩Token] 总结{recap_success if '成功' else '失败'},总结前Token:{token['token']},当前Token:{current_token['token']}"
            )
        else:
            pass

    def _wrap_read_skill_md(self, control_arguments):
        return self.skills_manager.read_skill_md(control_arguments["name"])

    def child_agent_chat(self, control_arguments: dict) -> dict:
        self.send_tools_ai_message(
            prompt=control_arguments["content"],
            image_source=None,
            is_child=True,
            child_id=int(control_arguments["id"]),
        )
        return {
            "success": True,
            "messages": serialize_messages(
                self.child_messages[control_arguments["id"]][1:-1]
            ),
        }

    def send_tools_ai_message(
        self, prompt, image_source, name=None, is_child=False, child_id=0
    ):
        finish_reason = None
        if len(self.child_messages) < (child_id + 1):
            for _ in range(child_id + 1):
                self.child_messages.append([self.begin_prompt])
        if self.config.setdefault("is_multimodal", "") and image_source:
            self.push_messages(
                {
                    "role": "user",
                    "name": "user" if name is None else name,
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_to_base64(image_source)}"
                            },
                        },
                    ],
                },
                is_child,
                child_id,
            )
        else:
            if not is_child:
                print("[警告] is_multimodal为false,因此不会发送屏幕截图")
            self.push_messages(
                {
                    "role": "user",
                    "name": "user" if name is None else name,
                    "content": [{"type": "text", "text": prompt}],
                },
                is_child,
                child_id,
            )
        try:
            while finish_reason is None or finish_reason == "tool_calls":
                self.on_ai_send_message_handler()
                if is_child:
                    completion = self.client.chat.completions.create(
                        model=self.config.setdefault("model", ""),
                        temperature=float(self.config.setdefault("temperature", 0.6)),
                        messages=self.child_messages[child_id],
                        tools=self.tools,
                        extra_body={
                            "thinking": {
                                "type": "enabled"
                                if self.config.setdefault("thinking", False)
                                else "disabled"
                            }
                        },
                    )
                else:
                    completion = self.client.chat.completions.create(
                        model=self.config.setdefault("model", ""),
                        temperature=float(self.config.setdefault("temperature", 0.6)),
                        messages=self.messages,
                        tools=self.tools,
                        extra_body={
                            "thinking": {
                                "type": "enabled"
                                if self.config.setdefault("thinking", False)
                                else "disabled"
                            }
                        },
                    )
                if completion.choices:
                    choice = completion.choices[0]
                    finish_reason = choice.finish_reason
                    message: Any = choice.message
                else:
                    choice = None
                    finish_reason = "stop"
                    message: Any = SimpleNamespace(
                        **{
                            "role": "assistant",
                            "content": "[异常] 模型不存在有效输出",
                            "name": "system_notice",
                            "reasoning_content": str(completion),
                        }
                    )

                if message:
                    self.push_messages(message, is_child, child_id)

                if message.content and finish_reason != "tool_calls" and not is_child:
                    print("[AI回复]", message.content)
                elif message.content and finish_reason != "tool_calls" and is_child:
                    print("[子AI回复]", message.content)

                if finish_reason == "tool_calls":
                    for tool_call in message.tool_calls:
                        tool_call_name = tool_call.function.name
                        tool_call_args = json.loads(tool_call.function.arguments)
                        tool_func = self.tool_map.get(tool_call_name)
                        if tool_func:
                            tool_result = None
                            if tool_call_name in self.allow_tools:
                                for handler in self.on_tool_use:
                                    tool_exec_decide = handler(
                                        {
                                            "tool_call_name": tool_call_name,
                                            "tool_call_args": tool_call_args,
                                        }
                                    )
                                    if not tool_exec_decide.get("exec"):
                                        tool_result = {
                                            "success": False,
                                            "error": tool_exec_decide.get(
                                                "msg", "此操作被阻止"
                                            ),
                                        }
                                if inspect.iscoroutinefunction(tool_func):
                                    tool_result = asyncio.run(tool_func(tool_call_args))
                                else:
                                    tool_result = tool_func(tool_call_args)
                            else:
                                tool_result = {
                                    "success": False,
                                    "error": "此操作不在允许清单内",
                                }
                            self.push_messages(
                                {
                                    "role": "tool",
                                    "tool_call_id": tool_call.id,
                                    "name": tool_call_name,
                                    "content": json.dumps(
                                        tool_result, ensure_ascii=False
                                    ),
                                },
                                is_child,
                                child_id,
                            )
                self.on_ai_send_message_handler()
            if (
                finish_reason == "stop"
                and choice is not None
                and choice.message.content
            ):
                self.on_ai_send_message_handler()
        except Exception as e:
            print("[异常] ", e)
            self.push_messages(
                {"name": "system_notice", "role": "assistant", "content": f"[异常] {e}"}
            )
            self.on_ai_send_message_handler()

    def send_ai_message(self, user_content, type="user", name=None):
        screenshot_path = None
        if self.config.setdefault("is_multimodal", ""):
            screenshot_path = screenshot()
        if screenshot_path:
            image_add_lim(screenshot_path)
        if user_content.split()[0] in self.commands.keys():
            self.do_command(user_content)
        else:
            self.send_tools_ai_message(user_content, screenshot_path, name)
        self.try_recap_messages()
        self.on_ai_send_message_handler()

    def do_command(self, command):
        self.push_messages(
            {
                "role": "user",
                "name": "user",
                "content": [{"type": "text", "text": command}],
            }
        )
        self.on_ai_send_message_handler()
        command_list = command.split()
        if command_list[0] in self.commands.keys():
            control = self.commands[command_list[0]]
            parameters_len = len(inspect.signature(control).parameters)
            if parameters_len > 0:
                if len(command_list) == parameters_len:
                    msg = control(*command_list)
                    self.push_messages({"role": "assistant", "content": msg})
                else:
                    self.push_messages(
                        {
                            "role": "assistant",
                            "content": f"[异常] 指令 {command_list[0]} 应获得 {parameters_len - 1} 个参数",
                        }
                    )
            else:
                msg = control()
            self.on_ai_send_message_handler()

    def main_loop(self):
        while True:
            print("")
            user_input = terminal_input()
            if user_input == "exit":
                return
            self.send_ai_message(user_input)

    def read_config(self):
        # 初始化配置管理器
        self.config_manager = ConfigManager()
        self.config = self.config_manager.read_config(
            self.BASE_DIR, os.path.expanduser("~/.ezautopc")
        )

        if self.config == {"error": True}:
            print("[读取配置] 读取失败")
            print("[读取配置] 正在退出程序...")
            sys.exit()

        # 初始化其他管理器
        self.skills_manager = SkillsManager(self.BASE_DIR)
        self.mcp_manager = MCPManager(self)

        # 初始化技能和MCP
        self.tools: list = TOOLS
        self.skills = self.skills_manager.get_skills_info()
        self.client.api_key = self.config.setdefault("api_key", "")
        self.client.base_url = self.config.setdefault("base_url", "")
        asyncio.run(self.mcp_manager.start_all_mcp())

        # 构建初始消息

        self.begin_prompt = {"role": "system", "content": TOOLS_PROMPT}
        self.messages: Any = [self.begin_prompt]
        self.child_messages: Any = []
        self._init_prompts()

        # 加载插件
        self.plugins_manager = PluginsManager(self)
        self.plugins_manager.load_plugins()

    def allow_tool(self, tool_name):
        if tool_name not in self.allow_tools:
            self.allow_tools.append(tool_name)
            print(f"[权限管理] 在本对话中已允许使用 {tool_name}")

    def not_allowed_tool(self, tool_name):
        if tool_name in self.allow_tools:
            self.allow_tools.remove(tool_name)
            print(f"[权限管理] 在本对话中已拒绝使用 {tool_name}")

    def push_messages(self, message, is_child=False, child_id=0):
        if is_child:
            self.child_messages[child_id].append(message)
        else:
            self.messages.append(message)
            self.full_messages.append(message)

    def exit_autopc(self):
        os._exit(0)
