"""
Particle Spelling Variants - Main Program
Integrates particle variant generation and data merging functionality
"""

import argparse
import os
import sys
from typing import List, Optional

from generator import ParticleVariantGenerator, get_standard_mcids
from data_merger import ParticleDataMerger


def main():
    parser = argparse.ArgumentParser(description="Particle spelling variants generator")
    parser.add_argument('--mode', choices=['generate', 'merge', 'both'], 
                       default='both', help='Operation mode')
    parser.add_argument('--mcids', nargs='+', type=int, 
                       help='Specify mcid list (uses standard list by default)')
    parser.add_argument('--input', nargs='+', help='Input file paths (merge mode)')
    parser.add_argument('--new-data', help='New data file path (merge mode)')
    parser.add_argument('--output', default='particle_variants_final.json',
                       help='Output file path')
    parser.add_argument('--temp-file', default='temp_generated.json',
                       help='Temporary generated file path')
    
    args = parser.parse_args()
    
    if args.mode in ['generate', 'both']:
        print("=" * 50)
        print("Starting particle variant data generation...")
        
        # 获取MCID列表
        mcid_list = args.mcids if args.mcids else get_standard_mcids()
        print(f"Will process {len(mcid_list)} particles")
        
        # 生成数据
        generator = ParticleVariantGenerator()
        results = generator.batch_generate(mcid_list)
        
        # 保存临时文件
        temp_output = args.temp_file if args.mode == 'both' else args.output
        with open(temp_output, "w", encoding="utf-8") as f:
            import json
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        print(f"Generation complete! Saved to {temp_output}")
        
        if args.mode == 'generate':
            return
    
    if args.mode in ['merge', 'both']:
        print("=" * 50)
        print("Starting data merge...")
        
        # 确定输入文件
        if args.mode == 'both':
            old_file = args.input[0] if args.input and len(args.input) > 0 else "particle_variants.json"
            new_file = args.temp_file
        else:
            if not args.input or len(args.input) < 1:
                print("Error: Merge mode requires at least one input file")
                return
            old_file = args.input[0]
            new_file = args.new_data if args.new_data else (args.input[1] if len(args.input) > 1 else None)
            
            if not new_file:
                print("Error: Merge mode requires two input files or use --new-data parameter")
                return
        
        # 检查文件存在
        for file_path in [old_file, new_file]:
            if not os.path.exists(file_path):
                print(f"Error: File does not exist {file_path}")
                return
        
        # 执行合并
        merger = ParticleDataMerger()
        success = merger.merge_files(old_file, new_file, args.output)
        
        if success:
            # 验证结果
            merged_data = merger.load_json(args.output)
            stats = merger.validate_data(merged_data)
            
            print("\n" + "=" * 30)
            print("Data Quality Statistics:")
            print(f"  Total records: {stats['total_count']}")
            print(f"  Valid MCIDs: {stats['valid_mcid_count']}")
            print(f"  Missing names: {stats['missing_name_count']}")
            print(f"  Empty aliases: {stats['empty_aliases_count']}")
            print(f"  Empty typos: {stats['empty_typo_count']}")
            
            if stats['duplicate_mcids']:
                print(f"  Duplicate MCIDs: {stats['duplicate_mcids']}")
        
        # 清理临时文件
        if args.mode == 'both' and os.path.exists(args.temp_file):
            os.remove(args.temp_file)
            print(f"Cleaned temporary file: {args.temp_file}")
    
    print("=" * 50)
    print("Processing complete!")


if __name__ == "__main__":
    main()