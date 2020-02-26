from lib.dataload import load_jieba_date


import jieba

def main():
    jieba_data = load_jieba_date("./sources/recipe_name_jieba.xlsx")
    jieba_data = list(jieba_data)[1:]
    jieba_data[0]

if __name__ == '__main__':
    seg_list = jieba.cut("烩河虾片", cut_all=False)
    print("Full Mode: " + "/ ".join(seg_list))
    main()