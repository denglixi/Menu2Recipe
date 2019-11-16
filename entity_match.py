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


def entity_match(source_entities, target_entities_list, attributes):
    max_matched_score = 0
    matched_target_idx = -1
    matched_target_str = ''

    attribute_uncount_set = attributes['other'] | attributes['shape'] | attributes['taste'] | attributes['type'] | attributes['cooking method']
    # Debug
    # source_str = "".join(source_entities)
    # if not source_str == '土豆肉片饭':
    #     return 0, 0, ''

    for target_i, target_entities in enumerate(target_entities_list):
        # Debug
        # target_str = "".join(target_entities)
        # if not (target_str == '土豆片炒肉' or target_str == '土豆片炒肉'):
        #     continue


        # clean useless attribute for calculating match scores.
        target_entities = [x for x in target_entities if x is not '']
        source_entities_use = [x for x in source_entities if x not in attribute_uncount_set]
        target_entities_use = [x for x in target_entities if x not in attribute_uncount_set]
        source_len = len(source_entities_use)
        target_len = len(target_entities_use) * 0.5
        # TODO which factor
        score_factor = source_len + target_len
        # score_factor = source_len
        # exclude empty target
        if target_len == 0:
            continue

        # calculate the match score for each source entities, i.e. each food
        matched_score = 0
        for source_entity in source_entities:
            if len(source_entity) == 0:
                continue
            matched_idx, matched_text, matched_len, matched_target = text_search(source_entity, target_entities)

            # increase the matched score of meat ingredients
            meat_match_len = 0
            if len(matched_text) > 0:
                _, _,  meat_match_len, _ = text_search(matched_text, ['猪','鸭','鱼','肉','牛','羊','虾'])
            if meat_match_len > 0:
                entity_matched_score = 1.2 * matched_len / len(source_entity)
            else:
                entity_matched_score = 1 * matched_len / len(source_entity)
            entity_matched_score =  1.5 * entity_matched_score

            if source_entity in attribute_uncount_set or matched_target in attribute_uncount_set or matched_text in attribute_uncount_set:
                matched_score += 0.01 * entity_matched_score / score_factor
            elif source_entity in attributes['cooking method'] or matched_target in attributes['cooking method'] or matched_text in attributes['cooking method']:
                matched_score += 0.1 * entity_matched_score / score_factor
            else:
                # 是ingredient了
                matched_score += entity_matched_score / score_factor
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

    attribute_path = './sources/recipe_attribute.csv'
    attribute_data = load_menu_data(attribute_path)
    # id,source,food name,entity,shape,taste,cooking method,other,type
    attr_entity = set(attribute_data['entity'])
    attr_shape = set(attribute_data['shape'])
    attr_taste = set(attribute_data['taste'])
    attr_cook = set(attribute_data['cooking method'])
    attr_other = set(attribute_data['other']) | {'大', '小', '大份', '小份', '大杯', '小杯', '(', ')', '（', '）'}
    attr_type = set(attribute_data['type'])
    attributes = {'entity': attr_entity,
                  'shape': attr_shape,
                  'taste': attr_taste,
                  'cooking method': attr_cook,
                  'other': attr_other,
                  'type': attr_type}

    recipe_jieba_path = './sources/recipe_name_jieba.xlsx'
    #recipe_jieba_path = './sources/recipe_name_jieba_exclude_meishijie.xlsx'
    recipe_jieba_data = load_recipe_jieba_date(recipe_jieba_path)
    # get the jieba results
    recipe_jieba_data = [x[1].split('/') for x in recipe_jieba_data]
    recipe_jieba_data = recipe_jieba_data[1:]

    recipe_data = recipe_jieba_data
    suffix_str = 'exclude_useless_attri'
    recipe_name = 'jieba_' \
                  '{}_{}'.format(len(recipe_data), suffix_str)
    print("length of recipes: {}".format(len(recipe_data)))

    record_file = open('outputs/match_record_{}.csv'.format(recipe_name), 'w', encoding='utf-8')
    error_file = open('outputs/error_menu_{}.txt'.format(recipe_name), 'w', encoding='utf-8')

    matched_weighted_result = []
    for menu_idx, menu in menu_data.iterrows():
        if menu_idx % 20 == 0:
            print(menu_idx)
        try:
            # for some menu are wrong
            menu_text = menu['name']
            menu_text_splited = list(jieba.cut(menu_text, cut_all=False))

            matched_score, matched_target_idx, matched_target_str = entity_match(menu_text_splited, recipe_jieba_data, attributes)
            matched_weighted_result.append(matched_score)
            record_str = "{}\t{}\t{:.2}\n".format(
                menu['name'],
                matched_target_str,
                matched_score
            )
            record_file.write(record_str)
            record_file.flush()
        except Exception as e:
            print(e)
    print(matched_weighted_result)
    draw_hist(matched_weighted_result, recipe_name)

if __name__ == '__main__':
    main()