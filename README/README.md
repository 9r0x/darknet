<!-- pandoc --pdf-engine=xelatex -V CJKmainfont="Songti SC" --highlight-style zenburn -N -V colorlinks -V urlcolor=NavyBlue -V geometry:"top=2cm, bottom=1.5cm, left=2cm, right=2cm" -f markdown-implicit_figures README.md -o README.pdf -->

# [labelImg](https://github.com/tzutalin/labelImg)图片标注

## 安装
1. 拷贝`labelImg.zip`并解压至想要安装的位置
2. 双击`python_install.exe`安装python环境
3. 勾选"Add Python 3.8 to path"的选项

![安装python](./1.png)

4. 点击"Install Now"
5. 双击执行`install.bat`来安装和编译labelImg(有的时候如果卡住就按一下回车, 是windows快速编辑模式的问题)

![编译labelImg](./2.png){height=200}

## 预处理
1. 在`data\predefined_classes.txt`提供预设类别
2. 预设类别不可以删除但可以增加, 因为删除会影响之前的次序

## 使用
1. 双击执行`Run.bat`
2. 点PascalVOC切换成YOLO模式
3. Open Dir打开图片所在文件夹

![标注](./3.png){height=200}

4. 快捷键

| 按键          | 作用            |
| ------------- | :-------------: |
| Ctrl s        | 保存            |
| w             | 新建标注框      |
| d             | 下一张图        |
| a             | 上一张图        |
| ctrl +        | 放大            |
| ctrl -        | 缩小            |
5. 标注完成的图片会生成一个同名的`.txt`后缀的文件
6. 其中第一个数字是类别(从0开始), 后四个为框的坐标

# [Darknet](https://github.com/AlexeyAB/darknet)图像识别
尽管原始作者是pjreddie, 考虑到对windows的兼容性, 使用AlexeyAB的版本

## 安装
首先拷贝darknet\_en.zip并解压至想要安装的位置, cn版操作相同

### Linux
1. 用编辑器打开Makefile
2. `GPU=0, CUDNN=0, OPENCV=0`这三个选项, 如果装了就改成1
3. cd到`darknet_en`下执行`make`
4. 当前目录即是最终文件包, 二进制文件是`./darknet`


### Windows
1. 安装VisualStudio 2015或更新版本
2. 用VS打开`build\darknet\darknet_no_gpu.sln`或者`darknet.sln`(取决于有没有GPU)
3. VS菜单执行`Build>Build darknet`
4. 编译完成, 最终文件包是`build\darknet\x64`, 二进制文件是`.\darknet.exe`或`.\darknet_no_gpu.exe`

## Matpool使用
1. 注册(使用我的二维码可以优惠)

![注册二维码](./qr.png){height=200}

2. 主机市场租用机器, 以小时计费
3. 预先将需要使用的darknet包以及初始weight放到我的网盘

![网盘挂载_1](./mnt1.png){height=100}

![网盘挂载_2](./mnt2.png){height=300}

4. 每当租用机器时, 网盘会挂在到`/mnt`的位置

![网盘挂载_3](./mnt3.png){height=300}

## 训练(GPU)
1. 租用2080Ti, 镜像选择"python3.7_多框架"

![租用机器_1](./machine1.png){height=200}

![租用机器_2](./machine2.png){width=50%}

2. 机器启动后在浏览器打开jupyterlab的链接

![租用机器_3](./machine3.png){height=50}

3. 编译darknet(GPU和CUDNN需要改成1)

![训练_1](./train1.png){height=100}

4. 将图片和标注数据按类别放在`data/obj`下, 没有被标注的图像将被忽略

![数据](./data.png){height=200}

4. 修改`data/obj.data`中的`classes`数

![训练_2](./train2.png){height=100}

5. `data/obj.names`应当与labelImg中的`data\predefined_classes.txt`相同
6. 修改`data/obj.cfg`
   * `max_batches`为`classes`*2000
   * `steps`为80%和90%的`max_batches`
   
   ![训练_3](./train3.png){height=50}

   * 寻找3个`[yolo]`组块修改`classes`数
   
   ![训练_4](./train4.png){height=50}

   * **仅在yolo上面的[convolutional]组块**修改`filters`为`(classes + 5)*3`
   
   ![训练_5](./train5.png){height=200}

   * 举例: classes=3, max_batches=6000, steps=4800,5400, filters=24
7. cd到`data`下, 运行`python helper.py`
8. 拷贝初始weight `init_weight`到`darknet_en`下
9. cd到`darknet_en`下, 运行`./darknet detector train data/obj.data data/obj.cfg init_weight -map`即开始训练
10. 每1000batch, 最新batch以及结果最好的batch的权重会放在`backup`下
   
![训练_6](./train6.png){height=200}

11. 1000batch后每100batch进行mAP计算, 显示准确率accuracy
12. 最优accuracy一般可以达到60%以上(3000+batch)

## 预测
1. 安装对应系统的darknet
2. 中文预测使用`darknet_cn`, 需cd到data/labels下删除旧label并运行`python make_label.py`(其中需手动安装ImageMagick的convert命令并自己设定字体路径 所以建议在Linux上完成). 生成labels之后拷贝到windows上亦可以使用
2. cd到`darknet_en`下, 运行`./darknet detector test data/obj.data data/obj.cfg best.weights -thresh 0.2 -ext_output data/obj/Ganlanche/Ganlanche_56.jpg`

![测试_1](./test1.jpg){height=200}

![测试_2](./test2.png){height=200}

3. 命令格式为 `./darknet detector test [obj.data的位置] [obj.cfg的位置] [weights的位置] -thresh [阈值] -ext_output [预测图片的位置]`
4. `-ext_output`可以用来输出每个框的位置
5. 预测多张图片 `./darknet detector test [obj.data的位置] [obj.cfg的位置] [weights的位置] -thresh [阈值] -ext_output -dont_show -out result.json < input.txt` 其中`input.txt`是包括一行一个图片路径的文本文件

![测试_3](./test3.jpg){height=200}

## 注意
1. windows的软件包在 `build\darknet\x64`, 所以上文涉及到data/等的相对路径指的是在这个目
录下相对的data而不是darknet下的data
2. `darknet_cn/data/data.names`为Linux/Mac支持的UTF-8编码, 而`darknet_cn/build/darknet/x64/data.names`为支持windows采用了GB2312编码

# [Flask](https://flask.palletsprojects.com/en/1.1.x/quickstart/)服务器端

## 安装python及flask(视情况使用sudo)

```
apt update && apt install -y python3.8 python3-pip
pip install flask
```

## 部署
1. 拷贝darknet和weight并修改MakeFile中的`LIBSO=1`(其他参数按需修改)
2. 用`make`命令编译
3. 确认当前文件夹下有libdark.so或libdarknet.so
4. 拷贝app.py至darknet下
5. 修改app.py 11行.so文件的绝对路径
6. 运行
```
export FLASK_APP=app.py
flask run --host=0.0.0.0
```
