# Python 根Python 根据文件名新建文件夹并移动到文件夹里面据文件名新建文件夹并移动到文件夹里面
import os
import shutil
 
 
def main():
    path = r"/home/xiaomeng/software/gvclass/vMAG"
    newPath = r"/home/xiaomeng/software/gvclass/v/%s"
    index = 1;
    for (root, dirs, files) in os.walk(path):
        for filename in files:
            # G:\刘安坚果云\001app\102\安果照片生成视频.jpg
            singleFile = os.path.join(root, filename)
            # ('安果文本阅读器', '.jpg')
            res = os.path.splitext(filename)
            # G:\刘安坚果云\001app\102免费图片PS处理
            newFileDirs = newPath % (str(index) + res[0]);
            # 文件不存在则新建文件
            if not os.path.exists(newFileDirs):
                os.mkdir(newFileDirs)
            # 将当前文件移动到新建的文件夹里面
            shutil.move(singleFile, newFileDirs + "//" + filename)
            index += 1
 
    pass
 
 
if __name__ == '__main__':
    main()
