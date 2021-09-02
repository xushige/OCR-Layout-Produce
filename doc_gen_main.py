from genericpath import exists
import os
from utils.generate_object import *
from utils.config import Config
from utils.util import *
from dataset.publaynet import Publaynet
import random
DEBUG_PUBLAYOUT = False
PATTERN = 'nlp' # choose from ['nlp', 'cv', 'ppt']
class batch_document_generator(object):
    def __init__(self, label_path, image_nums, figure_loader, text_loader, table_loader, 
    seal_loader, printing_equation_loader, handwritten_loader, tubiao_loader, 
    title_loader, TITLE_loader=None, footer_loader=None, header_loader=None, caption_loader=None, 
    config=None, list_loader=None, reference_loader=None, abstract_loader=None, author_loader=None, date_loader=None):
        super(batch_document_generator, self).__init__()
        self.label_path = label_path
        self.publaynet = Publaynet(label_path)
        
        self.image_nums = image_nums
        self.figure_loader = figure_loader
        self.table_loader = table_loader
        self.text_loader = text_loader
        self.seal_loader = seal_loader
        self.printing_equation_loader = printing_equation_loader
        self.handwritten_loader = handwritten_loader
        self.tubiao_loader = tubiao_loader
        self.title_loader = title_loader
        self.TITLE_loader = TITLE_loader
        self.caption_loader = caption_loader
        self.footer_loader = footer_loader
        self.header_loader = header_loader
        self.list_loader = list_loader
        self.reference_loader = reference_loader
        self.abstract_loader = abstract_loader
        self.author_loader = author_loader
        self.date_loader = date_loader
        self.config = config
    
    def gen_batch_document(self, output_dir):
        if (not os.path.exists(output_dir)):
            os.mkdir(output_dir)
        
        img_id = 1
        all_template_names = []
        modeselect = self.publaynet.train_examples
        for example in modeselect:
            all_template_names.append(example)
        random.shuffle(all_template_names)
        txt = open(output_dir+'/list.txt', 'w')
        for i in range(1, img_id):
            txt.write("%s_%07d.jpg\n" % (os.path.basename(output_dir), i))
        #单栏版面还是双栏版面
        pattern = 'single'
        clslabel = {}
        while 1:#版面数量如果不够则反复循环
            #中止
            if (img_id > self.image_nums):
                break
            for example in all_template_names:
                if (img_id > self.image_nums):
                    break
                Bbox_dict, width, height = modeselect[example][2], \
                                            modeselect[example][0], \
                                            modeselect[example][1]
                bbox_dict = Bbox_dict.copy()
                print ("current layout: ", example)
                if PATTERN != 'ppt':
                    #没有图和表就跳过版面
                    if (not len(bbox_dict["table"]) and not len(bbox_dict["figure"])):
                        continue
                    try:
                        #空白处理
                        bbox_dict = space_fill(bbox_dict, width, height, title_height_range=(25, 40), fill_degree=0.9, pattern=pattern, need_check=True)
                    except:
                        continue
                    # 模式切换，单栏双栏接近50%概率
                    if random.randint(0, 1):
                        pattern = None
                    else:
                        pattern = 'single'
                    # 经过space-fill后该版面被抛弃，则有10%概率使用自定义版面，90%概率选择下一张版面
                    if not bbox_dict:
                        if random.randint(0, 10) == 0:
                            #自定义版面
                            bbox_dict, width, height = makepage()
                            try:
                                bbox_dict = space_fill(bbox_dict, width, height, pattern=pattern, need_check=False)
                            except:
                                pass
                        else:
                            continue
                print("img_id: ", img_id)
                imgname = "%s_%07d.jpg" % (os.path.basename(output_dir), img_id)
                
                document_generator(self.config.bg_dir if PATTERN != 'ppt' else self.config.ppt_backgroud_path, self.config.fonts_dir,
                                    os.path.join(output_dir, imgname), #七位整数
                                    bbox_dict,
                                    reshape_size = (width, height), 
                                    figure_loader = self.figure_loader,
                                    text_loader = self.text_loader, 
                                    table_loader = self.table_loader,
                                    seal_loader = self.seal_loader,
                                    printing_equation_loader = self.printing_equation_loader,
                                    handwritten_loader = self.handwritten_loader,
                                    tubiao_loader = self.tubiao_loader,
                                    title_loader=self.title_loader,
                                    TITLE_loader=self.TITLE_loader,
                                    footer_loader = self.footer_loader,
                                    header_loader = self.header_loader,
                                    list_loader = self.list_loader,
                                    caption_loader = self.caption_loader,
                                    abstract_loader = self.abstract_loader,
                                    author_loader = self.author_loader,
                                    date_loader = self.date_loader,
                                    reference_loader = self.reference_loader,
                                    pattern=PATTERN).gen_complicate_true_doc()
                txt.write(imgname+'\n')
                #分类标签，ppt为1，ddsn为0
                clslabel[imgname] = 0
                img_id += 1
        txt.close()
        if not os.path.exists(output_dir+'/cls_label'):
            os.makedirs(output_dir+'/cls_label')
        with open(output_dir+'/cls_label/cls_label.json', 'w') as w:
            json.dump(clslabel, w)
            

config = Config()
figure_loader = figure_loader(config.figure_path_dict)
text_loader = text_loader(config.text_file_path)
table_loader = table_loader(config.table_path_dict)
seal_loader = seal_loader(config.seal_path_dict)
printing_equation_loader = printing_equation_loader(config.equation_path_dict)
handwritten_loader = handwritten_loader(config.handwritten_path_dict)
tubiao_loader = tubiao_loader(config.logo_path_dict)
title_loader = title_loader(config.title_path_dict)
TITLE_loader = TITLE_loader(config.TITLE_path_dict)
footer_loader = footer_loader(config.footer_path_dict)
header_loader = header_loader(config.header_path_dict)
caption_loader = caption_loader(config.caption_path_dict)
list_loader = list_loader(config.list_path_dict)
reference_loader = reference_loader(config.reference_path_dict)
abstract_loader = abstract_loader(config.abstract_path_dict)
author_loader = author_loader(config.author_path_dict)
date_loader = date_loader(config.date_path_dict)


batch_document_generator(config.publaynet_label_path if not PATTERN=='ppt' else config.ppt_label_path, 
                        config.img_num, 
                        figure_loader, 
                        text_loader, 
                        table_loader, 
                        seal_loader,
                        printing_equation_loader, 
                        handwritten_loader, 
                        tubiao_loader,
                        title_loader=title_loader,
                        TITLE_loader=TITLE_loader,
                        footer_loader=footer_loader,
                        header_loader=header_loader,
                        caption_loader=caption_loader,
                        list_loader=list_loader,
                        reference_loader=reference_loader,
                        abstract_loader=abstract_loader,
                        author_loader=author_loader,
                        date_loader=date_loader,
                        config=config).gen_batch_document(config.output_dir)

    
