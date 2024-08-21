import csv
import argparse

# 读取TSV文件并获取关键词对应的contig_id
def read_tsv(tsv_file, keyword):
    with open(tsv_file, 'r') as file:
        reader = csv.DictReader(file, delimiter='\t')
        contig_ids = [row['contig_id'] for row in reader if keyword in row['checkv_quality']]
    return contig_ids

# 从FASTA文件中提取序列
def extract_sequences_from_fasta(fasta_file, contig_ids):
    sequences = {}
    current_id = None
    with open(fasta_file, 'r') as file:
        for line in file:
            if line.startswith('>'):  # FASTA格式的序列ID行
                current_id = line.strip().split('>')[1]
            elif current_id in contig_ids:  # 仅提取需要的序列
                sequences[current_id] = sequences.get(current_id, '') + line.strip()
    return sequences

# 将提取的序列写入新的FASTA文件
def write_sequences_to_fasta(sequences, output_file):
    with open(output_file, 'w') as file:
        for contig_id, sequence in sequences.items():
            file.write(f">{contig_id}\n{sequence}\n")

# 主函数
def main(tsv_file, fasta_file, keyword, output_file):
    contig_ids = read_tsv(tsv_file, keyword)
    sequences = extract_sequences_from_fasta(fasta_file, contig_ids)
    write_sequences_to_fasta(sequences, output_file)

# 设置命令行参数
def parse_args():
    parser = argparse.ArgumentParser(description='Extract sequences from a FASTA file based on a keyword in the "checkv_quality" column of a TSV file and output them to a new FASTA file.')
    parser.add_argument('-t', '--tsv', type=str, required=True, help='Path to the TSV file.')
    parser.add_argument('-f', '--fasta', type=str, required=True, help='Path to the FASTA file.')
    parser.add_argument('-k', '--keyword', type=str, required=True, help='Keyword to search for in the "checkv_quality" column of the TSV file.')
    parser.add_argument('-o', '--output', type=str, required=True, help='Path to the output FASTA file.')
    return parser.parse_args()

# 运行脚本
if __name__ == "__main__":
    args = parse_args()
    main(args.tsv, args.fasta, args.keyword, args.output)
