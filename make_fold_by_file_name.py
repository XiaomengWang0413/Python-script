# Python 根据文件名新建文件夹并移动到文件夹里面据文件名新建文件夹并移动到文件夹里面
import os
import shutil
 
 
def main():
    path = r"/home/xiaomeng/software/gvclass/vMAG"
    newPath = r"/home/xiaomeng/software/gvclass/v/%s"
    index = 1;
    for (root, dirs, files) in os.walk(path):
        for filename in files:
            singleFile = os.path.join(root, filename)
            res = os.path.splitext(filename)
            newFileDirs = newPath % (str(index) + res[0]);
            if not os.path.exists(newFileDirs):
                os.mkdir(newFileDirs)
            shutil.move(singleFile, newFileDirs + "//" + filename)
            index += 1
 
    pass
 
 
if __name__ == '__main__':
    main()
