import os
import pandas as pd
import argparse

def rename_files(folder_path, csv_path):
    """
    根据CSV文件批量重命名文件夹中的文件
    
    参数:
    folder_path (str): 包含文件的文件夹路径
    csv_path (str): CSV文件路径，包含原始名称和新名称
    """
    # 读取CSV文件
    try:
        df = pd.read_csv(csv_path, header=None, names=['original', 'new_name'])
        name_map = dict(zip(df['original'], df['new_name']))
    except Exception as e:
        print(f"读取CSV文件出错: {e}")
        return
    
    # 获取文件夹中所有文件
    try:
        files = os.listdir(folder_path)
    except Exception as e:
        print(f"访问文件夹出错: {e}")
        return
    
    # 计数器
    renamed_count = 0
    skipped_count = 0
    
    # 遍历并重命名文件
    for filename in files:
        file_path = os.path.join(folder_path, filename)
        
        # 只处理文件，跳过子文件夹
        if not os.path.isfile(file_path):
            continue
        
        # 提取文件名和扩展名
        basename, extension = os.path.splitext(filename)
        
        # 检查是否在映射表中
        if basename in name_map:
            new_basename = name_map[basename]
            new_filename = f"{new_basename}{extension}"
            new_path = os.path.join(folder_path, new_filename)
            
            # 避免覆盖已存在文件
            if os.path.exists(new_path):
                print(f"警告: 目标文件已存在，跳过重命名 {filename} -> {new_filename}")
                skipped_count += 1
                continue
            
            # 执行重命名
            try:
                os.rename(file_path, new_path)
                print(f"重命名: {filename} -> {new_filename}")
                renamed_count += 1
            except Exception as e:
                print(f"重命名 {filename} 失败: {e}")
                skipped_count += 1
        else:
            skipped_count += 1
    
    # 打印结果摘要
    print("\n操作完成:")
    print(f"成功重命名文件数: {renamed_count}")
    print(f"跳过文件数: {skipped_count}")
    print(f"映射表中未找到的文件: {len(files) - renamed_count - skipped_count}")
    
    # 列出未处理的原始名称
    unprocessed = [name for name in name_map.keys() if name not in [os.path.splitext(f)[0] for f in files]]
    if unprocessed:
        print("\n以下CSV中的名称未在文件夹中找到:")
        for name in unprocessed:
            print(f"  - {name}")

if __name__ == "__main__":
    # 设置命令行参数
    parser = argparse.ArgumentParser(description='根据CSV文件批量重命名文件')
    parser.add_argument('folder', help='包含文件的文件夹路径')
    parser.add_argument('csv', help='CSV文件路径 (格式: 原始名称,新名称)')
    
    args = parser.parse_args()
    
    # 执行重命名
    rename_files(args.folder, args.csv)
