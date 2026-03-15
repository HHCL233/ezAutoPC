import pyautogui
import os
import base64
from openai import OpenAI
from openai.types.chat import ChatCompletionMessageParam
from typing import List
import json
import readline
import sys
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image

BASE_URL = "https://apis.iflow.cn/v1"
MODEL = "qwen3-vl-plus"
API_KEY = "sk-3135442530cca9a94ccc2b094c2e06bc"
client = OpenAI(api_key=API_KEY, base_url=BASE_URL)


def initReadline():
    readline.parse_and_bind("arrow-left: backward-char")
    readline.parse_and_bind("arrow-right: forward-char")
    readline.parse_and_bind("ctrl-a: beginning-of-line")
    readline.parse_and_bind("ctrl-e: end-of-line")


def terminalInput(prompt="> "):
    initReadline()
    try:
        return input(prompt)
    except KeyboardInterrupt:
        # 处理 Ctrl+C 中断
        print("\n输入已中断")
        sys.exit("程序已终止")
    except EOFError:
        # 处理 Ctrl+D 结束输入
        print("\n输入结束")
        return ""


def imageToBase64(image_path):
    with open(image_path, "rb") as image_file:
        base64_encoded = base64.b64encode(image_file.read()).decode("utf-8")
    return base64_encoded


def screenshot():
    filePath = "screenshots/screenshot.jpg"
    try:
        if not os.path.exists("screenshots"):
            os.makedirs("screenshots")
        if os.path.isfile(filePath):
            os.remove(filePath)
        screenshot_img = pyautogui.screenshot()
        screenshot_img.save(filePath)
        print(f"截图成功，保存路径：{filePath}")
    except Exception as e:
        print(f"截图失败：{e}")


def sendImageToAI(prompt, imageSource, isLocal=True):
    messages: List[ChatCompletionMessageParam] = [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": prompt},
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{imageToBase64(imageSource)}"
                        if isLocal
                        else imageSource
                    },
                },
            ],
        },
        {
            "role": "system",
            "content": """
你是一个可以操控电脑的AI模型,并且需要按照格式输出:
当前上传了一张屏幕截图,使用图片上的网格坐标作为坐标系,目前需要根据图片中内容执行对应操作,图片上的红色网格为坐标网格,坐标网格上的蓝色数字为截图中网格坐标,鼠标的每一次移动和点击都需要精准根据图片上的网格坐标确定位置,不可以使用真实坐标,必须使用截图中网格上显示的坐标(如截图中网格显示A在坐标(150,850),现在需要把鼠标移动到A,就需要移动到x=150,y=850),返回内容使用JSON格式,但不要夹带任何Markdown信息,JSON不使用```json```包裹而是直接输出,格式为
[{
    "type":"操作1操作类型",
    "arguments":{
        "参数1":"参数对应的值1",
        "参数2":"参数对应的值2"
    }
},{
    "type":"操作2操作类型",
    "arguments":{
        "参数1":"参数对应的值1",
        "参数2":"参数对应的值2"
    }
}]
可以在一次内执行无数个操作,并且执行的操作可以重复(例如可以在一次内执行100个mouse)
在进行所有坐标有关操作时必须使用图片上的网格坐标
操作说明:
模拟鼠标移动操作:
- type为"mouse"
- arguments有x(对应屏幕截图中网格的X坐标),y(对应屏幕截图中网格的Y坐标)2个argument
- {x=0,y=0}为屏幕左上角,{x=1920,y=0}为屏幕右上角,{x=1920,y=1080}为屏幕右下角,{x=0,y=1080}为屏幕左下角
- 在进行操作时必须基于图片上的网格坐标
模拟鼠标单次点击操作:
- type为"click"
- arguments为空
- 点击当前鼠标指针所在坐标
模拟鼠标双次点击操作:
- type为"doubleClick"
- arguments为空
- 点击当前鼠标指针所在坐标
模拟输入文本操作:
- type为"write"
- arguments有content,内容为向主机输入的内容
- 可以向处于焦点状态内的输入文本框内添加内容
与用户对话操作:
- type为"message"
- arguments有content,内容为向用户返回的内容
- 该操作用于与用户对话
继续任务操作:
- type为"continue"
- arguments为空
- 如果有一个大任务,并且在当前场景无法全部完成,可以在末尾加入此操作用于继续当前任务(此操作如要使用,需要放置在操作列表的末尾)
部分重点注意:
- 在进行所有坐标有关操作时必须基于图片上的网格坐标!
- 打开软件需要先把鼠标移动到图片上的对应网格坐标,再进行双次点击
- 如果有较为复杂的任务(如"打开B站","帮我打开开始菜单并寻找软件XXX"等)需要将这些任务分为小任务来操作
            """,
        },
    ]

    try:
        response = client.chat.completions.create(
            model=MODEL, messages=messages, temperature=0.7, max_tokens=1000
        )
        return response.choices[0].message.content

    except Exception as e:
        return f"请求失败：{str(e)}"


def handleAIMessage(content):
    try:
        controlsJSON = json.loads(content)
        for control in controlsJSON:
            controlType = control["type"]
            controlArguments = control["arguments"]
            if controlType == "mouse":
                pyautogui.FAILSAFE = False
                pyautogui.moveTo(
                    controlArguments["x"], controlArguments["y"], duration=0
                )
                print(
                    "[鼠标移动]位置",
                    controlArguments["x"],
                    ",",
                    controlArguments["y"],
                    "已移动",
                )
            elif controlType == "click":
                pyautogui.click()
            elif controlType == "doubleClick":
                pyautogui.doubleClick()
            elif controlType == "write":
                pyautogui.write(controlArguments["content"])
            elif controlType == "message":
                print("[AI消息]", controlArguments["content"])
            elif controlType == "continue":
                sendAIMessage(content)
    except Exception as e:
        print("[异常]", e)


def sendAIMessage(content):
    screenshot()
    imageAddLim("screenshots/screenshot.jpg")
    messages = sendImageToAI(content, "screenshots/screenshot.jpg")
    print(messages)
    handleAIMessage(messages)


def imageAddLim(path):
    img = Image.open(path)
    img_array = np.array(img)
    height, width = img_array.shape[:2]

    fig, ax = plt.subplots(figsize=(width / 96, height / 96), dpi=96)
    plt.subplots_adjust(left=0, right=1, top=1, bottom=0)
    ax.margins(x=0, y=0)

    ax.imshow(img_array)
    ax.grid(True, which="major", linestyle="-", linewidth=1.0, alpha=0.6, color="red")

    grid_step = 50
    x_ticks = np.arange(0, width + grid_step, grid_step)
    y_ticks = np.arange(0, height + grid_step, grid_step)
    ax.set_xticks(x_ticks)
    ax.set_yticks(y_ticks)
    ax.set_xlim(0, width)
    ax.set_ylim(height, 0)

    ax.spines["top"].set_visible(False)
    ax.spines["left"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["bottom"].set_visible(False)
    ax.tick_params(axis="both", which="both", length=0)
    ax.set_xticklabels([])
    ax.set_yticklabels([])

    x_coords = x_ticks[x_ticks <= width]
    y_coords = y_ticks[y_ticks <= height]

    for x in x_coords:
        for y_plot in y_coords:
            ax.text(
                x,
                y_plot,
                f"({int(x)},{int(y_plot)})",
                fontsize=6,
                color="lightblue",
                ha="center",
                va="center",
                bbox=dict(
                    boxstyle="round,pad=0.1",
                    facecolor="white",
                    alpha=0,
                    edgecolor="none",
                ),
                zorder=10,
            )

    ax.axvline(x=0, color="black", linewidth=2)
    ax.axhline(y=height, color="black", linewidth=2)

    plt.savefig(
        path,
        dpi=300,
        bbox_inches="tight",
        pad_inches=0,
        facecolor="white",
        edgecolor="none",
    )
    print(f"图像已保存至：{path}")
    plt.close(fig)


def main():
    while True:
        print("")
        userInput = terminalInput()
        if userInput == "exit":
            return
        sendAIMessage(userInput)


if __name__ == "__main__":
    main()
