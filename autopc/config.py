import os
import json
from typing import Dict, Any
import sys
from autopc.utils import dictionary_update


class ConfigManager:
    """配置管理器,负责读取和管理config.json"""

    @staticmethod
    def read_config(base_dir: str, config_dir: str) -> Dict[str, Any]:
        """
        读取配置文件
        :param base_dir: 项目根目录
        :return: 配置字典
        """
        try:
            config_path = os.path.join(config_dir, "config.json")
            if os.path.exists(config_path):
                print("[读取配置] config 文件存在,开始读取文件内容...")
                ConfigManager.update_config(base_dir)
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
                is_update = input(
                    f"[读取配置] 是否从 {base_dir} 下迁移配置至 {config_dir}?(y/N) "
                )
                if is_update.lower() != "y":
                    print("[读取配置] 正在退出程序...")
                    sys.exit()
                else:
                    config_content = ConfigManager.relocate_config(base_dir)
                    if config_content["success"]:
                        return ConfigManager.read_config(base_dir, config_dir)
                    else:
                        return {"error": True}
        except Exception as e:
            print("[读取配置] 遇到了错误:", e)
            return {"error": True}

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

    @staticmethod
    def relocate_config(base_dir: str):
        """
        将项目配置从根目录迁移至家目录
        :param base_dir: 项目根目录
        :return: 完整配置字典
        """
        home_dir = os.path.expanduser("~/.ezautopc/config.json")
        try:
            originally_config_path = os.path.join(base_dir, "config.json")
            if os.path.exists(originally_config_path):
                with open(originally_config_path, "r", encoding="utf-8") as f:
                    print("[更新配置] 已读取配置")
                    config_content = json.loads(f.read())

                dir_path = os.path.dirname(home_dir)
                os.makedirs(dir_path, exist_ok=True)

                with open(home_dir, "w", encoding="utf-8") as f:
                    print(f"[更新配置] 正在向 {home_dir} 写入配置内容...")
                    f.write(json.dumps(config_content, ensure_ascii=False, indent=4))
                    print(f"[更新配置] {home_dir} 写入完成")
                    return {"success": True, "config": config_content}
            else:
                print("[更新配置] 读取配置失败")
                return {"success": False, "error": "读取配置失败"}
        except Exception as e:
            print("[更新配置] 更新配置失败: ", e)
            return {"success": False, "error": "读取配置失败"}

    @staticmethod
    def update_config(base_dir: str):
        """
        更新配置版本
        :param base_dir: 模板根目录
        :return: 完成状态
        """
        home_dir = os.path.expanduser("~/.ezautopc/config.json")
        try:
            originally_config_path = os.path.join(base_dir, "config.json")
            with open(originally_config_path, "r", encoding="utf-8") as f:
                print("[更新配置] 已读取模板配置")
                template_content = json.loads(f.read())
            with open(home_dir, "r", encoding="utf-8") as f:
                print("[更新配置] 已读取当前配置")
                config_content = json.loads(f.read())

            new_content = dictionary_update(config_content, template_content)
            with open(home_dir, "w", encoding="utf-8") as f:
                print(f"[更新配置] 正在向 {home_dir} 写入配置内容...")
                f.write(json.dumps(new_content, ensure_ascii=False, indent=4))
                print(f"[更新配置] {home_dir} 写入完成")
                return {"success": True, "config": new_content}
        except Exception as e:
            print("[更新配置] 更新配置失败: ", e)
            return {"success": False, "error": "读取配置失败"}
