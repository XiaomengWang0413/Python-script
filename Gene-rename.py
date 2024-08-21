import os

def rename_genes_in_file(file_path, output_dir):
    # 获取文件名，不包含路径和扩展名
    base_name = os.path.basename(file_path).replace('.fa', '')
    
    with open(file_path, 'r') as f:
        lines = f.readlines()
    
    output_file_path = os.path.join(output_dir, os.path.basename(file_path))
    
    with open(output_file_path, 'w') as f:
        gene_counter = 1
        for line in lines:
            # 如果是基因名称行
            if line.startswith('>'):
                new_gene_name = f">{base_name}-{gene_counter}\n"
                f.write(new_gene_name)
                gene_counter += 1
            else:
                f.write(line)

def rename_genes_in_directory(input_dir, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    for file_name in os.listdir(input_dir):
        if file_name.endswith('.fa'):
            file_path = os.path.join(input_dir, file_name)
            rename_genes_in_file(file_path, output_dir)

# 使用示例
input_directory = '/home/xiaomeng/IOM/SCS/MAG/RAW'
output_directory = '/home/xiaomeng/IOM/SCS/MAG/rename'
rename_genes_in_directory(input_directory, output_directory)
