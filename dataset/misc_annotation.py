import pickle
import os
import glob
import json
from collections import OrderedDict
from tqdm import tqdm
from PIL import Image, ImageDraw, ImageFont
import numpy as np

def get_examples(label_path):
    
    if not os.path.exists(os.path.join(label_path, "document.pkl")):
        
        json_list = glob.glob(os.path.join(label_path, "*.json"))
        filename2dataset = {}

        for each_json in json_list:
            
            # each_json = "/data/home/hooverhu/DDSN_test_set/document/ddsn_general_370.json"
            imgFile = each_json.split(".json")[ 0 ] + ".jpg" # 目前仅支持这个
            cur_img = Image.open(imgFile)
            height, width, _ = np.shape(cur_img)

            with open(each_json) as f:
                data_filename1 = json.load(f, object_pairs_hook=OrderedDict)

            bbox = {"text": [], "title": [], "list": [], "table": [], "figure": []}
            for elem in data_filename1["shapes"]:
                # print("elem: ", elem)
                cur_points = elem["points"]
                cur_box = []
                
                minx, miny, maxx, maxy = 100000, 100000, -1, -1
                
                for each_point in cur_points:
                    # print ("each_point: ", each_point)
                    if int(each_point[0]) < minx:
                        minx = int(each_point[0]) 
                    if int(each_point[1]) < miny:
                        miny = int(each_point[1]) 
                    if int(each_point[0]) > maxx:
                        maxx = int(each_point[0]) 
                    if int(each_point[1]) > maxy:
                        maxy = int(each_point[1])  

                if maxx - minx < 0 or maxy - miny < 0:
                    continue # 非法输入框

                cur_box.append([minx, miny, maxx - minx, maxy - miny])
                # print ("cur_box: ", cur_box)

                if elem["label"] == "text":
                    bbox["text"].extend(cur_box)
                if elem["label"] == "title":
                    bbox["title"].extend(cur_box)
                if elem["label"] == "list":
                    bbox["list"].extend(cur_box)
                if elem["label"] == "table":
                    bbox["table"].extend(cur_box)
                if elem["label"] == "figure":
                    bbox["figure"].extend(cur_box)

                for key in bbox.keys():
                    bbox[key] = sorted(bbox[key], key=lambda x: (x[0], x[1]))
                filename2dataset[imgFile] = [width, height, bbox]
            with open(os.path.join(label_path, "document.pkl"), "wb") as f:
                pickle.dump(filename2dataset, f)
        
        return filename2dataset
    else:
        with open(os.path.join(label_path, "document.pkl"), "rb") as f:
            filename2dataset = pickle.load(f)
        return filename2dataset

class MiscAnnotation(object):
    def __init__(self,label_path):
        super(MiscAnnotation,self).__init__()
        self.label_path = label_path
        self.train_examples = get_examples(label_path)



if __name__=="__main__":
    MiscAnnotation("/data/home/hooverhu/DDSN_test_set/document")