import os
import csv
import glob
from pathlib import Path

def rename_fastq_files(csv_path, input_dir):
    # 读取CSV映射表
    name_map = {}
    with open(csv_path, 'r') as f:
        reader = csv.reader(f)
        next(reader)  # 跳过标题行
        for row in reader:
            if len(row) >= 2:
                original, new_name = row[0].strip(), row[1].strip()
                name_map[original] = new_name

    # 创建日志文件
    log = []
    success_count = 0
    fail_count = 0

    # 遍历所有fastq.gz文件
    for file_path in glob.glob(os.path.join(input_dir, "*.fastq.gz")):
        # 解析文件名
        filename = Path(file_path).name
        parts = filename.split(".R")
        if len(parts) < 2:
            log.append(f"跳过无法解析的文件: {filename}")
            continue
            
        original_prefix = parts[0]
        suffix = ".R" + parts[1]  # 保留.R1/.R2和扩展名

        # 检查映射关系
        if original_prefix not in name_map:
            log.append(f"没有映射关系: {filename}")
            fail_count += 1
            continue

        new_prefix = name_map[original_prefix]
        new_filename = f"{new_prefix}{suffix}"
        new_path = os.path.join(input_dir, new_filename)

        # 检查文件冲突
        if os.path.exists(new_path):
            log.append(f"文件已存在: {new_filename}")
            fail_count += 1
            continue

        # 执行重命名
        try:
            os.rename(file_path, new_path)
            log.append(f"成功: {filename} -> {new_filename}")
            success_count += 1
        except Exception as e:
            log.append(f"重命名失败: {filename} - {str(e)}")
            fail_count += 1

    # 写入日志文件
    with open("rename_log.txt", "w") as f:
        f.write("\n".join(log))
    
    return success_count, fail_count

if __name__ == "__main__":
    # 配置参数
    csv_path = "name.csv"    # CSV文件路径
    input_dir = "rename"          # 输入目录
    
    print("="*40)
    print("FASTQ文件重命名工具")
    print("="*40)
    print(f"映射文件: {csv_path}")
    print(f"输入目录: {input_dir}\n")
    
    success, fails = rename_fastq_files(csv_path, input_dir)
    
    print("\n执行结果:")
    print(f"成功重命名: {success} 个文件")
    print(f"失败数量: {fails} 个文件")
    print(f"详细日志请查看: {os.path.abspath('rename_log.txt')}")
