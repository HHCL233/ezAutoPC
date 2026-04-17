from flask import Flask, render_template, request, send_from_directory, jsonify
from autopc import AutoPC
from autopc.config import ConfigManager
from flask_socketio import SocketIO, emit, disconnect
import os
import time
import json
from flask_cors import CORS
import sys
from pathlib import Path
from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity,
    decode_token,
    set_access_cookies,
    set_refresh_cookies,
)
from datetime import timedelta
import bcrypt

# 自动添加包
ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT))

# 路径配置
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
VUE_DIST_DIR = os.path.join(BASE_DIR, "dashboard/dist")

# Flask 实例化
app = Flask(
    __name__,
    template_folder=VUE_DIST_DIR,
    static_folder=VUE_DIST_DIR,
)
CORS(
    app,
    supports_credentials=True,
)
app.config["SECRET_KEY"] = (
    "da9d19b64bf07bd70c00d2509b0c2bdb86b579ece51c0499b595b01f08a81d3b"
)
app.config["JWT_SECRET_KEY"] = (
    "da9d19b64bf07bd70c00d2509b0c2bdb86b579ece51c0499b595b01f08a81d3b"
)
app.config["JWT_TOKEN_LOCATION"] = ["cookies"]
app.config["JWT_ACCESS_COOKIE_NAME"] = "access_token"
app.config["JWT_REFRESH_COOKIE_NAME"] = "refresh_token"

app.config["JWT_COOKIE_SECURE"] = False
app.config["JWT_COOKIE_SAMESITE"] = "Lax"
app.config["JWT_COOKIE_HTTPONLY"] = True
app.config["JWT_COOKIE_PATH"] = "/"
app.config["JWT_COOKIE_CSRF_PROTECT"] = False

# SocketIO 初始化
socketio = SocketIO(
    app,
    async_mode="threading",
    cors_credentials=True,
    cors_allowed_origins="*",
)

# JWT 初始化
jwt = JWTManager(app)

# 业务类实例化
autopc = AutoPC()


# 生成密码哈希
def generatePasswordHash(password: str) -> str:
    # 字符串转字节
    passwordBytes = password.encode("utf-8")
    # 生成随机盐
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(passwordBytes, salt)
    # 返回字符串格式
    return hashed.decode("utf-8")


# 验证密码
def verifyPasswordHash(password: str, hashedPassword: str) -> bool:
    passwordBytes = password.encode("utf-8")
    hashedBytes = hashedPassword.encode("utf-8")
    return bcrypt.checkpw(passwordBytes, hashedBytes)


# 路由:首页
@app.route("/")
def home():
    return render_template("index.html")


# 路由:静态资源
@app.route("/assets/<path:filename>")
def serveaAssets(filename):
    assetsDir = os.path.join(VUE_DIST_DIR, "assets")
    # 确保目录存在
    if not os.path.exists(assetsDir):
        return {"success": False, "message": "assets目录不存在"}, 404
    return send_from_directory(assetsDir, filename)


@app.route("/set-cookie")
def set_cookie():
    resp = app.make_response("Cookie已设置")
    resp.set_cookie(
        "username",
        "test_user",
        max_age=3600,
        domain=request.host,
        path="/",
        secure=False,
        samesite="Lax",
    )
    return resp


# 接口:登陆
@app.route("/api/login", methods=["POST"])
def login():
    # 接收前端传的账号密码
    username = request.json.get("username")
    password = request.json.get("password")
    configPassword = ""

    # 简单验证
    homeDir = os.path.expanduser("~/.ezautopc/config.json")
    with open(homeDir, encoding="utf-8", mode="r") as config:
        jsonConfig = json.loads(config.read())
        configPassword = jsonConfig["webui"]["password"]

    if username == "admin" and configPassword == "":
        print("[后端] 检测到密码为空,创建")
        configPassword = generatePasswordHash(password)
        jsonConfig["webui"]["password"] = configPassword
        putInfo = upPutConfig(jsonConfig)
        if putInfo["success"]:
            print("[后端] 已推送该密码")
        else:
            print("[后端] 推送密码失败")
            return {"msg": f"{putInfo['message']}"}, 500

    # 这里应该使用密码哈希
    if username != "admin" or not verifyPasswordHash(password, configPassword):
        return {"msg": "账号或密码错误"}, 401

    # 生成令牌
    # 这里应该存储在配置中
    accessToken = create_access_token(
        identity=username, expires_delta=timedelta(days=1)
    )
    refreshToken = create_refresh_token(identity=username)

    resp = jsonify(
        {"msg": "登录成功", "access_token": accessToken, "refresh_token": refreshToken}
    )
    set_access_cookies(resp, accessToken)
    set_refresh_cookies(resp, refreshToken)
    return resp, 200


# 接口:刷新AccesToken
@app.route("/api/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    currentUser = get_jwt_identity()

    # 生成新的 Access Token
    newAccessToken = create_access_token(identity=currentUser)

    return {"access_token": newAccessToken}, 200


# 接口:写入配置
@app.route("/api/config", methods=["PUT"])
@jwt_required()
def putConfig():
    jsonConfig = request.json
    return upPutConfig(jsonConfig)


def upPutConfig(jsonConfig):
    try:
        configStr = json.dumps(jsonConfig, indent=4, ensure_ascii=False)
        home_dir = os.path.expanduser("~/.ezautopc/config.json")
        with open(home_dir, encoding="utf-8", mode="w") as config:
            config.write(configStr)
            config.close()
            autopc.read_config()
            return {
                "success": True,
                "message": "配置文件写入成功",
            }
    except Exception as e:
        return {"success": False, "message": f"配置文件写入失败: {e}"}


# 接口:更新配置
@app.route("/api/update-config", methods=["POST"])
@jwt_required()
def updateConfig():
    global autopc
    update_info = ConfigManager.relocate_config(BASE_DIR)
    autopc = AutoPC()
    return update_info


# 接口:获取配置
@app.route("/api/config")
@jwt_required()
def getConfig():
    try:
        homeDir = os.path.expanduser("~/.ezautopc/config.json")
        with open(homeDir, encoding="utf-8", mode="r") as config:
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
    # 从Cookie中获取token
    token = request.cookies.get("access_token")
    if not token:
        print("无token,拒绝连接")
        disconnect()
        return

    try:
        payload = decode_token(token)
        user_id = payload["sub"]

        # 验证成功
        print(f"用户 {user_id} 已连接")
        emit("response", {"msg": "已连接成功"})
    except Exception as e:
        # 验证失败
        print(f"token验证失败: {str(e)}")
        disconnect()


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
    print(f"[WebUI] 检查WebUI路径: {indexHtmlPath}")

    if os.path.exists(indexHtmlPath):
        print("[WebUI] WebUI文件检测成功,启动Web服务...")
        autopc.on_ai_send_message.append(onAISendMessage)
        socketio.run(app, host="0.0.0.0", port=5000, debug=True, use_reloader=False)
    else:
        print("[警告] 未检测到WebUI文件")
        print(f"[警告] 请在目录 {indexHtmlPath} 安装WebUI文件!")
        os._exit(0)
