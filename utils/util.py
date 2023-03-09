import numpy as np
import cv2
import os
import glob 
import json
from tqdm import tqdm
from PIL import Image, ImageDraw, ImageFont, ImageOps
import random

def save_mid_res(phases_imgs, phases_infos, output_path):
    h, w, _ = np.shape(phases_imgs[0])
    
    new_im = Image.new('RGB', (w * 11, h))
    x_offset = 0

    first = phases_imgs.pop(0)
    phases_imgs.append(first)

    first = phases_infos.pop(0)
    phases_infos.append(first)

    for img, info in zip(phases_imgs, phases_infos):
        draw = ImageDraw.Draw(img)
        # font = ImageFont.truetype("sans-serif.ttf", 16)
        draw.text((0, 0), info, (255, 0, 0))
        new_im.paste(img, (x_offset, 0))
        x_offset += w 
    print("output_path: ", output_path)
    postfix = output_path.split("/")[-1].split(".")[0]
    new_im.save("./debug_all_mid_res" + str(postfix) + ".png")

def blend_two_img(ori_img, added_img, bbox):
    '''
    :param ori_img: 背景图片
    :param added_img: 要往背景图片bbox位置上贴的图片
    :param bbox: 在往背景图片上贴的位置
    :return: 融合后的图片
    '''
    width = int(bbox[2])
    height = int(bbox[3])
    ori_img = ori_img.convert("RGBA")
    added_img = added_img.resize((width, height)).convert("RGBA")
    new_bbox = (bbox[0], bbox[1], bbox[0] + bbox[2], bbox[1] + bbox[3])
    crop_img = ori_img.crop(new_bbox)  # 把背景图片bbox位置的图片crop出来
    added_img = added_img.resize((width, height))
    blend_img = Image.blend(crop_img, added_img, 0.8)  # 融合
    ori_img.paste(blend_img, (bbox[0], bbox[1]))  # 把融合图片贴回原图
    return ori_img.convert("RGB")

def text_read(text_path):
    '''
    文本迭代器
    :param text_path: 文本文件路径
    :return:
    '''
    i = 0
    with open(text_path, 'r', encoding='utf-8') as f:
        line = f.readline()
        while line:
            i += 1
            yield line
            line = f.readline()

def transparent_back(img):
    '''
    :param img:
    :return:
    '''
    L, H = img.size
    color_0 = (255, 255, 255, 255)  # 要替换的颜色
    for h in range(H):
        for l in range(L):
            dot = (l, h)
            color_1 = img.getpixel(dot)
            if color_1 == color_0:
                is_saved = True
                color_1 = color_1[:-1] + (0,)
                img.putpixel(dot, color_1)
    return img

def reshape_img(img_path, reshape_size, keep_ratio=True, margin_crop=True):
    '''
    对图片reshape
    :param img_path: 待reshape图片路径
    :param reshape_size: reshape尺寸
    :return: reshape之后的图片
    '''
    reshape_size = list(reshape_size)
    if margin_crop:
        #去白边图
        image = crop_margin(img_path)
    else:
        #不去白边图
        image = Image.open(img_path).convert("RGB")  # numpy_shape(h,w,c),size(w,h)
    #保持纵横比
    if keep_ratio:
        img_width, img_height = image.size
        keepratio_width = reshape_size[1]*img_width//img_height
        if keepratio_width <= reshape_size[0]:
            reshape_size[0] = keepratio_width
    reshape_size = (max(1, reshape_size[0]), max(1, reshape_size[1])) #resize_shape(w, h)
    image = image.resize(reshape_size)
    return image, reshape_size[0]

def replace_symbol(str):
    '''
    替换text中的奇怪字符
    :param str:待替换字符串
    :return:替换后的字符
    '''
    return str.replace(",", "").replace("，", "").replace(".", "").replace("。", "").replace("“", "").replace("”",
                                                                                                            "").replace(
        "【", "").replace( \
        "】", "").replace("《", "").replace("》", "").replace("[", "").replace("]", "").replace("?", "").replace("！", "").replace(' ', '')

def get_imgs(path):
    '''
    得到所有图片
    :param path: 路径
    :return: 所有途径
    '''
    if os.path.exists(path + '/new_list.txt'):
        f = open(path + '/new_list.txt')
        imgs = f.read().replace('\n', ' ' + path + '/').split(' ')[:-1]
        imgs[0] = path + '/' + imgs[0]
        f.close()
    else:
        imgs = glob.glob(os.path.join(path, "*.jpg")) + glob.glob(os.path.join(path, "*.JPG")) + glob.glob(
            os.path.join(path, "*.png")) \
               + glob.glob(os.path.join(path, "*.PNG")) + glob.glob(os.path.join(path, "*.JPEG")) + glob.glob(
            os.path.join(path, "*.jpeg"))

    return imgs

def find_close_fast(arr, e, imgdict, box_area):
    '''
    通过二分查找和e最接近的
    arr:待查找的list
    e:要查找的值
    return:
    返回查找的值
    结果的下标
    '''
    setarr = list(set(arr))
    low = 0
    high = len(setarr) - 1
    mid = (low + high) // 2
    while low < high:
        if e == setarr[mid]:
            break
        elif e > setarr[mid]:
            low = mid + 1
        elif e < setarr[mid]:
            high = mid
        mid = (low + high) // 2
    idx = mid
    final_idx = arr.index(setarr[idx])
    range = 5
    resize_degree = 1000
    start = idx-range if idx-range >= 0 else 0
    for eachitem in setarr[start: idx+range+1]:
        returnimg = imgdict[arr.index(eachitem)]
        width, height, _ = cv2.imread(returnimg).shape
        new_degree = abs(box_area-width*height)/(width*height)
        if new_degree < resize_degree:
            resize_degree = new_degree
            final_idx = arr.index(eachitem)
    return arr[final_idx], final_idx, resize_degree

def is_chonghe(bbox1, bbox2):
    '''
    bbox:[x0,y0,x1,y1]
    '''
    new_bbox = bbox2.copy()
    new_bbox[ 2 ] = bbox2[ 2 ] - bbox2[ 0 ]
    new_bbox[ 3 ] = bbox2[ 3 ] - bbox2[ 1 ]
    iou = compute_iou(bbox1, new_bbox)
    # print("iou",iou)
    return iou > 0.005

def compute_iou(rec1, rec2):
    """
    computing IoU
    :param rec1: (y0, x0, w,h)
    :param rec2: (y0, x0,w,h)
    :return: scala value of IoU
    """
    # computing area of each rectangles
    S_rec1 = (rec1[2]) * (rec1[3])
    S_rec2 = (rec2[2]) * (rec2[3])
    # computing the sum_area
    sum_area = S_rec1 + S_rec2

    # find the each edge of intersect rectangle
    left_line = max(rec1[1], rec2[1])
    right_line = min(rec1[1]+rec1[3], rec2[1]+rec2[3])
    top_line = max(rec1[0], rec2[0])
    bottom_line = min(rec1[0]+rec1[2], rec2[0]+rec2[2])

    # judge if there is an intersect
    if left_line >= right_line or top_line >= bottom_line:
        return 0
    else:
        intersect = (right_line - left_line) * (bottom_line - top_line)
        return (intersect / (sum_area - intersect)) * 1.0

def cul_ratio(img_dirs, filename, margin_crop=True):
    '''
    input:img_dirs type:list  [dir1,dir2,dir3]
    return:{img_path:ratio}  文件路径：长宽比   字典
    '''
    img2ratio = {}  # key img_path
    if os.path.exists(filename):
        with open(filename, "r") as f:
            img2ratio = json.load(f)

    img_paths = [] #保存所有来源的所有图片地址
    for img_dir in img_dirs: #每一个来源目录
        img_list = get_imgs(img_dir) #得到列表形式的来源目录下的所有图片地址
        img_paths += img_list #附加到img_paths
    for img_path in tqdm(img_paths):  #进度条展现进度，保存每一张图片的宽高比
        if img_path in img2ratio.keys():
            continue
        if margin_crop: #去白边
            img = crop_margin(img_path)
        else: #不去白边
            img = Image.open(img_path)
        width, height = img.size
        img2ratio[ img_path ] = width * 1.0 / height #key为图片地址，value为对应宽高ratio
    with open(filename, "w") as f:
        json.dump(img2ratio, f)
    return img2ratio

def scale_img(target_bbox, img_path):
    '''
    保持原图的长宽比，对原图进行缩放
    :param target_bbox: 缩放图片缩放后要放的bbox
    :param img_path: 要缩放的图片
    :return: 缩放后的图片
    '''
    target_width, target_height = target_bbox[2], target_bbox[3]
    image = Image.open(img_path).convert("RGB")
    img_width, img_height = image.size
    scale_ratio = min(target_width * 1.0 / img_width, target_height * 1.0 / img_height)  # 计算缩放比例
    new_width, new_height = max(1, int(scale_ratio * img_width)), max(1, int(scale_ratio * img_height))
    image = image.resize((new_width, new_height))
    return image, new_width, new_height

def check_bbox(bbox_dict):
    '''
    去掉publaynet中重复的bbox
    '''
    new_bbox_dict = {} 
    drop_id = [] # 要drop的bbox
    bboxes = [] # 存储所有bbox
    new_bboxes = [] # 删除重叠框后的bbox
    bbox2key = {} # {bbox:类型}

    for key in bbox_dict.keys():
        for bbox in bbox_dict[ key ]:
            bbox2key[ tuple(bbox) ] = key
            bboxes.append(bbox)
    for i in range(len(bboxes)):
        for j in range(i + 1, len(bboxes)):
            iou = compute_iou(bboxes[ i ], bboxes[ j ])
            #print(iou)
            if iou > 0.0001:
                drop_id.append(i)

    for i in range(len(bboxes)):
        if i not in drop_id:
            key = bbox2key[ tuple(bboxes[i]) ]
            if key not in new_bbox_dict.keys():
                new_bbox_dict[ key ] = [ bboxes[i] ]
            else:
                new_bbox_dict[ key ].append(bboxes[i])
    return new_bbox_dict

def vis_publaynet(example, bbox_dict, width, height):
    # print(width, height)
    cur_img = np.zeros((height, width, 3), np.uint8)

    for key in bbox_dict.keys():
        
        if key == "table":
            cur_color = (255, 0, 0) # r
            for bbox in bbox_dict[key]:
                # print("table: ", bbox)
                pstart = (int(bbox[ 0 ]), int(bbox[ 1 ]))
                pend = (int(bbox[ 0 ]) + int(bbox[ 2 ]), int(bbox[ 1 ]) + int(bbox[ 3 ]))
                cv2.rectangle(cur_img, pstart, pend, cur_color, 1)
            
        elif key == "title":
            cur_color = (0, 255, 0) # g
            for bbox in bbox_dict[key]:
                # print("title: ", bbox)
                pstart = (int(bbox[ 0 ]), int(bbox[ 1 ]))
                pend = (int(bbox[ 0 ]) + int(bbox[ 2 ]), int(bbox[ 1 ]) + int(bbox[ 3 ]))
                cv2.rectangle(cur_img, pstart, pend, cur_color, 1)

        elif key == "figure":
            cur_color = (0, 0, 255) # b
            for bbox in bbox_dict[key]:
                # print("figure: ", bbox)
                pstart = (int(bbox[ 0 ]), int(bbox[ 1 ]))
                pend = (int(bbox[ 0 ]) + int(bbox[ 2 ]), int(bbox[ 1 ]) + int(bbox[ 3 ]))
                cv2.rectangle(cur_img, pstart, pend, cur_color, 1)

        elif key == "text":
            cur_color = (255, 255, 0) # y
            for bbox in bbox_dict[key]:
                # print("text: ", bbox)
                
                pstart = (int(bbox[ 0 ]), int(bbox[ 1 ]))
                pend = (int(bbox[ 0 ]) + int(bbox[ 2 ]), int(bbox[ 1 ]) + int(bbox[ 3 ]))
                cv2.rectangle(cur_img, pstart, pend, cur_color, 1)

        elif key == "list":
            cur_color = (0, 255, 255) # c
            for bbox in bbox_dict[key]:
                # print("list: ", bbox)
                pstart = (int(bbox[ 0 ]), int(bbox[ 1 ]))
                pend = (int(bbox[ 0 ]) + int(bbox[ 2 ]), int(bbox[ 1 ]) + int(bbox[ 3 ]))
                cv2.rectangle(cur_img, pstart, pend, cur_color, 1)

    print(np.shape(cur_img))
    if not os.path.exists("./publayout_vis"):
        os.mkdir("./publayout_vis")
    print("example: ", example)
    cv2.imwrite("./publayout_vis/test.jpg", cur_img)
    # cv2.imwrite("./publayout_vis/" + example, cur_img)

    cur_img = Image.fromarray(cur_img)

    return cur_img    
def makepage():
    '''
    自生成页面
    '''
    #总高宽
    height = 1700
    width = 1000
    #左右留白，上下留白，双栏页面中间留白
    edge_rl = int(width / 6 / 2)
    edge_ud = int(height / 8 / 2)
    edge_mid = edge_rl // 2
    
    real_width = width - 2*edge_rl #实际内容宽度
    per_line_width = (real_width-edge_mid) // 2 #每栏宽度
    real_height = height - 2*edge_ud #实际高度
    topleft = [edge_rl, edge_ud] #左上角坐标
    #标题，作者，摘要
    titleheight = int(real_height*random.randint(5, 10)/100) 
    title_box = [topleft[0], topleft[1], real_width, titleheight] 
    author_height = random.randint(25, 30) 
    author_box = [topleft[0], title_box[1]+titleheight+10, real_width, author_height]
    date_height = random.randint(20, 25)
    date_box = [topleft[0], author_box[1]+author_height+10, real_width, date_height]
    abstract_height = random.randint(3, 6) * 100
    abstract_box = [topleft[0], date_box[1]+date_height+20, per_line_width, abstract_height]
    #左栏摘要下侧放置图（表），如果再有位置，放置section和text；右栏放置从上到下放置text，图（表），text
    text_box = []
    section_box = []
    object1_height = random.randint(3, 6) * 100
    object1_box = [topleft[0], abstract_box[1]+abstract_box[3], per_line_width, object1_height]

    left_height = real_height - titleheight - 10 - author_height - 10 - date_height - 20 - abstract_height - object1_height - 10
    if 30 <= left_height <= 50:
        section_box = [topleft[0], abstract_box[1]+abstract_box[3]+object1_height+10, per_line_width, left_height]
    elif left_height >= 50:
        section_height = random.randint(30, 50)
        section_box = [topleft[0], abstract_box[1]+abstract_box[3]+object1_height+10, per_line_width, section_height]
        text_box.append([topleft[0], section_box[1]+section_box[3], per_line_width, left_height-section_height])
    
    right_left_height = real_height - titleheight - 10 - author_height - 10 - date_height - 20
    object2_height = random.randint(3, 6) * 100
    object2_box = [topleft[0]+per_line_width+edge_mid, abstract_box[1]+random.randint(200, right_left_height-200-object2_height), per_line_width, object2_height]
    text_box.append([object2_box[0], abstract_box[1], per_line_width, object2_box[1]-abstract_box[1]])
    text_box.append([object2_box[0], object2_box[1]+object2_height, per_line_width, right_left_height-(object2_box[1]-abstract_box[1])-object2_height])
    if random.randint(0, 1):
        figure_box = object1_box
        table_box = object2_box
    else:
        figure_box = object2_box
        table_box = object1_box
    
    bbox_dict = {'abstract': [abstract_box], 'TITLE': [title_box], 'section': [section_box], 'date': [date_box], 'author': [author_box], 'text': text_box, 'figure':[figure_box], 'table':[table_box]}
    return bbox_dict, width, height

def space_fill(bbox_dict, width, height, title_height_range=(17, 27), fill_degree=0.9, pattern=None, need_check=True):
    '''
    扩大title, text，list, table, figure范围，并且跳过不合理框架图
    bbox_dict，width，height:   主函数【doc_gen_main.py】中的三个内容
    title_height_range:         设定title字体的上界和下界【tuple or list】，取值包含头尾
    fill_degree:                填充程度，值越大填充越满，空白越少【float in range（0， 1）】
    '''
    # 记录所有bbox的底端y坐标（yend），顶端y坐标（ystart），双栏左（右）侧实际bbox累加高度（leftheight）
    new_bbox_dict = {}
    yleftstart = []
    yrightstart = []
    yleftend = []
    yrightend = []
    xleftstart = []
    xleftend = []
    xrightstart = []
    xrightend = []
    leftheight = 0
    rightheight = 0
    for eachkey in bbox_dict:
        new_bbox_dict[eachkey] = []
        for each in bbox_dict[eachkey]:
            if (eachkey == 'figure' or eachkey == 'table'):
                if each[3] < 150 or each[2] == 0 or each[3]/each[2] >= 5 or each[2]/each[3] >= 5:
                    # print('Figure or Table area is irregulal')
                    return None
            xstart = each[0]
            xend = each[0] + each[2]
            if 0 <= xstart <= width * 0.5 and 0 <= xend <= width * 0.5:
                if pattern == 'single':
                    each[2] = width-each[0]*2
                    xend = each[0] + each[2]
                    xleftstart.append(xstart)
                    xrightend.append(xend)
                    yleftstart.append(each[1])
                    yleftend.append(each[1] + each[3])
                    yrightstart.append(each[1])
                    yrightend.append(each[1] + each[3])
                    leftheight += each[3]
                    rightheight += each[3]
                else:
                    xleftstart.append(xstart)
                    xleftend.append(xend)
                    yleftstart.append(each[1])
                    yleftend.append(each[1] + each[3])
                    leftheight += each[3]

            elif width * 0.5 <= xstart <= width and width * 0.5 <= xend <= width:
                if pattern == 'single':
                    continue
                xrightstart.append(xstart)
                xrightend.append(xend)
                yrightstart.append(each[1])
                yrightend.append(each[1] + each[3])
                rightheight += each[3]
                
            else:
                xleftstart.append(xstart)
                xrightend.append(xend)
                yleftstart.append(each[1])
                yleftend.append(each[1] + each[3])
                yrightstart.append(each[1])
                yrightend.append(each[1] + each[3])
                leftheight += each[3]
                rightheight += each[3]
            new_bbox_dict[eachkey].append(each)
    bbox_dict = new_bbox_dict.copy()
    if not need_check:
        return bbox_dict
    #判断有无重叠box
    yleftstart.sort()
    yleftend.sort()
    yrightstart.sort()
    yrightend.sort()
    cur = 0
    leftprev = 0
    rightprev = 0
    while cur < len(yleftstart) or cur < len(yrightstart):
        if cur < len(yleftstart):
            if yleftstart[cur] > leftprev:
                leftprev = yleftend[cur]
            else:
                # print('     Overcover layout ! ! ! !')
                return None
        if cur < len(yrightstart):
            if yrightstart[cur] > rightprev:
                rightprev = yrightend[cur]
            else:
                # print('     Overcover layout ! ! ! !')
                return None
        cur += 1
    
    real_ystart = min(yleftstart+yrightstart)
    real_yend = max(yleftend+yrightend)
    real_height = real_yend - real_ystart
    
    minxleft = min(xleftstart) if xleftstart else 0

    maxxleft = max(xleftend) if xleftend else 0

    minxright = min(xrightstart) if xrightstart else 0

    maxxright = max(xrightend) if xrightend else 0
    
    real_width = maxxright - minxleft
    # 实际文档高度 < 左（或者右）部分所有类别的累加高度，说明文档是旋转90度的，跳过
    if real_height < leftheight or real_height < rightheight:
        print('     Rotated picture, SKIP ! ! ! !')
        return None
    # 实际文档宽度远小于页面宽度，跳过
    if (width - real_width) / real_width > 0.4:
        print('     Narrow Layout, SKIP ! ! ! !')
        return None
    # 处理title的所有bbox，使高度大于30或者小于17的都变为30,横向布满
    title_range = title_height_range
    title_list = []
    if 'section' in bbox_dict.keys():
        title_section_bboxdict = bbox_dict['section'] 
    else:
        title_section_bboxdict = bbox_dict['title']
    
    for i, eachtitlebbox in enumerate(title_section_bboxdict):
        # x轴的开始和结尾
        xstart = eachtitlebbox[0]
        xend = eachtitlebbox[0] + eachtitlebbox[2]
        # y轴的开始和结尾
        old_ystart = eachtitlebbox[1]
        old_yend = eachtitlebbox[1] + eachtitlebbox[3]
        if 0 <= xstart <= width * 0.5 and 0 <= xend <= width * 0.5:  # 左栏
            # 横向扩充
            eachtitlebbox[0] = minxleft
            eachtitlebbox[2] = maxxleft - eachtitlebbox[0]
            # 纵向扩充
            if eachtitlebbox[3] > title_range[1]:  # title高度过大
                eachtitlebbox[3] = title_range[1]  # 用设定最大值替换底端坐标，底端上移，顶端不变
                yleftend[yleftend.index(old_yend)] = old_ystart + title_range[1]  # 底端列表替换对应元素
            elif eachtitlebbox[3] < title_range[0]:  # title高度过小
                # 底端不变，向上搜寻空白高度是否满足填充
                yleftend.sort()
                index = yleftend.index(old_yend)
                if index > 0 and (old_yend - yleftend[index - 1]) > title_range[0]:  # 满足，则扩充，顶端上移，底端不变
                    eachtitlebbox[1] = old_yend - title_range[0]
                    eachtitlebbox[3] = title_range[0]
                    yleftstart[yleftstart.index(old_ystart)] = eachtitlebbox[1]  # 顶端列表替换对应元素
                else:  # 不满足
                    # 顶端底端列表删除对应元素
                    yleftstart.remove(old_ystart)
                    yleftend.remove(old_yend)
                    # 直接进入下一个box，此box丢弃
                    continue
        elif width * 0.5 <= xstart <= width and width * 0.5 <= xend <= width:  # 右栏同理
            eachtitlebbox[0] = minxright
            eachtitlebbox[2] = maxxright - eachtitlebbox[0]
            if eachtitlebbox[3] > title_range[1]:
                eachtitlebbox[3] = title_range[1]
                yrightend[yrightend.index(old_yend)] = old_ystart + title_range[1]
            elif eachtitlebbox[3] < title_range[0]:
                yrightend.sort()
                index = yrightend.index(old_yend)
                if index > 0 and (old_yend - yrightend[index - 1]) > title_range[0]:
                    eachtitlebbox[1] = old_yend - title_range[0]
                    eachtitlebbox[3] = title_range[0]
                    yrightstart[yrightstart.index(old_ystart)] = eachtitlebbox[1]
                else:
                    yrightstart.remove(old_ystart)
                    yrightend.remove(old_yend)
                    continue
        else:  # 跨栏
            eachtitlebbox[0] = minxleft
            eachtitlebbox[2] = maxxright - eachtitlebbox[0]
            if eachtitlebbox[3] > title_range[1]:
                eachtitlebbox[3] = title_range[1]
                yrightend[yrightend.index(old_yend)] = old_ystart + title_range[1]
                yleftend[yleftend.index(old_yend)] = old_ystart + title_range[1]
            elif eachtitlebbox[3] < title_range[0]:
                total = list(set(yleftend + yrightend))
                total.sort()
                index = total.index(old_yend)
                if index > 0 and (old_yend - total[index - 1]) > title_range[0]:
                    eachtitlebbox[1] = old_yend - title_range[0]
                    eachtitlebbox[3] = title_range[0]
                    yrightstart[yrightstart.index(old_ystart)] = eachtitlebbox[1]
                    yleftstart[yleftstart.index(old_ystart)] = eachtitlebbox[1]
                else:
                    yleftstart.remove(old_ystart)
                    yleftend.remove(old_yend)
                    yrightstart.remove(old_ystart)
                    yrightend.remove(old_yend)
                    continue
        # 对修改完毕后可以使用的box进行添加
        title_list.append(eachtitlebbox)
    # 整体改变字典中title的值
    if 'section' in bbox_dict.keys():
        bbox_dict['section'] = title_list
    else:
        bbox_dict['title'] = title_list
    # 处理其他4个类别的bbox，统一向上下扩增，将原本的空白处尽可能填充, 横向布满
    interval_ratio = 1-fill_degree  # boxes之间间隙的比例值，值越小间隙越小
    for eachkey in bbox_dict.keys():
        if eachkey not in ['title', 'footer', 'section', 'author', 'date', 'abstract']:
            for eachtarget in bbox_dict[eachkey]:
                old_ystart = eachtarget[1]
                old_yend = eachtarget[1] + eachtarget[3]
                xstart = eachtarget[0]
                xend = eachtarget[0] + eachtarget[2]
                if 0 <= xstart <= width * 0.5 and 0 <= xend <= width * 0.5:  # 左栏
                    #横向扩满
                    eachtarget[0] = minxleft
                    eachtarget[2] = maxxleft - eachtarget[0]
                    # 顶端上移
                    yleftend.sort()
                    for i in range(len(yleftend)):
                        if yleftend[i] > old_ystart:
                            if i == 0:  # 开头box向上填满
                                new_start = real_ystart
                            else:
                                offsetvalue = (old_ystart - yleftend[i - 1]) * interval_ratio
                                new_start = yleftend[i - 1] + offsetvalue
                            yleftstart[yleftstart.index(old_ystart)] = new_start  # 更新对应顶端列表
                            eachtarget[1] = new_start
                            break
                    
                    # 底端下移
                    yleftstart.sort()
                    for i in range(len(yleftstart)):
                        if yleftstart[i] > old_yend:
                            offsetvalue = (yleftstart[i] - old_yend) * interval_ratio
                            new_end = yleftstart[i] - offsetvalue
                            yleftend[yleftend.index(old_yend)] = new_end  # 更新对应底端列表
                            eachtarget[3] = new_end - eachtarget[1]
                            break
                        if i == len(yleftstart) - 1:  # 底部box向下填满
                            new_end = real_yend
                            yleftend[yleftend.index(old_yend)] = new_end
                            eachtarget[3] = new_end - eachtarget[1]
                elif width * 0.5 <= xstart <= width and width * 0.5 <= xend <= width:  # 右栏

                    eachtarget[0] = minxright
                    eachtarget[2] = maxxright - eachtarget[0]
                    yrightend.sort()
                    for i in range(len(yrightend)):
                        if yrightend[i] > old_ystart:
                            if i == 0:
                                new_start = real_ystart
                            else:
                                offsetvalue = (old_ystart - yrightend[i - 1]) * interval_ratio
                                new_start = yrightend[i - 1] + offsetvalue
                            yrightstart[yrightstart.index(old_ystart)] = new_start
                            eachtarget[1] = new_start
                            break
                    
                    yrightstart.sort()
                    for i in range(len(yrightstart)):
                        if yrightstart[i] > old_yend:
                            offsetvalue = (yrightstart[i] - old_yend) * interval_ratio
                            new_end = yrightstart[i] - offsetvalue
                            yrightend[yrightend.index(old_yend)] = new_end
                            eachtarget[3] = new_end - eachtarget[1]
                            break
                        if i == len(yrightstart) - 1:
                            new_end = real_yend
                            yrightend[yrightend.index(old_yend)] = new_end
                            eachtarget[3] = new_end - eachtarget[1]
                else:  # 跨栏
                    eachtarget[0] = minxleft
                    eachtarget[2] = maxxright - eachtarget[0]
                    total_ystart = list(set(yleftstart + yrightstart))
                    total_yend = list(set(yleftend + yrightend))
                    total_yend.sort()
                    for i in range(len(total_yend)):
                        if total_yend[i] > old_ystart:
                            if i == 0:
                                new_start = real_ystart
                            else:
                                offsetvalue = (old_ystart - total_yend[i - 1]) * interval_ratio
                                new_start = total_yend[i - 1] + offsetvalue
                            yleftstart[yleftstart.index(old_ystart)] = new_start
                            yrightstart[yrightstart.index(old_ystart)] = new_start
                            eachtarget[1] = new_start
                            break
                    
                    total_ystart.sort()
                    for i in range(len(total_ystart)):
                        if total_ystart[i] > old_yend:
                            offsetvalue = (total_ystart[i] - old_yend) * interval_ratio
                            new_end = total_ystart[i] - offsetvalue
                            yleftend[yleftend.index(old_yend)] = new_end
                            yrightend[yrightend.index(old_yend)] = new_end
                            eachtarget[3] = new_end - eachtarget[1]
                            break
                        if i == len(total_ystart) - 1:
                            new_end = real_yend
                            yleftend[yleftend.index(old_yend)] = new_end
                            yrightend[yrightend.index(old_yend)] = new_end
                            eachtarget[3] = new_end - eachtarget[1]
    return bbox_dict


def crop_margin(img_fileobj, padding=(0, 0, 0, 0)):
    '''
    除图片白边
    Args:
        img_fileobj: 图片路径
        padding: 封边

    Returns: Image格式图片

    '''
    # 转换成RGB格式，然后运用getbbox方法
    image = Image.open(img_fileobj).convert('RGB')
    # getbbox实际上检测的是黑边，所以要先将image对象反色
    ivt_image = ImageOps.invert(image)
    # 如果担心检测出来的bbox过小，可以加点padding
    bbox = ivt_image.getbbox()
    if not bbox:
        return image
    left = bbox[0] - padding[0]
    top = bbox[1] - padding[1]
    right = bbox[2] + padding[2]
    bottom = bbox[3] + padding[3]
    cropped_image = image.crop([left, top, right, bottom])
    return cropped_image


def random_get_color():
    '''
    随机获取颜色
    Returns: rgb颜色

    '''
    choice = np.random.choice(['black', 'grey', 'other'], p=[0.6, 0.3, 0.1])
    if choice == 'black':
        return (0, 0, 0)
    elif choice == 'grey':
        value = random.randint(0, 130)
        return (value, value, value)
    else:
        return (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))