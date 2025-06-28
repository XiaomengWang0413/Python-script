import pandas as pd
import os
import glob

def process_csv_files(input_folder, output_folder=None):
    """
    处理文件夹中的所有CSV文件，为每个病毒保留最高置信度的记录
    
    参数:
    input_folder (str): 包含CSV文件的输入文件夹路径
    output_folder (str): 可选，处理后的文件保存路径，默认为输入文件夹内的"filtered"子文件夹
    """
    # 设置默认输出路径
    if output_folder is None:
        output_folder = os.path.join(input_folder, "filtered")
    
    # 创建输出文件夹
    os.makedirs(output_folder, exist_ok=True)
    
    # 获取所有CSV文件
    csv_files = glob.glob(os.path.join(input_folder, "*.csv"))
    
    if not csv_files:
        print(f"在 {input_folder} 中未找到CSV文件")
        return
    
    print(f"找到 {len(csv_files)} 个CSV文件，开始处理...")
    
    processed_count = 0
    for file_path in csv_files:
        try:
            # 读取CSV文件
            df = pd.read_csv(file_path)
            
            # 检查必要列是否存在
            if "Virus" not in df.columns or "Confidence score" not in df.columns:
                print(f"跳过文件 {os.path.basename(file_path)}: 缺少必要的列")
                continue
            
            # 保留每个病毒的最高置信度记录
            filtered_df = df.loc[df.groupby("Virus")["Confidence score"].idxmax()]
            
            # 保存结果
            output_path = os.path.join(output_folder, os.path.basename(file_path))
            filtered_df.to_csv(output_path, index=False)
            print(f"已处理: {os.path.basename(file_path)} -> 保留 {len(filtered_df)} 条记录")
            processed_count += 1
            
        except Exception as e:
            print(f"处理 {os.path.basename(file_path)} 时出错: {str(e)}")
    
    print(f"\n处理完成! {processed_count}/{len(csv_files)} 个文件成功处理")
    print(f"结果保存在: {output_folder}")

if __name__ == "__main__":
    # 设置您的输入文件夹路径
    input_directory = "/data/home/xiaomeng/data/genome"
    
    # 可选：设置自定义输出路径
    # output_directory = "/data/home/xiaomeng/data/data"
    
    # 调用处理函数
    process_csv_files(input_directory)
    # 或使用自定义输出路径: process_csv_files(input_directory, output_directory)
