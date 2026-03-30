import sys
import os
from pathlib import Path
import importlib.util


class PluginsManager:
    """插件管理器"""

    def __init__(self, autopc):
        self.root = Path.cwd()
        print(self.root)
        self.plugins_dir = self.root / "plugins"
        sys.path.insert(0, str(self.root))
        self.autopc = autopc

    def load_plugins(self):
        """加载所有插件"""
        print("[插件管理] 加载插件中...")
        self.plugins_dir.mkdir(exist_ok=True)

        for file in os.listdir(self.plugins_dir):
            print(file)
            if not file.endswith(".py"):
                continue
            if file.startswith("_"):
                continue

            plugin_path = self.plugins_dir / file

            spec = importlib.util.spec_from_file_location(
                f"plugin.{file[:-3]}", plugin_path
            )

            if spec is None or spec.loader is None:
                print(f"[插件管理] 插件 {file} 加载失败：无效模块")
                continue

            plugin = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(plugin)

            print(f"[插件管理] 加载插件成功: {file}")
        from autopc.api.event import register_all_commands

        register_all_commands(self.autopc)
