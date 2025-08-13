"""
字符串处理工具模块
"""

import json
import re
from typing import Any


def fix_json_string(json_str: str) -> str:
    """修复常见的JSON格式问题"""
    if not isinstance(json_str, str):
        return json_str
    
    # 移除可能的markdown代码块标记
    json_str = json_str.strip()
    if json_str.startswith("```json"):
        json_str = json_str[7:]
    if json_str.startswith("```"):
        json_str = json_str[3:]
    if json_str.endswith("```"):
        json_str = json_str[:-3]
    
    json_str = json_str.strip()
    
    # 尝试修复常见的JSON问题
    # 修复单引号为双引号
    json_str = re.sub(r"'([^']*)':", r'"\1":', json_str)
    json_str = re.sub(r": '([^']*)'", r': "\1"', json_str)
    
    # 移除多余的逗号
    json_str = re.sub(r',\s*}', '}', json_str)
    json_str = re.sub(r',\s*]', ']', json_str)
    
    return json_str


def safe_json_loads(json_str: str) -> Any:
    """安全的JSON解析"""
    try:
        return json.loads(json_str)
    except json.JSONDecodeError:
        try:
            fixed_str = fix_json_string(json_str)
            return json.loads(fixed_str)
        except json.JSONDecodeError as e:
            print(f"JSON解析失败: {e}")
            return None


def normalize_particle_name(name: str) -> str:
    """标准化粒子名称"""
    if not name:
        return name
    
    # 移除多余的空格
    name = re.sub(r'\s+', ' ', name.strip())
    
    # 统一特殊符号
    replacements = {
        '−': '-',  # 统一负号
        '–': '-',  # 统一连字符
        '—': '-',  # 统一破折号
    }
    
    for old, new in replacements.items():
        name = name.replace(old, new)
    
    return name