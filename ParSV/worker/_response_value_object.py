


from dataclasses import dataclass, field
from pydantic import BaseModel, field_validator
from typing import Dict, Union, Literal, List, Optional, Any


class BranchingFractionVO(BaseModel):
    """分支比数据模型"""
    description: str
    value: float
    error_positive: Optional[float] = None
    error_negative: Optional[float] = None
    display_value_text: Optional[str] = None
    units: Optional[str] = None
    is_limit: Optional[bool] = None
    confidence_level: Optional[float] = None
    decay_products: Optional[List[str]] = None


def convert_pdg_branching_fraction(pdg_bf):
    """将 PdgBranchingFraction 对象转换为可序列化的字典"""
    try:
        decay_products = []
        if hasattr(pdg_bf, 'decay_products') and pdg_bf.decay_products:
            for product in pdg_bf.decay_products:
                if hasattr(product, 'item'):
                    # 提取粒子名称，去掉 PdgItem 包装
                    item_str = str(product.item)
                    if item_str.startswith('PdgItem("') and item_str.endswith('")'):
                        particle_name = item_str[9:-2]  # 提取引号内的内容
                        decay_products.append(particle_name)
                    else:
                        decay_products.append(item_str)
                else:
                    decay_products.append(str(product))

        return BranchingFractionVO(
            description=getattr(pdg_bf, 'description', ''),
            value=getattr(pdg_bf, 'value', 0.0),
            error_positive=getattr(pdg_bf, 'error_positive', None),
            error_negative=getattr(pdg_bf, 'error_negative', None),
            display_value_text=getattr(pdg_bf, 'display_value_text', None),
            units=getattr(pdg_bf, 'units', None),
            is_limit=getattr(pdg_bf, 'is_limit', None),
            confidence_level=getattr(pdg_bf, 'confidence_level', None),
            decay_products=decay_products if decay_products else None
        ).model_dump()
    except Exception as e:
        # 如果转换失败，返回一个基本的表示
        return {
            "description": str(pdg_bf) if pdg_bf else "Unknown",
            "value": 0.0,
            "error": f"Conversion failed: {str(e)}"
        }
        
def convert_generator_to_list(gen):
    """将生成器转换为列表"""
    if gen is None:
        return None
    if hasattr(gen, '__iter__') and not isinstance(gen, list):
        try:
            return list(gen)
        except Exception:
            return None
    return gen if isinstance(gen, list) else None

def convert_branching_fractions_list(bf_list):
    """转换分支比列表，处理生成器或列表输入"""
    if bf_list is None:
        return None

    bf_list = convert_generator_to_list(bf_list)

    if not bf_list:
        return None

    converted_list = []
    for bf in bf_list:
        converted = convert_pdg_branching_fraction(bf)
        converted_list.append(converted)

    return converted_list

class ParticleVO(BaseModel):
    """基于 Particle 类的响应数据模型"""

    # 基本标识信息
    name: str
    mcid: int = 0
    # id: int = 0

    # 不同格式的名称
    programmatic_name: Optional[str] = None
    latex_name: Optional[str] = None
    evtgen_name: Optional[str] = None
    html_name: Optional[str] = None
    unicode_name: Optional[str] = None

    # 层次结构
    mother: Optional[str] = None
    children: List[str] = []

    # 物理属性
    charge: Optional[float] = None
    mass: Optional[float] = None
    mass_err: Optional[float] = None
    lifetime: Optional[float] = None
    lifetime_err: Optional[float] = None
    width: Optional[float] = None
    width_err: Optional[float] = None

    # 量子数
    quantum_C: Optional[Union[int, str]] = None
    quantum_G: Optional[Union[int, str]] = None
    quantum_I: Optional[Union[int, str]] = None
    quantum_J: Optional[Union[int, str]] = None
    quantum_P: Optional[Union[int, str]] = None

    # 粒子类型标识
    is_baryon: Optional[bool] = None
    is_boson: Optional[bool] = None
    is_lepton: Optional[bool] = None
    is_meson: Optional[bool] = None
    is_quark: Optional[bool] = None
    
    # 衰变分支比
    branching_fractions: Optional[List[Dict]] = None
    exclusive_branching_fractions: Optional[List[Dict]] = None
    inclusive_branching_fractions: Optional[List[Dict]] = None
    # branching_fractions: Optional[List[BranchingFractionVO]] = None
    # exclusive_branching_fractions: Optional[List[BranchingFractionVO]] = None
    # inclusive_branching_fractions: Optional[List[BranchingFractionVO]] = None

    # 其他标识
    has_lifetime_entry: Optional[bool] = None
    has_mass_entry: Optional[bool] = None
    has_width_entry: Optional[bool] = None
    
    
    # @field_validator('branching_fractions', mode='before')
    @field_validator('branching_fractions', 'exclusive_branching_fractions', 'inclusive_branching_fractions', mode='before')
    @classmethod
    def validate_branching_fractions(cls, v):
        """验证并转换分支比字段"""
        if v is None:
            return None
        if isinstance(v, list):
            return convert_branching_fractions_list(v)
        return None
    
    
    
    
    
    