import os
import json
from typing import Dict, Any
import sys


class ConfigManager:
    """配置管理器,负责读取和管理config.json"""

    @staticmethod
    def read_config(base_dir: str) -> Dict[str, Any]:
        """
        读取配置文件
        :param base_dir: 项目根目录
        :return: 配置字典
        """
        try:
            config_path = os.path.join(base_dir, "config.json")
            if os.path.exists(config_path):
                print("[读取配置] config 文件存在,开始读取文件内容...")
                with open(config_path, "r", encoding="utf-8") as f:
                    config_content = f.read()
                    config_json = json.loads(config_content)
                    config_index = config_json["autopc"]["config_index"]
                    # 获取autopc配置
                    if config_index >= len(config_json["autopc"]["config_list"]):
                        autopc_config = config_json["autopc"]["config_list"][
                            len(config_json["autopc"]["config_list"]) - 1
                        ]
                    else:
                        autopc_config = config_json["autopc"]["config_list"][
                            config_index
                        ]
                    return autopc_config
            else:
                print("[读取配置] config 文件不存在")
                print("正在退出程序...")
                sys.exit()
        except Exception as e:
            print("[读取配置] 读取失败: ", e)
            print("正在退出程序...")
            sys.exit()

    @staticmethod
    def read_full_config(base_dir: str) -> Dict[str, Any]:
        """
        读取完整配置文件
        :param base_dir: 项目根目录
        :return: 完整配置字典
        """
        try:
            config_path = os.path.join(base_dir, "config.json")
            if os.path.exists(config_path):
                with open(config_path, "r", encoding="utf-8") as f:
                    return json.loads(f.read())
            else:
                return {}
        except Exception as e:
            print("[读取配置] 读取完整配置失败: ", e)
            return {}
