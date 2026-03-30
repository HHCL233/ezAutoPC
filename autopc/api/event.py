import time
from autopc import AutoPC

_command_registry = []


def registr_command(cmd_name):
    """装饰器：注册命令"""

    def decorator(func):
        _command_registry.append((cmd_name, func))
        return func

    return decorator


def register_all_commands(autopc):
    for cmd_name, func in _command_registry:
        autopc.commands[cmd_name] = func
    _command_registry.clear()
