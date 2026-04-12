import time

_command_registry = []
_ai_send_message_callback_registry = []


def registr_command(cmd_name):
    """注册命令"""

    def decorator(func):
        _command_registry.append((cmd_name, func))
        return func

    return decorator


def registr_ai_send_message_callback():
    """注册消息列表改变时回调"""

    def decorator(func):
        _ai_send_message_callback_registry.append(func)

    return decorator


def register_all_plugins_controls(autopc):
    for cmd_name, func in _command_registry:
        autopc.commands[cmd_name] = func
    for func in _ai_send_message_callback_registry:

        def wrapped_callback(f=func):
            msg = autopc.messages
            f(msg)

        autopc.on_ai_send_message.append(wrapped_callback)
    _command_registry.clear()
    _ai_send_message_callback_registry.clear()
