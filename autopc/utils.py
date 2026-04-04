import os
import base64
import readline
import sys
import subprocess
import threading
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
import pyautogui
import httpx
import matplotlib

# 固定matplotlib后端
matplotlib.use("Agg")


def init_readline():
    """初始化命令行输入支持"""
    readline.parse_and_bind("arrow-left: backward-char")
    readline.parse_and_bind("arrow-right: forward-char")
    readline.parse_and_bind("ctrl-a: beginning-of-line")
    readline.parse_and_bind("ctrl-e: end-of-line")


def terminal_input(prompt="> ") -> str:
    """
    获取终端输入
    :param prompt: 提示符
    :return: 输入字符串
    """
    init_readline()
    try:
        return input(prompt)
    except KeyboardInterrupt:
        print("\n输入已中断")
        sys.exit("程序已终止")
    except EOFError:
        print("\n输入结束")
        return ""


def image_to_base64(image_path: str) -> str:
    """
    将图片文件转为base64
    :param image_path: 图片路径
    :return: base64字符串
    """
    with open(image_path, "rb") as image_file:
        base64_encoded = base64.b64encode(image_file.read()).decode("utf-8")
    return base64_encoded


def screenshot() -> str | None:
    """
    截取屏幕
    :return: 截图保存路径
    """
    file_path = "screenshots/screenshot.jpg"
    try:
        if not os.path.exists("screenshots"):
            os.makedirs("screenshots")
        if os.path.isfile(file_path):
            os.remove(file_path)
        screenshot_img = pyautogui.screenshot()
        screenshot_img.save(file_path)
        print(f"截图成功，保存路径:{file_path}")
        return file_path
    except Exception as e:
        print(f"截图失败:{e}")
        return None


def image_add_lim(path: str):
    """
    在图片上添加网格和坐标
    :param path: 图片路径
    """
    img = Image.open(path)
    img_array = np.array(img)
    height, width = img_array.shape[:2]

    fig, ax = plt.subplots(figsize=(width / 96, height / 96), dpi=96)
    plt.subplots_adjust(left=0, right=1, top=1, bottom=0)
    ax.margins(x=0, y=0)

    ax.imshow(img_array)
    ax.grid(
        True,
        which="major",
        linestyle="-",
        linewidth=1.0,
        alpha=0.6,
        color="darkred",
    )

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
                fontsize=6.5,
                color="red",
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
    print(f"图像已保存至:{path}")
    plt.close(fig)


def run_command_silently(command: str):
    """
    静默执行终端命令（用于线程）
    :param command: 命令字符串
    """
    try:
        devnull = open(os.devnull, "w")
        subprocess.run(command, shell=True, stdout=devnull, stderr=devnull, check=True)
        devnull.close()
    except Exception as e:
        print(f"[单独线程运行命令] {e}")
        pass


def download_file(control_arguments: dict) -> dict:
    """
    下载文件
    :param control_arguments: 包含url和savePath的字典
    :return: 结果字典
    """
    try:
        print("[下载文件] 开始下载文件")
        save_path = os.path.expanduser(control_arguments["savePath"])
        response = httpx.get(control_arguments["url"])
        response.raise_for_status()

        os.makedirs(os.path.dirname(save_path), exist_ok=True)

        with open(save_path, "wb") as file:
            file.write(response.content)
        print(f"[下载文件] 下载完成: {save_path}")
        return {"success": True, "savePath": save_path}
    except Exception as e:
        print(f"[下载文件] {e}")
        return {"success": False}


def get_request(control_arguments: dict) -> dict:
    """
    get请求
    :param control_arguments: 包含url的字典
    :return: 结果字典
    """
    try:
        response = httpx.get(control_arguments["url"])
        response.raise_for_status()

        return {
            "success": True,
            "content": response.text,
            "status_code": response.status_code,
        }
    except Exception as e:
        print(f"[Get请求] {e}")
        return {"success": False}


def post_request(control_arguments: dict) -> dict:
    """
    post请求
    :param control_arguments: 包含url的字典
    :return: 结果字典
    """
    try:
        response = httpx.post(
            control_arguments["url"],
            json=control_arguments["json"],
            headers=control_arguments["headers"],
            cookies=control_arguments["cookies"],
        )
        response.raise_for_status()

        return {
            "success": True,
            "content": response.text,
            "status_code": response.status_code,
        }
    except Exception as e:
        print(f"[Get请求] {e}")
        return {"success": False}


# 对pyautogui的简单封装
def mouse_action(control_arguments: dict):
    pyautogui.FAILSAFE = False
    pyautogui.moveTo(
        int(control_arguments["x"]),
        int(control_arguments["y"]),
        duration=0,
    )
    print(
        "[鼠标移动]位置", control_arguments["x"], ",", control_arguments["y"], "已移动"
    )


def click_action():
    pyautogui.click()
    return {"success": True}


def double_click_action():
    pyautogui.doubleClick()
    return {"success": True}


def write_action(control_arguments: dict):
    pyautogui.write(control_arguments["content"])
    return {"success": True}


def press_action(control_arguments: dict):
    pyautogui.press(control_arguments["key"])
    return {"success": True}


def terminal_action(control_arguments: dict):
    run_command = control_arguments["command"]
    print("[执行命令]", run_command)
    thread = threading.Thread(target=run_command_silently, args=(run_command,))
    thread.daemon = False
    thread.start()
    return {"success": True}


def return_terminal_action(control_arguments: dict):
    run_command = control_arguments["command"]
    print("[执行命令]", run_command)
    result = subprocess.run(run_command, shell=True, capture_output=True, text=True)
    return {"success": True, "content": result.stdout.strip()}
