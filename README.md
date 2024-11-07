# Python-script
Count.py: 第一列相同的项，后面每一列相加

如果你想了解如何使用请运行：python count.py -h


checkv.py 
python checkv.py -h :checkv结果筛选
~~~
python /home/xiaomeng/scripts/python/checkv.py -h


python /home/xiaomeng/scripts/python/checkv.py -t Checkv/quality_summary.tsv -f EIO.fasta -k Complete -o Complete.fasta
python /home/xiaomeng/scripts/python/checkv.py -t Checkv/quality_summary.tsv -f EIO.fasta -k High-quality -o High.fasta
python /home/xiaomeng/scripts/python/checkv.py -t Checkv/quality_summary.tsv -f EIO.fasta -k Medium-quality -o Medium.fasta


Gene-rename.py:python Gene-rename.py
说明：

    rename_genes_in_file(file_path, output_dir) 函数：
        读取文件内容。
        修改基因名称为文件名加上连续的数字。
        将修改后的内容写入输出文件。

    rename_genes_in_directory(input_dir, output_dir) 函数：
        遍历输入目录中的所有 .fa 文件。
        对每个文件调用 rename_genes_in_file 进行基因名称修改。
        如果输出目录不存在，则创建它。

使用方法：

    将 input_directory 和 output_directory 修改为你的输入文件路径和输出文件路径。
    运行脚本。

这个脚本会遍历指定目录下的所有 .fa 文件，并将每个基因名称修改为文件名（去掉 .fa 后缀）加上连续的数字，最后将修改后的文件保存到输出目录中。



select-protein.py：根据非冗余基因集的基因名，提取对用的蛋白序列。

~~~
python select-protein.py -fna path/to/your/input.fna -faa path/to/your/input.faa -out path/to/your/output.faa
~~~







