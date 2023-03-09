#!/usr/bin/env python
from __future__ import print_function
import argparse
import glob
import os
import os.path as osp
import imgviz
import numpy as np
from PIL import Image
import labelme
import math
import uuid
import numpy as np
import PIL.Image
import PIL.ImageDraw
import random
def shape_to_mask(
    img_shape, points, shape_type=None, line_width=10, point_size=5
):
    mask = np.zeros(img_shape[:2], dtype=np.uint8)
    mask = PIL.Image.fromarray(mask)
    draw = PIL.ImageDraw.Draw(mask)
    xy = [tuple(point) for point in points]
    if shape_type == "circle":
        assert len(xy) == 2, "Shape of shape_type=circle must have 2 points"
        (cx, cy), (px, py) = xy
        d = math.sqrt((cx - px) ** 2 + (cy - py) ** 2)
        draw.ellipse([cx - d, cy - d, cx + d, cy + d], outline=1, fill=1)
    elif shape_type == "rectangle":
        assert len(xy) == 2, "Shape of shape_type=rectangle must have 2 points"
        draw.rectangle(xy, outline=1, fill=1)
    elif shape_type == "line":
        assert len(xy) == 2, "Shape of shape_type=line must have 2 points"
        draw.line(xy=xy, fill=1, width=line_width)
    elif shape_type == "linestrip":
        draw.line(xy=xy, fill=1, width=line_width)
    elif shape_type == "point":
        assert len(xy) == 1, "Shape of shape_type=point must have 1 points"
        cx, cy = xy[0]
        r = point_size
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=1, fill=1)
    else:
        assert len(xy) > 2, "Polygon must have points more than 2"
        draw.polygon(xy=xy, outline=1, fill=1)
    mask = np.array(mask, dtype=bool)
    return mask

def boost(points):
    height = points[1][1]-points[0][1]
    width = points[1][0] - points[0][0]
    if height*0.8 <= 50 or width*0.8 <= 50:
        return points
    points[0][0] += width*0.1
    points[1][0] -= width*0.1
    points[0][1] += height*0.1
    points[1][1] -= height*0.1
    height = int(points[1][1]-points[0][1])
    width = int(points[1][0] - points[0][0])

    minwidth = int(width*0.6)
    maxwidth = int(width*0.95)
    minheight = int(height*0.6)
    maxheight = int(height*0.95)

    select_width = random.randint(minwidth, maxwidth)
    select_height = random.randint(minheight, maxheight)
    points[0][0] = random.randint(int(points[0][0]), int(points[1][0])-select_width)
    points[1][0] = points[0][0]+select_width
    points[0][1] = random.randint(int(points[0][1]), int(points[1][1])-select_height)
    points[1][1] = points[0][1]+select_height
    return points

def shapes_to_label(img_shape, shapes, label_name_to_value, need_booststrap=False):
    cls = np.zeros(img_shape[:2], dtype=np.int32)
    cls_copy = np.zeros(img_shape[:2], dtype=np.int32)
    instances = []
    for shape in shapes:
        points = shape["points"]
        label = shape["label"]
        
        group_id = shape.get("group_id")
        if group_id is None:
            group_id = uuid.uuid1()
        shape_type = shape.get("shape_type", None)

        cls_name = label
        instance = (cls_name, group_id)

        if instance not in instances:
            instances.append(instance)
        cls_id = label_name_to_value[cls_name]
        
        mask = shape_to_mask(img_shape[:2], points, shape_type)
        cls[mask] = cls_id
        
        if label in ['figure', 'table'] and need_booststrap:
            points = boost(points)
            mask = shape_to_mask(img_shape[:2], points, shape_type)
        cls_copy[mask] = cls_id
    return cls, cls_copy
def main():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
   
    parser.add_argument('--input_dirs', nargs='+')
    parser.add_argument("--test_dir", help="test dataset directory")
    parser.add_argument("--output_dir", help="output dataset directory", default='segmentation_out')
    parser.add_argument("--labels", help="labels file", default='labelme/examples/semantic_segmentation/labels.txt')
    parser.add_argument("--noviz", help="no visualization", action="store_true")
    parser.add_argument('--booststrap', action='store_true', default=False,
                        help='booststrap')
    
    args = parser.parse_args()
    
    
    print('=================================================================\ninput_dirs: ', args.input_dirs, '\noutput_dirs: ', args.output_dir)
    if not osp.exists(args.output_dir):
        os.makedirs(args.output_dir)
        os.makedirs(osp.join(args.output_dir, "JPEGImages"))
        os.makedirs(osp.join(args.output_dir, "SegmentationClass"))
        os.makedirs(osp.join(args.output_dir, "SegmentationClassPNG"))
    
    if not os.path.exists(os.path.join(args.output_dir,"ImageSets")):
        os.mkdir(os.path.join(args.output_dir,"ImageSets"))
        os.mkdir(os.path.join(args.output_dir,"ImageSets",'Segmentation'))
    if os.path.exists(args.input_dirs[0]+'/cls_label/cls_label.json'):
        print('Exist cls_label.json')
        import shutil
        shutil.copyfile(args.input_dirs[0]+'/cls_label/cls_label.json', args.output_dir+'/cls_label.json')
    if not args.noviz and not os.path.exists( os.path.join(args.output_dir, "SegmentationClassVisualization")):
        os.makedirs(osp.join(args.output_dir, "SegmentationClassVisualization"))
    print("Creating dataset:", args.output_dir)

    class_names = []
    class_name_to_id = {'__ignore__': -1, '_background_': 0, 'backgroud-color': 0, 'figure': 1, 'text': 2, 'date': 2, 'reference': 2, 'abstract': 2, 'section': 2, 'textline': 2, 'list': 2, 'author': 2, 'paragraph': 2, 'table': 3, 'footerandheader': 2, 'header': 2, 'footer': 2, 'FooterAndHeader': 2, 'handwritten': 2, 'title': 2, 'caption': 2, 'Caption': 2, 'equation': 2, 'formula': 2, 'formula_number': 2,'code': 2, 'seal': 0, 'watermark': -1, 'VerticalDvidingLine': 0, 'dottline': 0, "ValidLine": 4, "tableedge":0, "figureedge":0, "equationedge":0}
    
    print('need_booststrap: %s' % (args.booststrap))
    print("class_names:", class_names)
    out_class_names_file = osp.join(args.output_dir, "class_names.txt")
    with open(out_class_names_file, "w") as f:
        f.writelines("\n".join(class_names))
    print("Saved class_names:", out_class_names_file)

    for i, line in enumerate(open(args.labels).readlines()):
        class_id = i - 1  # starts with -1
        class_name = line.strip()
        if class_id == -1:
            assert class_name == "__ignore__"
            continue
        elif class_id == 0:
            assert class_name == "_background_"
        class_names.append(class_name)
    class_names = tuple(class_names)
    print("class_names:", class_names)

    import random
    train_imgs=[]
    print("args.input_dirs: ", args.input_dirs)
    for input_dir in args.input_dirs:
            train_imgs+=glob.glob(osp.join(input_dir, "*.json"))
    random.shuffle(train_imgs)
    test_imgs=glob.glob(osp.join(args.test_dir, "*.json"))

    if args.booststrap:
        ftrain = open(os.path.join(args.output_dir,"ImageSets",'Segmentation',"train.txt"),"w")
        
    print("num of train_imgs, and num of test_imgs: ", len(train_imgs), len(test_imgs))
    for idx, filename in enumerate(train_imgs+test_imgs):
        print("idx: ", idx, " Generating dataset from:", filename)

    
        label_file = labelme.LabelFile(filename=filename)
        
        base = osp.splitext(osp.basename(filename))[0]
        out_img_file = osp.join(args.output_dir, "JPEGImages", base + ".jpg")
        out_png_file = osp.join(args.output_dir, "SegmentationClassPNG", base + ".png")


        if not args.noviz:
            out_viz_file = osp.join(args.output_dir, "SegmentationClassVisualization", base + ".jpg")
        if not os.path.exists(os.path.dirname(out_img_file)):
            os.makedirs(os.path.dirname(out_img_file))
        
        with open(out_img_file, "wb") as f:
            f.write(label_file.imageData)

        img = labelme.utils.img_data_to_arr(label_file.imageData)

        _, _, c = np.shape(img)
        if c == 4:
            img = np.array(Image.fromarray(img, 'RGBA').convert('RGB'))

        lbl, lblcopy = shapes_to_label(
            img_shape=img.shape,
            shapes=label_file.shapes,
            label_name_to_value=class_name_to_id,
            need_booststrap = args.booststrap
        )
        
        
        if not os.path.exists(os.path.dirname(out_png_file)):
            os.makedirs(os.path.dirname(out_png_file))
        
        labelme.utils.lblsave(out_png_file, lbl)
        if (lblcopy != lbl).any() and filename not in test_imgs:
            print('booststrap')
            labelme.utils.lblsave(out_png_file[:-4]+'_booststrap.png', lblcopy)
            mask = lblcopy==0
            img[mask] = img[mask].mean(0)
            Image.fromarray(img).save(out_img_file[:-4]+'_booststrap.jpg')
            ftrain.write(os.path.basename(out_img_file)[:-4]+'_booststrap\n')

        if not args.noviz:
            viz = imgviz.label2rgb(
                label=lbl,
                image=imgviz.rgb2gray(img),
                font_size=15,
                label_names=class_names,
                loc="rb",
            )
            imgviz.io.imsave(out_viz_file, viz)

    if args.booststrap:
        ftrain.close()
    with open(os.path.join(args.output_dir,"ImageSets",'Segmentation',"train.txt"),"a") as ftrain:
        for img in train_imgs:
            ftrain.write(os.path.basename(img)[:-5]+"\n")
    with open(os.path.join(args.output_dir, "ImageSets", 'Segmentation', "val.txt"), "a") as ftest:
        for img in test_imgs:
            ftest.write(os.path.basename(img)[:-5] + "\n")
    with open(os.path.join(args.output_dir, "ImageSets", 'Segmentation', "aug.txt"), "a") as faug:
        pass

if __name__ == "__main__":
    main()
