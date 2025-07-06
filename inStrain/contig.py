import os
import argparse
from Bio import SeqIO

def generate_contig_gene_map(contig_file, prodigal_file, output_file):
    """
    生成contig到基因的映射文件
    
    参数:
    contig_file: contig FASTA格式文件路径
    prodigal_file: Prodigal预测结果文件路径
    output_file: 输出文件路径
    """
    # 步骤1：读取contig文件，提取所有contig名称
    contig_names = set()
    with open(contig_file, "r") as f:
        for record in SeqIO.parse(f, "fasta"):
            # 提取contig名称（不含描述部分）
            contig_id = record.id.split()[0]  # 只取第一个空格前的部分
            contig_names.add(contig_id)
    
    # 步骤2：解析Prodigal文件，提取基因与contig的对应关系
    gene_map = []
    valid_genes = 0
    
    with open(prodigal_file, "r") as f:
        current_contig = None
        
        for line in f:
            # 处理序列行
            if line.startswith(">"):
                # 格式：>NODE_1_length_1000_cov_2.5_1 # 2 # 100 # 1 # ...
                parts = line[1:].split("_")
                
                # 尝试提取contig名称（原始格式中数字前缀）
                # 重建contig名称直到第一个下划线前的部分
                contig_candidate = "_".join(parts[:-1])
                
                # 检查这是否是一个有效的contig名称
                if contig_candidate in contig_names:
                    current_contig = contig_candidate
                    gene_name = line[1:].split()[0]
                    gene_map.append((current_contig, gene_name))
                    valid_genes += 1
                else:
                    # 如果未找到匹配，尝试另一种提取方法
                    gene_name = line[1:].split()[0]
                    contig_base = gene_name.rsplit("_", 1)[0]
                    if contig_base in contig_names:
                        current_contig = contig_base
                        gene_map.append((current_contig, gene_name))
                        valid_genes += 1
                    else:
                        current_contig = None
            
            # 处理其他行（可选）
            elif current_contig:
                # 如果是序列行，可以跳过或处理
                pass
    
    # 步骤3：将结果写入输出文件
    with open(output_file, "w") as out_f:
        for contig, gene in gene_map:
            out_f.write(f"{contig}\t{gene}\n")
    
    # 打印统计信息
    print(f"处理完成! 共发现 {valid_genes} 个基因")
    print(f"结果已保存至: {output_file}")

if __name__ == "__main__":
    # 设置命令行参数解析
    parser = argparse.ArgumentParser(description='生成contig到基因的映射文件')
    parser.add_argument('-c', '--contig', required=True, help='输入contig文件(FASTA格式)')
    parser.add_argument('-p', '--prodigal', required=True, help='Prodigal基因预测文件')
    parser.add_argument('-o', '--output', default='contig_gene_map.txt', help='输出文件路径')
    
    args = parser.parse_args()
    
    # 检查文件是否存在
    if not os.path.exists(args.contig):
        raise FileNotFoundError(f"Contig文件不存在: {args.contig}")
    if not os.path.exists(args.prodigal):
        raise FileNotFoundError(f"Prodigal文件不存在: {args.prodigal}")
    
    # 执行主函数
    generate_contig_gene_map(args.contig, args.prodigal, args.output)
