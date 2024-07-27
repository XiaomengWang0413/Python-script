#!/usr/bin/env python
import  pandas  as  pd 
#pip  install  pandas

#  读取CSV文件
df  =  pd.read_csv('data.csv')

#  按第一列分组，并对其他列求和
result  =  df.groupby(df.columns[0]).sum()

#  输出结果
print(result)
#  保存结果到新的CSV文件
result.to_csv('summed_data.csv',  index=False)
