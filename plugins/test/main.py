from autopc.api.event import (
    registr_command,
    registr_ai_send_message_callback,
    registr_ai_use_tool_callback,
)
import requests


# 指令示例
@registr_command("测试指令")
def test_command(command, url):
    print("你输入了url:", url)
    content = requests.get(url)
    return "网站内容:" + content.text


"""@registr_ai_use_tool_callback()
def test_callback2(tool_call):
    print("工具调用信息:", tool_call)
    return {"exec": False}
"""

"""
@registr_ai_send_message_callback()
def test_callback(messages):
    print(messages)
"""
