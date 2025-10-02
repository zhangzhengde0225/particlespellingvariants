"""
粒子拼写变体生成器
根据mcid生成粒子名称的拼写变体数据
"""

import json
import os
import sys
from typing import Dict, List, Optional

import pdg
from hepai import HepAI
from particle import Particle as ExternalParticle

from pathlib import Path
here = Path(__file__).parent.resolve()

try:
    from ParSV import __version__
except ImportError:
    sys.path.append(str(here.parent.parent))
    from ParSV import __version__
    
from ParSV.utils import safe_json_loads, normalize_particle_name


class ParticleVariantGenerator:
    def __init__(self, data_file: str = "particle_variants.json"):
        self.data_file = data_file
        self._file_cache = None
        
    def _load_cache(self):
        """加载本地数据缓存"""
        if self._file_cache is None:
            try:
                with open(self.data_file, "r", encoding="utf-8") as f:
                    self._file_cache = json.load(f)
            except FileNotFoundError:
                self._file_cache = []
        return self._file_cache
    
    def _call_llm_api(self, system_message: str, prompt: str, 
                     model_name: str = "openai/gpt-4o-mini",
                     api_key: Optional[str] = None,
                     api_url: str = "https://aiapi.ihep.ac.cn/apiv2") -> str:
        """调用LLM API生成拼写变体"""
        client = HepAI(
            api_key=api_key or os.environ.get("HEPAI_API_KEY"),
            base_url=api_url
        )
        
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": prompt}
            ],
            stream=False
        )
        
        content = response.choices[0].message.content
        
        # 清理JSON格式
        if content.startswith("```json\n"):
            content = content[len("```json\n"):]
        if content.endswith("\n```"):
            content = content[:-len("\n```")]
            
        return content
    
    def _get_particle_info(self, mcid: int) -> Dict:
        """获取粒子基本信息"""
        # 从PDG API获取信息
        try:
            api = pdg.connect()
            particle = api.get_particle_by_mcid(mcid)
            
            # 从Particle包获取额外信息
            particle_list = ExternalParticle.findall(lambda p: p.pdgid == mcid)
            particle_ex = particle_list[0] if particle_list else None
            
            return {
                "name": normalize_particle_name(getattr(particle_ex, 'name', str(mcid))),
                "programmatic_name": getattr(particle_ex, 'programmatic_name', None),
                "latex_name": getattr(particle_ex, 'latex_name', None),
                "evtgen_name": getattr(particle_ex, 'evtgen_name', None),
                "html_name": getattr(particle_ex, 'html_name', None),
                "unicode_name": getattr(particle_ex, 'unicode_name', None),
            }
        except Exception:
            return {"name": str(mcid)}
    
    def _generate_basic_variants(self, name: str) -> List[str]:
        """生成基础拼写变体"""
        if not name:
            return []
            
        variants = set()
        
        # 符号转换
        symbol_map = {
            'Λ': 'Lambda', 'Δ': 'Delta', 
            'Σ': 'Sigma', 'Ξ': 'Xi'
        }
        for greek, latin in symbol_map.items():
            if greek in name:
                variants.add(name.replace(greek, latin))
            if latin in name:
                variants.add(name.replace(latin, greek))
        
        # 分隔符处理
        for sep in ['-', '_', '']:
            variants.add(name.replace('_', sep))
        
        # LaTeX清理
        if '$' in name:
            variants.add(name.replace('$', ''))
            
        return list(variants)
    
    def generate_variants(self, mcid: int) -> Dict:
        """为指定mcid生成完整的拼写变体数据"""
        # 获取粒子基本信息
        particle_info = self._get_particle_info(mcid)
        
        # 构建数据模板
        data_template = {
            "name": particle_info.get("name"),
            "mcid": mcid,
            "programmatic_name": particle_info.get("programmatic_name"),
            "latex_name": particle_info.get("latex_name"),
            "evtgen_name": particle_info.get("evtgen_name"),
            "html_name": particle_info.get("html_name"),
            "unicode_name": particle_info.get("unicode_name"),
            "aliases": [],
            "typo": []
        }
        
        # 生成基础变体
        name_fields = ['name', 'programmatic_name', 'latex_name', 
                      'evtgen_name', 'html_name', 'unicode_name']
        base_variants = set()
        for field in name_fields:
            if data_template[field]:
                base_variants.update(self._generate_basic_variants(data_template[field]))
        
        # 使用LLM增强生成
        if data_template["name"]:
            llm_prompt = f"""
                基于以下粒子信息生成拼写变体：
                {json.dumps(data_template, indent=2)}

                生成要求：
                1. aliases: 包含不同符号体系、格式变化、编码格式等变体
                2. typo: 包含常见拼写错误、符号位置错误等
                3. 补全空字段的合适值
                4. 每个列表2-7个条目，避免重复
                5. 输出可解析的JSON格式

                输出格式：
                {{
                    "programmatic_name": "值或null",
                    "latex_name": "值或null", 
                    "evtgen_name": "值或null",
                    "html_name": "值或null",
                    "unicode_name": "值或null",
                    "aliases": ["变体1", "变体2"],
                    "typo": ["错误1", "错误2"]
                }}
            """
            
            try:
                response = self._call_llm_api("", llm_prompt)
                llm_data = safe_json_loads(response)
                
                if llm_data:
                    # 更新数据
                    for field in ['programmatic_name', 'latex_name', 'evtgen_name', 
                                 'html_name', 'unicode_name']:
                        if not data_template[field] and llm_data.get(field):
                            data_template[field] = llm_data[field]
                    
                    data_template["aliases"] = llm_data.get("aliases", [])
                    data_template["typo"] = llm_data.get("typo", [])
                    
                    # 去重处理
                    primary_values = {str(data_template[key]) for key in name_fields 
                                    if data_template[key] is not None}
                    
                    data_template["aliases"] = [a for a in data_template["aliases"] 
                                              if a not in primary_values]
                    data_template["typo"] = [t for t in data_template["typo"] 
                                           if t not in primary_values]
                
            except Exception as e:
                print(f"LLM生成失败: {mcid} - {e}")
        
        return data_template
    
    def batch_generate(self, mcid_list: List[int]) -> List[Dict]:
        """批量生成粒子变体数据"""
        results = []
        for i, mcid in enumerate(mcid_list):
            print(f"处理 {i+1}/{len(mcid_list)}: mcid={mcid}")
            try:
                result = self.generate_variants(mcid)
                results.append(result)
            except Exception as e:
                print(f"生成失败 mcid={mcid}: {e}")
                results.append({
                    "name": str(mcid),
                    "mcid": mcid,
                    "error": str(e)
                })
        return results


def get_standard_mcids() -> List[int]:
    """获取标准粒子MCID列表，按绝对值排序"""
    mcids = []
    
    # Quarks (夸克)
    quarks = [1, 2, 3, 4, 5, 6, 7, 8]  # d, u, s, c, b, t, b', t'

    # Leptons (轻子)
    leptons = [11, 12, 13, 14, 15, 16, 17, 18]  # e-, νe, µ-, νµ, τ-, ντ, τ'-, ντ'
    
    # Gauge and Higgs Bosons (规范玻色子和希格斯玻色子)
    bosons = [21, 22, 23, 24, 25, 32, 33, 34, 35, 36, 37, 38, 39, 40]  # g, γ, Z0, W+, h0/H0, Z'/Z0, Z''/Z0, W'/W+, H0/H0, A0/H0, H+, H++, G (graviton), a0/H0

    # Special Particles (特殊粒子)
    special_particles = [41, 42, 51, 52, 53, 110, 990, 9990]  # R0, LQc, DM (S=0), DM (S=1/2), DM (S=1), reggeon, pomeron, odderon

    # Diquarks (双夸克)
    diquarks = [1103, 2101, 2103, 2203, 3101, 3103, 3201, 3203, 3303, 4101, 4103, 4201, 4203, 4301, 4303, 4403, 5101, 5103, 5201, 5203, 5301, 5303, 5401, 5403, 5503]

    # SUSY Particles (超对称粒子)
    susy_particles = [1000001, 1000002, 1000003, 1000004, 1000005, 1000006, 1000011, 1000012, 1000013, 1000014, 1000015, 1000016, 2000001, 2000002, 2000003, 2000004, 2000005, 2000006, 2000011, 2000013, 2000015, 1000021, 1000022, 1000023, 1000024, 1000025, 1000035, 1000037, 1000039]

    # Light I=1 Mesons (轻I=1介子)
    light_i1_mesons = [111, 211, 9000111, 9000211, 100111, 100211, 10111, 10211, 9010111, 9010211, 113, 213, 10113, 10213, 20113, 20213, 9000113, 9000213, 100113, 100213, 9010113, 9010213, 9020113, 9020213, 30113, 30213, 9030113, 9030213, 9040113, 9040213, 115, 215, 10115, 10215, 9000115, 9000215, 9010115, 9010215, 117, 217, 9000117, 9000217, 9010117, 9010217, 119, 219]

    # Light I=0 Mesons (轻I=0介子)
    light_i0_mesons = [221, 331, 9000221, 9010221, 100221, 10221, 9020221, 100331, 9030221, 10331, 9040221, 9050221, 9060221, 9070221, 9080221, 223, 333, 10223, 20223, 10333, 20333, 1000223, 9000223, 9010223, 30223, 100333, 225, 9000225, 335, 9010225, 9020225, 10225, 9030225, 10335, 9040225, 9050225, 9060225, 9070225, 9080225, 9090225, 227, 337, 229, 9000229, 9010229]

    # Strange Mesons (奇异介子)
    strange_mesons = [130, 310, 311, 321, 9000311, 9000321, 10311, 10321, 100311, 100321, 9010311, 9010321, 9020311, 9020321, 313, 323, 10313, 10323, 20313, 20323, 100313, 100323, 9000313, 9000323, 30313, 30323, 315, 325, 9000315, 9000325, 10315, 10325, 20315, 20325, 9010315, 9010325, 9020315, 9020325, 317, 327, 9010317, 9010327, 319, 329, 9000319, 9000329]

    # Charmed Mesons (粲介子)
    charmed_mesons = [411, 421, 10411, 10421, 413, 423, 10413, 10423, 20413, 20423, 415, 425, 431, 10431, 433, 10433, 20433, 435]

    # Bottom Mesons (底介子)
    bottom_mesons = [511, 521, 10511, 10521, 513, 523, 10513, 10523, 20513, 20523, 515, 525, 531, 10531, 533, 10533, 20533, 535, 541, 10541, 543, 10543, 20543, 545]

    # cc Mesons (cc介子)
    cc_mesons = [441, 10441, 100441, 443, 10443, 20443, 100443, 30443, 9000443, 9010443, 9020443, 445, 100445]

    # bb Mesons (bb介子)
    bb_mesons = [551, 10551, 100551, 110551, 200551, 210551, 553, 10553, 20553, 30553, 100553, 110553, 120553, 130553, 200553, 210553, 220553, 300553, 9000553, 9010553, 555, 10555, 20555, 100555, 110555, 120555, 200555, 557, 100557]

    # Light Baryons (轻重子)
    light_baryons = [2212, 2112, 2224, 2214, 2114, 1114]

    # Strange Baryons (奇异重子)
    strange_baryons = [3122, 3222, 3212, 3112, 3224, 3214, 3114, 3322, 3312, 3324, 3314, 3334]

    # Charmed Baryons (粲重子)
    charmed_baryons = [4122, 4222, 4212, 4112, 4224, 4214, 4114, 4232, 4132, 4322, 4312, 4324, 4314, 4332, 4334, 4412, 4422, 4414, 4424, 4432, 4434, 4444]

    # Bottom Baryons (底重子)
    bottom_baryons = [5122, 5112, 5212, 5222, 5114, 5214, 5224, 5132, 5232, 5312, 5322, 5314, 5324, 5332, 5334, 5142, 5242, 5412, 5422, 5414, 5424, 5342, 5432, 5434, 5442, 5444, 5512, 5522, 5514, 5524, 5532, 5534, 5542, 5544, 5554]

    # Pentaquarks (五夸克态)
    pentaquarks = [9221132, 9331122]
    
    all_particles = quarks + leptons + bosons + special_particles + diquarks + susy_particles + \
                   light_i1_mesons + light_i0_mesons + strange_mesons + charmed_mesons + bottom_mesons + \
                   cc_mesons + bb_mesons + light_baryons + strange_baryons + charmed_baryons + bottom_baryons + \
                   pentaquarks
    
    # 包含粒子和反粒子
    for pid in all_particles:
        mcids.extend([pid, -pid])
    
    # 按绝对值排序
    return sorted(set(mcids), key=abs)


if __name__ == "__main__":
    generator = ParticleVariantGenerator()
    mcid_list = get_standard_mcids()
    
    # 生成数据
    results = generator.batch_generate(mcid_list)
    
    # 保存结果
    with open("particle_variants.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"已生成{len(results)}个粒子的变体数据")