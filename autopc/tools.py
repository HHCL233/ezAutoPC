from openai.types.chat import ChatCompletionToolParam
from typing import List

# 定义所有可用的工具
TOOLS: List[ChatCompletionToolParam] = [
    {
        "type": "function",
        "function": {
            "name": "download",
            "description": "下载文件操作,可以下载指定URL的文件到本地目录",
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
                        "description": "保存路径,使用绝对路径(可以使用'~'表示家目录)",
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
                        "description": "屏幕截图中网格的X坐标,{x=0,y=0}为屏幕左上角,{x=1920,y=1080}为屏幕右下角",
                    },
                    "y": {
                        "type": "integer",
                        "description": "屏幕截图中网格的Y坐标,{x=0,y=0}为屏幕左上角,{x=1920,y=1080}为屏幕右下角",
                    },
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "click",
            "description": "模拟鼠标单次点击操作,点击当前鼠标指针所在坐标",
            "parameters": {"type": "object", "required": [], "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "doubleClick",
            "description": "模拟鼠标双次点击操作,点击当前鼠标指针所在坐标",
            "parameters": {"type": "object", "required": [], "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "write",
            "description": "模拟输入文本操作,向处于焦点状态内的输入文本框内添加内容",
            "parameters": {
                "type": "object",
                "required": ["content"],
                "properties": {
                    "content": {
                        "type": "string",
                        "description": "向主机输入的内容,不建议直接输入英文",
                    }
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "press",
            "description": "模拟键盘按键点击操作,不能使用组合键",
            "parameters": {
                "type": "object",
                "required": ["key"],
                "properties": {
                    "key": {
                        "type": "string",
                        "description": "模拟的键盘按键,全小写,如esc、f11、enter等",
                    }
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "terminal",
            "description": "终端操作,执行单条bash指令,不可获取运行指令的输出内容,不要启动命令行程序,优先使用终端相关操作而不是鼠标相关操作",
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
            "description": "可返回终端操作,执行单条bash指令,可获取运行指令的输出内容,可运行命令行程序,优先使用终端相关操作而不是鼠标相关操作",
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
            "description": "读取SKILL.md操作,获取对应Skill内SKILL.md的内容",
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
    {
        "type": "function",
        "function": {
            "name": "getRequest",
            "description": "使用Get请求方式访问API并获取内容",
            "parameters": {
                "type": "object",
                "required": ["url"],
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "API的URL",
                    }
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "postRequest",
            "description": "使用Post请求方式访问API并获取内容",
            "parameters": {
                "type": "object",
                "required": ["url"],
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "API的URL",
                    },
                    "json": {
                        "type": "object",
                        "description": "请求JSON",
                    },
                    "headers": {
                        "type": "object",
                        "description": "请求头",
                    },
                    "cookies": {
                        "type": "object",
                        "description": "请求Cookies",
                    },
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "readAutoPCConfig",
            "description": "读取ezAutoPC的配置",
            "parameters": {
                "type": "object",
                "required": [],
                "properties": {},
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "childAgentChat",
            "description": "与子Agent对话,返回消息列表",
            "parameters": {
                "type": "object",
                "required": ["id", "content"],
                "properties": {
                    "id": {
                        "type": "integer",
                        "description": "子Agent编号,从0开始",
                    },
                    "content": {
                        "type": "string",
                        "description": "向Agent发送的内容",
                    },
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "readFile",
            "description": "以文本格式获取对应目录下的文件,返回的文件内容中每一行对应列表的一项",
            "parameters": {
                "type": "object",
                "required": ["path"],
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "文件目录",
                    },
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "readLinesFile",
            "description": "以文本格式获取对应目录下的文件部分内容,返回的文件内容中每一行对应列表的一项",
            "parameters": {
                "type": "object",
                "required": ["path", "startLine", "endLine"],
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "文件目录",
                    },
                    "startLine": {
                        "type": "integer",
                        "description": "开始读取的行数,从0开始",
                    },
                    "endLine": {
                        "type": "integer",
                        "description": "结束读取的行数",
                    },
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "readDirList",
            "description": "读取对应目录下的文件列表",
            "parameters": {
                "type": "object",
                "required": ["dir"],
                "properties": {
                    "dir": {
                        "type": "string",
                        "description": "文件夹目录",
                    },
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "insertFile",
            "description": "以文本格式向对应文件的某一行插入内容,返回更改后的文件内容,返回的文件内容中每一行对应列表的一项",
            "parameters": {
                "type": "object",
                "required": ["path", "insertLine", "content"],
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "文件目录",
                    },
                    "insertLine": {
                        "type": "integer",
                        "description": "插入行",
                    },
                    "content": {
                        "type": "string",
                        "description": "插入内容",
                    },
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "deleteFileLine",
            "description": "以文本格式删除对应文件的某一行,返回更改后的文件内容,返回的文件内容中每一行对应列表的一项",
            "parameters": {
                "type": "object",
                "required": ["path", "deleteLine"],
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "文件目录",
                    },
                    "deleteLine": {
                        "type": "integer",
                        "description": "删除行",
                    },
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "newTask",
            "description": "向任务列表新建任务",
            "parameters": {
                "type": "object",
                "required": ["name"],
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "新增任务名称",
                    }
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "deleteTask",
            "description": "在任务列表删除任务",
            "parameters": {
                "type": "object",
                "required": ["name"],
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "删除任务名称",
                    }
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "setTaskState",
            "description": "设置任务列表的任务状态",
            "parameters": {
                "type": "object",
                "required": ["name", "state"],
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "任务名称",
                    },
                    "state": {
                        "type": "boolean",
                        "description": "设置的任务状态",
                    },
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "getTasksList",
            "description": "获取任务列表",
            "parameters": {
                "type": "object",
                "required": [],
                "properties": {},
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "removeFile",
            "description": "删除文件",
            "parameters": {
                "type": "object",
                "required": ["path"],
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "文件路径",
                    },
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "removeFolder",
            "description": "删除文件夹",
            "parameters": {
                "type": "object",
                "required": ["path"],
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "文件夹路径",
                    },
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "newFile",
            "description": "新建UTF8编码文件并写入内容",
            "parameters": {
                "type": "object",
                "required": ["path", "content"],
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "文件目录,使用绝对路径",
                    },
                    "content": {
                        "type": "string",
                        "description": "要写入的完整文本内容",
                    },
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "createFolder",
            "description": "新建文件夹",
            "parameters": {
                "type": "object",
                "required": ["path"],
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "文件夹目录,使用绝对路径",
                    },
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "moveDir",
            "description": "移动文件夹/文件,也可用于重命名文件",
            "parameters": {
                "type": "object",
                "required": ["srcPath", "dstPath", "isCover"],
                "properties": {
                    "srcPath": {
                        "type": "string",
                        "description": "源文件/文件夹目录",
                    },
                    "dstPath": {
                        "type": "string",
                        "description": "移动后文件/文件夹目录",
                    },
                    "isCover": {
                        "type": "boolean",
                        "description": "是否直接覆盖移动后文件/文件夹目录对应的文件",
                    },
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "copyFolder",
            "description": "复制文件夹",
            "parameters": {
                "type": "object",
                "required": ["srcPath", "dstPath"],
                "properties": {
                    "srcPath": {
                        "type": "string",
                        "description": "源文件夹目录",
                    },
                    "dstPath": {
                        "type": "string",
                        "description": "移动后文件夹目录",
                    },
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "copyFile",
            "description": "复制文件",
            "parameters": {
                "type": "object",
                "required": ["srcPath", "dstPath", "isCover"],
                "properties": {
                    "srcPath": {
                        "type": "string",
                        "description": "源文件目录",
                    },
                    "dstPath": {
                        "type": "string",
                        "description": "复制后文件目录",
                    },
                    "isCover": {
                        "type": "boolean",
                        "description": "是否直接覆盖复制后文件目录对应的文件",
                    },
                },
            },
        },
    },
]
