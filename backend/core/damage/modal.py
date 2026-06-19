from __future__ import annotations
from typing import Any, Dict, List

# charId -> 模态列表 (顺序即展示顺序; 第 0 个为默认):
#   key   稳定标识 (与 branchName 解耦, 入 redis key / 上传 / 请求)
#   name  中文名 (展示 + 命令后缀)
#   match 在 role.get_skill_branch().branchName 里的匹配子串
MODAL_CHARS: Dict[int, List[Dict[str, str]]] = {
    1109: [
        {"key": "frost", "name": "霜渐", "match": "霜渐"},
        {"key": "phantom", "name": "声骸", "match": "声骸"},
    ],
}

# 取不到分支(is_limit / 用户没切模态)时的默认模态; 不指定则用列表第 0 个
_DEFAULT_MODAL: Dict[int, str] = {1109: "phantom"}


def get_role_modal(role: Any) -> str:
    """按 role 当前激活的共鸣模态分支返回 modal key。

    - 非模态角色: ""
    - 模态角色但取不到/匹配不到分支(is_limit 等): fallback 到默认模态
    """
    char_id = role.role.roleId
    options = MODAL_CHARS.get(char_id)
    if not options:
        return ""
    branch = role.get_skill_branch()
    name = getattr(branch, "branchName", "") or ""
    for opt in options:
        if opt["match"] in name:
            return opt["key"]
    return _DEFAULT_MODAL.get(char_id, options[0]["key"])


def get_modal_options(char_id: int) -> List[Dict[str, str]]:
    """该角色的可选模态项 [{key, name}]; 无模态角色返回 []。"""
    return [{"key": o["key"], "name": o["name"]} for o in MODAL_CHARS.get(char_id, [])]


def get_modal_name(char_id: int, key: str) -> str:
    """modal key -> 中文名; 找不到返回 ""。"""
    for o in MODAL_CHARS.get(char_id, []):
        if o["key"] == key:
            return o["name"]
    return ""


def get_modal_key_by_name(char_id: int, name: str) -> str:
    """中文名 (命令后缀) -> modal key; 找不到返回 ""。"""
    for o in MODAL_CHARS.get(char_id, []):
        if o["name"] == name:
            return o["key"]
    return ""
