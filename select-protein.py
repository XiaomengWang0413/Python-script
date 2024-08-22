import argparse
from Bio import SeqIO

def extract_sequences(fna_file, faa_file, output_file):
    # 读取fna文件中的基因名称
    gene_names = set()
    for record in SeqIO.parse(fna_file, "fasta"):
        gene_name = record.id
        gene_names.add(gene_name)
    
    # 从faa文件中提取对应的序列
    extracted_sequences = []
    for record in SeqIO.parse(faa_file, "fasta"):
        if record.id in gene_names:
            extracted_sequences.append(record)
    
    # 将提取的序列写入输出文件
    SeqIO.write(extracted_sequences, output_file, "fasta")
    print(f"提取了 {len(extracted_sequences)} 条序列，保存到 {output_file}")

def main():
    parser = argparse.ArgumentParser(description="根据fna文件提取faa文件中的序列")
    parser.add_argument("-fna", required=True, help="输入的fna文件路径")
    parser.add_argument("-faa", required=True, help="输入的faa文件路径")
    parser.add_argument("-out", required=True, help="输出的faa文件路径")
    parser.add_argument("-h", "--help", action="help", help="显示帮助信息")
    
    args = parser.parse_args()
    
    extract_sequences(args.fna, args.faa, args.out)

if __name__ == "__main__":
    main()
