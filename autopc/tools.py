from openai.types.chat import ChatCompletionToolParam
from typing import List

# 定义所有可用的工具
TOOLS: List[ChatCompletionToolParam] = [
    {
        "type": "function",
        "function": {
            "name": "download",
            "description": "下载文件操作，可以下载指定URL的文件到本地目录",
            "parameters": {
                "type": "object",
                "required": ["url", "savePath"],
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "下载文件URL",
                    },
                    "savePath": {
                        "type": "string",
                        "description": "保存路径，使用绝对路径(可以使用'~'表示家目录)",
                    },
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "mouse",
            "description": "模拟鼠标移动操作",
            "parameters": {
                "type": "object",
                "required": ["x", "y"],
                "properties": {
                    "x": {
                        "type": "integer",
                        "description": "屏幕截图中网格的X坐标，{x=0,y=0}为屏幕左上角,{x=1920,y=1080}为屏幕右下角",
                    },
                    "y": {
                        "type": "integer",
                        "description": "屏幕截图中网格的Y坐标，{x=0,y=0}为屏幕左上角,{x=1920,y=1080}为屏幕右下角",
                    },
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "click",
            "description": "模拟鼠标单次点击操作，点击当前鼠标指针所在坐标",
            "parameters": {"type": "object", "required": [], "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "doubleClick",
            "description": "模拟鼠标双次点击操作，点击当前鼠标指针所在坐标",
            "parameters": {"type": "object", "required": [], "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "write",
            "description": "模拟输入文本操作，向处于焦点状态内的输入文本框内添加内容",
            "parameters": {
                "type": "object",
                "required": ["content"],
                "properties": {
                    "content": {
                        "type": "string",
                        "description": "向主机输入的内容，不建议直接输入英文",
                    }
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "press",
            "description": "模拟键盘按键点击操作，不能使用组合键",
            "parameters": {
                "type": "object",
                "required": ["key"],
                "properties": {
                    "key": {
                        "type": "string",
                        "description": "模拟的键盘按键，全小写，如esc、f11、enter等",
                    }
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "terminal",
            "description": "终端操作，执行单条bash指令，优先使用，可启动带有GUI的应用，不要启动命令行程序",
            "parameters": {
                "type": "object",
                "required": ["command"],
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "要执行的单条bash终端指令",
                    }
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "returnTerminal",
            "description": "可返回终端操作，执行单条bash指令，可获取运行指令的输出内容，可运行命令行程序",
            "parameters": {
                "type": "object",
                "required": ["command"],
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "要执行的单条bash终端指令",
                    }
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "readSkillMd",
            "description": "读取SKILL.md操作，获取对应Skill内SKILL.md的内容",
            "parameters": {
                "type": "object",
                "required": ["name"],
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "读取SKILL.md的对应skill名称（Skill的文件夹名称）",
                    }
                },
            },
        },
    },
]
