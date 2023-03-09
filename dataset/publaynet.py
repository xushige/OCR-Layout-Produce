import pickle
import os
from pycocotools.coco import COCO
from tqdm import tqdm
# d = {1:'paragraph', 2:'section', 3:'caption', 4:'equation', 5:'figure', 6:'date', 7:'abstract', 8:'author', 9:'title', 10:'table', 11:'list', 12:'reference', 13:'footer'}
d = {1:'tubiao', 2:'section', 3:'text', 4:'TITLE', 5:'figure', 6:'author', 7:'list', 8:'table'}
def get_examples(label_path, mode):
    if not os.path.exists(os.path.join(label_path, "publaynet_" + mode + ".pkl")):
        annFile = os.path.join(label_path, "%s.json" % mode)
        if not os.path.exists(annFile):
            return None
        publaynet = COCO(annFile)
        filename2dataset = {}
        for img, img2ann in tqdm(zip(publaynet.imgs, publaynet.imgToAnns)):
            
            img = publaynet.imgs[img]
            img2ann = publaynet.imgToAnns[img2ann]
            file_name = img["file_name"]
            width, height = img["width"], img["height"]
            bbox = {}
            for eachvalue in d.values():
                bbox[eachvalue] = []
            for l in img2ann:
                bbox[d[l['category_id']]].append(l['bbox'])
            for key in bbox.keys():
                bbox[key] = sorted(bbox[key], key=lambda x: (x[0], x[1]))
            
            filename2dataset[file_name] = [width, height, bbox]
        with open(os.path.join(label_path, "publaynet_" + mode + ".pkl"), "wb") as f:
            pickle.dump(filename2dataset, f)
        return filename2dataset
    else:
        with open(os.path.join(label_path, "publaynet_" + mode + ".pkl"), "rb") as f:
            filename2dataset = pickle.load(f)
        return filename2dataset

class Publaynet(object):
    def __init__(self,label_path):
        super(Publaynet,self).__init__()
        self.label_path = label_path
        self.train_examples = get_examples(label_path,"train") 
        self.val_examples = get_examples(label_path,"val")
        self.all_examples = None

if __name__=="__main__":
    qw=Publaynet("E:\publaynet")
