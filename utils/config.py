import os
class Config(object):
    def __init__(self):
        super(Config, self).__init__()
        
        self.img_num = 20
        self.home_dir = "/data/home/shigexu/ft_local/1_resource_0317/" #素材库
        self.output_dir = "/data/home/shigexu/ft_local/DDSN_gen_data/" + 'example' #输出目录
        
        self.bg_dir = self.home_dir + "backgrounds"
        self.fonts_dir = self.home_dir + "fonts"
        #字典后数字为倍数，原因在于figurehard和cn图片数量较少，保持相对平衡
        self.figure_path_dict = {
            self.home_dir + "figures_publaynet": 2,
            self.home_dir + "train2017": 1,
            self.home_dir + "figure_hard/axis": 600,
            self.home_dir + "figure_cn": 100
            # self.home_dir + 'T': 100
        }
        self.text_file_path = {'Chinese': [
                                            "/data/home/shigexu/ft_local/1_resource_0317/NLP_source/news2016/news_baike_web_text.txt",
                                            '/data/home/shigexu/ft_local/1_resource_0317/NLP_source/news2016/test_text.txt'
                                          ],
                                'English': [
                                            '/data/home/shigexu/ft_local/1_resource_0317/NLP_source/news2016/eng_story_sents_0320.txt',
                                            '/data/home/shigexu/ft_local/1_resource_0317/NLP_source/news2016/test_text_eng.txt'
                                           ]
        }
        self.date_path_dict = {'Chinese': [
                                            '/data/home/shigexu/ft_local/1_resource_0317/NLP_source/date/test_date.txt'
                                          ],
                                'English': [
                                            '/data/home/shigexu/ft_local/1_resource_0317/NLP_source/date/test_date_eng.txt'
                                           ]
        }
        self.author_path_dict = {'Chinese': [
                                            '/data/home/shigexu/ft_local/1_resource_0317/NLP_source/author/test_author.txt'
                                          ],
                                'English': [
                                            '/data/home/shigexu/ft_local/1_resource_0317/NLP_source/author/test_author_eng.txt'
                                           ]
        }
        self.TITLE_path_dict = {'Chinese': [
                                            '/data/home/shigexu/ft_local/1_resource_0317/NLP_source/title_section/test_title.txt'
                                          ],
                                'English': [
                                            '/data/home/shigexu/ft_local/1_resource_0317/NLP_source/title_section/test_title_eng.txt'
                                           ]
        }
        self.title_path_dict = {'Chinese': [
                                            '/data/home/shigexu/ft_local/1_resource_0317/NLP_source/title_section/test_section.txt'
                                          ],
                                'English': [
                                            '/data/home/shigexu/ft_local/1_resource_0317/NLP_source/title_section/test_section_eng.txt'
                                           ]
        }
        self.header_path_dict = {'Chinese': [
                                            '/data/home/shigexu/ft_local/1_resource_0317/NLP_source/footerandheader/test_header.txt'
                                          ],
                                'English': [
                                            '/data/home/shigexu/ft_local/1_resource_0317/NLP_source/footerandheader/test_header_eng.txt'
                                           ]
        }
        self.footer_path_dict = {'Chinese': [
                                            "/data/home/shigexu/ft_local/1_resource_0317/NLP_source/footerandheader/test_footer.txt"
                                            
                                          ],
                                'English': [
                                            '/data/home/shigexu/ft_local/1_resource_0317/NLP_source/footerandheader/test_footer_eng.txt'
                                           ]
        }
        self.caption_path_dict = {'Chinese': [
                                            '/data/home/shigexu/ft_local/1_resource_0317/NLP_source/caption/test_caption.txt'
                                          ],
                                'English': [
                                            '/data/home/shigexu/ft_local/1_resource_0317/NLP_source/caption/test_caption_eng.txt'
                                           ]
        }
        self.list_path_dict = {'Chinese': [
                                            '/data/home/shigexu/ft_local/1_resource_0317/NLP_source/list/test_list.txt'
                                          ],
                                'English': [
                                            '/data/home/shigexu/ft_local/1_resource_0317/NLP_source/list/test_list_eng.txt'
                                           ]
        }
        self.reference_path_dict = {'Chinese': [
                                            '/data/home/shigexu/ft_local/1_resource_0317/NLP_source/reference/test_reference.txt'
                                          ],
                                'English': [
                                            '/data/home/shigexu/ft_local/1_resource_0317/NLP_source/reference/test_reference_eng.txt'
                                           ]
        }
        self.abstract_path_dict = {'Chinese': [
                                            '/data/home/shigexu/ft_local/1_resource_0317/NLP_source/abstract/test_abstract.txt'
                                          ],
                                'English': [
                                            '/data/home/shigexu/ft_local/1_resource_0317/NLP_source/abstract/test_abstract_eng.txt'
                                           ]
        }
        
        self.table_path_dict = {
            self.home_dir + "tables_youtu": 2,
            self.home_dir + "tables_chinese": 16,
            self.home_dir + "tables_hard": 100
        }
        self.seal_path_dict = {
            self.home_dir + "seals": 1
        }
        self.equation_path_dict = {
            self.home_dir + "printing_equation": 1
        }
        self.handwritten_path_dict = {
            self.home_dir + "handwritten_image": 1
        }
        self.logo_path_dict = {
            self.home_dir + "figure_hard/logo":10000
        }
        self.publaynet_label_path = self.home_dir + "publaynet"
        
        #ppt版面和背景
        self.ppt_label_path = self.home_dir + "ppt_layout/total_label"
        self.ppt_backgroud_path = self.home_dir + 'ppt_background'
        



if __name__ == "__main__":
    config = Config()
