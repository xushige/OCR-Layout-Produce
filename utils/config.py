import os
class Config(object):
    def __init__(self):
        super(Config, self).__init__()
        
        self.img_num = 10000
        self.output_dir = "" #输出目录
        
        self.bg_dir = "background-imgdir-path"
        self.fonts_dir = "fonts-dir-path"
        #字典后数字为倍数衡
        self.figure_path_dict = {
            "figdir-0": 200,
            "figdir-1": 100,
            "figdir-2": 600,
            "figdir-3": 100
        }
        self.text_file_path = {'Chinese': [
                                            "text-cn-file"
                                          ],
                                'English': [
                                            "text-En-file"
                                           ]
        }
        self.date_path_dict = {'Chinese': [
                                            "date-cn-file"
                                          ],
                                'English': [
                                            "date-En-file"
                                           ]
        }
        self.author_path_dict = {'Chinese': [
                                            "author-cn-file"
                                          ],
                                'English': [
                                            "author-En-file"
                                           ]
        }
        self.TITLE_path_dict = {'Chinese': [
                                            "TITLE-cn-file"
                                          ],
                                'English': [
                                            "TITLE-En-file"
                                           ]
        }
        self.title_path_dict = {'Chinese': [
                                            "title-cn-file"
                                          ],
                                'English': [
                                            "title-En-file"
                                           ]
        }
        self.header_path_dict = {'Chinese': [
                                            "header-cn-file"
                                          ],
                                'English': [
                                            "header-En-file"
                                           ]
        }
        self.footer_path_dict = {'Chinese': [
                                            "footer-cn-file"
                                          ],
                                'English': [
                                            "footer-En-file"
                                           ]
        }
        self.caption_path_dict = {'Chinese': [
                                            "caption-cn-file"
                                          ],
                                'English': [
                                            "caption-En-file"
                                           ]
        }
        self.list_path_dict = {'Chinese': [
                                            "list-cn-file"
                                          ],
                                'English': [
                                            "list-En-file"
                                           ]
        }
        self.reference_path_dict = {'Chinese': [
                                            "reference-cn-file"
                                          ],
                                'English': [
                                            "reference-En-file"
                                           ]
        }
        self.abstract_path_dict = {'Chinese': [
                                            "abstract-cn-file"
                                          ],
                                'English': [
                                            "abstract-En-file"
                                           ]
        }
        
        self.table_path_dict = {
            "tabledir-0": 200,
            "tabledir-1": 150,
            "tabledir-2": 100
        }
        self.seal_path_dict = {
            "seal-dir": 10
        }
        self.equation_path_dict = {
            "equation-dir": 10
        }
        self.handwritten_path_dict = {
            "handwritten-dir": 10
        }
        self.logo_path_dict = {
            "logo-dir":10
        }
        self.publaynet_label_path = "publaynet-dir" # 包含publay的train.json 和 test.json
        
        #ppt版面和背景
        self.ppt_label_path = "ppt_layout-dir"
        self.ppt_backgroud_path = 'ppt_background-dir'
        



if __name__ == "__main__":
    config = Config()
