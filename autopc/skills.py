import os
from typing import Dict, Any, List
from markdown import Markdown


class SkillsManager:
    """技能管理器,负责加载和管理Skills"""

    def __init__(self, base_dir: str):
        self.base_dir = base_dir
        self.skills: Dict[str, Any] = {}

    def get_skills_info(self) -> Dict[str, Any]:
        """
        加载skills目录下所有技能信息
        :return: 技能字典
        """
        try:
            skills_dir = os.path.join(self.base_dir, "skills")
            entries = os.listdir(skills_dir)
            for skill_entries in entries:
                skill_dir = os.path.join(skills_dir, skill_entries)
                md_dir = os.path.join(skill_dir, "SKILL.md")
                try:
                    with open(md_dir, "r", encoding="utf-8") as skill_md:
                        md = Markdown(extensions=["meta"])
                        html_output = md.convert(skill_md.read())
                        meta: Dict[str, List[str]] = getattr(md, "Meta", {})
                        meta["dir"] = [skill_dir]
                        self.skills[skill_entries] = meta
                except Exception as e:
                    print(f"[Skills] 读取Skill {skill_entries} 失败: ", e)
            print(f"[Skills] 共加载 {len(self.skills)} 个 Skills: ", self.skills)
            return self.skills
        except Exception as e:
            print("[Skills] 读取全部Skills失败: ", e)
            return self.skills

    def read_skill_md(self, name: str) -> Dict[str, Any]:
        """
        读取指定Skill的SKILL.md内容
        :param name: Skill文件夹名称
        :return: 读取结果
        """
        try:
            skill_meta = self.skills[name]
            skill_md_dir = os.path.join(skill_meta["dir"][0], "SKILL.md")
            with open(skill_md_dir, "r", encoding="utf-8") as skill_md:
                print("[Skills读取] 已成功读取SkillMd")
                return {"success": True, "content": skill_md.read()}
        except Exception as e:
            print("[Skills读取] ", e)
            return {"success": False, "content": f"遇到了错误: {e}"}
