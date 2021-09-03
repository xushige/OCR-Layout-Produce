# ocr-版面构造

## 修改配置文件
* 配置文件路径：ocr-dataproduce/utils/config.py
* 版面构造需要各种语料，以字典形式分为中英文，修改对应目录即可

## 数据构造
运行构造数据主函数文件路径：python doc_gen_main.py 【PATTERN 从cv，nlp，ppt中选择模式与用途】

## 转换数据格式
构造的数据集格式的label是labelme格式的，在训练时要转换成voc或者coco格式的形式才可训练。

* MotherFolder/ImageSets/Segmentation/train.txt：存放训练集中每个图片的文件名，文件名不包括后缀名（如训练集图片10000.jpg存为10000）
* MotherFolder/ImageSets/Segmentation/test.txt:存放增强训练集中每个图片的文件名，文件名不包括后缀名（如增强集图片10000.jpg存为10000）
* MotherFolder/ImageSets/Segmentation/test.txt:存放测试集中每个图片的文件名，文件名不包括后缀名（如测试集图片10000.jpg存为10000）
* MotherFolder/JPEGImages：存放训练图片，jpg格式
* MotherFolder/SegmentationClassPNG：存放mask
* MotherFolder/SegmentationClassVisualization:图片和mask结合的效果，用于检查mask和图片是否对应
* MotherFolder/cls_label.json: 存放每张图片的分类标签（该文件非必要，当需要处理分类时需要）

利用ocr-dataproduce/labelme/examples/semantic_segmentation/labelme2voc.py将labelme格式label转成voc格式标签。
首先在ocr-dataproduce/labelme/examples/semantic_segmentation/labels.txt中写入所有的类别，然后运行如下命令：
```
python labelme2voc.py --input_dirs 训练集路径1 训练集路径2 训练集路径3 --test_dir 测试集路径 --labels labels.txt --noviz （不需要可视化） --booststrap （开启booststrap）
```
其中注意点
1. noviz表示不生成SegmentationClassVisualization文件夹，确认无误后可关闭加速。
2. booststrap打开后会对figure和table类进行booststrap，同时保存booststrap后的jpg原图和png掩码图。
用于实际训练例子：
```
python labelme/examples/semantic_segmentation/labelme2voc.py 
--input_dirs file-train
--test_dir file-test
--labels labels.txt 
--output_dir voc-dataset
--booststrap
```
当需要对预测类别进行改变时可修改ocr-dataproduce/labelme/examples/semantic_segmentation/labelme2voc.py中的类别字典。

