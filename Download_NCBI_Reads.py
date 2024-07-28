#!/usr/bin/env python
import  os
import  csv
import  sys
import  pandas  as  pd
from  Bio  import  Entrez
from  Bio  import  SeqIO

#  设置NCBI邮箱，用于访问权限
Entrez.email  =  'your_email@example.com'

def  download_and_split_fasta(accession_numbers,  output_folder):
      for  acc  in  accession_numbers:
          try:
              #  下载SRA文件
              handle  =  Entrez.efetch(db="sra",  id=acc,  rettype="fastq",  retmode="text")
              out_path  =  os.path.join(output_folder,  f"{acc}.fastq")
              with  open(out_path,  "w")  as  out_file:
                  out_file.write(handle.read())
              handle.close()
             
              #  将fastq文件分为双端序列
              records  =  SeqIO.parse(out_path,  "fastq")
              for  record  in  records:
                  if  record.id.startswith(acc):
                      if  '1'  in  record.id:
                          SeqIO.write(record,  os.path.join(output_folder,  f"{acc}_1.fastq"),  "fastq")
                      elif  '2'  in  record.id:
                          SeqIO.write(record,  os.path.join(output_folder,  f"{acc}_2.fastq"),  "fastq")
          except  Exception  as  e:
              print(f"Error  downloading  {acc}:  {e}")

def  main():
      if  len(sys.argv)  <  3  or  sys.argv[1]  in  ["-h",  "--help"]:
          print("Usage:  python Download_NCBI_Reads.py   -i  accession.number.csv  -o  ./folder")
          sys.exit()
     
      input_file  =  sys.argv[1].split('-i  ')[1]
      output_folder  =  sys.argv[2].split('-o  ')[1]
     
      #  确保输出文件夹存在
      if  not  os.path.exists(output_folder):
          os.makedirs(output_folder)
     
      #  读取CSV文件中的accession  numbers
      df  =  pd.read_csv(input_file)
      accession_numbers  =  df['accession_number'].tolist()
     
      #  下载并分割序列
      download_and_split_fasta(accession_numbers,  output_folder)

if  __name__  ==  "__main__":
      main()
