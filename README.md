## ocr-版面构造

1. 修改配置文件
* 配置文件路径：ocr-dataproduce/utils/config.py
* 版面构造需要各种语料，以字典形式分为中英文，修改对应目录即可

2. 数据构造
运行构造数据主函数文件路径：python doc_gen_main.py

3. 转换数据格式
构造的数据集格式的label是labelme格式的，在训练时要转换成voc或者coco格式的形式才可训练。
利用ocr-dataproduce/labelme/examples/semantic_segmentation/labelme2voc.py将labelme格式label转成voc格式标签。
首先在ocr-dataproduce/labelme/examples/semantic_segmentation/labels.txt中写入所有的类别，然后运行如下命令：
```
python labelme2voc.py --input_dirs 训练集路径1 训练集路径2 训练集路径3 --test_dir 测试集路径 --labels labels.txt 
```
其中noviz表示不生成SegmentationClassVisualization文件夹，确认无误后可关闭加速。
```
python labelme/examples/semantic_segmentation/labelme2voc.py 
--input_dirs file-train
--test_dir file-test
--labels labels.txt 
--output_dir voc-dataset
```
当需要对预测类别进行改变时可修改ocr-dataproduce/labelme/examples/semantic_segmentation/labelme2voc.py中的类别字典。
