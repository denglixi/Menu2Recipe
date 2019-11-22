import pandas as pd
import json
import matplotlib.pyplot as plt
import numpy as np
import os
import xlrd

def load_recipe_jieba_date(path):
    data = xlrd.open_workbook(path)
    table = data.sheets()[0]
    return zip(table.col_values(0), table.col_values(3))

def load_recipe_data(path):
    """
    load recipe data with json format
    :param path:
    :return:
    """
    with open(path, encoding='utf-8') as f:
        json_data = json.load(f)
    return json_data


def merger_all_json(path):
    """
    merge all json on the path
    :param path:
    :return:
    """
    json_data = []
    for root, dirs, files in os.walk(path):
        for f in files:
            if os.path.splitext(f)[-1] == '.json':
                print("loading form {}".format(root + f))
                try:
                    with open(os.path.join(root, f), encoding='utf-8') as json_f:
                        tmp_recipe_data = json.load(json_f)
                    json_data.extend(tmp_recipe_data)
                except Exception as e:
                    print(e)
                    continue
    return json_data

def read_bohe_recipe(path):
    recipe = []
    for root, dir, files in os.walk(path):
        for f in files:
            if os.path.splitext(f)[-1] == '.csv':
                try:
                    temp_csv_data = pd.read_csv(os.path.join(root, f), error_bad_lines=False)
                    recipe.append(temp_csv_data['FoodName'][0])
                except Exception as e:
                    print(e)
                    print(f)
    return recipe

