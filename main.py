from flask import Flask, render_template, request, send_from_directory
from autopc import AutoPC
from flask_socketio import SocketIO, emit
import os
import time
import json
from flask_cors import CORS

# 路径配置
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
VUE_DIST_DIR = os.path.join(BASE_DIR, "dashboard/dist")

# Flask 实例化
app = Flask(
    __name__,
    template_folder=VUE_DIST_DIR,
    static_folder=VUE_DIST_DIR,
)
CORS(app)
app.config["SECRET_KEY"] = "key-1234567890"

# SocketIO 初始化
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="threading")

# 业务类实例化
autopc = AutoPC()


# 路由:首页
@app.route("/")
def home():
    return render_template("index.html")


# 路由:静态资源
@app.route("/assets/<path:filename>")
def serveaAssets(filename):
    assetsDir = os.path.join(VUE_DIST_DIR, "assets")
    # 确保目录存在，避免报错
    if not os.path.exists(assetsDir):
        return {"success": False, "message": "assets目录不存在"}, 404
    return send_from_directory(assetsDir, filename)


# 接口:发送消息给AI
@app.route("/api/sendMessages", methods=["POST"])
def sendMessagesToAI():
    payload = request.get_json(force=False, silent=True)

    if payload is None:
        return {"success": False, "message": "无效的 JSON 负载"}, 400

    autopc.send_ai_message(payload.get("content"))

    return {"success": True, "message": "AI请求完成"}


# 接口:写入配置
@app.route("/api/config", methods=["PUT"])
def putConfig():
    try:
        jsonConfig = request.json
        configStr = json.dumps(jsonConfig, indent=4, ensure_ascii=False)
        with open("config.json", encoding="utf-8", mode="w") as config:
            config.write(configStr)
            config.close()
            autopc.read_config()
            return {
                "success": True,
                "message": "配置文件写入成功",
            }
    except Exception as e:
        return {"success": False, "message": f"配置文件写入失败: {e}"}


# 接口:获取配置
@app.route("/api/config")
def getConfig():
    try:
        with open("config.json", encoding="utf-8", mode="r") as config:
            jsonConfig = json.loads(config.read())
            return {
                "success": True,
                "message": "配置文件获取成功",
                "config": jsonConfig,
            }
    except Exception as e:
        return {"success": False, "message": f"配置文件获取失败: {e}"}


def serializeMessages(messages):
    serialized = []
    for msg in messages:
        try:
            if hasattr(msg, "model_dump"):
                serialized.append(msg.model_dump())
            elif isinstance(msg, dict):
                serialized.append(msg)
            elif hasattr(msg, "__dict__"):
                serialized.append(msg.__dict__)
            else:
                serialized.append(str(msg))
        except Exception:
            serialized.append({"role": "assistant", "content": str(msg)})
    return serialized


def onAISendMessage():
    emit(
        "response",
        {
            "msg": serializeMessages(autopc.full_messages),
            "timestamp": time.time(),
            "type": "getAllMessages",
            "token": (autopc.get_messages_token())["token"],
        },
        broadcast=True,
    )


# SocketIO:客户端连接
@socketio.on("connect")
def handleConnect():
    print("新的客户端已连接")
    emit("response", {"msg": "已连接成功"})


# SocketIO:处理消息
@socketio.on("message")
def handleMessage(data):
    print(f"收到客户端的消息:{data}")
    try:
        jsonData = json.loads(data)
    except json.JSONDecodeError:
        emit(
            "response",
            {"msg": "无效的 JSON 格式", "type": "error", "timestamp": time.time()},
        )
        return

    # 处理获取所有消息请求
    if jsonData["type"] == "getAllMessages":
        onAISendMessage()
    elif jsonData["type"] == "allowTool":
        autopc.allow_tool(jsonData["msg"])
    elif jsonData["type"] == "notAllowedTool":
        autopc.not_allowed_tool(jsonData["msg"])
    elif jsonData["type"] == "getAllTools":
        emit(
            "response",
            {
                "msg": json.dumps(
                    {
                        "allTools": list(autopc.tool_map.keys()),
                        "allowTools": autopc.allow_tools,
                    }
                ),
                "type": "getAllTools",
                "timestamp": time.time(),
            },
        )
    # 处理发送消息给AI请求
    elif jsonData["type"] == "sendMessagesToAI":
        emit(
            "response",
            {"type": "disabledSend", "timestamp": time.time()},
        )
        content = jsonData.get("content")
        if not content:
            emit(
                "response",
                {"msg": "缺少 content 参数", "type": "error", "timestamp": time.time()},
            )
            return

        autopc.send_ai_message(content)
        emit(
            "response",
            {
                "msg": "AI请求完成",
                "timestamp": time.time(),
                "type": "enableSend",
            },
        )


# SocketIO:客户端断开
@socketio.on("disconnect")
def handleDisconnect():
    print("客户端已断开连接")


# 主函数
if __name__ == "__main__":
    indexHtmlPath = os.path.join(VUE_DIST_DIR, "index.html")
    print(f"检查index.html路径: {indexHtmlPath}")

    if os.path.exists(indexHtmlPath):
        print("WebUI文件检测成功,启动Web服务...")
        autopc.on_ai_send_message.append(onAISendMessage)
        socketio.run(app, host="0.0.0.0", port=5000, debug=True)
    else:
        print("[警告] 未检测到WebUI文件,启动终端模式")
        autopc.main_loop()
