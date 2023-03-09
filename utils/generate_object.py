# -*- coding: utf-8 -*
import glob
from PIL import Image, ImageDraw, ImageFont
import os
import numpy as np
import random
from utils.util import *
import re
needimg = True #是否需要图片
DEBUG = False
MARGIN_CROP = True #去除图片白边
EQUATION_HEIGHT = [i for i in range(105, 140)] #公式box高度设置
nlpdict = {'figure': 1, 'textline': 21, 'list': 22, 'section': 23, 'date': 24, 'title': 25, 'author': 26, 'abstract': 27, 'reference': 28, 'caption': 29, 'table': 3, 'header': 4, 'footer': 41, 'handwriting': 5, 'equation': 8, 'textequation': 81, 'seal': 9, 'watermark': 10, 'verticaldividingline': 11, 'backgroundcolor': 12, 'ValidLine': 13}

class figure_loader:
    '''
    图像加载器
    '''
    def __init__(self, img_dict):
        super(figure_loader, self).__init__()
        print("Init figure_loader ...")
        imgs = []
        img_dirs = []
        self.img_dict = img_dict

        for img_dir in img_dict.keys():  # 所有图片来源目录
            imgs += get_imgs(img_dir) * img_dict[img_dir]  # 目录来源下的所有图片地址按倍数添加到imgs中
            img_dirs.append(img_dir)  # 来源目录添加到列表中

        self.img2ratio = cul_ratio(img_dirs, "./ratio2img.pkl", margin_crop=MARGIN_CROP)  # 对所有来源目录中的所有图片，计算并保存长宽比

        random.shuffle(imgs)
        self.image_list = imgs
        self.id = 0
        self.ratio_dict = self.get_ratio_dict()
        self.image_lists = []
        self.ratios = []
        for ratio_dict in self.ratio_dict:
            img_list = list(self.ratio_dict[ratio_dict].keys()) * self.img_dict[ratio_dict]  # [路径]*倍数
            ratio = list(self.ratio_dict[ratio_dict].values()) * self.img_dict[ratio_dict]  # [长宽比]*倍数
            sorted_idx = sorted(range(len(list(img_list))), key=lambda k: ratio[k])  # ratios 排序返回索引
            image_list = list(np.array(img_list)[sorted_idx])  # 排序后的image_list
            ratio = list(np.array(ratio)[sorted_idx])  # 排序后的ratio
            self.image_lists.append(image_list)
            self.ratios.append(ratio)

    def get_ratio_dict(self):
        ratio_dict = {}
        print("Loading figure ratio ...")
        for img_dir in self.img_dict.keys():
            ratio_dict[img_dir] = {}
            for img_path in get_imgs(img_dir):
                ratio_dict[img_dir][img_path] = self.img2ratio[img_path]
        return ratio_dict

    def get_nearest_ratio_figure_path(self, target_width, target_height, RANDOM=True):
        '''
        target_width:目标bbox的宽度
        target_height:目标bbox的宽度
        return: 找到宽高比合适的图片路径
        '''
        if not RANDOM:
            # 从所有来源中找到最适合的
            resize_degree_list = []
            ratio_id_list = []
            for i in range(len(self.image_lists)):
                target_ratio = target_width / target_height  # 目标bbox的长宽比
                _, ratio_id, resize_degree = find_close_fast(self.ratios[i], target_ratio, imgdict=self.image_lists[i],
                                                             box_area=target_width * target_height)  # 从排序好的ratios中查找
                ratio_id_list.append(ratio_id)
                resize_degree_list.append(resize_degree)
            selected_id = resize_degree_list.index(min(resize_degree_list))
            ratio_id = ratio_id_list[selected_id]
        else:
            # 从随机来源挑选最适合的
            selected_id = random.randint(0, len(self.image_lists) - 1)
            _, ratio_id, resize_degree = find_close_fast(self.ratios[selected_id], target_width / target_height,
                                                         imgdict=self.image_lists[selected_id],
                                                         box_area=target_width * target_height)  # 从排序好的ratios中查找
        return_img = self.image_lists[selected_id][ratio_id]
        self.image_lists[selected_id].pop(ratio_id)  # 将图片从原来的list中删除
        self.ratios[selected_id].pop(ratio_id)  # 将图片的比例删除
        return return_img

class tubiao_loader:
    '''
    图标加载器
    '''
    def __init__(self, img_dict):
        super(tubiao_loader, self).__init__()
        print("Init tubiao_loader ...")
        imgs = []
        for img_dir in img_dict.keys():
            imgs += get_imgs(img_dir) * img_dict[img_dir]
        random.shuffle(imgs)
        self.image_list = imgs
        self.id = 0

    def update_id(self):
        self.id = (self.id + 1) % len(self.image_list)

class table_loader:
    '''
    表格加载器
    '''
    def __init__(self, img_dict):
        super(table_loader, self).__init__()
        print("Init table_loader ...")
        imgs = []
        img_dirs = []
        self.img_dict = img_dict
        for img_dir in img_dict.keys():
            imgs += get_imgs(img_dir) * img_dict[img_dir]
            img_dirs.append(img_dir)
        random.shuffle(imgs)
        self.img2ratio = cul_ratio(img_dirs, "./ratio2table.pkl", margin_crop=MARGIN_CROP)
        self.table_list = imgs
        self.id = 0
        self.ratio_dict = self.get_ratio_dict()
        self.image_lists = []
        self.ratios = []
        for ratio_dict in self.ratio_dict:
            img_list = list(self.ratio_dict[ratio_dict].keys()) * self.img_dict[ratio_dict]  # [路径]
            ratio = list(self.ratio_dict[ratio_dict].values()) * self.img_dict[ratio_dict]  # [长宽比]
            sorted_idx = sorted(range(len(list(img_list))), key=lambda k: ratio[k])  # ratios 排序返回索引
            image_list = list(np.array(img_list)[sorted_idx])  # 排序后的image_list
            ratio = list(np.array(ratio)[sorted_idx])  # 排序后的ratio
            self.image_lists.append(image_list)
            self.ratios.append(ratio)

    def get_ratio_dict(self):
        ratio_dict = {}
        print("Loading table ratio ...")
        for img_dir in self.img_dict.keys():
            ratio_dict[img_dir] = {}
            for img_path in get_imgs(img_dir):
                ratio_dict[img_dir][img_path] = self.img2ratio[img_path]
        return ratio_dict

    def get_nearest_ratio_figure_path(self, target_width, target_height, RANDOM=True):
        '''
        target_width:目标bbox的宽度
        target_height:目标bbox的宽度
        '''
        if not RANDOM:
            # 从所有来源中找到最适合的
            resize_degree_list = []
            ratio_id_list = []
            for i in range(len(self.image_lists)):
                target_ratio = target_width / target_height  # 目标bbox的长宽比
                _, ratio_id, resize_degree = find_close_fast(self.ratios[i], target_ratio, imgdict=self.image_lists[i],
                                                             box_area=target_width * target_height)  # 从排序好的ratios中查找
                ratio_id_list.append(ratio_id)
                resize_degree_list.append(resize_degree)
            selected_id = resize_degree_list.index(min(resize_degree_list))
            ratio_id = ratio_id_list[selected_id]
        else:
            # 随机挑选来源找到最适合的
            selected_id = random.randint(0, len(self.image_lists) - 1)
            _, ratio_id, resize_degree = find_close_fast(self.ratios[selected_id], target_width / target_height,
                                                         imgdict=self.image_lists[selected_id],
                                                         box_area=target_width * target_height)  # 从排序好的ratios中查找
        return_img = self.image_lists[selected_id][ratio_id]
        self.image_lists[selected_id].pop(ratio_id)  # 将图片从原来的list中删除
        self.ratios[selected_id].pop(ratio_id)  # 将图片的比例删除
        # print('get_nearest_ratio_figure_path_add==================================FIGURE==============================')
        return return_img

class handwritten_loader:
    '''
    手写体加载类
    '''

    def __init__(self, img_dict):
        super(handwritten_loader, self).__init__()
        print("Init handwritten_loader ...")
        imgs = []
        for img_dir in img_dict.keys():
            imgs += get_imgs(img_dir) * img_dict[img_dir]
        random.shuffle(imgs)
        self.img_list = imgs
        self.id = 0

    def update_id(self):
        self.id = (self.id + 1) % len(self.img_list)

class seal_loader:
    '''
    印章加载类
    '''
    def __init__(self, img_dict):
        super(seal_loader, self).__init__()
        print("Init seal_loader ...")
        imgs = []
        for img_dir in img_dict.keys():
            imgs += get_imgs(img_dir) * img_dict[img_dir]
        random.shuffle(imgs)
        self.seal_list = imgs
        self.id = 0

    def update_id(self):
        self.id = (self.id + 1) % len(self.seal_list)
class reference_loader(object):
    '''
    参考文献加载类
    '''
    def __init__(self, path):
        super(reference_loader, self).__init__()
        if isinstance(path, dict):
            self.path_dict = path
            self.read_dict = self.path_dict.copy()
            for eachkey in self.read_dict.keys():
                for i, eachpath in enumerate(self.read_dict[eachkey]):
                    self.read_dict[eachkey][i] = text_read(eachpath)
        self.reader = None
        self.path = None
        self.language = None
    # 获取文本内容
    def get_text(self, lines=None):
        object = []
        while len(object) < lines:
            tem_str = next(self.reader).strip()
            if (tem_str.isprintable()):
                object.append(tem_str)
        return object
    # 设定语言
    def random_select_language(self, language=None):
        self.language = random.choice(['Chinese', 'English']) if not language else language
        readerlist = self.read_dict[self.language]
        pathlist = self.path_dict[self.language]
        index = random.choice([i for i in range(len(pathlist))])
        self.reader = readerlist[index]
        self.path = pathlist[index]
        return self.language
class list_loader(object):
    '''
    列表加载类
    '''
    def __init__(self, path):
        super(list_loader, self).__init__()
        if isinstance(path, dict):
            self.path_dict = path
            self.read_dict = self.path_dict.copy()
            for eachkey in self.read_dict.keys():
                for i, eachpath in enumerate(self.read_dict[eachkey]):
                    self.read_dict[eachkey][i] = text_read(eachpath)
        self.reader = None
        self.path = None
        self.language = None
    def get_text(self, charnum=None):
        object = ''
        while len(object) < charnum:
            tem_str = next(self.reader).strip()
            if (tem_str.isprintable()):
                object += tem_str
        return object[:charnum]
    def random_select_language(self, language=None):
        self.language = random.choice(['Chinese', 'English']) if not language else language
        readerlist = self.read_dict[self.language]
        pathlist = self.path_dict[self.language]
        index = random.choice([i for i in range(len(pathlist))])
        self.reader = readerlist[index]
        self.path = pathlist[index]
        return self.language
class footer_loader(object):
    '''
    页脚加载类
    '''
    def __init__(self, path):
        super(footer_loader, self).__init__()
        if isinstance(path, dict):
            self.path_dict = path
            self.read_dict = self.path_dict.copy()
            for eachkey in self.read_dict.keys():
                for i, eachpath in enumerate(self.read_dict[eachkey]):
                    self.read_dict[eachkey][i] = text_read(eachpath)
        self.reader = None
        self.path = None
        self.language = None
    def get_text(self):
        
        tem_str = next(self.reader).strip()
        if (tem_str.isprintable()):
            object = tem_str
        
        return tem_str
    def random_select_language(self, language=None):
        self.language = random.choice(['Chinese', 'English']) if not language else language
        readerlist = self.read_dict[self.language]
        pathlist = self.path_dict[self.language]
        index = random.choice([i for i in range(len(pathlist))])
        self.reader = readerlist[index]
        self.path = pathlist[index]
        return self.language
class header_loader(object):
    '''
    页眉加载类
    '''
    def __init__(self, path):
        super(header_loader, self).__init__()
        if isinstance(path, dict):
            self.path_dict = path
            self.read_dict = self.path_dict.copy()
            for eachkey in self.read_dict.keys():
                for i, eachpath in enumerate(self.read_dict[eachkey]):
                    self.read_dict[eachkey][i] = text_read(eachpath)
        self.reader = None
        self.path = None
        self.language = None
    def get_text(self):
        
        tem_str = next(self.reader).strip()
        if (tem_str.isprintable()):
            object = tem_str
        
        return tem_str
    def random_select_language(self, language=None):
        self.language = random.choice(['Chinese', 'English']) if not language else language
        readerlist = self.read_dict[self.language]
        pathlist = self.path_dict[self.language]
        index = random.choice([i for i in range(len(pathlist))])
        self.reader = readerlist[index]
        self.path = pathlist[index]
        return self.language
class caption_loader(object):
    '''
    图注加载类
    '''
    def __init__(self, path):
        super(caption_loader, self).__init__()
        if isinstance(path, dict):
            self.path_dict = path
            self.read_dict = self.path_dict.copy()
            for eachkey in self.read_dict.keys():
                for i, eachpath in enumerate(self.read_dict[eachkey]):
                    self.read_dict[eachkey][i] = text_read(eachpath)
        self.reader = None
        self.path = None
        self.language = None
    def get_text(self):
        
        tem_str = next(self.reader).strip()
        if (tem_str.isprintable()):
            object = tem_str
        
        return tem_str
    def random_select_language(self, language=None):
        self.language = random.choice(['Chinese', 'English']) if not language else language
        readerlist = self.read_dict[self.language]
        pathlist = self.path_dict[self.language]
        index = random.choice([i for i in range(len(pathlist))])
        self.reader = readerlist[index]
        self.path = pathlist[index]
        return self.language
class title_loader(object):
    '''
    章节加载类
    '''
    def __init__(self, path):
        super(title_loader, self).__init__()
        if isinstance(path, dict):
            self.path_dict = path
            self.read_dict = self.path_dict.copy()
            for eachkey in self.read_dict.keys():
                for i, eachpath in enumerate(self.read_dict[eachkey]):
                    self.read_dict[eachkey][i] = text_read(eachpath)
        self.reader = None
        self.path = None
        self.language = None
    def get_text(self):
        
        tem_str = next(self.reader).strip()
        if (tem_str.isprintable()):
            object = tem_str
        
        return tem_str
    def random_select_language(self, language=None):
        self.language = random.choice(['Chinese', 'English']) if not language else language
        readerlist = self.read_dict[self.language]
        pathlist = self.path_dict[self.language]
        index = random.choice([i for i in range(len(pathlist))])
        self.reader = readerlist[index]
        self.path = pathlist[index]
        return self.language
class TITLE_loader(object):
    '''
    大标题加载类
    '''
    def __init__(self, path):
        super(TITLE_loader, self).__init__()
        if isinstance(path, dict):
            self.path_dict = path
            self.read_dict = self.path_dict.copy()
            for eachkey in self.read_dict.keys():
                for i, eachpath in enumerate(self.read_dict[eachkey]):
                    self.read_dict[eachkey][i] = text_read(eachpath)
        self.reader = None
        self.path = None
        self.language = None
    def get_text(self):
        
        tem_str = next(self.reader).strip()
        if (tem_str.isprintable()):
            object = tem_str
        
        return tem_str
    def random_select_language(self, language=None):
        self.language = random.choice(['Chinese', 'English']) if not language else language
        readerlist = self.read_dict[self.language]
        pathlist = self.path_dict[self.language]
        index = random.choice([i for i in range(len(pathlist))])
        self.reader = readerlist[index]
        self.path = pathlist[index]
        return self.language
class author_loader(object):
    '''
    作者加载类
    '''
    def __init__(self, path):
        super(author_loader, self).__init__()
        if isinstance(path, dict):
            self.path_dict = path
            self.read_dict = self.path_dict.copy()
            for eachkey in self.read_dict.keys():
                for i, eachpath in enumerate(self.read_dict[eachkey]):
                    self.read_dict[eachkey][i] = text_read(eachpath)
        self.reader = None
        self.path = None
        self.language = None
    def get_text(self):
        
        tem_str = next(self.reader).strip()
        if (tem_str.isprintable()):
            object = tem_str
        
        return tem_str
    def random_select_language(self, language=None):
        self.language = random.choice(['Chinese', 'English']) if not language else language
        readerlist = self.read_dict[self.language]
        pathlist = self.path_dict[self.language]
        index = random.choice([i for i in range(len(pathlist))])
        self.reader = readerlist[index]
        self.path = pathlist[index]
        return self.language
class date_loader(object):
    '''
    日期加载类
    '''
    def __init__(self, path):
        super(date_loader, self).__init__()
        if isinstance(path, dict):
            self.path_dict = path
            self.read_dict = self.path_dict.copy()
            for eachkey in self.read_dict.keys():
                for i, eachpath in enumerate(self.read_dict[eachkey]):
                    self.read_dict[eachkey][i] = text_read(eachpath)
        self.reader = None
        self.path = None
        self.language = None
    def get_text(self):
        
        tem_str = next(self.reader).strip()
        if (tem_str.isprintable()):
            object = tem_str
        
        return tem_str
    def random_select_language(self, language=None):
        self.language = random.choice(['Chinese', 'English']) if not language else language
        readerlist = self.read_dict[self.language]
        pathlist = self.path_dict[self.language]
        index = random.choice([i for i in range(len(pathlist))])
        self.reader = readerlist[index]
        self.path = pathlist[index]
        return self.language
class abstract_loader(object):
    '''
    摘要加载类
    '''
    def __init__(self, path):
        super(abstract_loader, self).__init__()
        if isinstance(path, dict):
            self.path_dict = path
            self.read_dict = self.path_dict.copy()
            for eachkey in self.read_dict.keys():
                for i, eachpath in enumerate(self.read_dict[eachkey]):
                    self.read_dict[eachkey][i] = text_read(eachpath)
        self.reader = None
        self.path = None
        self.language = None
    def get_text(self, charnums):
        object = ''
        while len(object) < charnums:
            tem_str = next(self.reader).strip()
            if (tem_str.isprintable()):
                object += tem_str
        
        return object[:charnums]
    def random_select_language(self, language=None):
        self.language = random.choice(['Chinese', 'English']) if not language else language
        readerlist = self.read_dict[self.language]
        pathlist = self.path_dict[self.language]
        index = random.choice([i for i in range(len(pathlist))])
        self.reader = readerlist[index]
        self.path = pathlist[index]
        return self.language    

class text_loader(object):
    '''
    文本加载类
    '''
    def __init__(self, text_path):
        super(text_loader, self).__init__()
        if isinstance(text_path, (list, tuple)):
            self.read_text_list = []
            self.text_path_list = []
            for eachfile in text_path:
                self.read_text_list.append(text_read(eachfile))
                self.text_path_list.append(eachfile)
        elif isinstance(text_path, (dict)):
            self.text_path_dict = text_path
            self.read_text_dict = self.text_path_dict.copy()
            for eachkey in self.read_text_dict.keys():
                for i, eachpath in enumerate(self.read_text_dict[eachkey]):
                    self.read_text_dict[eachkey][i] = text_read(eachpath)
        else:
            self.read_text_list = [text_read(text_path)]
            self.text_path_list = [text_path]

        self.text_reader = None
        self.text_path = None
        self.language = None
    def get_text(self, char_nums=100):
        '''
        取char_nums个文本
        :param line_num: 文本行数量
        :return: 取得的文本
        '''
        text = ""
       
        while (len(text) < char_nums):
            tem_str = next(self.text_reader).rstrip().strip(" ")
            if (tem_str.isprintable()):
                text += tem_str
        return text[:char_nums]
    def random_select_language(self, language=None):
        self.language = random.choice(['Chinese', 'English']) if not language else language
        textreaderlist = self.read_text_dict[self.language]
        textpathlist = self.text_path_dict[self.language]
        index = random.choice([i for i in range(len(textpathlist))])
        self.text_reader = textreaderlist[index]
        self.text_path = textpathlist[index]
        return self.language


class printing_equation_loader(object):
    '''
    公式加载类
    '''
    def __init__(self, img_dict):
        super(printing_equation_loader, self).__init__()
        print("Init equation_loader ...")
        imgs = []
        img_dirs = []
        self.img_dict = img_dict
        for img_dir in img_dict.keys():
            imgs += get_imgs(img_dir) * img_dict[img_dir]
            img_dirs.append(img_dir)
        random.shuffle(imgs)
        self.equation_list = imgs
        self.img2ratio = cul_ratio(img_dirs, "./ratio2equation.pkl", margin_crop=MARGIN_CROP)
        self.id = 0
        self.ratio_dict = self.get_ratio_dict()
        self.image_lists = []
        self.ratios = []
        for ratio_dict in self.ratio_dict:
            img_list = list(self.ratio_dict[ratio_dict].keys()) * self.img_dict[ratio_dict]  # [路径]
            ratio = list(self.ratio_dict[ratio_dict].values()) * self.img_dict[ratio_dict]  # [长宽比]
            sorted_idx = sorted(range(len(list(img_list))), key=lambda k: ratio[k])  # ratios 排序返回索引
            image_list = list(np.array(img_list)[sorted_idx])  # 排序后的image_list
            ratio = list(np.array(ratio)[sorted_idx])  # 排序后的ratio
            self.image_lists.append(image_list)
            self.ratios.append(ratio)

    def get_ratio_dict(self):
        ratio_dict = {}
        print("Loading equation ratio ...")
        for img_dir in self.img_dict.keys():
            ratio_dict[img_dir] = {}
            for img_path in get_imgs(img_dir):
                ratio_dict[img_dir][img_path] = self.img2ratio[img_path]
        return ratio_dict

    def get_nearest_ratio_figure_path(self, target_width, target_height, RANDOM=True):
        '''
        target_width:目标bbox的宽度
        target_height:目标bbox的宽度
        '''
        if not RANDOM:
            # 从所有来源中挑选最适合的
            resize_degree_list = []
            ratio_id_list = []
            for i in range(len(self.image_lists)):
                target_ratio = target_width / target_height  # 目标bbox的长宽比
                _, ratio_id, resize_degree = find_close_fast(self.ratios[i], target_ratio, imgdict=self.image_lists[i],
                                                             box_area=target_width * target_height)  # 从排序好的ratios中查找
                ratio_id_list.append(ratio_id)
                resize_degree_list.append(resize_degree)
            selected_id = resize_degree_list.index(min(resize_degree_list))
            ratio_id = ratio_id_list[selected_id]
        else:
            # 从随机来源挑选
            selected_id = random.randint(0, len(self.image_lists) - 1)
            _, ratio_id, resize_degree = find_close_fast(self.ratios[selected_id], target_width / target_height,
                                                         imgdict=self.image_lists[selected_id],
                                                         box_area=target_width * target_height)  # 从排序好的ratios中查找
        return_img = self.image_lists[selected_id][ratio_id]
        self.image_lists[selected_id].pop(ratio_id)  # 将图片从原来的list中删除
        self.ratios[selected_id].pop(ratio_id)  # 将图片的比例删除
        # print('get_nearest_ratio_figure_path_add==================================FIGURE==============================')
        return return_img


class document_generator(object):
    '''
    文档生成器
    '''
    def __init__(self, bg_dir, font_dir, output_path, bbox_dict=None, reshape_size=(1024, 768), figure_loader=None,
                 text_loader=None, table_loader=None, seal_loader=None, printing_equation_loader=None,
                 handwritten_loader=None, tubiao_loader=None, title_loader=None, TITLE_loader=None, footer_loader=None, header_loader=None, caption_loader=None, 
                 list_loader=None, reference_loader=None, abstract_loader=None, author_loader=None, date_loader=None, pattern=None):

        super(document_generator, self).__init__()
        # 50%概率文档里所有元素（text，title，caption, footandhead）分别字体字号颜色都一样
        self.same_elem = random.choice([0, 1]) #开关键，1为开启所有元素一致，0为关闭
        self.text = {}
        self.title = {}
        self.caption = {}
        self.footerandheader = {}
        self.list = {}
        self.TITLE = {}

        self.recnlp = [] # 存放nlplabel
        self.group = 1 # 群组起始值
        self.bg_list = glob.glob(os.path.join(bg_dir, "*.jpg"))+glob.glob(os.path.join(bg_dir, "*.JPG"))  # 背景图片
        self.image_path = random.choice(self.bg_list)  # 从背景图片中随机选一张作为背景

        self.fonts = glob.glob(os.path.join(font_dir, "*"))  # 字体列表
        self.font_nottc = self.fonts[:] #可加粗字体
        #ttc文件不可加粗，移除
        for each in self.font_nottc:
            if 'ttc' in each:
                self.font_nottc.remove(each)
        
        self.pattern = pattern # 模式选择 ppt， cv， nlp 三选一
        self.ppt_label = [] # ppt-label
        self.ddsn_label = [] # cv-label
        self.reshape_ratio = random.randint(100, 150) * 1.0 / 100  # 版面高宽比
        if self.pattern == 'ppt':
            self.reshape_ratio = 1/self.reshape_ratio # ppt高小于宽，所以比例取倒数
        self.reshape_height = 1684 #填充语料时固定高度1684（测试集高度的中位数）为基准，方便设置字号，行间距等
        self.reshape_width = int(self.reshape_height / self.reshape_ratio) #算出填充版面宽度
        # 初始以1684来保证最后缩小后仍然图片清晰
        publaynet_width, publaynet_height = reshape_size #publaynet版面的数据
        reshape_ratio_w = self.reshape_width / publaynet_width #相比publay版面，宽度改变比率
        reshape_ratio_h = self.reshape_height / publaynet_height #相比publay版面，高度改变比率

        # 生成图片最终的宽度，ppt与ddsn区分
        if self.pattern == 'ppt':
            self.final_width = random.randint(10, 14)*100
        else:
            self.final_width = random.randint(7, 11)*100 
        self.final_height = int(self.final_width * self.reshape_ratio) #高宽比不变，得出最终的高度，相当于整体缩放
        self.x_ratio = self.final_width / self.reshape_width #在宽度上缩放比率，用于最后对point进行缩放
        self.y_ratio = self.final_height / self.reshape_height #在高度上缩放比率，用于最后对point进行缩放

        self.bboxes = []  # 每张图片版式中的bbox
        #移除空box并且缩放每个box
        self.bbox_dict = bbox_dict.copy()
        for key in bbox_dict.keys():
            for bbox in bbox_dict[key]:
                #空box移除
                if not bbox:
                    self.bbox_dict[key].remove(bbox)
                    continue
                #缩放
                bbox[0] = int(bbox[0] * reshape_ratio_w)
                bbox[1] = int(bbox[1] * reshape_ratio_h)
                bbox[2] = int(bbox[2] * reshape_ratio_w)
                bbox[3] = int(bbox[3] * reshape_ratio_h)
                self.bboxes.append([bbox[0], bbox[1], bbox[2], bbox[3]])

        coord_bbox = np.array(self.bboxes)  # 所有bbox 格式[x0,y0,x1,y1]
        coord_bbox[:, 2] = coord_bbox[:, 0] + coord_bbox[:, 2]
        coord_bbox[:, 3] = coord_bbox[:, 1] + coord_bbox[:, 3]

        self.coord_bbox = coord_bbox

        ## 设定文档内容边界，用于确定素材填充区域 ##
        edge_margin = random.choice([i for i in range(5, 10)])

        lt_x = 0
        lt_y = 0
        if np.min(coord_bbox[:, 0]) - edge_margin < 0:
            pass
        else:
            lt_x = np.min(coord_bbox[:, 0]) - edge_margin

        if np.min(coord_bbox[:, 1]) - edge_margin < 0:
            pass
        else:
            lt_y = np.min(coord_bbox[:, 1]) - edge_margin
        self.top_left = (lt_x, lt_y)  # 每张版面的top_left坐标

        rb_x = self.reshape_width
        rb_y = self.reshape_height
        if np.max(coord_bbox[:, 2]) + edge_margin > self.reshape_width:
            pass
        else:
            rb_x = np.max(coord_bbox[:, 2]) + edge_margin

        if np.max(coord_bbox[:, 3]) + edge_margin > self.reshape_height:
            pass
        else:
            rb_y = np.max(coord_bbox[:, 3]) + edge_margin
        if rb_y < 1000:
            rb_y = random.randint(10, 15)*100
        self.bottom_right = (rb_x, rb_y)  # 每张版面的bottom_right坐标

        self.reshape_size = [self.reshape_width, self.reshape_height]  # 版面填充时的大小
        self.output_path = output_path  # 图片输出路径
        
        self.image, _ = reshape_img(self.image_path, (self.reshape_width, self.reshape_height), keep_ratio=False,
                                        margin_crop=False)  # reshape之后的图片，不锁定纵横比，因为是空白页面。不进行去白边处理，因为全是白色
        
        #加载各类loader
        self.tubiao_loader = tubiao_loader
        self.figure_loader = figure_loader
        self.text_loader = text_loader
        self.table_loader = table_loader
        self.seal_loader = seal_loader
        self.printing_equation_loader = printing_equation_loader
        self.handwritten_loader = handwritten_loader
        self.caption_loader = caption_loader
        self.title_loader = title_loader
        self.TITLE_loader = TITLE_loader
        self.footer_loader = footer_loader
        self.header_loader = header_loader
        self.list_loader = list_loader
        self.reference_loader = reference_loader
        self.abstract_loader = abstract_loader
        self.author_loader = author_loader
        self.date_loader = date_loader
        #版面语言确定
        self.select = 'Chinese' # 默认中文，如需英文需要在utils/config.py中添加英文预料文件
        self.select = self.text_loader.random_select_language(self.select)  # 随机选择语言
        self.title_loader.random_select_language(self.select)
        self.TITLE_loader.random_select_language(self.select)
        self.caption_loader.random_select_language(self.select)
        self.footer_loader.random_select_language(self.select)
        self.header_loader.random_select_language(self.select)
        self.list_loader.random_select_language(self.select)
        self.reference_loader.random_select_language(self.select)
        self.abstract_loader.random_select_language(self.select)
        self.author_loader.random_select_language(self.select)
        self.date_loader.random_select_language(self.select)
        #版面所有text内容，保证同一版面文字部分语义完整
        self.textcontent = self.text_loader.get_text(random.randint(8, 12)*1000)
    def gen_complicate_true_doc(self):
        '''
        构造文档函数
        '''
        boxes_ = []
        labels = []

        text_boxes = []
        
        title_bboxes = []
    
        TITLE_bboxes = []

        table_bboxes = []

        tubiao_bboxes = []

        equation_bboxes = []

        figure_bboxes = []

        caption_bboxes = []

        reference_bboxes = []

        author_bboxes = []

        date_bboxes = []

        abstract_bboxes = []
        
        handwritten_bboxes = []
        
        list_bboxes = []
        list_labels = []

        color = random.choices([(0, 0, 0), (255, 0, 0), (0, 0, 255)], [8, 1, 1])[0]  # 选择字体颜色
        ### 基本构成块信息组织 ###
        gap = 6 # 图和表的box被切分成2块时，两块之间的间距
        for key in self.bbox_dict.keys():
            if (key == "table"):
                for bbox in self.bbox_dict[key]:
                    pattern = random.choice([0, 1, 2])
                    # 如果box面积占版面总面积小于1/4，不进行拆分，默认填充一张图
                    if bbox[2] * bbox[3] / (self.image.size[0] * self.image.size[1]) <= 0.25:
                        table_bboxes.append(bbox)
                        boxes_.extend([bbox])
                        continue
                    # box面积大于页面面积50%的情况，以两种形式进行拆分
                    elif bbox[2] * bbox[3] / (self.image.size[0] * self.image.size[1]) >= 0.5 and pattern:
                        if pattern == 1:  # 四象限分
                            BOX = [[bbox[0], bbox[1], bbox[2] // 2, bbox[3] // 2],
                                   [bbox[0] + bbox[2] - bbox[2] // 2, bbox[1], bbox[2] // 2, bbox[3] // 2],
                                   [bbox[0], bbox[1] + bbox[3] - bbox[3] // 2, bbox[2] // 2, bbox[3] // 2],
                                   [bbox[0] + bbox[2] - bbox[2] // 2, bbox[1] + bbox[3] - bbox[3] // 2, bbox[2] // 2,
                                    bbox[3] // 2]]
                        elif pattern == 2:  # 从上至下分
                            eachheight = bbox[3] // 4
                            BOX = [[bbox[0], bbox[1], bbox[2], eachheight],
                                   [bbox[0], bbox[1] + eachheight, bbox[2], eachheight],
                                   [bbox[0], bbox[1] + eachheight * 2, bbox[2], eachheight],
                                   [bbox[0], bbox[1] + eachheight * 3, bbox[2], eachheight]]
                        for i in range(len(BOX)):
                            if i % 2:
                                table_bboxes.append(BOX[i])
                            else:
                                figure_bboxes.append(BOX[i])
                            boxes_.extend([BOX[i]])
                        continue
                    # 面积在 25-50%， 或者面积大于50%但是没有进行拆分的
                    prob = random.choice([2, 3, 4, 5]) #随机概率，按照长宽特点，再次拆分
                    if (prob == 2) and bbox[2] >= bbox[3]:  # 表格bbox中左图右表
                        figure_box = [bbox[0], bbox[1], int(bbox[2] / 2), bbox[3]]
                        table_box = [bbox[0] + gap + int(bbox[2] / 2), bbox[1], int(bbox[2] / 2) - gap, bbox[3]]
                        figure_bboxes.append(figure_box)
                        table_bboxes.append(table_box)
                        boxes_.extend([figure_box])
                        boxes_.extend([table_box])
                    elif (prob == 3) and bbox[2] <= bbox[3]:  # 表格bbox中上图下表
                        figure_box = [bbox[0], bbox[1], bbox[2], int(bbox[3] / 2)]
                        table_box = [bbox[0], bbox[1] + gap + int(bbox[3] / 2), bbox[2], int(bbox[3] / 2 - gap)]
                        figure_bboxes.append(figure_box)
                        table_bboxes.append(table_box)
                        boxes_.extend([figure_box])
                        boxes_.extend([table_box])
                    elif (prob == 4) and bbox[2] >= bbox[3]:  # 表格bbox中左表右表
                        table_box = [bbox[0], bbox[1], int(bbox[2] / 2), bbox[3]]
                        table_box2 = [bbox[0] + gap + int(bbox[2] / 2), bbox[1], int(bbox[2] / 2) - gap, bbox[3]]
                        table_bboxes.append(table_box)
                        table_bboxes.append(table_box2)
                        boxes_.extend([table_box])
                        boxes_.extend([table_box2])
                    elif (prob == 5) and bbox[2] <= bbox[3]:  # 表格bbox中上表下表
                        table_box = [bbox[0], bbox[1], bbox[2], int(bbox[3] / 2)]
                        table_box2 = [bbox[0], bbox[1] + gap + int(bbox[3] / 2), bbox[2], int(bbox[3] / 2 - gap)]
                        table_bboxes.append(table_box)
                        table_bboxes.append(table_box2)
                        boxes_.extend([table_box])
                        boxes_.extend([table_box2])
                    else: # 不拆分的
                        table_bboxes.append(bbox)
                        boxes_.extend([bbox])
            if (key in ["section", 'title']): #publay中的title实际是section
                for bbox in self.bbox_dict[key]:
                    if self.pattern == 'ppt': # ppt版面情况 
                        background_color = (random.randint(128,255), random.randint(128,255), random.randint(128,255)) # 该box的背景色随机浅色
                        background = Image.new('RGB', (bbox[2], bbox[3]), background_color) # 背景大小
                        self.image.paste(background, (bbox[0], bbox[1])) # 背景填充
                        TITLE_bboxes.append(bbox) # 在ppt中标题和章节都划入大标题类
                    else: # ddsn版面
                        title_bboxes.append(bbox) # 划入章节box
                    boxes_.extend(bbox)
                    
            if key == 'TITLE':  # 大标题
                for bbox in self.bbox_dict[key]:
                    if self.pattern == 'ppt': 
                        background_color = (random.randint(128,255), random.randint(128,255), random.randint(128,255))
                        background = Image.new('RGB', (bbox[2], bbox[3]), background_color)
                        self.image.paste(background, (bbox[0], bbox[1]))
                    boxes_.extend(bbox)
                    TITLE_bboxes.append(bbox)
            if key == 'tubiao': # 图标
                tubiao_bboxes.extend(self.bbox_dict[key]) 
            if (key == "figure"): # 图
                for bbox in self.bbox_dict[key]:
                    # ppt情况因为layout中没有表格，所以图的box有1/2概率划入table-box
                    if self.pattern == 'ppt': 
                        if random.randint(0, 1):
                            figure_bboxes.append(bbox)
                        else:
                            table_bboxes.append(bbox)
                        continue
                    # 拆分模式，同上面table处理方法
                    pattern = random.choice([0, 1, 2])
                    # box面积太小不切割
                    if bbox[2] * bbox[3] / (self.image.size[0] * self.image.size[1]) <= 0.25:
                        figure_bboxes.append(bbox)
                        boxes_.extend([bbox])
                        continue
                    # box面积大于页面面积50%分情况进行拆分
                    elif bbox[2] * bbox[3] / (self.image.size[0] * self.image.size[1]) >= 0.5 and pattern:
                        if pattern == 1:  # 四象限分
                            BOX = [[bbox[0], bbox[1], bbox[2] // 2, bbox[3] // 2],
                                   [bbox[0] + bbox[2] - bbox[2] // 2, bbox[1], bbox[2] // 2, bbox[3] // 2],
                                   [bbox[0], bbox[1] + bbox[3] - bbox[3] // 2, bbox[2] // 2, bbox[3] // 2],
                                   [bbox[0] + bbox[2] - bbox[2] // 2, bbox[1] + bbox[3] - bbox[3] // 2, bbox[2] // 2,
                                    bbox[3] // 2]]
                        elif pattern == 2:  # 从上至下分
                            eachheight = bbox[3] // 4
                            BOX = [[bbox[0], bbox[1], bbox[2], eachheight],
                                   [bbox[0], bbox[1] + eachheight, bbox[2], eachheight],
                                   [bbox[0], bbox[1] + eachheight * 2, bbox[2], eachheight],
                                   [bbox[0], bbox[1] + eachheight * 3, bbox[2], eachheight]]
                        for i in range(len(BOX)):
                            if i % 2:
                                table_bboxes.append(BOX[i])
                            else:
                                figure_bboxes.append(BOX[i])
                            boxes_.extend([BOX[i]])
                        continue
                    # 进一步根据长宽拆分
                    prob = random.choice([2, 3, 4, 5])
                    if (prob == 2) and bbox[2] >= bbox[3]:  # 单个figure box中 左图右表
                        figure_box = [bbox[0], bbox[1], int(bbox[2] / 2), bbox[3]]
                        
                        table_box = [bbox[0] + gap + int(bbox[2] / 2), bbox[1], int(bbox[2] / 2) - gap, bbox[3]]
                        figure_bboxes.append(figure_box)
                        table_bboxes.append(table_box)

                        boxes_.extend([figure_box])
                        boxes_.extend([table_box])

                    elif (prob == 3) and bbox[2] <= bbox[3]:  # 单个figure bbox中上图下表
                        figure_box = [bbox[0], bbox[1], bbox[2], int(bbox[3] / 2)]
                        
                        table_box = [bbox[0], bbox[1] + gap + int(bbox[3] / 2), bbox[2], int(bbox[3] / 2 - gap)]
                        figure_bboxes.append(figure_box)
                        table_bboxes.append(table_box)

                        boxes_.extend([figure_box])
                        boxes_.extend([table_box])

                    elif (prob == 4) and bbox[2] >= bbox[3]:  # 单个figure_bbox中左图右图
                        figure_box = [bbox[0], bbox[1], int(bbox[2] / 2), bbox[3]]
                        figure_box2 = [bbox[0] + gap + int(bbox[2] / 2), bbox[1], int(bbox[2] / 2) - gap, bbox[3]]
                        figure_bboxes.append(figure_box)
                        figure_bboxes.append(figure_box2)

                        boxes_.extend([figure_box])
                        boxes_.extend([figure_box2])
                    elif (prob == 5) and bbox[2] <= bbox[3]:  # 单个figure_bbox中上图下图
                        figure_box = [bbox[0], bbox[1], bbox[2], int(bbox[3] / 2)]
                        figure_box2 = [bbox[0], bbox[1] + gap + int(bbox[3] / 2), bbox[2], int(bbox[3] / 2 - gap)]
                        figure_bboxes.append(figure_box)
                        figure_bboxes.append(figure_box2)

                        boxes_.extend([figure_box])
                        boxes_.extend([figure_box2])
                    else: # 不拆分
                        figure_bboxes.append(bbox)
                        boxes_.extend([bbox])

            if key in ['list']: # 列表
                for bbox in self.bbox_dict[key]:
                    if self.pattern == 'ppt':
                        background_color = (random.randint(128,255), random.randint(128,255), random.randint(128,255))
                        background = Image.new('RGB', (bbox[2], bbox[3]), background_color)
                        self.image.paste(background, (bbox[0], bbox[1]))
                    boxes_.append(bbox)
                    list_bboxes.append(bbox)
            if key in ['abstract']: # 摘要
                for bbox in self.bbox_dict[key]:
                    if not abstract_bboxes:
                        abstract_bboxes.append(bbox)
            if key in ['author']: # 作者
                for bbox in self.bbox_dict[key]:
                    if self.pattern == 'ppt':
                        background_color = (random.randint(128,255), random.randint(128,255), random.randint(128,255))
                        background = Image.new('RGB', (bbox[2], bbox[3]), background_color)
                        self.image.paste(background, (bbox[0], bbox[1]))
                    author_bboxes.append(bbox)
            if key in ['date']: # 日期
                for bbox in self.bbox_dict[key]:
                    if self.pattern == 'ppt':
                        background_color = (random.randint(128,255), random.randint(128,255), random.randint(128,255))
                        background = Image.new('RGB', (bbox[2], bbox[3]), background_color)
                        self.image.paste(background, (bbox[0], bbox[1]))
                    date_bboxes.append(bbox)
            if key in ["text", 'paragraph', 'caption', 'equation', 'reference']:  # 全部用来文本
                for bbox in self.bbox_dict[key]:
                    boxes_.append(bbox)
                    if self.pattern == 'ppt':
                        background_color = (random.randint(128,255), random.randint(128,255), random.randint(128,255))
                        background = Image.new('RGB', (bbox[2], bbox[3]), background_color)
                        self.image.paste(background, (bbox[0], bbox[1]))
                    # ddsn版面情况下，当box高度很高时，有概率划入reference，abstract，list中
                    if bbox[3] > 350 and self.pattern != 'ppt':
                        prob = random.randint(0, 19)
                        #参考
                        if not reference_bboxes and prob in range(1, 5):
                            reference_bboxes.append(bbox)
                            continue
                        #摘要
                        elif not abstract_bboxes and prob == 0:
                            abstract_bboxes.append(bbox)
                            continue
                        #列表
                        elif prob in range(5, 8):
                            list_bboxes.append(bbox)
                            continue

                    if random.randint(0, 1) and ((bbox[0]+bbox[2])<0.5*self.reshape_width or bbox[0] > 0.5*self.reshape_width):  # 双栏情况下1/2的概率 存在公式
                        split_bboxes = []  # 将text_box切分
                        equation_height = random.choice(EQUATION_HEIGHT)  # 公式高度
                        # ppt版面较大，所以公式高度增加
                        if self.pattern == 'ppt':
                            equation_height += 20
                        if (bbox[3] < equation_height):  # box高度小于公式高度直接加入text_bboxes
                            text_boxes.append(bbox)
                            continue
                        already_split_height = equation_height  # 已经切分的text_bbox高度
                        # 切分过程
                        while (already_split_height < bbox[3]):
                            split_bboxes.append(
                                [bbox[0], bbox[1] + already_split_height - equation_height, bbox[2], equation_height])
                            equation_height = random.choice(EQUATION_HEIGHT)
                            # 公式高度在ppt版面增加
                            if self.pattern == 'ppt':
                                equation_height += 20
                            already_split_height += equation_height
                        try:
                            equation_num = random.choice(
                                [i for i in range(1, len(split_bboxes) + 1)])  # 切分的box选equation_num个box用来加入公式
                        except:
                            equation_num = 0
                        selected_equation_indexes = random.choices([i for i in range(0, len(split_bboxes))],
                                                                   k=equation_num)
                        selected_equation_bboxes = []  # split_bboxes中的公式的bbox
                        selected_text_bboxes = []  # splict_bboxes 中文本的bbox
                        prev_text_idx = 0
                        for idx in [i for i in range(0, len(split_bboxes))]:
                            if (idx in selected_equation_indexes):
                                # 公式box保存
                                selected_equation_bboxes.append(split_bboxes[idx])
                                # 公式box的前面所有textbox合并保存
                                if split_bboxes[prev_text_idx: idx]:
                                    selected_text_bboxes.append([split_bboxes[prev_text_idx][0],
                                                                 split_bboxes[prev_text_idx][1],
                                                                 split_bboxes[idx - 1][0] + split_bboxes[idx - 1][2] -
                                                                 split_bboxes[prev_text_idx][0],
                                                                 split_bboxes[idx - 1][1] + split_bboxes[idx - 1][3] -
                                                                 split_bboxes[prev_text_idx][1]])
                                prev_text_idx = idx + 1
                        # 最后一部分的textbox保存
                        if split_bboxes[prev_text_idx:]:
                            selected_text_bboxes.append([split_bboxes[prev_text_idx][0],
                                                         split_bboxes[prev_text_idx][1],
                                                         split_bboxes[-1][0] + split_bboxes[-1][2] -
                                                         split_bboxes[prev_text_idx][0],
                                                         split_bboxes[-1][1] + split_bboxes[-1][3] -
                                                         split_bboxes[prev_text_idx][1]])

                        equation_bboxes.extend(selected_equation_bboxes)  # 将选择的公式bbox加入到equation_bboxes
                        text_boxes.extend(selected_text_bboxes)  # 将选择的文本bbox加入到text_boxes
                    else:
                        text_boxes.append(bbox)


        ### START增加页脚页眉区域，并在对应区域添加小图标/文字logo ###
        if self.pattern != 'ppt': # ppt版面没有页眉页脚，ddsn版面才有
            _, tubiao_bboxes = self.add_footerandheader()
        #对每个tubiao-box填图
        for tubiao_bbox in tubiao_bboxes:
            cur_tubiao_bbox = (tubiao_bbox[0], tubiao_bbox[1], tubiao_bbox[2], tubiao_bbox[3])
            object_label, _, _, caption_bboxes = self.add_simple_figure(cur_tubiao_bbox, self.tubiao_loader.image_list[self.tubiao_loader.id], usage='tubiao')
            self.tubiao_loader.update_id()
            # ppt版面label保存
            self.ppt_label.append(object_label)
        
        ### START Figure ###
        for figure_bbox in figure_bboxes:
            # 添加图像
            if figure_bbox[2] == 0 or figure_bbox[3] == 0:
                continue
            # ppt版面则不进行处理之间填图
            if self.pattern == 'ppt':
                object_label, _, _, caption_bboxes, _ = self.add_simple_figure(
                    figure_bbox,
                    self.figure_loader.get_nearest_ratio_figure_path(figure_bbox[2], figure_bbox[3]),
                    usage='figure',
                    keep_ratio=False,
                    need_caption=False)
                self.ppt_label.append(object_label)
                continue
            # ddsn版面情况
            if random.randint(0, 5)==0: #publay中figure版面居多，有1/6概率图的box来填表
                table_bboxes.append(figure_bbox)
                continue
            # 高宽不合理的进行拆分
            #figure_box 过宽或过长则对半切分
            if figure_bbox[2] / figure_bbox[3] >= 3:
                newwidth = figure_bbox[2] // 2 - gap // 2
                BOX = [[figure_bbox[0], figure_bbox[1], newwidth, figure_bbox[3]],
                       [figure_bbox[0] + figure_bbox[2] - newwidth, figure_bbox[1], newwidth, figure_bbox[3]]]
            elif figure_bbox[3] / figure_bbox[2] >= 3:
                newheight = figure_bbox[3] // 2
                BOX = [[figure_bbox[0], figure_bbox[1], figure_bbox[2], newheight],
                       [figure_bbox[0], figure_bbox[1] + figure_bbox[3] - newheight, figure_bbox[2], newheight]]
            else:
                BOX = [[figure_bbox[0], figure_bbox[1], figure_bbox[2], figure_bbox[3]]]
            # 填充
            for cur_figure_bbox in BOX:
                # box随机宽度, 泛化每次检索到的图片语料
                dropratio = random.choice([0, 1, 2, 3, 4, 5])
                droplength = cur_figure_bbox[2] * dropratio // 20
                cur_figure_bbox[0] = cur_figure_bbox[0] + droplength
                cur_figure_bbox[2] = cur_figure_bbox[2] - 2 * droplength
                object_label, _, _, caption_bboxes, _ = self.add_simple_figure(
                    cur_figure_bbox,
                    self.figure_loader.get_nearest_ratio_figure_path(cur_figure_bbox[2], cur_figure_bbox[3]),
                    usage='figure')
                boxes_.extend([caption_bboxes])  # 添加的legend也要和分割线进行关联
                     
        ### START Table ###
        for table_bbox in table_bboxes:  # 添加表格
            if table_bbox[2] == 0 or table_bbox[3] == 0:
                continue
            # ppt版面之间填表
            if self.pattern == 'ppt':
                object_label, _, _, caption_bboxes, _ = self.add_table(
                    table_bbox,
                    self.table_loader.get_nearest_ratio_figure_path(table_bbox[2], table_bbox[3]),
                    keep_ratio=False,
                    need_caption=False)
                self.ppt_label.append(object_label)
                continue
            # ddsn版面情况
            # 高宽不合理的box进行拆分
            if table_bbox[2] / table_bbox[3] >= 3:
                newwidth = table_bbox[2] // 2 - gap // 2
                BOX = [[table_bbox[0], table_bbox[1], newwidth, table_bbox[3]],
                       [table_bbox[0] + table_bbox[2] - newwidth, table_bbox[1], newwidth, table_bbox[3]]]
            elif table_bbox[3] / table_bbox[2] >= 3:
                newheight = table_bbox[3] // 2
                BOX = [[table_bbox[0], table_bbox[1], table_bbox[2], newheight],
                       [table_bbox[0], table_bbox[1] + table_bbox[3] - newheight, table_bbox[2], newheight]]
            else:
                BOX = [[table_bbox[0], table_bbox[1], table_bbox[2], table_bbox[3]]]
            #填充，与figure类似
            for cur_table_bbox in BOX:
                # 随机宽度
                dropratio = random.choice([0, 1, 1, 2])  # 宽度总计丢弃0%，10%， 10%， 20%
                droplength = cur_table_bbox[2] * dropratio // 20
                cur_table_bbox[0] = cur_table_bbox[0] + droplength
                cur_table_bbox[2] = cur_table_bbox[2] - 2 * droplength
                # 填图
                _, _, _, caption_bboxes, _ = self.add_table(
                    cur_table_bbox,
                    self.table_loader.get_nearest_ratio_figure_path(cur_table_bbox[2], cur_table_bbox[3])
                )
        ### START Equation ###
        for equation_bbox in equation_bboxes:  # 添加公式
            # 宽度随机丢弃
            drop_ratio = random.choice([1, 1, 1, 2, 2, 2, 3])
            # 左（右）侧丢弃长度
            drop_length_oneside = equation_bbox[2] * drop_ratio // 20
            cur_equation_bbox = (equation_bbox[0]+drop_length_oneside, equation_bbox[1], equation_bbox[2]-2*drop_length_oneside, equation_bbox[3])
            # 填充公式
            equation_label, _ = self.add_equation(
                cur_equation_bbox,
                self.printing_equation_loader.get_nearest_ratio_figure_path(cur_equation_bbox[2], cur_equation_bbox[3]),
                group=self.group)
            #label保存
            self.recnlp.append(equation_label)
            self.ddsn_label.append(equation_label)
            self.ppt_label.append(equation_label)
            #填充公式序号（算作文本）
            equation_text = '(%d)' % (random.randint(1, 20)) #随机序号
            font = ImageFont.truetype(random.choice(self.fonts), random.randint(20, 25)) #随机字体字号
            image_draw = ImageDraw.Draw(self.image) #图片导入
            line_size_x, line_size_y = image_draw.textsize(equation_text, font=font) #获得文本宽高
            if line_size_x < equation_bbox[0] + equation_bbox[2] - equation_label['points'][1][0]: #确认宽度够放
                equation_text_box = [equation_bbox[0]+equation_bbox[2]-line_size_x, equation_bbox[1]+(equation_bbox[3]-line_size_y)//2, line_size_x, line_size_y] #公式序号box
                if needimg:
                    image_draw.text([equation_text_box[0], equation_text_box[1]], equation_text, font=font, fill=(0, 0, 0)) #填充公式序号
                equation_text_label = {"label": "textline", 
                "points": [[equation_text_box[0], equation_text_box[1]],[equation_text_box[0]+equation_text_box[2], equation_text_box[1]+equation_text_box[3]]], 
                "type": "rectangle",
                'content': equation_text,
                'group': self.group} #保存point
                self.recnlp.append(equation_text_label) # nlp保存label
                self.ddsn_label.append(equation_text_label) # cv保存label
                # ppt label保存
                ppt_label = equation_text_label.copy()
                ppt_label['label'] = 'text'
                self.ppt_label.append(ppt_label)
            #群组更新
            self.group += 1
        ### START textline ###
        for text_bbox in text_boxes:
            text = None
            # 每个box随机选择字体
            font = random.choice(self.fonts)
            self.add_text(text_bbox, text, font=font, color=color)

        ### START list ###
        for list_bbox in list_bboxes:
            list_label = self.add_list(list_bbox, self.group)
            list_labels.extend(list_label)
            self.group += 1 # 群组更新
        self.recnlp.extend(list_labels)

        ### START abstract ###
        for abstract_box in abstract_bboxes:
            self.add_abstract(abstract_box)

        ### START reference ###
        for reference_box in reference_bboxes:
            self.add_reference(reference_box)

        ### START title ###
        for T_box in TITLE_bboxes:
            self.add_TITLE(T_box)
            
        ### START author ###
        for author_box in author_bboxes:
            self.add_author(author_box)

        ### START date ###
        for date_box in date_bboxes:
            self.add_date(date_box)

        ### START section ###
        for title_bbox in title_bboxes:
            font = random.choice(self.font_nottc)
            title_label = self.add_title(title_bbox, color, font)
            self.ppt_label.append(title_label)

        ### START handwriting ###
        for handwritten_bbox in handwritten_bboxes:
            cur_handwritten_bbox = (handwritten_bbox[0], handwritten_bbox[1], handwritten_bbox[2], handwritten_bbox[3])
            handwritten_label = self.add_handwritten(
                cur_handwritten_bbox, self.handwritten_loader.img_list[self.handwritten_loader.id])
            handwritten_label['content'] = '<handwriting>'
            handwritten_label['group'] = self.group
            self.group += 1
            self.handwritten_loader.update_id()
            self.recnlp.append(handwritten_label)

        ### START validline ###
        if 0 != random.choice([0, 1, 2]) and self.pattern != 'ppt':  # 2/3概率添加边框线
            valid_line_labels = self.gen_edge_line()
            self.recnlp.extend(valid_line_labels)
            self.ddsn_label.extend(valid_line_labels)

        ### START 整体（图片和box）缩放 ###
        self.image = self.image.resize((self.final_width, self.final_height))
        leftdict = {} # 左侧box
        rightdict = {} # 右侧box
        totallist = [] # 单栏
        if self.pattern == 'ppt':
            labels = self.ppt_label
        elif self.pattern == 'cv':
            labels = self.ddsn_label
        else:
            labels = self.recnlp
        #遍历缩放，nlp设置阅读顺序
        header = []
        footer = []
        for eachdict in labels:
            if eachdict:
                temp = eachdict['points'][:]
                if not temp:
                    print(eachdict)
                #控制越界
                if temp[0][0] < 0:
                    temp[0][0] = 0 
                    print(eachdict)
                if temp[1][0]>self.reshape_width:
                    temp[1][0]=self.reshape_width
                    print(eachdict)
                
                #point对应放大
                eachdict['points'] = [[temp[i][0]*self.x_ratio, temp[i][1]*self.y_ratio] for i in range(len(temp))]
                #nlp阅读顺序
                if self.pattern == 'nlp':
                    # 0和100 对应页眉和页脚，将非页眉页脚的points,按照其所在侧（左侧or右侧）进行分别存放
                    # 以字典形式，key为左上角纵坐标，value为整个labeldict
                    if eachdict['group'] not in [0, 100]:
                        #重复纵坐标处理
                        while eachdict['points'][0][1] in leftdict.keys() or eachdict['points'][0][1] in rightdict.keys():  
                            eachdict['points'][0][1] += 0.01
                        #左侧
                        if eachdict['points'][-1][0] < 0.5*self.final_width:
                            leftdict[eachdict['points'][0][1]] = eachdict
                        #右侧
                        elif 0.5*self.final_width < eachdict['points'][0][0]:
                            rightdict[eachdict['points'][0][1]] = eachdict
                        #全栏情况，两侧都添加该纵坐标，同时totallist保存该dict
                        else:
                            leftdict[eachdict['points'][0][1]] = eachdict
                            rightdict[eachdict['points'][0][1]] = eachdict
                            totallist.append(eachdict)
                    #页脚label单独放进footer
                    elif eachdict['group'] == 100:
                        footer.append(eachdict)
                    #页眉label单独放进header
                    else:
                        header.append(eachdict)
        if self.pattern == 'nlp':
            #从页眉开始，group为0
            result = header
            #左右栏纵坐标按从上到下顺序排列
            leftlist = list(leftdict.keys())
            rightlist = list(rightdict.keys())
            leftlist.sort()
            rightlist.sort()
            
            g = 0 # 新group
            preg = 0 # 上一目标的group
            prelabel = '' # 上一目标的类别
            #按从上至下，从左至右的规则进行group的重新设置
            while leftlist or rightlist:
                # 左侧非全栏的labeldict进行设置group
                while leftlist and leftdict[leftlist[0]] not in totallist:
                    curdict = leftdict[leftlist.pop(0)] # 当前labeldict
                    # 如果该labeldict的旧group和上一labeldict的旧group一致，那么新group也一致
                    if curdict['group'] == preg:
                        curdict['group'] = g
                    # 如果和上一labeldict旧group不一致，说明是新的group
                    else:
                        #先把该labeldict的旧group保存，用于对下面labeldict的同群组判断
                        preg = curdict['group']
                        #如果 上一labeldict为章节类，当前labeldict为textline，二者划为同group；否则，group+1更新
                        if prelabel != 'section' or curdict['label'] != 'textline':
                            g += 1
                        # 当前类别保存记录
                        prelabel = curdict['label']
                        # 设置新group
                        curdict['group'] = g
                    # result保存新的labeldict
                    result.append(curdict)
                # 右侧非全栏labeldict进行设置group，当右侧全部设置完毕或者遇到全栏则结束，同上面左侧处理方式
                while rightlist and rightdict[rightlist[0]] not in totallist:
                    curdict = rightdict[rightlist.pop(0)]
                    if curdict['group'] == preg:
                        curdict['group'] = g
                    else:
                        preg = curdict['group']
                        if prelabel != 'section' or curdict['label'] != 'textline':
                            g += 1
                        prelabel = curdict['label']
                        curdict['group'] = g
                    result.append(curdict)
                # 左侧，右侧均处理完毕，如果还有坐标，说明是全栏
                if leftlist or rightlist:
                    # 全栏labeldict
                    curdict = leftdict[leftlist.pop(0)]
                    # 左右侧都pop出，因为当时全栏的dict左右侧都添加了
                    rightlist.pop(0)
                    #处理方式同理
                    if curdict['group'] == preg:
                        curdict['group'] = g
                    else:
                        preg = curdict['group']
                        if prelabel != 'section' or curdict['label'] != 'textline':
                            g += 1
                        prelabel = curdict['label']
                        curdict['group'] = g
                    result.append(curdict)
            # 全部处理完毕再处理footer的group
            for each in footer:
                each['group'] = g+1
            # 总label
            labels = result+footer
        # cv 生成json
        if self.pattern == 'ppt' or self.pattern == 'cv':
            self.convert_to_json(labels)
        # nlp生成rec
        else:
            self.nlprec(labels)
        self.save_img()
        ### 全部结束 ###
    def nlprec(self, labels):
        '''
        生成rec
        '''
        recf_filename = self.output_path[:-4]+'.recf'
        with open(recf_filename, 'w') as f:
            for eachlabeldict in labels:
                point = eachlabeldict['points']
                if len(point) == 2: # 两点直接取box
                    box = [point[0][0], point[0][1], point[1][0], point[1][1]]
                else: # 多点取最大box
                    x = [point[i][0] for i in range(len(point))]
                    y = [point[i][1] for i in range(len(point))]
                    box = [min(x), min(y), max(x), max(y)]
                # print(eachlabeldict)
                content = '%d %s %d %d %d %d %d\n' % (int(nlpdict[eachlabeldict['label']]), eachlabeldict['content'], 
                int(box[0]), int(box[1]), int(box[2])+1, int(box[3])+1, int(eachlabeldict['group']))
                f.write(content)
    def convert_to_json(self, object_labels):
        '''
        生成json
        '''
        json_label = {"version": "4.0.4",
                      "flags": {},
                      "shapes": [],
                      "imageWidth": float(self.image.size[0]),
                      "imageHeight": float(self.image.size[1]),
                      "imageData": None
                      }
        img_name = os.path.basename(self.output_path)  # 只有图片名
        json_label["imagePath"] = img_name
        for object_label in object_labels:
            if object_label and object_label["points"] and len(object_label["points"]) != 0:
                single_dict = {}
                label = object_label["label"]
                points = object_label["points"]
                single_dict["label"] = label
                single_dict["points"] = []
                single_dict["group_id"] = None
                single_dict["shape_type"] = object_label["type"]
                single_dict["flags"] = {}
                for point in points:
                    single_dict["points"].append([float(point[0]), float(point[1])])
                json_label["shapes"].append(single_dict)
        labeldir = os.path.dirname(self.output_path)
        filename = os.path.join(labeldir, img_name.split(".")[0] + ".json")
        with open(filename, 'w') as file_obj:
            json.dump(json_label, file_obj)
    def add_handwritten(self, bbox, figure_path):
        '''
        :param bbox: 待填充位置
        :param figure_path: 图路径
        :return: 标签
        '''
        x0, y0, width, height = bbox
        added_figure, new_width, new_height = scale_img(bbox, figure_path)
        self.image.paste(added_figure, (x0, y0))
        points = [[x0, y0], [x0 + new_width, y0 + new_height]]
        object_label = {"label": "handwritten", "points": points, "type": "rectangle"}
        return object_label

    def add_list(self, bbox, group):
        '''
        bbox: 填充位置
        group: 群组
        '''
        #列表符号
        listpattern = random.choice(list('*▲Δ●√'))
        #间距，字号，字体，颜色
        interval = random.choice([i for i in range(10, 15)])
        font_size = np.random.choice([i for i in range(19, 24)], p=[0.1, 0.3, 0.4, 0.15, 0.05])
        if self.pattern == 'ppt':
            font_size += 15
        font = random.choice(self.fonts)
        color = random.choices([(0, 0, 0), (255, 0, 0), (0, 0, 255)], [8, 1, 1])[0]
        #版面统一
        if self.same_elem:
            #列表属于文本，因此与text一致
            if not self.text:
                self.text['listpattern'] = listpattern
                self.text['font_size'] = font_size
                self.text['font'] = font
                self.text['interval'] = interval
                self.text['color'] = color
            else:
                font_size = self.text['font_size']
                font = self.text['font']
                interval = self.text['interval']
                color = self.text['color']
                if 'listpattern' in self.text.keys():
                    listpattern = self.text['listpattern']
                else:
                    self.text['listpattern'] = listpattern

        font = ImageFont.truetype(font, font_size)
        image_draw = ImageDraw.Draw(self.image)
        labels = [] #存放列表label
        linenum = bbox[3] // (font_size+interval) #box可支持行数
        eachbbox_height = font_size+interval # 一行高度
        textnum = bbox[2]//font_size - 2 #每行可容纳中文字体个数，-2是去除开头的pattern
        
        text = self.list_loader.get_text(3000) #列表语料
        
        iflistpattern = True #是否有开头的图案
        startposition = 0 #语料开始位置

        left_point, right_point = [], []

        for i in range(linenum): #每一行填充
            eachbbox = [bbox[0], bbox[1] + i*eachbbox_height, bbox[2], eachbbox_height]
            #当前是否有起始图案
            if iflistpattern:
                #判断下一行是否需要图案，如果下一行需要图案，则该行长度随机；如果下一行不需要图案，该行长度填满
                iflistpattern = random.choice([True, False])
                if not iflistpattern:
                    #循环判定
                    endposition = startposition + textnum
                    patternx, patterny = image_draw.textsize(listpattern+'   ', font=font)
                    while 1:
                        content = text[startposition: endposition]
                        x, y = image_draw.textsize(content, font=font)
                        
                        if x < eachbbox[2]-patternx:
                            endposition += 1
                        else:
                            break
                        if len(content) == len(text[startposition: endposition+1]):
                            endposition += 1
                            break
                    endposition -= 1
                else:
                    endposition = random.randint(startposition+1, startposition+textnum)

                textcontent = listpattern+'   '+ text[startposition: endposition]
                line_size_x, line_size_y = image_draw.textsize(textcontent, font=font)
                point = [[eachbbox[0], eachbbox[1]], [eachbbox[0]+line_size_x, eachbbox[1]+line_size_y+interval]]
                if needimg:
                    image_draw.text((point[0][0], point[0][1]), textcontent, fill=color, font=font)
            #当前无起始图案  
            else:
                iflistpattern = random.choice([True, False])
                #同上进行循环判断，根据下一行是否有起始图案进行填充
                if not iflistpattern:
                    endposition = startposition + textnum
                    patternx, patterny = image_draw.textsize('    ', font=font)
                    while 1:
                        content = text[startposition: endposition]
                        x, y = image_draw.textsize(content, font=font)
                        if x < eachbbox[2]-patternx:
                            endposition += 1
                        else:
                            break
                        if len(content) == len(text[startposition: endposition+1]):
                            endposition += 1
                            break
                    endposition -= 1
                else:
                    endposition = random.randint(startposition+1, startposition+textnum)
                start = '    '
                textcontent = text[startposition: endposition]
                line_size_x, line_size_y = image_draw.textsize(textcontent, font=font)
                space_x, space_y = image_draw.textsize(start, font=font)
                point = [[eachbbox[0]+space_x, eachbbox[1]], [eachbbox[0]+space_x+line_size_x, eachbbox[1]+line_size_y+interval]]
                #需要图片才填图
                if needimg:
                    image_draw.text((point[0][0], point[0][1]), textcontent, fill=color, font=font)
            startposition = endposition
            # nlp的label因为是一行一行的，所以会有多个listlabel，group也为同一group
            labels.append({'label': 'list', 'points': point, 'type':'rectangle', 'content':textcontent, 'group':group})
            # cv 记录 每一行point的坐标点，分左右侧，方向统一从上至下
            if self.pattern != 'nlp':
                left_point.append([point[0][0], point[0][1]])
                left_point.append([point[0][0], point[1][1]])
                right_point.append([point[1][0], point[0][1]])
                right_point.append([point[1][0], point[1][1]])
        # cv labeldict 设置
        if self.pattern != 'nlp' and left_point and right_point:
            # 左侧点坐标顺序变为从下至上
            left_point.reverse()
            # 此时 rightpoint+leftpoint 变为从右上侧向下，然后到右下侧，然后左下侧，然后左上侧，形成闭环polygon
            self.ppt_label.append({'label': 'list', 'points': right_point+left_point, 'type':'polygon'})
            self.ddsn_label.append({'label': 'list', 'points': right_point+left_point, 'type':'polygon'})
        return labels

    def add_reference(self, bbox):
        #reference section
        reference_title_height = random.randint(25, 40) # section高度
        reference_title_bbox = [bbox[0], bbox[1], bbox[2], reference_title_height]
        title_content = '参考文献' if self.select == 'Chinese' else random.choice(['Reference', 'reference', 'REFERENCE']) #section内容
        #section中加入数字
        if random.randint(0, 3):#75%概率title中含有题号
            start = str(random.randint(1, 9))
            # 是否有小数点
            if random.randint(0, 1):
                start += '.' + str(random.randint(1, 9))
            title_content = start + " " + title_content
        self.add_title(reference_title_bbox, text=title_content, group=self.group) # 填充section
        #reference text
        #与上侧的section有10的间距
        bbox[1] += reference_title_height+10
        bbox[3] -= reference_title_height+10
        #行间距，字号，字体，颜色
        interval = random.choice([i for i in range(10, 15)])
        font_size = np.random.choice([i for i in range(19, 24)], p=[0.1, 0.3, 0.4, 0.15, 0.05])
        font = random.choice(self.fonts)
        color = random.choices([(0, 0, 0), (255, 0, 0), (0, 0, 255)], [8, 1, 1])[0]
        # 版式统一
        if self.same_elem:
            if not self.text:
                self.text['font_size'] = font_size
                self.text['font'] = font
                self.text['interval'] = interval
                self.text['color'] = color
            else:
                if 'font_size' in self.text.keys():
                    font_size = self.text['font_size']
                else:
                    self.text['font_size'] = font_size
                font = self.text['font']
                if 'interval' in self.text.keys():
                    interval = self.text['interval']
                else:
                    self.text['interval'] = interval
                color = self.text['color']
        
        lines = bbox[3] // (font_size + interval)# box可容纳行数
        reference_list = self.reference_loader.get_text(lines)# 取多少行内容，以列表形式保存
        
        font = ImageFont.truetype(font, font_size)
        image_draw = ImageDraw.Draw(self.image)
        st_point = [bbox[0], bbox[1]]
        point_right, point_left = [], [] # 左右侧point，用于生成cv label， 具体解释见 add—list
        # 按行数进行填入，
        while lines:
            reference_content = reference_list.pop() #当前一条参考文献语料
            x, y = image_draw.textsize(reference_content, font) # 长度，高度
            occupied_line = x // bbox[2] + 1 #该语料占了多少行
            chars_per_line = bbox[2] // font_size if self.select == 'Chinese' else bbox[2] * 2 // font_size # 多少字符数（不准确，因为可能有中英混杂）
            if lines < occupied_line:#不够了就截断
                occupied_line = lines
            lines -= occupied_line # 剩余lines减少
            start = 0 #起始索引，用于语料的提取
            for i in range(occupied_line): # 开始填充当前条的语料
                preleng = 0 #
                end = start + chars_per_line # 尾部索引
                # 循环判定，获得能保证每行元素填满的尾部索引值
                while 1:
                    perline_text = reference_content[start: end]
                    perlinex, perliney = image_draw.textsize(perline_text, font)
                    if perlinex == preleng:
                        break
                    if perlinex > int(bbox[2]):
                        end -= 1
                        perline_text = reference_content[start: end]
                        perlinex = bbox[2]
                        break
                    preleng = perlinex
                    end += 1
                start = end# 将起始索引变为当前的尾部索引，用于下一行进行语料提取
                if needimg:
                    image_draw.text(st_point, perline_text, fill=color, font=font)
                # 点坐标，左上，右下
                point = [st_point[:], [st_point[0]+perlinex, st_point[1]+font_size+interval]]
                st_point[1] += font_size + interval
                self.recnlp.append({'label': 'reference', 'points': point, 'type':'rectangle', 'content':perline_text, 'group':self.group})
                # cv版面label整理
                if self.pattern == 'cv':
                    point_left.extend([ [point[0][0], point[0][1]] , [point[0][0], point[1][1]] ])
                    point_right.extend([ [point[1][0], point[0][1]] , [point[1][0], point[1][1]] ])
        # 所有reference填充完毕后，nlp的group进行更新
        self.group += 1
        #cv label设置
        if self.pattern == 'cv':
            point_right.reverse()
            self.ddsn_label.append({"label": 'reference', "points": point_left+point_right, "type": "polygon"})
    def add_abstract(self, bbox):
        title_up = random.randint(0, 1) # 50%概率"摘要"二字单独一行或者在内容的开头
        if title_up: # 摘要单独一行就当做section进行填充，同上add-reference
            title_height = random.randint(25, 40)
            title_bbox = [bbox[0], bbox[1], bbox[2], title_height]
            title_content = '摘要' if self.select == 'Chinese' else random.choice(['Abstract', 'ABSTRACT', 'abstract'])
            self.add_title(title_bbox, text=title_content, group=self.group, center=0)
            bbox[1] += title_height+10
            bbox[3] -= title_height+10
        # 摘要文本内容，取2k字符数
        text = self.abstract_loader.get_text(2000)
        if not title_up: #“摘要”在内容开头就在2000字符串的开头添加
            title_content = random.choice(['摘 要', '摘要']) if self.select == 'Chinese' else random.choice(['Abstract', 'ABSTRACT', 'abstract'])
            text = title_content + ' : ' + text
        #填充摘要内容
        self.add_text(bbox, text, group=self.group, type='abstract')
        self.group += 1
    def add_text(self, bbox, text, font=None, fontsize=None, stroke_width=0, INTERVAL=None, retract=2, color=None,
                 type="textline", group=None):
        '''
        填充文本函数
        :param bbox: 待填充文本的bbox
        :param text: 待填充的文本
        :param font: 字体
        :param font_size: 字体大小
        :param retract:
        :param color:
        :param type: 类型
        :return:
        '''
        text_labels = []
        bottom_rights = []
        if (bbox[3] < 0):
            return
        # 字体，行间距，字号
        if not font:
            font = random.choice(self.fonts)
        if isinstance(INTERVAL, int):
            interval = INTERVAL
        else:
            interval = random.choice([i for i in range(10, 15)])  # 行间距
        if isinstance(fontsize, int):
            font_size = fontsize
        else:
            font_size = np.random.choice([i for i in range(19, 24)], p=[0.1, 0.3, 0.4, 0.15, 0.05])
        if self.pattern == 'ppt':
            font_size += 15
        # 统一版面
        if self.same_elem and type in ['textline', 'abstract']:
            if not self.text:
                self.text['font_size'] = font_size
                self.text['font'] = font
                self.text['interval'] = interval
                self.text['color'] = color
            else:
                if 'font_size' in self.text.keys():
                    font_size = self.text['font_size']
                else:
                    self.text['font_size'] = font_size
                font = self.text['font']
                if 'interval' in self.text.keys():
                    interval = self.text['interval']
                else:
                    self.text['interval'] = interval
                color = self.text['color']
        if (bbox[3] > 200 and type == "textline"):  # 当一个文本bbox的高度大于100 以一定的概率把bbox分成多段，加强分段能力
            r = random.choice([0] + [1 for i in range((bbox[3]-200)//(font_size+interval)+1)]) #text_box越高，分段概率越高
            if (r):  # 概率分段
                lineheight = font_size+interval # 每行高度
                para_num = int(bbox[3]) // lineheight #总行数
                startbox = [bbox[0], bbox[1], bbox[2], 0] #每行的box
                count = -1 
                for i in range(para_num):
                    startbox[3] += lineheight
                    if ((i-count) == 2 and random.randint(0, 4)) or (i-count) == 3 or i == (para_num-1):
                        para_bbox = startbox[:]
                        startbox[1] += startbox[3]
                        startbox[3] = 0
                        count = i
                    
                        text_label, cvpoint = self._draw_text(text, font, font_size, para_bbox, interval, retract,
                                                                color, group=self.group, type=type)
                        self.group += 1
                return text_labels, bottom_rights
        if type == 'textline':
            text_label, cvpoint = self._draw_text(text, font, font_size, bbox, interval, retract, color,
                                                   stroke_width=stroke_width, type=type, group=self.group)
            self.group += 1
        elif type in ['caption', 'abstract']:
            text_label, cvpoint = self._draw_text(text, font, font_size, bbox, interval, retract, color,
                                                   stroke_width=stroke_width, type=type, group=group)
        else:
            text_label, cvpoint = self._draw_text(text, font, font_size, bbox, interval, retract, color,
                                                   stroke_width=stroke_width, type=type)
        return text_label, cvpoint

    def add_seal(self, bbox, figure_path):
        '''
        添加印章
        :param bbox:
        :param figure_path:
        :return:
        '''
        seal = Image.open(figure_path)
        seal = transparent_back(seal)
        self.image = blend_two_img(self.image, seal, bbox)

        object_label = {"label": "seal", "points": [[bbox[0], bbox[1]], [bbox[0] + bbox[2], bbox[1] + bbox[3]]],
                        "type": "rectangle"}
        return object_label

    def add_caption(self, fig_tab_box, usage, group='None', need_caption=True):
        '''
        添加caption标题
        '''
        #25%概率没有caption或者指定
        if (random.randint(0, 3) == 0 and need_caption == True) or need_caption == False:
            return fig_tab_box[2], fig_tab_box[3], [[fig_tab_box[0], fig_tab_box[1]],[fig_tab_box[0] + fig_tab_box[2],fig_tab_box[1] + fig_tab_box[3]]], None, None, None, []
        caption_fontsize = random.choice([i for i in range(19, 22)])  # caption字体大小
        interval = 6 # 行间距 单位像素
        font = random.choice(self.fonts)# 字体列表
        color = random.choices([(0, 0, 0), (255, 0, 0), (0, 0, 255)], [8, 1, 1])[0]
        #同步
        if self.same_elem:
            if not self.caption:
                self.caption['font_size'] = caption_fontsize
                self.caption['font'] = font
                self.caption['interval'] = interval
                self.caption['color'] = color
            else:
                caption_fontsize = self.caption['font_size']
                font = self.caption['font']
                interval = self.caption['interval']
                color = self.caption['color']
        FONT = ImageFont.truetype(font, caption_fontsize)
        draw = ImageDraw.Draw(self.image)
        
        addition_length = False #是否扩长语料(用于英文长caption)
        caption_out = False #（英文的特征符 figure 1 / table 3.2 是否单独提出）
        
        #caption内容
        if self.select == 'English' and fig_tab_box[3] > 300 and random.randint(0, 1): #英文caption扩长
            if random.randint(0, 1): # 50%概率特征符提出
                caption_out = True
            addition_length = True 
            caption_text = self.caption_loader.get_text() # 取一行caption
            h = random.choice([3, 3, 4, 4, 4, 5, 5]) # caption 高度
            x, y = draw.textsize(caption_text, font=FONT)
            while x // fig_tab_box[2]+1 < h: # 如果填不满 h 高度则再取一行caption进行叠加
                cur_caption_split = self.caption_loader.get_text().split(' ')[2:]
                if not cur_caption_split:
                    continue
                caption_text += ' ' + ' '.join(cur_caption_split)
                x, y = draw.textsize(caption_text, font=FONT)
        else: # caption不扩长
            caption_text = self.caption_loader.get_text()  # caption文本
        # caption前缀
        key =  {'English':{'figure': ['Figure', 'FIGURE', 'figure', 'Fig', 'FIG', 'fig'], 'table': ['table', 'TABLE', 'Table', 'tab', 'Tab', 'TAB']},
                'Chinese': {'figure': ['图'], 'table': ['表']}}
        pattern = {'English':{'figure': ['table', 'tab', 'Tab', 'TAB', 'TABLE', 'Table'], 'table': ['Figure', 'Fig', 'FIG', 'FIGURE', 'fig', 'figure']},
                'Chinese': {'figure': ['表'], 'table': ['图']}}
        #判断是否存在特征符，如果存在再判断是否正确，将不正确的特征符进行修正
        skip = False
        for eachk in key[self.select].keys():
            if skip:
                break
            for each in key[self.select][eachk]:
                if each == caption_text[:len(each)]:
                    if eachk != usage:
                        caption_text = caption_text.replace(each, random.choice(pattern[self.select][eachk]))
                    skip = True
                    break
        # 不存在特征符的情况，随机添加特征符
        if not skip:
            start = ''
            # 是否加小数点
            if random.randint(0, 1):
                if random.randint(0, 1):
                    start += '.' + str(random.randint(1, 9))
                else:
                    start += '-' + str(random.randint(1, 9))
            # 是否加冒号
            if random.randint(0, 1):
                start += ':' if self.select == 1 else '.'
            start += ' '
            if self.select == 'Chinese':  # 中文
                if usage == 'figure':
                    start = '图 ' + str(random.randint(1, 20)) + start  # 图号
                elif usage == 'table':
                    start = '表 ' + str(random.randint(1, 20)) + start  # 表号
                else:
                    start = ''
            elif self.select == 'English':  # 英文
                if usage == 'figure':
                    start = random.choice(['Figure ', 'Fig ', 'FIG ']) + str(
                        random.randint(1, 20)) + start  # 图号
                elif usage == 'table':
                    start = random.choice(['Table ', 'TABLE ']) + str(random.randint(1, 20)) + start  # 表号
                else:
                    start = ''
            caption_text = start + caption_text
        
        x0, y0, Width, Height = fig_tab_box
        caption_validline_label = []#保存caption线的label
        selected_width = random.choice([1, 2, 3])  # 线的宽度
        gap = 2*interval #caption和figure距离
        width = int(Width) #box宽度
        # 特征符检索提出为front，剩下部分为caption-text
        if caption_out:
            captiontext_list = caption_text.split(' ')
            front = captiontext_list.pop(0)
            if bool(re.search(r'\d', captiontext_list[0])):
                front += ' ' + captiontext_list.pop(0)
            caption_text = ' '.join(captiontext_list)

        x, y = draw.textsize(caption_text, font=FONT) #caption文本长度
        caption_rows = x // width + 1 #caption行数
        #特征符提出则文本长度需要增加一行
        if caption_out:
            caption_rows += 1
        margin_length = (width-x) // 2 if caption_rows == 1 else 0 # 每行两端的空白长度，单行进行居中，多行不居中
        caption_height = caption_rows * (caption_fontsize + interval)  # caption高度
        height = int(Height - caption_height - gap) # figure/table 高度

        # 选择caption在图上方还是下方（1为上方，0为下方）
        top_or_bottom = random.randint(0, 1)
        # 表格caption恒定在上方
        if usage == 'table':
            top_or_bottom = 1
        # 英文caption长度增加，则默认在下方
        if addition_length:
            top_or_bottom = 0
        if top_or_bottom:
            # caption在上方
            # 如果只有一行则有3/4的概率居中，不止一行则不居中
            if caption_rows == 1 and random.randint(0, 3):  # 居中
                caption_bbox = [x0 + margin_length, y0+interval, int(width - 2 * margin_length), caption_height]
                center = True
            else:  # 左对齐
                caption_bbox = [x0, y0+interval, width, caption_height]
                center = False
            # 去除caption后的剩余用来填充图表的box points
            points = [[x0, y0 + caption_height + gap], [x0 + width, y0 + caption_height + gap + height]]

            #33%概率图表左下方有注解
            if random.randint(0, 2) == 0:
                downtext_interval = 4
                downtext_fontsize = caption_fontsize - 2
                points[1][1] = points[1][1] - downtext_fontsize - 3*downtext_interval
                height = height - downtext_fontsize - 3*downtext_interval
                downtext_point = [[x0, points[1][1]+downtext_interval], [x0 + random.randint(width//3, width), points[1][1]+downtext_interval+downtext_fontsize]]
                FONT = ImageFont.truetype(font,downtext_fontsize)
                downtext_length = (downtext_point[1][0] - downtext_point[0][0]) // downtext_fontsize
                if self.select == 'English':
                    downtext_length *= 2
                textcontent = ''
                while len(textcontent) < downtext_length:
                    content = self.caption_loader.get_text()[4:] if self.select == 'Chinese' else ' '.join(self.caption_loader.get_text().split(' ')[2:])
                    if not content:
                        continue
                    textcontent += content + ' '
                textcontent = textcontent[:downtext_length]
                downtext_x, downtext_y = draw.textsize(textcontent, font=FONT)
                downtext_point[1][0] = x0 + downtext_x
                if needimg:
                    draw.text((downtext_point[0][0], downtext_point[0][1]), text=textcontent, font=FONT, fill=(0, 0, 0))
                self.recnlp.append({"label": "caption", "points": downtext_point, "type": "rectangle", 'content':textcontent, 'group':group})
                self.ddsn_label.append({"label": "caption", "points": downtext_point, "type": "rectangle"})
                #%50概率注解与图表之间有实线
                if random.randint(0, 1):
                    point_validline = [[downtext_point[0][0], downtext_point[0][1]-downtext_interval//2], [x0+width, downtext_point[0][1]-downtext_interval//2]]
                    if needimg:
                        draw.line((point_validline[0][0], point_validline[0][1], point_validline[1][0], point_validline[1][1]), fill=random_get_color(), width=selected_width)
                    point_validline[0][1] -= (1 + selected_width//2)
                    point_validline[1][1] += (1 + selected_width//2)
                    caption_validline_label.append({"label": "ValidLine", "points": point_validline, "type": "rectangle", 'content':'<validline>', 'group':group})

            #20%概率caption上下有实线
            if random.randint(0, 4)==0:
                if center == False:
                    point_validlineup = [[x0, caption_bbox[1]-interval], [x0+random.randint(caption_bbox[2], width), caption_bbox[1]-interval]]
                    point_validlinedown = [[x0, caption_bbox[1]+caption_bbox[3]], [x0+random.randint(caption_bbox[2], width), caption_bbox[1]+caption_bbox[3]]]
                else:
                    distance = random.randint(0, caption_bbox[0]-x0)
                    point_validlineup = [[caption_bbox[0]-distance, caption_bbox[1]-interval], [caption_bbox[0]+caption_bbox[2]+distance, caption_bbox[1]-interval]]
                    point_validlinedown = [[caption_bbox[0]-distance, caption_bbox[1]+caption_bbox[3]], [caption_bbox[0]+caption_bbox[2]+distance, caption_bbox[1]+caption_bbox[3]]]
                validline_points = [point_validlineup, point_validlinedown]
                for each in validline_points:
                    if needimg:
                        draw.line((each[0][0], each[0][1], each[1][0], each[1][1]), fill=random_get_color(), width=selected_width)
                    each[0][1] -= (1 + selected_width//2)
                    each[1][1] += (1 + selected_width//2)
                    caption_validline_label.append({"label": "ValidLine", "points": each, "type": "rectangle", 'content':'<validline>', 'group':group})

        else:
            # caption在下方
            # 去除caption后的剩余用来填充图表的box points
            points = [[x0, y0], [x0 + width, y0 + height]]
            # 一行居中，两行居左
            caption_bbox = [x0 + margin_length, y0 + height + int(0.7*gap), int(width - 2 * margin_length), caption_height]

        

        # 文字添加
        caption_bbox[3] += interval # caption和下面的内容增加间隔
        # 英文下方特征符单独一行的情况先单独保存该行的label
        if caption_out:
            x_pattern, y_pattern = draw.textsize(front, FONT)
            if needimg:
                draw.text((caption_bbox[0], caption_bbox[1]), text=front, fill=color, font=FONT)
            caption_out_point = [ [caption_bbox[0], caption_bbox[1]], [caption_bbox[0]+x_pattern, caption_bbox[1]+y_pattern] ]
            self.recnlp.append({"label": "caption", 
            "points": caption_out_point, 
            "type": "rectangle", 'content': front, 'group':group})
            # 剩余box
            caption_bbox[1] += y_pattern + interval
            caption_bbox[3] -= y_pattern + interval
        # 在剩余box中填充caption语句
        caption_label, cvpoint = self.add_text(caption_bbox, caption_text, font=font,
                                                    stroke_width=0,
                                                    fontsize=caption_fontsize, INTERVAL=interval, retract=0,
                                                    type="caption", color=color, group=group)
        # 返回的剩余caption和特征符合并成一个 polygon label
        if caption_out:
            cvpoint += [[caption_out_point[1][0], caption_out_point[1][1]], 
                        [caption_out_point[1][0], caption_out_point[0][1]],
                        [caption_out_point[0][0], caption_out_point[0][1]],
                        [caption_out_point[0][0], caption_out_point[1][1]]]
        # cv caption label保存
        self.ddsn_label.append({"label": 'caption', "points": cvpoint, "type": "polygon"})
        return width, height, points, caption_bbox, caption_label, None, caption_validline_label

    def add_simple_figure(self, bbox, figure_path, add_table=False, usage='figure', keep_ratio=True, need_caption=True):
        '''
        图片填充
        '''
        edge_width, edge_height = 0, 0  # figure edge边缘宽度 每一边的edge宽度是一半
        points1 = [(bbox[0], bbox[1]), (bbox[0] + bbox[2], bbox[1] + edge_height / 2)]  # edge上边bbox
        points2 = [(bbox[0], bbox[1]), (bbox[0] + edge_width / 2, bbox[1] + bbox[3])]  # edge左边bbox
        points3 = [(bbox[0] + bbox[2] - edge_width / 2, bbox[1]), (bbox[0] + bbox[2], bbox[1] + bbox[3])]  # edge右边边缘
        points4 = [(bbox[0], bbox[1] + bbox[3] - edge_height / 2), (bbox[0] + bbox[2], bbox[1] + bbox[3])]  # edge下边边缘
        new_bbox = [0, 0, 0, 0]
        new_bbox[0] = bbox[0] + int(edge_width / 2)
        new_bbox[1] = bbox[1] + int(edge_height / 2)
        new_bbox[2] = bbox[2] - edge_width
        new_bbox[3] = bbox[3] - edge_height
        bbox = new_bbox  # 图像加边之后的new_bbox
        
        if usage != 'figure':# 填充的图片用作figure类
            width, height, points, caption_bbox, caption_label, bottom_right = bbox[2], bbox[3], [[bbox[0], bbox[1]],
                                                                                                  [bbox[0] + bbox[2],
                                                                                                   bbox[1] + bbox[
                                                                                                       3]]], None, None, None
        else: # 填充的图片用作图标类
            width, height, points, caption_bbox, caption_label, bottom_right, caption_validline_label = self.add_caption(bbox, usage=usage, group=self.group, need_caption=need_caption)
        # 获取去除白边的图片语料和图片宽度
        added_figure, fillimg_width = reshape_img(figure_path, (width, height), keep_ratio=keep_ratio,
                                                  margin_crop=MARGIN_CROP)
        # 图片居中
        width_offset = (points[1][0] - points[0][0] - fillimg_width) // 2
        points[0][0] += width_offset
        points[1][0] -= width_offset
        # 填充
        if needimg:
            self.image.paste(added_figure, (points[0][0], points[0][1]))
        # points为去除caption后的剩余用来填充图表的box points
        object_label = {"label": "figure", "points": points, "type": "rectangle", 'content': '<figure>'}  # 图标标签
        if bottom_right:
            points2 = [points2[0], (points2[1][0], bottom_right[1])]
        if bottom_right:
            points3 = [points3[0], (points3[1][0], bottom_right[1])]
        if bottom_right:
            points4 = [(points4[0][0], bottom_right[1]), (points4[1][0], bottom_right[1] + int(edge_width / 2))]

        edge_label1 = {"label": "figureedge", "points": points1, "type": "rectangle"}
        edge_label2 = {"label": "figureedge", "points": points2, "type": "rectangle"}
        edge_label3 = {"label": "figureedge", "points": points3, "type": "rectangle"}
        edge_label4 = {"label": "figureedge", "points": points4, "type": "rectangle"}
        edge_labels = [edge_label1, edge_label2, edge_label3, edge_label4]

        if usage == 'figure': # 保存figure-label
            object_label['group'] = self.group # 群组
            self.recnlp.extend([object_label]+caption_validline_label) # 图片label和注解线label 在nlp保存
            self.group += 1
            self.ddsn_label.extend([object_label]+caption_validline_label) # 图片label和注解线label 在cv保存
            return object_label, caption_label, edge_labels, caption_bbox, caption_validline_label
        else: # 图标
            return object_label, caption_label, edge_labels, caption_bbox
    def add_table(self, bbox, table_path, add_figure=False, keep_ratio=True, need_caption=True):
        '''
        处理方法类似图片的填充
        :param bbox: table bbox
        :param table_path: table图片路径
        :return:
        table标签
        tableedge标签
        '''
        new_bbox = [0, 0, 0, 0]
        edge_width, edge_height = 0, 0  # table_edge宽度
        points1 = [(bbox[0], bbox[1]), (bbox[0] + bbox[2], bbox[1] + edge_height / 2)]  # tableedge上边
        points2 = [(bbox[0], bbox[1]), (bbox[0] + edge_width / 2, bbox[1] + bbox[3])]  # tableedg左边
        points3 = [(bbox[0] + bbox[2] - edge_width / 2, bbox[1]), (bbox[0] + bbox[2], bbox[1] + bbox[3])]  # tableedge右边
        points4 = [(bbox[0], bbox[1] + bbox[3] - edge_height / 2),
                   (bbox[0] + bbox[2], bbox[1] + bbox[3])]  # tableedge下边

        # 加edge之后新的table bbox
        new_bbox[0] = int(bbox[0] + edge_width / 2)
        new_bbox[1] = int(bbox[1] + edge_height / 2)
        new_bbox[2] = int(bbox[2] - edge_width)
        new_bbox[3] = int(bbox[3] - edge_height)
        bbox = new_bbox
        # 填充表格caption并获取剩余用来填充表格的box-point
        width, height, points, caption_bbox, caption_label, bottom_right, caption_validline_label = self.add_caption(bbox, usage='table', group=self.group, need_caption=need_caption)
        # 处理表格语料
        added_table, fillimg_width = reshape_img(table_path, (width, height), keep_ratio=keep_ratio,
                                                 margin_crop=MARGIN_CROP)  # reshape之后的table
        # 居中
        width_offset = (points[1][0] - points[0][0] - fillimg_width) // 2
        points[0][0] += width_offset
        points[1][0] -= width_offset
        if needimg:
            self.image.paste(added_table, (points[0][0], points[0][1]))
        
        object_label = {"label": "table", "points": points, "type": "rectangle", 'content':'<table>', 'group':self.group}
        if bottom_right:
            points2 = [points2[0], (points2[1][0], bottom_right[1])]
        if bottom_right:
            points3 = [points3[0], (points3[1][0], bottom_right[1])]
        if bottom_right:
            points4 = [(points4[0][0], bottom_right[1]), (points4[1][0], bottom_right[1] + int(edge_width / 2))]
        edge_label1 = {"label": "tableedge", "points": points1, "type": "rectangle"}
        edge_label2 = {"label": "tableedge", "points": points2, "type": "rectangle"}
        edge_label3 = {"label": "tableedge", "points": points3, "type": "rectangle"}
        edge_label4 = {"label": "tableedge", "points": points4, "type": "rectangle"}
        edge_labels = [edge_label1, edge_label2, edge_label3, edge_label4]
        # label 保存
        self.recnlp.extend([object_label]+caption_validline_label)
        self.group += 1
        self.ddsn_label.extend([object_label]+caption_validline_label)
        return object_label, caption_label, edge_labels, caption_bbox, caption_validline_label

    def gen_edge_line(self):
        '''
        产生边框线
        '''

        labels = [] 
        edge_width = [1, 2] 
        selected_width = random.choice(edge_width)  # 页面框线的宽度
        # 产生页面的边框线
        ## 上下框线
        draw = ImageDraw.Draw(self.image)
        if random.randint(0, 9) == 0: # 10%概率上下的框线较粗
            updown_selected_width = random.choice([3, 4, 5])
        else:
            updown_selected_width = selected_width
        # 上框线填充
        if needimg:
            draw.line((self.top_left[0], self.top_left[1], self.bottom_right[0], self.top_left[1]), fill=random_get_color(),
                    width=updown_selected_width)
        #上侧validline-label保存
        new_upper = self.top_left[1] - int(selected_width / 2)
        new_lower = new_upper + selected_width
        label = {"label": "ValidLine", "points": [[self.top_left[0], new_upper], [self.bottom_right[0], new_lower]],
                 "type": "rectangle", 'content': '<validline>', 'group':self.group}
        labels.append(label)
        #下框线填充
        if needimg:
            draw.line((self.top_left[0], self.bottom_right[1], self.bottom_right[0], self.bottom_right[1]),
                    fill=random_get_color(), width=updown_selected_width)
        #下侧validline-label保存
        new_upper = self.bottom_right[1] - int(selected_width / 2)
        new_lower = new_upper + selected_width
        label = {"label": "ValidLine", "points": [[self.top_left[0], new_upper], [self.bottom_right[0], new_lower]],
                 "type": "rectangle", 'content': '<validline>', 'group':self.group}
        labels.append(label)

        ## 左右框线有1/3概率生成
        if (random.choice([0, 1, 2]) == 0):
            if needimg:
                #左
                draw.line((self.top_left[0], self.top_left[1], self.top_left[0], self.bottom_right[1]),
                        fill=random_get_color(), width=selected_width)
                #右
                draw.line((self.bottom_right[0], self.top_left[1], self.bottom_right[0], self.bottom_right[1]),
                        fill=random_get_color(), width=selected_width)

            new_left = self.top_left[0] - int(selected_width / 2)
            new_right = new_left + selected_width
            label = {"label": "ValidLine", "points": [[new_left, self.top_left[1]], [new_right, self.bottom_right[1]]],
                     "type": "rectangle", 'content': '<validline>', 'group':self.group}
            labels.append(label)

            new_left = self.bottom_right[0] - int(selected_width / 2)
            new_right = new_left + selected_width
            label = {"label": "ValidLine", "points": [[new_left, self.top_left[1]], [new_right, self.bottom_right[1]]],
                     "type": "rectangle", 'content': '<validline>', 'group':self.group}
            labels.append(label)
        self.group  += 1
        return labels

    def add_footerandheader(self):
        '''
        :param font: 页脚页眉字体
        :param color: 颜色
        :return:
        footerandheader_labels：页脚页眉标签
        all_tubiao_bboxes：图标的bbox
        '''
        all_tubiao_bboxes = []  # 图标_bbox
        color = random.choices([(0, 0, 0), (255, 0, 0), (0, 0, 255)], [8, 1, 1])[0]
        font_size = random.choice([i for i in range(18, 21)])
        font = random.choice(self.fonts)
        #版面元素统一
        if self.same_elem:
            if not self.footerandheader:
                self.footerandheader['color'] = color
                self.footerandheader['font_size'] = font_size
                self.footerandheader['font'] = font
            else:
                color = self.footerandheader['color']
                font_size = self.footerandheader['font_size']
                font = self.footerandheader['font']

        edge_margin = 5 # 页边距
        cur_box = (self.top_left[0], max(0, self.top_left[1] - font_size - edge_margin), self.bottom_right[0], self.top_left[1])
        # 添加页眉
        header_points, header_tubiao_bboxes = self.add_headerorfooter_text(cur_box, "header", font_size, font=font,
                                                                           color=color)  
        if header_tubiao_bboxes: # 保存页眉中的图标box
            all_tubiao_bboxes.extend(header_tubiao_bboxes)

        # 页脚的字体如果不需要版式统一就随机选择
        font = random.choice(self.fonts) if not self.same_elem else self.footerandheader['font']
        cur_box = (self.top_left[0], self.bottom_right[1] + edge_margin, self.bottom_right[0], self.reshape_size[1])
        # 添加页脚
        footer_points, footer_tubiao_bboxes = self.add_headerorfooter_text(cur_box, "footer", font_size, font=font,
                                                                           color=color)
        if footer_tubiao_bboxes: # 保存页脚中的图标box
            all_tubiao_bboxes.extend(footer_tubiao_bboxes)
        #将图标box返回用于在 add-figure中填充
        return None, all_tubiao_bboxes

    def add_headerorfooter_text(self, bbox, dtype, font_size, font=None, color=None):
        '''
        页眉页脚添加
        '''
        color = (0, 0, 0)
        width = bbox[2] - bbox[0]
        page_width = self.bottom_right[0] - self.top_left[0]
        # 一行存在几个页眉（页脚），初始默认是三个，左中右
        three = True
        two = True
        object_num = random.choice([1, 2, 2, 3, 3])  # 随机页脚页眉的数量
        tubiao_bboxes = [] # 保存图标box
        
        image_draw = ImageDraw.Draw(self.image)
        font_file = ImageFont.truetype(font, font_size)

        points = []
        gap = 3  # 图标与页眉页脚的间隔
        max_tubiaoheight = 50  # 图标最大尺寸（50*50）
        min_tubiaoheight = 0  # 图标最小尺寸
        if object_num >= 1:  # 第一个页眉页脚，将其放在页面左上角或者左下角
            st_point = (bbox[0], bbox[1])  # 左上角的坐标
            # 弹出小于页面宽度的语料
            while 1:
                text = self.header_loader.get_text() if dtype == 'header' else self.footer_loader.get_text()  # 读取填充文本
                line_size_x, line_size_y = image_draw.textsize(text, font=font_file)  # 填充文本的长度和高度
                if line_size_x <= page_width:
                    break
            # 如果语料长度 在1/3-1/2， 那么就不可以存在3个页眉（页脚）了
            if page_width // 2 > line_size_x > page_width // 3:
                three = False
            # 如果语料长度大于1/2，那么该行只可以存在一个
            elif line_size_x > page_width // 2:
                two = False
                three = False
            if needimg:
                image_draw.text(st_point, text, font=font_file, fill=color)  # 填充
            # 页眉（页脚）的point
            footheaderpoint = [[st_point[0], st_point[1]], [st_point[0] + line_size_x, st_point[1] + line_size_y]]
            
            if (dtype is "header"):  # 页眉
                self.recnlp.append({'label': 'header', 'points': footheaderpoint, "type": "rectangle", 'content': text, 'group':0})
                self.ddsn_label.append({'label': 'footerandheader', 'points': footheaderpoint, "type": "rectangle"})
                # 在页眉和页面顶部的空间生成随机大小的box用于填充图标
                tubiao_height = int((st_point[1] - gap - 0) * (random.randint(2, 9) / 10))  # 图标高度是随机页眉和顶部高度的20-90%
                # 给限制范围
                if tubiao_height > max_tubiaoheight:  # 大于最大值则设置为最大限制值
                    tubiao_height = max_tubiaoheight
                if tubiao_height > min_tubiaoheight:  # 大于最小值说明满足条件，保存图标的box用于后续的填充，否则不填充图标
                    figurebox = [st_point[0], st_point[1] - gap - tubiao_height, tubiao_height, tubiao_height]
                    figurepoint = [[figurebox[0], figurebox[1]], [figurebox[0]+figurebox[2], figurebox[1]+figurebox[3]]]
                    tubiao_bboxes.append(figurebox)
                    self.recnlp.append({'label': 'figure', 'points': figurepoint, "type": "rectangle", 'content': '<figure>', 'group':0})
                    self.ddsn_label.append({'label': 'figure', 'points': figurepoint, "type": "rectangle"})

            elif (dtype is "footer"):  # 页脚
                self.recnlp.append({'label': 'footer', 'points': footheaderpoint, "type": "rectangle", 'content': text, 'group':100})
                self.ddsn_label.append({'label': 'footerandheader', 'points': footheaderpoint, "type": "rectangle"})
                # 在页脚和页面底部的空间生成随机大小的box用于填充图标
                tubiao_height = int((self.reshape_size[1] - (st_point[1] + line_size_y + gap)) * random.randint(2, 9) / 10)  # 图标高度是随机页脚和底部高度的20-90%
                # 给限制范围
                if tubiao_height > max_tubiaoheight:
                    tubiao_height = max_tubiaoheight
                if tubiao_height > min_tubiaoheight:  # 满足就填充，否则不填充
                    figurebox = [st_point[0], st_point[1] + line_size_y + gap, tubiao_height, tubiao_height]
                    figurepoint = [[figurebox[0], figurebox[1]], [figurebox[0]+figurebox[2], figurebox[1]+figurebox[3]]]
                    tubiao_bboxes.append(figurebox)
                    self.recnlp.append({'label': 'figure', 'points': figurepoint, "type": "rectangle", 'content': '<figure>', 'group':100})
                    self.ddsn_label.append({'label': 'figure', 'points': figurepoint, "type": "rectangle"})

        if object_num >= 2 and two == True:  # 第二个页脚页眉，第一个左上（下）角已经设置好，第二个固定在右上（下）角，方法同上
            while 1:
                text = self.header_loader.get_text() if dtype == 'header' else self.footer_loader.get_text()
                line_size_x, line_size_y = image_draw.textsize(text, font=font_file)
                if line_size_x < page_width // 2:
                    break
            if three and line_size_x > page_width // 3:
                three = False
            st_point = (bbox[2] - line_size_x - 1, bbox[1])
            if needimg:
                image_draw.text(st_point, text, font=font_file, fill=color)
            footheaderpoint = [[st_point[0], st_point[1]], [st_point[0] + line_size_x, st_point[1] + line_size_y]]
            if (dtype is "header"):
                self.recnlp.append({'label': 'header', 'points': footheaderpoint, "type": "rectangle", 'content': text, 'group':0})
                self.ddsn_label.append({'label': 'footerandheader', 'points': footheaderpoint, "type": "rectangle"})
                tubiao_height = int((st_point[1] - gap - 0) * (random.randint(2, 9) / 10))
                if tubiao_height > max_tubiaoheight:
                    tubiao_height = max_tubiaoheight
                if tubiao_height > min_tubiaoheight:
                    figurebox = [st_point[0], st_point[1] - gap - tubiao_height, tubiao_height, tubiao_height]
                    figurepoint = [[figurebox[0], figurebox[1]], [figurebox[0]+figurebox[2], figurebox[1]+figurebox[3]]]
                    tubiao_bboxes.append(figurebox)
                    self.recnlp.append({'label': 'figure', 'points': figurepoint, "type": "rectangle", 'content': '<figure>', 'group':0})
                    self.ddsn_label.append({'label': 'figure', 'points': figurepoint, "type": "rectangle"})
            elif (dtype is "footer"):
                self.recnlp.append({'label': 'footer', 'points': footheaderpoint, "type": "rectangle", 'content': text, 'group':100})
                self.ddsn_label.append({'label': 'footerandheader', 'points': footheaderpoint, "type": "rectangle"})
                tubiao_height = int(
                    (self.reshape_size[1] - (st_point[1] + line_size_y + gap)) * random.randint(2, 9) / 10)
                if tubiao_height > max_tubiaoheight:
                    tubiao_height = max_tubiaoheight
                if tubiao_height > min_tubiaoheight:
                    figurebox = [st_point[0], st_point[1] + line_size_y + gap, tubiao_height, tubiao_height]
                    figurepoint = [[figurebox[0], figurebox[1]], [figurebox[0]+figurebox[2], figurebox[1]+figurebox[3]]]
                    tubiao_bboxes.append(figurebox)
                    self.recnlp.append({'label': 'figure', 'points': figurepoint, "type": "rectangle", 'content': '<figure>', 'group':100})
                    self.ddsn_label.append({'label': 'figure', 'points': figurepoint, "type": "rectangle"})

        if object_num >= 3 and three == True:  # 第三个页脚页眉，居中
            while 1:
                text = self.header_loader.get_text() if dtype == 'header' else self.footer_loader.get_text()
                line_size_x, line_size_y = image_draw.textsize(text, font=font_file)
                if line_size_x < page_width // 3:
                    break
            st_point = ((bbox[0] + bbox[2]) // 2 - line_size_x // 2, bbox[1])
            if needimg:
                image_draw.text(st_point, text, font=font_file, fill=color)
            footheaderpoint = [[st_point[0], st_point[1]], [st_point[0] + line_size_x, st_point[1] + line_size_y]]
            if (dtype is "header"):
                self.recnlp.append({'label': 'header', 'points': footheaderpoint, "type": "rectangle", 'content': text, 'group':0})
                self.ddsn_label.append({'label': 'footerandheader', 'points': footheaderpoint, "type": "rectangle"})
                tubiao_height = int((st_point[1] - gap - 0) * (random.randint(2, 9) / 10))
                if tubiao_height > max_tubiaoheight:
                    tubiao_height = max_tubiaoheight
                if tubiao_height > min_tubiaoheight:
                    figurebox = [st_point[0], st_point[1] - gap - tubiao_height, tubiao_height, tubiao_height]
                    figurepoint = [[figurebox[0], figurebox[1]], [figurebox[0]+figurebox[2], figurebox[1]+figurebox[3]]]
                    tubiao_bboxes.append(figurebox)
                    self.recnlp.append({'label': 'figure', 'points': figurepoint, "type": "rectangle", 'content': '<figure>', 'group':0})
                    self.ddsn_label.append({'label': 'figure', 'points': figurepoint, "type": "rectangle"})
                    
            elif (dtype is "footer"):
                self.recnlp.append({'label': 'footer', 'points': footheaderpoint, "type": "rectangle", 'content': text, 'group':100})
                self.ddsn_label.append({'label': 'footerandheader', 'points': footheaderpoint, "type": "rectangle"})
                tubiao_height = int(
                    (self.reshape_size[1] - (st_point[1] + line_size_y + gap)) * random.randint(2, 9) / 10)
                if tubiao_height > max_tubiaoheight:
                    tubiao_height = max_tubiaoheight
                if tubiao_height > min_tubiaoheight:
                    figurebox = [st_point[0], st_point[1] + line_size_y + gap, tubiao_height, tubiao_height]
                    figurepoint = [[figurebox[0], figurebox[1]], [figurebox[0]+figurebox[2], figurebox[1]+figurebox[3]]]
                    tubiao_bboxes.append(figurebox)
                    self.recnlp.append({'label': 'figure', 'points': figurepoint, "type": "rectangle", 'content': '<figure>', 'group':100})
                    self.ddsn_label.append({'label': 'figure', 'points': figurepoint, "type": "rectangle"})
        return points, tubiao_bboxes
    def add_date(self, bbox):
        '''
        日期添加
        '''
        #日期默认单行
        text = self.date_loader.get_text() 
        font = random.choice(self.fonts) 
        color = random.choices([(0, 0, 0), (255, 0, 0), (0, 0, 255)], [8, 1, 1])[0]
        if self.same_elem:
            if not self.text:
                self.text['font'] = font
                self.text['color'] = color
            else:
                font = self.text['font']
                color = self.text['color']
        font_size = bbox[3] # 字号与box高度相等

        image_draw = ImageDraw.Draw(self.image)
        FONT = ImageFont.truetype(font, font_size)
        x, y = image_draw.textsize(text, font=FONT)
        start_x = random.randint(bbox[0], bbox[0]+bbox[2]-x)
        point = [ [start_x, bbox[1]], [start_x+x, bbox[1]+y] ]
        self.recnlp.append({'label':'date', 'points': point, "type": "rectangle", 'content': text, 'group': self.group})
        self.ddsn_label.append({'label':'date', 'points': point, "type": "rectangle"})
        self.group += 1
        if needimg:
            image_draw.text((point[0][0], point[0][1]), text=text, fill=color, font=FONT)

    def add_author(self, bbox):
        '''
        作者添加
        '''
        text = self.author_loader.get_text().replace(',', ' ').replace('，', ' ') # 语料中英文逗号换成空格
        font = random.choice(self.fonts)
        color = random.choices([(0, 0, 0), (255, 0, 0), (0, 0, 255)], [8, 1, 1])[0]
        if self.same_elem:
            if not self.text:
                self.text['font'] = font
                self.text['color'] = color
            else:
                font = self.text['font']
                color = self.text['color']
        font_size = bbox[3]

        image_draw = ImageDraw.Draw(self.image)
        FONT = ImageFont.truetype(font, font_size)
        x, y = image_draw.textsize(text, font=FONT)
        if x > bbox[2]:
            num = int(bbox[2] / font_size) - 4 #填满少几个，方便居中
            if self.select == 'English':
                num *= 2
            text = text[: num]
        x, y = image_draw.textsize(text, font=FONT)
        #居中填充
        space_one_side = (bbox[2]-x) // 2
        point = [ [bbox[0]+space_one_side, bbox[1]], [bbox[0]+space_one_side+x, bbox[1]+y] ]
        self.recnlp.append({'label':'author', 'points': point, "type": "rectangle", 'content': text, 'group': self.group})
        self.ddsn_label.append({'label':'author', 'points': point, "type": "rectangle"})
        self.group += 1
        if needimg:
            image_draw.text((point[0][0], point[0][1]), text=text, fill=color, font=FONT)
        if self.pattern == 'ppt':
            self.ppt_label.append({'label':'author', 'points': point, "type": "rectangle"})

    def add_TITLE(self, bbox):
        '''
        大标题添加
        '''
        if self.pattern != 'ppt': # 用于ddsn时，标题上侧留白30，用于ppt不用留白
            upsapce = 30
            bbox[1] += upsapce
            bbox[3] -= upsapce
        text = self.TITLE_loader.get_text() # 用于nlp填充为了保证语义，需要完整语料
        if self.pattern == 'ppt' and len(text)>10: #用于ppt填充时标题不需要完整语料
            text = text[:10]
        #标题box随机宽度切割
        space_oneside = int(bbox[2] * random.randint(2, 4) / 10 / 2)
        bbox[0] += space_oneside
        bbox[2] -= space_oneside * 2
        
        font = random.choice(self.font_nottc)
        color = random.choices([(0, 0, 0), (255, 0, 0), (0, 0, 255)], [8, 1, 1])[0]
        stroke_width = random.randint(0, 1)
        if self.same_elem:
            if not self.title:
                self.title['font'] = font
                self.title['color'] = color
                self.title['stroke_width'] = stroke_width
            else:
                font = self.title['font']
                color = self.title['color']
                stroke_width = self.title['stroke_width']

        image_draw = ImageDraw.Draw(self.image)
        font_size = 40 # 初始字号
        interval = random.randint(5, 15) #行间距
        # 按语料实际占用行数与box最大可容纳行数进行增减字号，二者相等时停止
        select = None 
        while 1:
            Font = ImageFont.truetype(font, font_size)
            x, y = image_draw.textsize(text, font=Font)
            if x // bbox[2] + 1 > bbox[3]//(font_size+interval):
                # print(0)
                if not select:
                    select = 'minus'
                elif select != 'minus':
                    break
                font_size -= 1
            elif x // bbox[2] + 1 < bbox[3]//(font_size+interval):
                # print(1)
                if not select:
                    select = 'add'
                elif select != 'add':
                    break
                font_size += 1
            else:
                break
        # 单行title进行居中
        if x <= bbox[2]:
            space_oneside = (bbox[2]-x) // 2
            bbox[0] += space_oneside
            bbox[2] -= space_oneside*2
        # 填充
        self._draw_text(text, font=font, font_size=font_size, bbox=bbox, retract=0, type='title', stroke_width=stroke_width, color=color, col_interval=interval, group=self.group)
        self.group += 1

    def add_one_line_text(self, bbox, font, text, color, font_size, retract=0, TYPE='title', group=None, center=None, stroke_width=None):
        '''
        单行文字，当前仅用于填充section
        '''
        if 0 == font_size:
            return
        if retract:#首行缩进
            bbox = [bbox[0]+retract*font_size, bbox[1], bbox[2]-retract*font_size, bbox[3]]
    
        image_draw = ImageDraw.Draw(self.image)
        width = int(bbox[2])
        font = ImageFont.truetype(font, font_size)  # 设置字体
        line_size_x, line_size_y = image_draw.textsize(text, font=font)  # 文本行长，宽
        #循环判断最长语料位置
        end = 0
        while line_size_x > width: #语料过长
            end -= 1
            text = text[:end]
            line_size_x = line_size_x, line_size_y = image_draw.textsize(text, font=font)
        textcontent = text
        # 未设定center则20%概率居中
        if center == None:
            center = random.randint(0, 5)
        if center > 0:#不居中
            st_point = (int(bbox[0]), int(bbox[1]))
        else:#居中
            st_point = (int(bbox[0])+(bbox[2]-line_size_x)//2, int(bbox[1]))

        if not color:
            color = random.choices([(0, 0, 0), (255, 0, 0), (0, 0, 255), (255, 255, 0)], [8, 1, 1, 1])[0]
        try:
            if stroke_width == None:
                if TYPE == 'title':
                    stroke_width=random.randint(0, 1)
                else:
                    stroke_width=0
            
            if needimg:
                image_draw.text(st_point, textcontent, font=font, fill=color,
                                stroke_width=stroke_width)  # draw text文本, 1/2概率加粗
            
        except:
            print("error")
            return
        # section point
        point = [[st_point[0], st_point[1]], [st_point[0] + line_size_x, st_point[1] + line_size_y]] 
        if TYPE == 'title':
            if not group:
                self.recnlp.append({'label':'section', 'points': point, "type": "rectangle", 'content': textcontent, 'group': self.group})
                self.group += 1
            else:
                self.recnlp.append({'label':'section', 'points': point, "type": "rectangle", 'content': textcontent, 'group': group})
            self.ddsn_label.append({'label':'section', 'points': point, "type": "rectangle"})
        return point

    def add_equation(self, bbox, figure_path, group=None, keep_ratio=True):
        '''
        公式填充
        类似图，表的填充，没有caption
        '''
        new_bbox = [0, 0, 0, 0]
        rightedge_width, leftedge_width, upedge_height, downedge_height = 0, 0, 0, 6  # 上下左右留白
        points1 = [(bbox[0], bbox[1]), (bbox[0] + bbox[2], bbox[1] + upedge_height)]  # equation_edge上边
        points2 = [(bbox[0], bbox[1]), (bbox[0] + leftedge_width, bbox[1] + bbox[3])]  # equation_edge左边
        points3 = [(bbox[0] + bbox[2] - rightedge_width, bbox[1]),
                   (bbox[0] + bbox[2], bbox[1] + bbox[3])]  # equation_edge右边
        points4 = [(bbox[0], bbox[1] + bbox[3] - downedge_height),
                   (bbox[0] + bbox[2], bbox[1] + bbox[3])]  # equation_edge下边
        edge_label1 = {"label": "equationedge", "points": points1, "type": "rectangle"}
        edge_label2 = {"label": "equationedge", "points": points2, "type": "rectangle"}
        edge_label3 = {"label": "equationedge", "points": points3, "type": "rectangle"}
        edge_label4 = {"label": "equationedge", "points": points4, "type": "rectangle"}
        edge_labels = [edge_label1, edge_label2, edge_label3
            , edge_label4]
        # 加入edge后equation新的bbox
        new_bbox[0] = bbox[0] + leftedge_width
        new_bbox[1] = bbox[1] + upedge_height
        new_bbox[2] = bbox[2] - (rightedge_width + leftedge_width)
        new_bbox[3] = bbox[3] - (upedge_height + downedge_height)
        bbox = new_bbox
        x0, y0, width, height = bbox
        width, height = max(1, width), max(1, height)
        added_figure, fillimg_width = reshape_img(figure_path, (width, height), keep_ratio=keep_ratio,
                                                  margin_crop=MARGIN_CROP)  # reshape后的公式
        # 保持纵横比后居中
        width_offset = (width - fillimg_width) // 2
        x0 += width_offset
        width -= width_offset * 2
        if needimg:
            self.image.paste(added_figure, (int(x0), int(y0)))
        points = [[x0, y0], [x0 + width, y0 + height]]
        label = {"label": "equation", "points": points, "type": "rectangle", 'content': '<equation>', 'group': group}
        return label, edge_labels

    def add_title(self, bbox, color=None, font=None, text=None, group=None, center=None):
        '''
        section填充
        '''
        if not text: #未指定文本就从语料中弹出
            text = self.title_loader.get_text()
            if self.pattern == 'ppt': #如果是ppt用途则不需要section前面的特征符【类似3.2, 1.2】
                text = ' '.join(text.split(' ')[1:])
        if not font:
            font = random.choice(self.font_nottc)
        if not color:
            color = random.choices([(0, 0, 0), (255, 0, 0), (0, 0, 255)], [8, 1, 1])[0]
        gap = 5 # section底部留白
        maxfontsize = int(bbox[3] - gap)
        # 选择字体大小
        if maxfontsize <= 19:
            return
        elif maxfontsize > 24:
            chooselist = [21, 22, 22, 23, 23, 24, 24, 25] * 2 + [i for i in range(19, maxfontsize+1)] #box过大情况尽量选择合理大小字号
        else:
            chooselist = [i for i in range(19, maxfontsize+1)]
        font_size = random.choice(chooselist)
        stroke_width = random.choice([0, 1, 1]) #加粗概率66.7%
        if self.same_elem:
            if not self.title:
                self.title['font'] = font
                self.title['color'] = color
                self.title['stroke_width'] = stroke_width
            else:
                font = self.title['font']
                color = self.title['color']
                stroke_width = self.title['stroke_width']

        text_point = self.add_one_line_text(bbox, font, text, color, font_size, group=group, center=center, stroke_width=stroke_width)  # 填充文本
        text_label = {"label": "title", "points": text_point, "type": "rectangle"} #用于ppt-label保存
        return text_label

    def add_watermark(self, text, font, font_size, diaphaneity):
        '''
        增加水印
        :param text:
        :param font:
        :param font_size:
        :param diaphaneity:
        :return:
        '''
        font = self._check_font(font)
        ## (598,419)
        image = self.image
        image_x, image_y = self.reshape_size
        text_diap = diaphaneity  ####  设置字体透明度  越小越透明 （0,100）
        font = ImageFont.truetype(font, font_size)  ## 设置字体和大小
        layer = image.convert('RGBA')  ## 转换图像格式：A为透明度
        max_size = max(image_x, image_y)
        text_overlayer = Image.new('RGBA', (2 * max_size, 2 * max_size), (255, 255, 255, 0))  ## 生成同等大小的透明图片
        image_draw = ImageDraw.Draw(text_overlayer)  ## 画图
        text_size_x, text_size_y = image_draw.textsize(text, font=font)  ## 获取文本大小
        # print(text_size_x,text_size_y)   ### 字体大小 （250,50）
        x_count, y_count = self._draw_font_box(text_overlayer.size, (text_size_x, text_size_y))
        for i in x_count:
            for j in y_count:
                # text_x,text_y = text_xy((image_x,image_y)) ## 设置文本位置
                image_draw.text((int(i), int(j)), text, font=font, fill=(0, 0, 0, text_diap))  ## 设置文本颜色和透明度
        text_overlayer = text_overlayer.rotate(45)  # 设置逆时针旋转45度
        #######  设置切割点  ##############
        box_x = (text_overlayer.size[0] - image_x) / 2
        box_y = (text_overlayer.size[1] - image_y) / 2
        box = [box_x, box_y, box_x + image_x, box_y + image_y]
        new_img = text_overlayer.crop(box)
        new_img = new_img.resize(layer.size)
        # text_overlayer.save('text_overlayer_after.png')  ## 生成的水印png图片
        # new_img.save('new_img.png')  ## 生成的水印png图片
        after = Image.alpha_composite(layer, new_img)  ## （im1,im2）将im2复合到im1上，返回一个Image对象
        self.image = after
        after.convert('RGB').save("./1.jpg")  ### .png 可以直接保存RGBA格式

    def save_img(self):
        '''
        保存图片
        '''
        if needimg:
            self.image.save(self.output_path)

    def _draw_text(self, text, font, font_size, bbox, col_interval, retract=2, color=None, stroke_width=0, type='textline', group='None'):
        '''
        填充文本函数
        :param text: 带填充文本
        :param font:
        :param bbox:
        :param col_interval: 行间距
        :param retract: 首行缩进数值
        :param color:
        :param font_size
        :return:textlabel
        text_label right_bottom坐标
        '''
        update = False 
        if type == 'textline': # 如果是文本，则需要把用过的text语料从总语料中去除
            text = self.textcontent
            update = True
        if not color:
            color = random.choices([(0, 0, 0), (255, 0, 0), (0, 0, 255)], [8, 1, 1])[0]
        if (bbox[3] < 20 or bbox[2] < 20):  # 当height和width小于20 首行缩进为0
            retract = 0
        image = self.image
        image_x, image_y = self.reshape_size
        font = ImageFont.truetype(font, font_size)  ## 设置字体和大小
        layer = image.convert('RGBA')  # 转png
        text_overlayer = Image.new('RGBA', (image_x, image_y), (255, 255, 255, 0))  # 创造白板
        image_draw = ImageDraw.Draw(text_overlayer)
        #用于保存cv-label
        points_left = []
        points_right = []
        
        x0 = int(bbox[0])
        y0 = int(bbox[1])
        
        # 增加首行缩进
        if (font_size == 0):
            return None, None
        lines_num = int(bbox[3]) // (font_size + col_interval)
        char_per_line = int(bbox[2]) // font_size  # 每行的字符数
        if (lines_num == 1): #如果只有一行，就不需要缩进
            retract = 0
        
        if retract is not None:#指定缩进
            text = "  " * retract + text
            self.textcontent = "  " * retract + self.textcontent
        
        if (lines_num == 0 or char_per_line == 0):
            return None, None

        if type in ['textline', 'abstract']: #摘要，文本情况最后一行随机长度
            char_end_line_num = random.choice([i for i in range(1, char_per_line + 1)])  
        else: # 标题情况最后一行填完所有语料保证语义
            char_end_line_num = 100 

        char_nums = char_per_line * (lines_num - 1) + char_end_line_num  # 总的字符数
        if char_nums > len(text) and type=='textline':
            self.textcontent = self.text_loader.get_text(10000)
            text = self.textcontent

        cv_point = []
        st = 0
        for i in range(lines_num):
            # 每个文本行左边的点
            line_size_x, line_size_y = image_draw.textsize(text[st: st + char_per_line], font=font)
            text_length = char_per_line
            if line_size_x + font_size < bbox[2] and ((i != lines_num - 1) or (i == 0)):  # 当一行不满时填满
                loop = 0
                while (line_size_x < bbox[2]):
                    line_size_x, line_size_y = image_draw.textsize(text[st: st + text_length], font=font)
                    
                    text_length += 1
                    loop += 1
                    if loop > 500:
                        break
                text_length -= 2

            line_size_x, line_size_y = image_draw.textsize(text[st: st + text_length], font=font)
            
            # 每个文本行右边的点n
            if (i == 0): #第一行
                retract_x, _ = image_draw.textsize("  " * retract, font=font)
                points_left.append([x0 + retract_x, y0 + i * (font_size + col_interval)])
                points_left.append([x0 + retract_x, y0 + (i+1) * (font_size + col_interval)])
                points_right.append([x0 + line_size_x, y0 + i * (font_size + col_interval)])
                points_right.append([x0 + line_size_x, y0 + (i+1) * (font_size + col_interval)])
                textcontent = text[st:st + text_length]
                if needimg:
                    image_draw.text((x0, y0 + i * (font_size + col_interval)),  # 填充文本
                                    textcontent, font=font, fill=color, stroke_width=stroke_width)
                st += text_length

            elif i != lines_num - 1: #中间行
                points_left.append([x0, y0 + i * (font_size + col_interval)])
                points_left.append([x0, y0 + (i+1) * (font_size + col_interval)])
                points_right.append([x0 + line_size_x, y0 + i * (font_size + col_interval)])
                points_right.append([x0 + line_size_x, y0 + (i+1) * (font_size + col_interval)])
                textcontent = text[st:st + text_length]
                
                if needimg:
                    image_draw.text((x0, y0 + i * (font_size + col_interval)),  # 填充文本
                                    textcontent, font=font, fill=color, stroke_width=stroke_width)
                st += text_length
            else:# 最后一行
                points_left.append([x0, y0 + i * (font_size + col_interval)])
                points_left.append([x0, y0 + (i+1) * (font_size + col_interval)])
                line_size_x, line_size_y = image_draw.textsize(text[st:st + char_end_line_num],
                                                               font=font)
                
                points_right.append([x0 + line_size_x, y0 + i * (font_size + col_interval)])
                points_right.append(
                    [x0 + line_size_x, y0 + (i+1) * (font_size + col_interval)])
                textcontent = text[st:st + char_end_line_num]
                
                if needimg:
                    image_draw.text((x0, y0 + i * (font_size + col_interval)),  # 填充文本
                                    textcontent, font=font, fill=color, stroke_width=stroke_width)
                st += char_end_line_num
            point = [ points_left[2*i], points_right[2*i+1] ]
            self.recnlp.append({'label': type, 'points': point, "type": "rectangle", 'content':textcontent, 'group':group})
        if update: #将用过的语料从总体text语料中移除
            self.textcontent = self.textcontent[st:]
        self.image = Image.alpha_composite(layer, text_overlayer).convert('RGB')
        #保存cv polygon labe
        points_right.reverse()
        cv_point += points_left + points_right
        label = type if type != 'textline' else 'text'
        if self.pattern == 'ppt':
            self.ppt_label.append({"label": label, "points": cv_point, "type": "polygon"})
        if label != 'caption':
            self.ddsn_label.append({"label": label, "points": cv_point, "type": "polygon"})
        
        return None, cv_point[:]

    def _draw_font_box(self, image_size, font_size):
        img_w, img_h = image_size
        font_w, font_h = font_size
        all_x = []
        x = 0
        all_x.append(x)
        while x < img_w:
            x = font_w + 50 + x  ####  隔50 画一次文字
            all_x.append(x)

        all_y = []
        y = 0
        all_y.append(y)
        while y < img_h:
            y = font_h + 50 + y  ####  隔50 画一次文字
            all_y.append(y)
        return all_x, all_y
