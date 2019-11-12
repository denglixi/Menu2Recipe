import pandas as pd
import json
import matplotlib.pyplot as plt
import numpy as np
import os
from dataload import load_menu_data, load_recipe_data, merger_all_json, read_bohe_recipe
from text_search import text_search
from visulization import draw_hist





def get_unmatched_text(source_text, target_text, matched_text):
    # result a list of strings
    return source_text.split(matched_text), target_text.split(matched_text)


def cook_attr_func():
    pass

def process_of_attriute(attr_type):
    if attr_type == 'cooking method':
        return cook_attr_func


def clean_unmatched_text_by_attribute(attributes, unmatched_text):
    result_dict = {}
    for item in unmatched_text:
        item_added = False
        for k in attributes:
            if item in attributes[k]:
                if k not in result_dict:
                    result_dict[k] = [item]
                else:
                    result_dict[k].append(item)
                item_added = True
                break
        if not item_added:
            if 'unknow' not in result_dict:
                result_dict['unknow'] = [item]
            else:
                result_dict['unknow'].append(item)

    return result_dict


def main():
    """
    main function
    """
    menu_path = './sources/sample_menu_cleaned2.csv'
    menu_data = load_menu_data(menu_path)

    attribute_path = './sources/recipe_attribute.csv'
    attribute_data = load_menu_data(attribute_path)
    # id,source,food name,entity,shape,taste,cooking method,other,type
    attr_entity = set(attribute_data['entity'])
    attr_shape = set(attribute_data['shape'])
    attr_taste = set(attribute_data['taste'])
    attr_cook = set(attribute_data['cooking method'])
    attr_other = set(attribute_data['other'])
    attr_type = set(attribute_data['type'])
    attributes = {'entity': attr_entity,
                  'shape': attr_shape,
                  'taste': attr_taste,
                  'cooking method': attr_cook,
                  'other': attr_other,
                  'type': attr_type}

    # json data
    # meishijie_recipe_path = './sources/recipe/meishiji'
    # meishijie_recipe_data = merger_all_json(meishijie_recipe_path)
    # meishijie_recipe_data = [x['name'] for x in meishijie_recipe_data]

    # bohe_recipe_path = './sources/recipe/beehoo_recipe'
    # bohe_recipe_data = read_bohe_recipe(bohe_recipe_path)

    mini_pro_recipe_path = "./sources/recipe/mini_pro_recipe.csv"
    mini_pro_recipe_data = load_menu_data(mini_pro_recipe_path)
    mini_pro_recipe_data = [x[1]['name'] for x in mini_pro_recipe_data.iterrows()]

    # noisy_recipe_path = './sources/recipe.json'
    # noisy_recipe_data = load_recipe_data(noisy_recipe_path)
    # noisy_recipe_data = [x['name'] for x in noisy_recipe_data]

    # recipe_data = set(noisy_recipe_data + mini_pro_recipe_data + bohe_recipe_data + meishijie_recipe_data)
    recipe_data = set(mini_pro_recipe_data)
    recipe_name = 'mini_pro_' \
                  '{}'.format(len(recipe_data))
    print("length of recipes: {}".format(len(recipe_data)))

    record_file = open('outputs/match_record_{}.csv'.format(recipe_name), 'w', encoding='utf-8')
    error_file = open('error_menu.txt', 'w', encoding='utf-8')
    matched_result = []
    matched_weighted_result = []

    for menu_idx, menu in menu_data.iterrows():
        if menu_idx % 20 == 0:
            print(menu_idx)
        try:
            # for some menu are wrong
            source_text = menu['name']
            matched_idx, matched_text, matched_len, matched_target = text_search(menu['name'],
                                                                                 recipe_data)
            unmatched_source_text, unmatched_target_text = get_unmatched_text(menu['name'], matched_target,
                                                                              matched_text)
            cleaned_source_text = clean_unmatched_text_by_attribute(attributes, unmatched_source_text)
            cleaned_target_text = clean_unmatched_text_by_attribute(attributes, unmatched_target_text)

            unmatched_attr_len = {}
            for k in cleaned_source_text:
                unmatched_attr_len[k] = len(cleaned_source_text[k])

            matched_result.append(matched_len / len(menu['name']))
            matched_weighted_result.append((matched_len / len(menu['name']) + matched_len / len(matched_target)) / 2)
            record_str = "{}\t{}\t{}\t{:.2%}\t{:.2%}\n".format(
                menu['name'],
                matched_text,
                matched_target,
                matched_len / len(menu['name']),
                (matched_len / len(menu['name']) + matched_len / len(matched_target)) / 2
            )
            record_file.write(record_str)
            record_file.flush()
        except Exception as e:
            print(e)
            error_file.write(str(menu_idx) + '\n')
            continue

    # draw hist
    # print(matched_result)
    # draw_hist(matched_result, )
    print(matched_weighted_result)
    draw_hist(matched_weighted_result, recipe_name)


if __name__ == '__main__':
    main()
    #draw_hist(bohe_result, "bohe")