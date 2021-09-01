## 文档生成引擎使用流程

1. 修改配置文件

* 配置文件路径：doc_data_generator/utils/config.py
* 修改生成图片数量，背景素材文件夹，字体文件夹，publaynet文档结构模板，构造数据存放位置等参数。
注意：如需新加入字体文件，一定要确保字体的完整性，否则存在特定文本无法渲染导致的图片-标签对不齐情况。
为避免此类问题，最好在构造后抽样部分转voc格式，人工过一下segmentation-visualization效果，确认数据无误。
* 修改图片类素材配置，可修改的配置包括图表路径，公章路径，公式路径，手写体图片路径，及logo类图片。
配置为字典类型，字典键值是路径，对应值是复制倍数，部分素材仍然不足，需要持续扩充

2. 数据构造

运行构造数据主函数文件路径：python doc_gen_main.py。
当配置文件路径改变时，首次运行时会计算图片路径中每张图片的长宽比，并保存在doc_data_generator/img2ratio.pkl路径之中。

3. 转换数据格式

构造的数据集格式的label是labelme格式的，在训练时要转换成voc或者coco格式的形式才可训练。

* MotherFolder/ImageSets/Segmentation/train.txt：存放训练集中每个图片的文件名，文件名不包括后缀名（如训练集图片10000.jpg存为10000）
* MotherFolder/ImageSets/Segmentation/test.txt:存放训练集中每个图片的文件名，文件名不包括后缀名（如测试集图片10000.jpg存为10000）
* MotherFolder/JPEGImages：存放训练图片，jpg格式
* MotherFolder/SegmentationClassPNG：存放mask
* MotherFolder/SegmentationClassVisualization:图片和mask结合的效果，用于检查mask和图片是否对应

利用doc_data_generator/labelme/examples/semantic_segmentation/labelme2voc.py将labelme格式label转成voc格式标签。
首先在doc_data_generator/labelme/examples/semantic_segmentation/labels.txt中写入所有的类别，然后运行如下命令：
```
python labelme2voc.py --input_dirs 训练集路径1 训练集路径2 训练集路径3 --test_dir 测试集路径 --labels labels.txt --merge_text_without_handwritten --noviz
```

其中noviz表示不生成SegmentationClassVisualization文件夹，确认无误后可关闭加速。
用于实际训练例子：
```
python labelme/examples/semantic_segmentation/labelme2voc.py 
--input_dirs /apdcephfs/share_887471/staffs/hooverhu/DDSN_gen_data/catelog_255_new /apdcephfs/share_887471/staffs/hooverhu/DDSN_gen_data/hoover_v1_0_vertical_optimize 
--test_dir /apdcephfs/share_887471/staffs/hooverhu/DDSN_gen_data/testset_document 
--labels /data/home/hooverhu/DDSN/doc_data_generator/labelme/examples/semantic_segmentation/labels.txt 
--hoover_default 
--output_dir train_v1.0
```
当需要对预测类别进行改变时可修改doc_data_generator/labelme/examples/semantic_segmentation/labelme2voc.py中的种类和对应代表数字的类别字典。

4. 合并两个数据集（如在当前数据中加入docbank数据集）。
当想在训练集中追加数据时如在训练数据时加入目录类型数据时又不想将原有数据集重走3.2的步骤时，将要追加的数据集走一遍3.2的流程之后，然后按照3.3将这两个数据合并。
这一步不是必须的，也可以按照3.2的方法在 --input_dirs参数后输入多个训练集路径合并。
当按照步骤2的方法处理了多个数据集时，有快速合并这些数据集的需求时，当多个数据集中测试集均相同的时候可以直接使用/doc_data_generator/labelme/examples/semantic_segmentation/merge_two_dataset.py进行合并，假如测试集不一样的话请用3.2所示的方法统一测试集。

docbank是一个英文数据集，docbank数据集比较大，实际使用中可以选择一部分单独放在一个路径，然后合并数据集。
合并可以通过两种方式进行：
```
python labelme2voc.py --input_dirs 构造数据集路径 cate_255路径 docbank子集地址 --test_dir 测试集路径 --labels labels.txt --merge_text_without_handwritten --noviz
```

假如构造数据集和docbank子集都已经分别用labelme2voc.py(要确保两个用labelme2voc.py处理后的测试集是一致的)转换成voc格式之后可以用如下命令：
```
python merge_two_dataset.py --dataset_path1 一个构造数据集（voc格式）路径 --dataset_path2 docbank子集（voc格式）路径 --output_dir 合并后数据集的输出路径
```

例如：
```
python merge_two_dataset.py --dataset_path1 /apdcephfs/share_887471/staffs/hooverhu/DDSN_gen_data/voc_gen_2w+catelog_583/ --dataset_path2 /apdcephfs/share_887471/staffs/hooverhu/DDSN_gen_data/voc_20210420_ECI_500_1st/ --output_dir /apdcephfs/share_887471/staffs/hooverhu/DDSN_gen_data/voc_default+voc_20210420_ECI_500_1st
```

## 素材说明

| 文件夹名称 | 说明 |
| --- | --- |
| backgrounds | 背景图片 |
| catelog_583 | 583张目录labelme标注格式图片 |
| figures_chinese | 841张带中文数据的图 |
| figures_publaynet | 109057张从publaynet数据集上截下来的图片 |
| figure_hard/axis | 111张带坐标轴的图片 |
| figure_hard/logo | 103张不带文字的商标 |
| figure_hard/logo2word | 101张带文字的商标 |
| tables_hard | 200张分割线较少的表格，小表格 |
| tables_chinese | 680张含中文比较多的表格图片 |
| tables_youtu | 11590张表格图片 from fujiko |
| handwritten_image | 20w手写体图片 |
| printing_equation | 76306张公式图片 from hooverhu |
| fonts | 中文字体文件 |
| fonts_bkp | 部分渲染文本可能失败的中文字体文件 |
| seals | 10000张生成的公章 |
| news2016 | 新闻语料库，用于填充中文文本 |
| publaynet/train.json | publaynet训练集label |
| publaynet/val.json | publaynet测试集label |
| train2017 | coco数据集 |
| docbank | docbank的labelme格式的数据集 |
| 20210420_ECI_500_1st | 真实标注500 - ECI采集第一批 |
| <strike>shijuan_train_new_label<strike> | <strike>训练平台格式的训练数据集<strike> |
| <strike>shijuan_test_new_label<strike> | <strike>训练平台格式的测试数据集<strike> |
| <strike>shijuan_train<strike> | <strike>yolov5源代码格式的训练数据集<strike> |
| <strike>shijuan_test<strike> | <strike>yolov5源代码格式的测试数据集<strike> |




