autopc = None


def register_autopc_class(func):
    global autopc
    autopc = func


def send_user_text_message(user_name: str, content: str):
    if autopc is None:
        return
    autopc.send_ai_message(content, user_name)
