import os
import json
from time import sleep
from typing import List, Dict, Any
from openai import OpenAI
from openai.types.chat import ChatCompletionMessageParam, ChatCompletionMessage
from termcolor import colored
import inspect

from .prompts import TOOLS_PROMPT, NO_TOOLS_PROMPT, RECAP_PROMPT
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
)
from .plugins import PluginsManager


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
        self.allow_tools = []
        self.commands = {}

        # 初始化
        self.read_config()

        # 工具映射
        self.tool_map = {
            "mouse": lambda args: (mouse_action(args), None)[1],
            "click": lambda args: click_action(),
            "doubleClick": lambda args: double_click_action(),
            "write": lambda args: write_action(args),
            "press": lambda args: press_action(args),
            "terminal": lambda args: terminal_action(args),
            "returnTerminal": lambda args: return_terminal_action(args),
            "readSkillMd": self._wrap_read_skill_md,
            "download": lambda args: download_file(args),
        }

    def _init_prompts(self):
        """根据配置初始化提示词"""
        self.no_tools_prompt = NO_TOOLS_PROMPT
        self.recap_prompt = RECAP_PROMPT

        if self.config.get("tool_calls"):
            print("[警告] tool_calls模式目前不稳定")
            self.all_tools_prompt = (
                TOOLS_PROMPT
                + f"""
{
                    [
                        {
                            "arguments": {
                                "is_multimodal": self.config["is_multimodal"],
                                "prompt": self.config["lines_prompt"],
                                "skills": self.skills,
                            },
                        }
                    ]
                }
"""
            )
            self.messages = [{"role": "system", "content": self.all_tools_prompt}]
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
        text_parts = []
        for msg in self.messages[1:]:
            role = msg.get("role") if isinstance(msg, dict) else msg.role
            content: Any = msg.get("content") if isinstance(msg, dict) else msg.content
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
            model=self.config["model"],
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

    def try_recap_messages(self):
        token = self.get_messages_token()
        if token["token"] >= (int(self.config["context_window"]) * 0.9):
            self.push_messages(
                {
                    "role": "assistant",
                    "name": "system_notice",
                    "content": f"当前Token({token['token']})过多,尝试压缩中",
                }
            )
            self.on_ai_send_message_handler()
            print("[压缩Token] 达到Token上限,开始总结")
            self.recap_messages()
            current_token = self.get_messages_token()
            self.push_messages(
                {
                    "role": "assistant",
                    "name": "system_notice",
                    "content": f"Token压缩完成,总结前Token:{token['token']},当前Token:{current_token['token']}",
                }
            )
            self.on_ai_send_message_handler()
            print(
                f"[压缩Token] 总结完成,总结前Token:{token['token']},当前Token:{current_token['token']}"
            )
        else:
            pass

    def _wrap_read_skill_md(self, control_arguments):
        return self.skills_manager.read_skill_md(control_arguments["name"])

    def send_image_to_ai(self, prompt, image_source, is_local=True):
        if self.config["is_multimodal"]:
            new_messages = {
                "role": "user",
                "name": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{image_to_base64(image_source)}"
                            if is_local
                            else image_source
                        },
                    },
                ],
            }
            self.push_messages(new_messages)
        else:
            print("[警告] is_multimodal为false,因此不会发送屏幕截图")
            new_messages = {
                "role": "user",
                "name": "user",
                "content": [{"type": "text", "text": prompt}],
            }
            self.push_messages(new_messages)

        try:
            self.client.api_key = self.config["api_key"]
            self.client.base_url = self.config["base_url"]
            response = self.client.chat.completions.create(
                model=self.config["model"],
                messages=self.messages,
                temperature=float(self.config["temperature"]),
                extra_body={
                    "thinking": {
                        "type": "enabled" if self.config["thinking"] else "disabled"
                    }
                },
            )
            new_msg = {
                "name": "assistant",
                "role": "assistant",
                "content": response.choices[0].message.content,
            }
            self.push_messages(new_msg)
            return response.choices[0].message.content

        except Exception as e:
            error_str = json.dumps(
                [{"type": "error", "arguments": {"content": f"请求失败:{str(e)}"}}]
            )
            self.push_messages(
                {"role": "assistant", "name": "system_notice", "content": error_str}
            )
            return error_str

    def handle_ai_message(self, content, user_message):
        try:
            controls_json = json.loads(content)
            for control in controls_json:
                control_type = control["type"]
                control_args = control["arguments"]

                if control_type == "mouse":
                    mouse_action(control_args)
                elif control_type == "click":
                    click_action()
                elif control_type == "doubleClick":
                    double_click_action()
                elif control_type == "write":
                    write_action(control_args)
                elif control_type == "press":
                    press_action(control_args)
                elif control_type == "message":
                    print("[AI消息]", control_args["content"])
                elif control_type == "continue":
                    json_content = json.loads(user_message)
                    sleep(int(control_args["wait"]))
                    self.send_ai_message(
                        f"继续操作({json_content[0]['arguments']['content'].encode('raw_unicode_escape').decode('utf-8')})",
                        "application",
                    )
                elif control_type == "terminal":
                    terminal_action(control_args)
                elif control_type == "returnTerminal":
                    result = return_terminal_action(control_args)
                    self.send_ai_message(
                        f"终端操作已完成,输出:{result['content']}", "application"
                    )
                elif control_type == "readSkillMd":
                    result = self.skills_manager.read_skill_md(control_args["name"])
                    self.send_ai_message(
                        f"读取SKILL.md操作已完成,文件内容:{result['content']}",
                        "application",
                    )
                self.on_ai_send_message_handler()
        except Exception as e:
            print("[异常]", e)

    def send_tools_ai_message(self, prompt, image_source):
        finish_reason = None
        if self.config["is_multimodal"]:
            self.push_messages(
                {
                    "role": "user",
                    "name": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_to_base64(image_source)}"
                            },
                        },
                    ],
                }
            )
        else:
            print("[警告] is_multimodal为false,因此不会发送屏幕截图")
            self.push_messages(
                {
                    "role": "user",
                    "name": "user",
                    "content": [{"type": "text", "text": prompt}],
                }
            )
        try:
            while finish_reason is None or finish_reason == "tool_calls":
                self.on_ai_send_message_handler()
                completion = self.client.chat.completions.create(
                    model=self.config["model"],
                    temperature=float(self.config["temperature"]),
                    messages=self.messages,
                    tools=self.tools,
                    extra_body={
                        "thinking": {
                            "type": "enabled" if self.config["thinking"] else "disabled"
                        }
                    },
                )
                print("enabled" if self.config["thinking"] else "disabled")
                choice = completion.choices[0]
                finish_reason = choice.finish_reason
                message: Any = choice.message

                if message:
                    self.push_messages(message)

                if message.content and finish_reason != "tool_calls":
                    print("[AI回复]", message.content)

                if finish_reason == "tool_calls":
                    for tool_call in message.tool_calls:
                        tool_call_name = tool_call.function.name
                        tool_call_args = json.loads(tool_call.function.arguments)
                        tool_func = self.tool_map.get(tool_call_name)
                        if tool_func:
                            tool_result = None
                            if tool_call_name in self.allow_tools:
                                tool_result = tool_func(tool_call_args)
                            else:
                                tool_result = {
                                    "success": False,
                                    "error": "此操作不在允许清单内",
                                }
                            print(tool_result)
                            self.push_messages(
                                {
                                    "role": "tool",
                                    "tool_call_id": tool_call.id,
                                    "name": tool_call_name,
                                    "content": json.dumps(
                                        tool_result, ensure_ascii=False
                                    ),
                                }
                            )
                self.on_ai_send_message_handler()
            if finish_reason == "stop" and choice.message.content:
                self.on_ai_send_message_handler()
        except Exception as e:
            print("[异常] ", e)
            self.push_messages(
                {"name": "system_notice", "role": "assistant", "content": f"[异常] {e}"}
            )
            self.on_ai_send_message_handler()

    def send_ai_message(self, user_content, type="user"):
        print(self.config)
        input_json = [
            {
                "type": type,
                "arguments": {
                    "content": user_content,
                    "is_multimodal": self.config["is_multimodal"],
                    "prompt": self.config["lines_prompt"],
                    "skills": self.skills,
                },
            }
        ]
        input_content = json.dumps(input_json)
        screenshot_path = screenshot()
        if screenshot_path:
            image_add_lim(screenshot_path)
            if user_content.split()[0] in self.commands.keys():
                self.do_command(user_content)
            elif self.config.get("tool_calls"):
                self.send_tools_ai_message(user_content, screenshot_path)
            else:
                ai_response = self.send_image_to_ai(input_content, screenshot_path)
                print(ai_response)
                self.handle_ai_message(ai_response, input_content)
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
        # 初始化管理器
        self.config_manager = ConfigManager()
        self.skills_manager = SkillsManager(self.BASE_DIR)
        self.plugins_manager = PluginsManager(self)

        # 初始化配置和技能
        self.config = self.config_manager.read_config(self.BASE_DIR)
        self.skills = self.skills_manager.get_skills_info()
        self.client.api_key = self.config["api_key"]
        self.client.base_url = self.config["base_url"]

        # 构建初始消息

        self.messages: Any = [{"role": "system", "content": NO_TOOLS_PROMPT}]
        self.full_messages: Any = [{"role": "system", "content": NO_TOOLS_PROMPT}]

        # 加载插件
        self.plugins_manager.load_plugins()

        self._init_prompts()

    def allow_tool(self, tool_name):
        if tool_name not in self.allow_tools:
            self.allow_tools.append(tool_name)
            print(f"[权限管理] 在本对话中已允许使用 {tool_name}")

    def not_allowed_tool(self, tool_name):
        if tool_name in self.allow_tools:
            self.allow_tools.remove(tool_name)
            print(f"[权限管理] 在本对话中已拒绝使用 {tool_name}")

    def push_messages(self, message):
        self.messages.append(message)
        self.full_messages.append(message)
