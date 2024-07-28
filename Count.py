#!/usr/bin/env python
import  csv
import  argparse
from  collections  import  defaultdict

def  process_csv(input_file,  output_file):
      #  使用defaultdict来存储累加的数据，键为第一列的值，值为一个列表，列表中存储后续列的累加值
      data_sum  =  defaultdict(list)

      #  读取CSV文件
      with  open(input_file,  'r',  newline='',  encoding='utf-8')  as  csvfile:
          reader  =  csv.reader(csvfile)
          headers  =  next(reader)    #  获取表头

          for  row  in  reader:
              key  =  row[0]    #  第一列作为键
              #  累加后续列的值
              for  i  in  range(1,  len(row)):
                  #  确保数据可以转换为浮点数，如果不是数字则跳过
                  try:
                      value  =  float(row[i])
                      data_sum[key].append(value)
                  except  ValueError:
                      continue

      #  写入结果到输出文件
      with  open(output_file,  'w',  newline='',  encoding='utf-8')  as  csvfile:
          writer  =  csv.writer(csvfile)
          writer.writerow(headers)    #  写入表头

          for  key,  values  in  data_sum.items():
              #  写入第一列的键和后续列的累加值
              row  =  [key]  +  values
              writer.writerow(row)

def  main():
      parser  =  argparse.ArgumentParser(description='Sum  columns  for  each  unique  value  in  the  first  column  of  a  CSV  file.')
      parser.add_argument('-i',  '--input_file',  type=str,  required=True,  help='Input  CSV  file  path')
      parser.add_argument('-o',  '--output_file',  type=str,  required=True,  help='Output  CSV  file  path')
      args  =  parser.parse_args()

      process_csv(args.input_file,  args.output_file)

if  __name__  ==  '__main__':
      main()
