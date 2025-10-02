"""
粒子变体数据合并器
合并新旧拼写变体数据并按mcid绝对值排序
"""

import json, sys
from typing import Dict, List, Any
from pathlib import Path
here = Path(__file__).parent.resolve()

try:
    from ParSV import __version__
except ImportError:
    sys.path.append(str(here.parent.parent))
    from ParSV import __version__

class ParticleDataMerger:
    def __init__(self):
        pass
    
    def load_json(self, file_path: str) -> List[Dict]:
        """加载JSON文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"文件未找到: {file_path}")
            return []
        except json.JSONDecodeError as e:
            print(f"JSON解析错误 {file_path}: {e}")
            return []
    
    def save_json(self, file_path: str, data: List[Dict]) -> bool:
        """保存JSON文件"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"保存失败 {file_path}: {e}")
            return False
    
    def _is_duplicate_value(self, value: str, item_data: Dict) -> bool:
        """检查值是否在其他字段中已存在"""
        main_fields = ['name', 'programmatic_name', 'latex_name', 
                      'evtgen_name', 'html_name', 'unicode_name']
        
        for field in main_fields:
            if item_data.get(field) == value:
                return True
        
        # 检查aliases和typo列表
        for field in ['aliases', 'typo']:
            if field in item_data and isinstance(item_data[field], list):
                if value in item_data[field]:
                    return True
        
        return False
    
    def _merge_lists(self, old_list: List[str], new_list: List[str], 
                    item_data: Dict) -> List[str]:
        """合并两个列表，去重并过滤重复值"""
        merged = list(old_list) if old_list else []
        
        for item in (new_list or []):
            if item not in merged and not self._is_duplicate_value(item, item_data):
                merged.append(item)
        
        return sorted(merged, key=lambda x: (len(x), x))
    
    def merge_particle_data(self, old_item: Dict, new_item: Dict) -> Dict:
        """合并单个粒子的数据"""
        merged_item = old_item.copy()
        
        # 更新基础字段（优先使用新数据）
        name_fields = ['name', 'programmatic_name', 'latex_name', 
                      'evtgen_name', 'html_name', 'unicode_name']
        
        for field in name_fields:
            if new_item.get(field) and not old_item.get(field):
                merged_item[field] = new_item[field]
        
        # 合并aliases和typo列表
        merged_item['aliases'] = self._merge_lists(
            old_item.get('aliases', []), 
            new_item.get('aliases', []), 
            merged_item
        )
        
        merged_item['typo'] = self._merge_lists(
            old_item.get('typo', []), 
            new_item.get('typo', []), 
            merged_item
        )
        
        return merged_item
    
    def merge_datasets(self, old_data: List[Dict], new_data: List[Dict]) -> List[Dict]:
        """合并两个数据集"""
        # 建立mcid到数据项的映射
        old_map = {item['mcid']: item for item in old_data if 'mcid' in item}
        new_map = {item['mcid']: item for item in new_data if 'mcid' in item}
        
        # 合并数据
        merged_map = {}
        
        # 处理旧数据
        for mcid, item in old_map.items():
            if mcid in new_map:
                # 存在新数据，进行合并
                merged_map[mcid] = self.merge_particle_data(item, new_map[mcid])
            else:
                # 只有旧数据
                merged_map[mcid] = item
        
        # 添加只在新数据中存在的项
        for mcid, item in new_map.items():
            if mcid not in old_map:
                merged_map[mcid] = item
        
        # 转换为列表并按绝对值排序
        result = list(merged_map.values())
        return sorted(result, key=lambda x: abs(x.get('mcid', 0)))
    
    def merge_files(self, old_file: str, new_file: str, output_file: str) -> bool:
        """Merge two JSON files"""
        print(f"Loading old data: {old_file}")
        old_data = self.load_json(old_file)
      
        print(f"Loading new data: {new_file}")
        new_data = self.load_json(new_file)
      
        print(f"Merging data...")
        merged_data = self.merge_datasets(old_data, new_data)
      
        print(f"Saving merged result: {output_file}")
        success = self.save_json(output_file, merged_data)
      
        if success:
            print(f"Merge completed! Total {len(merged_data)} records")
            print(f"Old data: {len(old_data)} records, New data: {len(new_data)} records")
      
        return success
    
    def validate_data(self, data: List[Dict]) -> Dict[str, Any]:
        """验证数据质量"""
        stats = {
            'total_count': len(data),
            'valid_mcid_count': 0,
            'missing_name_count': 0,
            'empty_aliases_count': 0,
            'empty_typo_count': 0,
            'duplicate_mcids': []
        }
        
        seen_mcids = set()
        for item in data:
            mcid = item.get('mcid')
            if mcid is not None:
                stats['valid_mcid_count'] += 1
                if mcid in seen_mcids:
                    stats['duplicate_mcids'].append(mcid)
                seen_mcids.add(mcid)
            
            if not item.get('name'):
                stats['missing_name_count'] += 1
            
            if not item.get('aliases'):
                stats['empty_aliases_count'] += 1
            
            if not item.get('typo'):
                stats['empty_typo_count'] += 1
        
        return stats


if __name__ == "__main__":
    merger = ParticleDataMerger()
    
    # 合并示例
    old_file = f"{here}/particle_variants.json"
    new_file = f"{here}/new_variants.json"
    output_file = f"{here}/merged_variants.json"

    if merger.merge_files(old_file, new_file, output_file):
        # 验证结果
        merged_data = merger.load_json(output_file)
        stats = merger.validate_data(merged_data)
        
        print("\n数据质量统计:")
        for key, value in stats.items():
            print(f"  {key}: {value}")