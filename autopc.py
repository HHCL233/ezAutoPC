import pyautogui
import os
import base64
from openai import OpenAI
from openai.types.chat import ChatCompletionMessageParam
from typing import List, Dict
import json
import readline
import sys
import subprocess
import threading
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
from time import sleep
from markdown import Markdown


class AutoPC:
    # 类常量定义
    BASE_URL = "https://api.moonshot.cn/v1"
    MODEL = "kimi-k2.5"
    API_KEY = ""
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

    def __init__(self):
        # 初始化实例变量
        self.skills = {}
        self.config = {}
        self.client = OpenAI(api_key=self.API_KEY, base_url=self.BASE_URL)
        self.messages: List[ChatCompletionMessageParam] = [
            {
                "role": "system",
                "content": """
你是一个可以操控电脑的AI模型,名字叫做ezAutoAI
用户输入格式为[{
    "type":"user",
    "arguments":{
        "content":"用户输入的内容",
        "is_multimodal":true/false,
        "skills":{
    'Skill的文件夹名称': {
        'dir':[
            'Skill的目录'
        ]
        'name': [
            'Skill的名字'
        ],
        'description': [
            'Skill的简介'
        ],
        'license': [
            'Skill的许可证'
        ],
        'metadata': [
            ''
        ],
        'author': [
            'Skill的作者'
        ],
        'version': [
            'Skill的版本'
        ]
    }
},
    }
}]
Skill是一个被标准化封装,可主动调用,用于完成特定任务的能力单元,skills内可以存在多个skill,每个skill都会存在SKILL.md,用于介绍和说明Skill如何使用,大部分Skill中所写的Python模块都在 Skill的目录/scripts 中,不要修改每个Skill内的文件,除非是自己创建的
is_multimodal对应一个布尔值,代表在当前对话中是否能识别图像并执行和鼠标有关的操作
程序返回(执行支持返回的操作后)格式为[{
    "type":"application",
    "arguments":{
        "content":"用户输入的内容",
    }
}]
需要按照格式输出:
当前上传了一张屏幕截图,目前需要根据图片中内容执行对应操作,鼠标的每一次移动和点击都需要精准根据图片对应位置的坐标,返回内容使用JSON格式,但不要夹带任何Markdown信息,JSON不使用```json```包裹而是直接输出,只输出符合格式的JSON格式内容,格式为
[{
    "type":"操作1操作类型",
    "arguments":{
        "参数1":"参数对应的值1",
        "参数2":"参数对应的值2"
    }
},
{
    "type":"操作2操作类型",
    "arguments":{
        "参数1":"参数对应的值1",
        "参数2":"参数对应的值2"
    }
},
{
    "type":"操作3操作类型(这个列表还可以添加更多操作......)",
    "arguments":{
        "参数1":"参数对应的值1",
        "参数2":"参数对应的值2"
    }
}]
可以在一次内执行无数个操作,并且执行的操作可以重复(例如可以在一次内执行100个mouse)
坐标注意事项:
- y=0 是屏幕最顶部
- y=1080 是屏幕最底部
- 在进行所有坐标有关操作时必须使用图片对应位置的坐标
操作说明:
模拟鼠标移动操作:
- type为"mouse"
- arguments有x(对应屏幕截图中网格的X坐标)(int类型),y(对应屏幕截图中网格的Y坐标)(int类型)2个argument
- {x=0,y=0}为屏幕左上角,{x=1920,y=0}为屏幕右上角,{x=1920,y=1080}为屏幕右下角,{x=0,y=1080}为屏幕左下角
- 在进行所有坐标有关操作时必须使用图片对应位置的坐标
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
- 不建议直接输入英文,可能会因为主机中的中文输入法而导致错误
模拟键盘按键点击操作:
- type为"press"
- arguments有key,内容为模拟的键盘按键(全小写,如"esc","f11","enter"等)
- 可以按下对应的键盘按键,在需要按下字母键位以外的键时很有用
- 此操作不能使用组合键
说明操作:
- type为"message"
- arguments有content,内容为一次内操作的简要说明
- 该操作必须在每一次中加入,用于说明一次内操作的简要说明
- 如果要和用户进行对话,也需要使用该操作
继续任务操作:
- type为"continue"
- arguments为wait,内容为等待的秒数(int类型)(限制在0-1.5区间)
- 如果有一个大任务,并且在当前场景无法全部完成,可以在末尾加入此操作用于继续当前任务(此操作如要使用,需要放置在操作列表的末尾)
任务困难操作
- type为"difficulty"
- arguments为空
- 如果用户提出的操作要求无法实现则需要在该次的开头添加此操作
终端操作
- type为"terminal"
- arguments有command,内容为要执行的单条终端指令
- 当前主机使用的终端为bash,使用bash指令进行操作
- 此操作可用于启动带有GUI的应用等(不要启动命令行程序)
可返回终端操作
- type为"returnTerminal"
- arguments有command,内容为要执行的单条终端指令
- 当前主机使用的终端为bash,使用bash指令进行操作
- 此操作可以获取运行指令的输出内容,可以运行命令行程序程序(例如ping,python等)
读取SKILL.md操作
- type为"readSkillMd"
- arguments有name,内容为读取SKILL.md的对应skill名称(Skill的文件夹名称)
- 此操作可以获取该Skill内SKILL.md的内容,用于获取该Skill的介绍和使用指南
重点:
- 打开软件需要先把鼠标移动到图片上的对应坐标网格坐标,再进行双次点击
- 如果有较为复杂或需要不只一张屏幕截图的任务(如"打开B站","帮我打开开始菜单并寻找软件XXX"等)需要主动将这些任务分为小任务并使用"继续任务操作"来操作
- 在进行任何操作时优先使用"终端操作"
- "终端操作"优先,"模拟鼠标移动操作"为辅
- "终端操作"无法获得终端输出,因此不要检测是否存在此软件
- 在每一次完成后需要使用"继续任务操作"检测任务是否完成(如果已经因为其他原因存在"继续任务操作"则忽略)
- 在大部分场景中,输出完成内容后需要按下enter才能打开/访问/搜索/发送
- 在大部分场景中,Skills的优先级始终高于自己
            """,
            },
        ]
        self.onAISendMessage = []
        # 初始化配置
        self.readConfig()
        self.getSkillsInfo()

    def getSkillsInfo(self):
        try:
            skillsDir = os.path.join(self.BASE_DIR, "skills")
            entries = os.listdir(skillsDir)
            for skillEntries in entries:
                skillDir = os.path.join(skillsDir, skillEntries)
                mdDir = os.path.join(skillDir, "SKILL.md")
                try:
                    with open(mdDir, "r", encoding="utf-8") as skillMd:
                        md = Markdown(extensions=["meta"])
                        htmlOutput = md.convert(skillMd.read())
                        meta: Dict[str, List[str]] = getattr(md, "Meta", {})
                        meta["dir"] = [skillDir]
                        self.skills[skillEntries] = meta
                except Exception as e:
                    print(f"[Skills] 读取Skill {skillEntries} 失败: ", e)
            print(f"[Skills] 共加载 {len(self.skills)} 个 Skills: ", self.skills)
        except Exception as e:
            print("[Skills] 读取全部Skills失败: ", e)

    def readConfig(self):
        try:
            if os.path.exists("config.json"):
                print("[读取配置] config 文件存在,开始读取文件内容...")
                with open("config.json", "r", encoding="utf-8") as f:
                    configContent = f.read()
                    configJSON = json.loads(configContent)
                    self.config = configJSON
            else:
                print("[读取配置] config 文件不存在")
                print("[读取配置] 启用 main 内配置")
                self.config = {
                    "api_key": self.API_KEY,
                    "model": self.MODEL,
                    "base_url": self.BASE_URL,
                }
        except Exception as e:
            print("[读取配置] 读取失败: ", e)
            print("[读取配置] 启用 main 内配置")
            self.config = {
                "api_key": self.API_KEY,
                "model": self.MODEL,
                "base_url": self.BASE_URL,
            }

    def initReadline(self):
        readline.parse_and_bind("arrow-left: backward-char")
        readline.parse_and_bind("arrow-right: forward-char")
        readline.parse_and_bind("ctrl-a: beginning-of-line")
        readline.parse_and_bind("ctrl-e: end-of-line")

    def terminalInput(self, prompt="> "):
        self.initReadline()
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

    def imageToBase64(self, image_path):
        with open(image_path, "rb") as image_file:
            base64_encoded = base64.b64encode(image_file.read()).decode("utf-8")
        return base64_encoded

    def screenshot(self):
        filePath = "screenshots/screenshot.jpg"
        try:
            if not os.path.exists("screenshots"):
                os.makedirs("screenshots")
            if os.path.isfile(filePath):
                os.remove(filePath)
            screenshot_img = pyautogui.screenshot()
            screenshot_img.save(filePath)
            print(f"截图成功，保存路径：{filePath}")
            return filePath
        except Exception as e:
            print(f"截图失败：{e}")
            return None

    def sendImageToAI(self, prompt, imageSource, isLocal=True):
        if self.config["is_multimodal"]:
            self.messages.append(
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{self.imageToBase64(imageSource)}"
                                if isLocal
                                else imageSource
                            },
                        },
                    ],
                }
            )
        else:
            print("[警告] is_multimodal为false,因此不会发送屏幕截图")
            self.messages.append(
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                    ],
                }
            )

        try:
            self.client.api_key = self.config["api_key"]
            self.client.base_url = self.config["base_url"]
            response = self.client.chat.completions.create(
                model=self.config["model"],
                messages=self.messages,
                temperature=0.6,
                max_tokens=1000,
                extra_body={"thinking": {"type": "disabled"}},
            )
            self.messages.append(
                {
                    "role": "assistant",
                    "content": response.choices[0].message.content,
                }
            )
            return response.choices[0].message.content

        except Exception as e:
            errorStr = json.dumps(
                [
                    {
                        "type": "error",
                        "arguments": {"content": f"请求失败：{str(e)}"},
                    }
                ]
            )
            self.messages.append(
                {
                    "role": "assistant",
                    "content": errorStr,
                }
            )
            return errorStr

    def runCommandSilently(self, command):
        try:
            devnull = open(os.devnull, "w")
            subprocess.run(
                command, shell=True, stdout=devnull, stderr=devnull, check=True
            )
            devnull.close()
        except Exception as e:
            print(f"[单独线程运行命令] {e}")
            pass

    def handleAIMessage(self, content, userMessage):
        try:
            controlsJSON = json.loads(content)
            for control in controlsJSON:
                controlType = control["type"]
                controlArguments = control["arguments"]
                if controlType == "mouse":
                    pyautogui.FAILSAFE = False
                    pyautogui.moveTo(
                        int(controlArguments["x"]),
                        int(controlArguments["y"]),
                        duration=0,
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
                elif controlType == "press":
                    pyautogui.press(controlArguments["key"])
                elif controlType == "message":
                    print("[AI消息]", controlArguments["content"])
                elif controlType == "continue":
                    jsonContent = json.loads(userMessage)
                    sleep(int(controlArguments["wait"]))
                    self.sendAIMessage(
                        f"继续操作({jsonContent[0]['arguments']['content'].encode('raw_unicode_escape').decode('utf-8')})",
                        "application",
                    )
                elif controlType == "terminal":
                    runCommand = controlArguments["command"]
                    print("[执行命令]", runCommand)
                    thread = threading.Thread(
                        target=self.runCommandSilently, args=(runCommand,)
                    )
                    thread.daemon = False
                    thread.start()
                elif controlType == "returnTerminal":
                    runCommand = controlArguments["command"]
                    print("[执行命令]", runCommand)
                    result = subprocess.run(
                        runCommand, shell=True, capture_output=True, text=True
                    )
                    self.sendAIMessage(
                        f"终端操作已完成,输出:{result.stdout.strip()}", "application"
                    )
                elif controlType == "readSkillMd":
                    skillMeta = self.skills[controlArguments["name"]]
                    skillMdDir = os.path.join(skillMeta["dir"][0], "SKILL.md")
                    with open(skillMdDir, "r", encoding="utf-8") as skillMd:
                        print("[Skills读取] 已成功读取SkillMd")
                        self.sendAIMessage(
                            f"读取SKILL.md操作已完成,文件内容:{skillMd.read()}",
                            "application",
                        )
                for handler in self.onAISendMessage:
                    handler()
        except Exception as e:
            print("[异常]", e)

    def sendAIMessage(self, userContent, type="user"):
        inputJson = [
            {
                "type": type,
                "arguments": {
                    "content": userContent,
                    "is_multimodal": self.config["is_multimodal"],
                    "skills": self.skills,
                },
            }
        ]
        inputContent = json.dumps(inputJson)
        screenshotPath = self.screenshot()
        if screenshotPath:
            self.imageAddLim(screenshotPath)
            aiResponse = self.sendImageToAI(inputContent, screenshotPath)
            print(aiResponse)
            for handler in self.onAISendMessage:
                handler()
            self.handleAIMessage(aiResponse, inputContent)

    def imageAddLim(self, path):
        img = Image.open(path)
        imgArray = np.array(img)
        height, width = imgArray.shape[:2]

        fig, ax = plt.subplots(figsize=(width / 96, height / 96), dpi=96)
        plt.subplots_adjust(left=0, right=1, top=1, bottom=0)
        ax.margins(x=0, y=0)

        ax.imshow(imgArray)
        ax.grid(
            True, which="major", linestyle="-", linewidth=1.0, alpha=0.6, color="red"
        )

        gridStep = 50
        xTicks = np.arange(0, width + gridStep, gridStep)
        yTicks = np.arange(0, height + gridStep, gridStep)
        ax.set_xticks(xTicks)
        ax.set_yticks(yTicks)
        ax.set_xlim(0, width)
        ax.set_ylim(height, 0)

        ax.spines["top"].set_visible(False)
        ax.spines["left"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.spines["bottom"].set_visible(False)
        ax.tick_params(axis="both", which="both", length=0)
        ax.set_xticklabels([])
        ax.set_yticklabels([])

        xCoords = xTicks[xTicks <= width]
        yCoords = yTicks[yTicks <= height]

        for x in xCoords:
            for yPlot in yCoords:
                ax.text(
                    x,
                    yPlot,
                    f"({int(x)},{int(yPlot)})",
                    fontsize=6.5,
                    color="darkred",
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

    def mainLoop(self):
        while True:
            print("")
            userInput = self.terminalInput()
            if userInput == "exit":
                return
            self.sendAIMessage(userInput)
