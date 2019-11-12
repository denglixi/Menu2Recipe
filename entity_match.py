import pandas as pd
import json
import matplotlib.pyplot as plt
import numpy as np
import os
from dataload import load_menu_data, load_recipe_data, merger_all_json, read_bohe_recipe, load_recipe_jieba_date
from text_search import text_search
from visulization import draw_hist
import jieba
import math


def add_voc_by_attribute(path):
    attribute_data = load_menu_data(path)
    # id,source,food name,entity,shape,taste,cooking method,other,type
    for attr_key in ['shape', 'taste', 'cooking method', 'other', 'type']: #eclude 'entity'
        attr_entity = set(attribute_data[attr_key])
        for entity in attr_entity:
            if type(entity) is not str:
                continue
            jieba.add_word(entity)


def entity_match(source_entities, target_entities_list):
    max_matched_score = 0
    matched_target_idx = -1
    matched_target_str = ''
    for target_i, target_entities in enumerate(target_entities_list):
        matched_len_total = 0
        target_entities = [x for x in target_entities if x is not '']
        source_len = len(''.join(source_entities))
        target_len = len(''.join(target_entities))
        score_factor = source_len + target_len
        if target_len == 0:
            continue
        for source_entity in source_entities:
            if len(source_entity) == 0:
                continue
            matched_idx, matched_text, matched_len, matched_target = text_search(source_entity, target_entities)
            # matched_len = matched_len * weight , which reflect the importance of entity type.
            matched_len_total += matched_len
        matched_score = 2 * matched_len_total / score_factor
        if max_matched_score < matched_score:
            max_matched_score = matched_score
            matched_target_idx = target_i
            matched_target_str = "".join(target_entities)
    return max_matched_score, matched_target_idx, matched_target_str




def main():
    menu_path = './sources/sample_menu_cleaned2.csv'
    menu_data = load_menu_data(menu_path)
    attribute_path = './sources/recipe_attribute.csv'
    add_voc_by_attribute(attribute_path)

    recipe_jieba_path = './sources/recipe_name_jieba_exclude_meishijie.xlsx'
    recipe_jieba_data = load_recipe_jieba_date(recipe_jieba_path)
    # get the jieba results
    recipe_jieba_data = [x[1].split('/') for x in recipe_jieba_data]
    recipe_jieba_data = recipe_jieba_data[1:]

    recipe_data = recipe_jieba_data
    recipe_name = 'jieba_' \
                  '{}'.format(len(recipe_data))
    print("length of recipes: {}".format(len(recipe_data)))

    record_file = open('outputs/match_record_{}.csv'.format(recipe_name), 'w', encoding='utf-8')
    error_file = open('outputs/error_menu_{}.txt'.format(recipe_name), 'w', encoding='utf-8')



    for menu_idx, menu in menu_data.iterrows():
        if menu_idx % 20 == 0:
            print(menu_idx)
        try:
            # for some menu are wrong
            menu_text = menu['name']
            menu_text_splited = list(jieba.cut(menu_text, cut_all=False))
            matched_score, matched_target_idx, matched_target_str = entity_match(menu_text_splited, recipe_jieba_data)

            record_str = "{}\t{}\t{:.2%}\n".format(
                menu['name'],
                matched_target_str,
                matched_score
            )
            record_file.write(record_str)
            record_file.flush()
        except Exception as e:
            print(e)

if __name__ == '__main__':
    main()