import sys
import os
from pathlib import Path
import importlib.util
import subprocess


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

        for item in os.listdir(self.plugins_dir):
            plugin_folder = self.plugins_dir / item
            if not plugin_folder.is_dir():
                continue
            main_file = plugin_folder / "main.py"
            requirements_file = plugin_folder / "requirements.txt"
            if not main_file.exists():
                continue

            # 自动安装依赖
            if requirements_file.exists():
                # 依赖安装
                print(f"[插件管理] 检测到 {item} 存在依赖文件")
                if item in self.autopc.config["no_detect_plugin"]:
                    print(f"[插件管理] {item} 在排除列表内,不安装依赖")
                    return
                is_install_requirements = input(
                    f"[插件管理] 是否在当前环境安装 {item} 的依赖? (y/N)"
                )
                if is_install_requirements.lower() != "y":
                    print(f"[插件管理] 拒绝安装 {item} 的依赖")
                    print(f"[插件管理] {item} 停止导入")
                    continue
                print(f"[插件管理] 安装 {item} 依赖中...")
                install_cmd = [
                    sys.executable,
                    "-m",
                    "pip",
                    "install",
                    "-r",
                    str(requirements_file),
                ]
                try:
                    subprocess.check_call(install_cmd)
                    print(f"[插件管理] {item} 的依赖安装成功")
                except subprocess.CalledProcessError as e:
                    print(f"[插件管理] {item} 的依赖安装失败: {e}")
                    print(f"[插件管理] {item} 停止导入")
                    continue

            spec = importlib.util.spec_from_file_location(f"plugin.{item}", main_file)
            if spec is None or spec.loader is None:
                print(f"[插件管理] 插件 {item} 加载失败：无效模块")
                continue

            plugin = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(plugin)
            print(f"[插件管理] 加载插件成功: {item}")
        from autopc.api.event import register_all_commands

        register_all_commands(self.autopc)
