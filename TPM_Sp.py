import pandas as pd

# 读取数据
# 丰度文件（假设基因列为索引）
abundance = pd.read_csv("TPM_merged.csv", index_col=0)

# 分组文件（包含两列：sample_id, group）
group_df = pd.read_csv("group.csv")

# 数据预处理 ------------------------------------------------------------
# 将分组信息转换为字典便于查询
group_dict = group_df.set_index('sample_id')['group'].to_dict()

# 验证样本匹配性
missing_samples = set(abundance.columns) - set(group_dict.keys())
if missing_samples:
    print(f"警告：以下样本缺少分组信息将被忽略：{missing_samples}")

# 按分组拆分数据 --------------------------------------------------------
for group_name, group_data in group_df.groupby('group'):
    # 获取当前组的样本列表
    samples_in_group = group_data['sample_id'].tolist()
    
    # 筛选存在的样本（避免KeyError）
    valid_samples = [s for s in samples_in_group if s in abundance.columns]
    
    # 提取当前组的数据（保留基因列，筛选样本列）
    group_abundance = abundance[valid_samples]
    
    # 保存到CSV（文件名添加组名）
    output_filename = f"abundance_{group_name.replace(' ', '_')}.csv"
    group_abundance.to_csv(output_filename)
    
    print(f"已生成分组文件：{output_filename}（包含{len(valid_samples)}个样本）")

# 验证输出 ------------------------------------------------------------
print("\n处理完成！各组样本统计：")
print(group_df['group'].value_counts())
