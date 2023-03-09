# ocr-版面构造
### 支持CV/NLP的labelme标注形式中英文“类真实“版面构造【目前只放了小部分中文语料】
## 修改配置文件
* 配置文件路径：OCR-Layout-Produce/utils/config.py
* 主要修改
————self.img_num【生成图片数量，默认10】
————self.output_dir【生成图片和label的保存位置，默认OCR-Layout-Produce/gen_out】
* 版面构造需要各种语料/图料/表料，以字典形式分为中英文，修改对应目录即可

## 数据构造
运行构造数据主函数文件路径：【PATTERN 从cv，nlp，ppt中选择模式与用途】
```
$ cd OCR-Layout-Produce
$ python doc_gen_main.py
```

## 转换数据格式
数据构造完毕后，因为构造的数据集格式的label是labelme格式的，所以在训练时要转换成voc（coco）格式的形式才可训练。
需要利用OCR-Layout-Produce/labelme/examples/semantic_segmentation/labelme2voc.py将labelme格式label转成voc格式标签。
首先在OCR-Layout-Produce/labelme/examples/semantic_segmentation/labels.txt中写入所有的类别，然后运行如下程序：
```
$ cd OCR-Layout-Produce
$ python ./labelme/examples/semantic_segmentation/labelme2voc.py --input_dirs ./gen_out --test_dir ./
```

* MotherFolder/ImageSets/Segmentation/train.txt：存放训练集中每个图片的文件名，文件名不包括后缀名（如训练集图片10000.jpg存为10000）
* MotherFolder/ImageSets/Segmentation/test.txt:存放增强训练集中每个图片的文件名，文件名不包括后缀名（如增强集图片10000.jpg存为10000）
* MotherFolder/ImageSets/Segmentation/test.txt:存放测试集中每个图片的文件名，文件名不包括后缀名（如测试集图片10000.jpg存为10000）
* MotherFolder/JPEGImages：存放训练图片，jpg格式
* MotherFolder/SegmentationClassPNG：存放mask
* MotherFolder/SegmentationClassVisualization:图片和mask结合的效果，用于检查mask和图片是否对应
* MotherFolder/cls_label.json: 存放每张图片的分类标签（该文件非必要，当需要处理分类时需要）

其中注意点
1. 上述例子中test_dir用了无效目录，真实场景需要填入同样labelme标注格式的test图片和标签
2. noviz表示不生成SegmentationClassVisualization文件夹，确认无误后可关闭加速。

