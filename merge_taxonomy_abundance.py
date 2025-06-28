import os
import pandas as pd
import numpy as np
from pathlib import Path
import re

def parse_gtdb_classification(gtdb_str):
    """解析GTDB分类字符串为不同分类级别"""
    # 定义分类级别顺序
    levels = ['Domain', 'Phylum', 'Class', 'Order', 'Family', 'Genus', 'Species']
    
    # 分割分类字符串
    parts = gtdb_str.split(';') if pd.notna(gtdb_str) else []
    
    # 创建字典存储结果
    result = {level: np.nan for level in levels}
    
    # 解析每个部分
    for part in parts:
        if '__' in part:
            prefix, name = part.split('__', 1)
            level = {
                'd': 'Domain',
                'p': 'Phylum',
                'c': 'Class',
                'o': 'Order',
                'f': 'Family',
                'g': 'Genus',
                's': 'Species'
            }.get(prefix.lower(), None)
            
            if level and level in levels:
                result[level] = name
    
    return pd.Series(result)

def process_taxonomy(taxonomy_file):
    """处理分类文件"""
    print(f"正在处理分类文件: {taxonomy_file}")
    
    # 读取分类文件
    tax_df = pd.read_csv(taxonomy_file, header=None, names=['featureID', 'GTDB_classification'])
    
    # 解析分类字符串
    tax_df = pd.concat([
        tax_df,
        tax_df['GTDB_classification'].apply(parse_gtdb_classification)
    ], axis=1)
    
    # 清理数据
    tax_df.replace('', np.nan, inplace=True)
    
    print(f"分类文件处理完成，共 {len(tax_df)} 个特征")
    return tax_df

def process_abundance_files(tax_df, abundance_dir):
    """处理所有丰度文件"""
    print(f"\n正在处理丰度文件目录: {abundance_dir}")
    
    # 获取所有CSV文件
    abundance_files = list(Path(abundance_dir).glob('*.csv'))
    
    if not abundance_files:
        print("错误: 未找到任何CSV文件")
        return pd.DataFrame()
    
    print(f"找到 {len(abundance_files)} 个丰度文件")
    
    all_results = []
    
    for file_path in abundance_files:
        print(f"处理文件: {file_path.name}")
        
        try:
            # 读取丰度文件
            abd_df = pd.read_csv(file_path)
            
            # 检查featureID列是否存在
            if 'featureID' not in abd_df.columns:
                # 尝试识别第一列
                first_col = abd_df.columns[0]
                if 'feature' in first_col.lower() or 'id' in first_col.lower():
                    abd_df = abd_df.rename(columns={first_col: 'featureID'})
                else:
                    print(f"  警告: 无法识别featureID列，使用第一列作为featureID")
                    abd_df = abd_df.rename(columns={abd_df.columns[0]: 'featureID'})
            
            # 合并分类信息
            merged = abd_df.merge(tax_df, on='featureID', how='left')
            
            # 添加文件标识
            merged['SourceFile'] = file_path.name
            
            all_results.append(merged)
            
        except Exception as e:
            print(f"  错误处理文件 {file_path.name}: {str(e)}")
    
    if not all_results:
        print("错误: 所有文件处理失败")
        return pd.DataFrame()
    
    # 合并所有结果
    combined = pd.concat(all_results, ignore_index=True)
    
    print(f"合并完成，共 {len(combined)} 条记录")
    return combined

def summarize_by_phylum(combined_df):
    """按门分类汇总数据"""
    print("\n按门分类汇总数据...")
    
    # 识别数值列（样本列）
    non_numeric_cols = ['featureID', 'GTDB_classification', 'Domain', 'Phylum', 
                         'Class', 'Order', 'Family', 'Genus', 'Species', 'SourceFile']
    
    sample_cols = [col for col in combined_df.columns 
                  if col not in non_numeric_cols
                  and pd.api.types.is_numeric_dtype(combined_df[col])]
    
    if not sample_cols:
        print("警告: 未找到样本列")
        return combined_df
    
    # 填充缺失的Phylum值
    combined_df['Phylum'] = combined_df['Phylum'].fillna('Unclassified')
    
    # 按Phylum分组汇总
    grouped = combined_df.groupby(['Phylum', 'SourceFile'])[sample_cols].sum().reset_index()
    
    # 计算平均丰度
    grouped['AverageAbundance'] = grouped[sample_cols].mean(axis=1)
    
    # 按平均丰度排序
    grouped = grouped.sort_values('AverageAbundance', ascending=False)
    
    print(f"汇总完成，共 {len(grouped)} 个门分类")
    return grouped

def main():
    # 配置路径 - 根据实际情况修改
    taxonomy_file = 'path/to/your/taxonomy.csv'  # 分类文件路径
    abundance_dir = 'path/to/your/abundance_files'  # 丰度文件目录
    output_file = 'combined_results.csv'  # 输出文件名
    summary_file = 'phylum_summary.csv'  # 汇总文件名
    
    # 1. 处理分类文件
    tax_df = process_taxonomy(taxonomy_file)
    
    if tax_df.empty:
        print("错误: 分类文件处理失败")
        return
    
    # 2. 处理丰度文件
    combined_df = process_abundance_files(tax_df, abundance_dir)
    
    if combined_df.empty:
        print("错误: 丰度文件处理失败")
        return
    
    # 3. 保存完整合并结果
    combined_df.to_csv(output_file, index=False)
    print(f"\n完整结果已保存到: {output_file}")
    
    # 4. 按门分类汇总
    summary_df = summarize_by_phylum(combined_df)
    summary_df.to_csv(summary_file, index=False)
    print(f"门级汇总已保存到: {summary_file}")
    
    # 5. 显示前5个门的平均丰度
    print("\n丰度最高的5个门:")
    print(summary_df[['Phylum', 'AverageAbundance']].head(5).to_string(index=False))

if __name__ == "__main__":
    main()
