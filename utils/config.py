import os
class Config(object):
    def __init__(self):
        super(Config, self).__init__()
        
        self.img_num = 10
        self.output_dir = "gen_out" #输出目录
        
        self.bg_dir = "elements/backgrounds/normal"
        self.fonts_dir = "elements/fonts"
        #字典后数字为复制倍数，以防预料/图料不够
        self.figure_path_dict = {
            "elements/figure": 2000
        }
        self.text_file_path = {'Chinese': [
                                            "elements/text/wiki_zh_2019.txt"
                                          ],
                                'English': [
                                            "text-En-file"
                                           ]
        }
        self.date_path_dict = {'Chinese': [
                                            "elements/text/date.txt"
                                          ],
                                'English': [
                                            "date-En-file"
                                           ]
        }
        self.author_path_dict = {'Chinese': [
                                            "elements/text/author.txt"
                                          ],
                                'English': [
                                            "author-En-file"
                                           ]
        }
        self.TITLE_path_dict = {'Chinese': [
                                            "elements/text/title.txt"
                                          ],
                                'English': [
                                            "TITLE-En-file"
                                           ]
        }
        self.title_path_dict = {'Chinese': [
                                            "elements/text/section.txt"
                                          ],
                                'English': [
                                            "title-En-file"
                                           ]
        }
        self.header_path_dict = {'Chinese': [
                                            "elements/text/foot_head.txt"
                                          ],
                                'English': [
                                            "header-En-file"
                                           ]
        }
        self.footer_path_dict = {'Chinese': [
                                            "elements/text/foot_head.txt"
                                          ],
                                'English': [
                                            "footer-En-file"
                                           ]
        }
        self.caption_path_dict = {'Chinese': [
                                            "elements/text/caption.txt"
                                          ],
                                'English': [
                                            "caption-En-file"
                                           ]
        }
        self.list_path_dict = {'Chinese': [
                                            "elements/text/list.txt"
                                          ],
                                'English': [
                                            "list-En-file"
                                           ]
        }
        self.reference_path_dict = {'Chinese': [
                                            "elements/text/reference.txt"
                                          ],
                                'English': [
                                            "reference-En-file"
                                           ]
        }
        self.abstract_path_dict = {'Chinese': [
                                            "elements/text/abstract.txt"
                                          ],
                                'English': [
                                            "abstract-En-file"
                                           ]
        }
        
        self.table_path_dict = {
            "elements/table": 2000,
        }
        self.seal_path_dict = {
            "seal-dir": 10
        }
        self.equation_path_dict = {
            "elements/equation": 2000
        }
        self.handwritten_path_dict = {
            "handwritten-dir": 10
        }
        self.logo_path_dict = {
            "elements/head_foot_fig":2000
        }
        self.publaynet_label_path = "elements/layout" # 包含publay的json文件，这里只放了val.json
        
        #ppt版面和背景
        self.ppt_label_path = "elements/layout" # 需要自行标注ppt版面的label，这里暂时用通用publaynet版面
        self.ppt_backgroud_path = 'elements/backgrounds/normal' # 暂用纯白，与通用版面一致
        



if __name__ == "__main__":
    config = Config()
