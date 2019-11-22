import pandas as pd
import json
import matplotlib.pyplot as plt
import numpy as np
import os
from dataload import load_recipe_data, merger_all_json, read_bohe_recipe, load_recipe_jieba_date
from attribute import read_attribute_from_csv
from text_search import text_search
from visulization import draw_hist
import jieba
from concurrent.futures import ProcessPoolExecutor
import time
import math


def add_voc_by_attribute(path):
    attribute_data = pd.read_csv(path, error_bad_lines=False, encoding='utf-8')
    # id,source,food name,entity,shape,taste,cooking method,other,type
    for attr_key in ['shape', 'taste', 'cooking method', 'other', 'type']:  # eclude 'entity'
        attr_entity = set(attribute_data[attr_key])
        for entity in attr_entity:
            if type(entity) is not str:
                continue
            jieba.add_word(entity)


def entity_match(source_entities, target_entities_list, attributes):
    max_matched_score = 0
    matched_target_idx = -1
    matched_target_str = ''

    attribute_uncount_set = attributes['other'] | attributes['shape'] | attributes['taste'] | attributes['type'] | \
                            attributes['cooking method']
    # Debug
    # source_str = "".join(source_entities)
    # if not source_str == '凉瓜牛肉饭':
    #     return 0, 0, ''

    for target_i, target_entities in enumerate(target_entities_list):
        # Debug
        # target_str = "".join(target_entities)
        # if not (target_str == '凉瓜牛肉' or target_str == '土豆片炒肉'):
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
                _, _, meat_match_len, _ = text_search(matched_text, ['猪', '鸭', '鱼', '肉', '牛', '羊', '虾'])
            if meat_match_len > 0:
                entity_matched_score = 1.2 * matched_len / len(source_entity)
            else:
                entity_matched_score = 1 * matched_len / len(source_entity)
            entity_matched_score = 1.5 * entity_matched_score

            if source_entity in attribute_uncount_set or matched_target in attribute_uncount_set or matched_text in attribute_uncount_set:
                matched_score += 0.01 * entity_matched_score / score_factor
            elif source_entity in attributes['cooking method'] or matched_target in attributes[
                'cooking method'] or matched_text in attributes['cooking method']:
                matched_score += 0.1 * entity_matched_score / score_factor
            else:
                # 是ingredient了
                matched_score += entity_matched_score / score_factor

        if max_matched_score < matched_score:
            max_matched_score = matched_score
            matched_target_idx = target_i
            matched_target_str = "".join(target_entities)

    return max_matched_score, matched_target_idx, matched_target_str,


def all_in_set(sources, targets):
    for s in sources:
        if s not in targets:
            return False
    return True


def find_unmatched_entities(sources, targets):
    sources = list(jieba.cut(sources, cut_all=False))
    targets = list(jieba.cut(targets, cut_all=False))
    unmatched_entities = []
    for entity in sources:
        matched_idx, matched_text, matched_len, matched_target = text_search(entity, targets)
        if matched_len != len(entity) or matched_len != len(matched_target):
            if len(entity) != 0:
                unmatched_entities.append(entity)
            if len(matched_target) != 0:
                unmatched_entities.append(matched_target)

    for entity in targets:
        matched_idx, matched_text, matched_len, matched_target = text_search(entity, sources)
        if matched_len != len(entity) or matched_len != len(matched_target):
            if len(entity) != 0:
                unmatched_entities.append(entity)
            if len(matched_target) != 0:
                unmatched_entities.append(matched_target)
    return unmatched_entities


def main():

    # Initialization
    #menu
    menu_path = './sources/sample_menu_cleaned2.csv'
    menu_data = pd.read_csv(menu_path, error_bad_lines=False, encoding='utf-8')
    #attribute
    attribute_path = './sources/recipe_attribute.csv'
    add_voc_by_attribute(attribute_path)
    attributes = read_attribute_from_csv(attribute_path)
    #recipe
    recipe_jieba_path = './sources/recipe_name_jieba.xlsx'
    # recipe_jieba_path = './sources/recipe_name_jieba_exclude_meishijie.xlsx'
    recipe_jieba_data = load_recipe_jieba_date(recipe_jieba_path)
    # get the jieba results
    recipe_jieba_data = [x[1].split('/') for x in recipe_jieba_data]
    recipe_jieba_data = recipe_jieba_data[1:]
    #saving setting
    recipe_data = recipe_jieba_data
    suffix_str = 'exclude_useless_attri'
    recipe_name = 'jieba_' \
                  '{}_{}'.format(len(recipe_data), suffix_str)
    print("length of recipes: {}".format(len(recipe_data)))
    record_file = open('outputs/match_record_{}.csv'.format(recipe_name), 'w', encoding='utf-8')
    error_file = open('outputs/error_menu_{}.txt'.format(recipe_name), 'w', encoding='utf-8')
    totalmatched_record_file = open('outputs/match_record_{}_totalmatched.csv'.format(recipe_name), 'w',
                                    encoding='utf-8')
    type_record_file = open('outputs/match_record_{}_type.csv'.format(recipe_name), 'w', encoding='utf-8')
    cooking_record_file = open('outputs/match_record_{}_cooking.csv'.format(recipe_name), 'w', encoding='utf-8')
    useless_record_file = open('outputs/match_record_{}_useless.csv'.format(recipe_name), 'w', encoding='utf-8')
    style_record_file = open('outputs/match_record_{}_style.csv'.format(recipe_name), 'w', encoding='utf-8')
    ingredient_record_file = open('outputs/match_record_{}_ingredient.csv'.format(recipe_name), 'w', encoding='utf-8')
    #visualization
    matched_weighted_result = []
    #multi processing setting
    procsss_pool = ProcessPoolExecutor()


    # processing matching
    for menu_idx, menu in menu_data.iterrows():
        if menu_idx % 20 == 0:
            print(menu_idx)
        try:
            # try exception for some menu are wrong
            menu_text = menu['name']
            menu_text_splited = list(jieba.cut(menu_text, cut_all=False))
            matched_score, matched_target_idx, matched_target_str = entity_match(menu_text_splited,
                                                                                 recipe_jieba_data,
                                                                                 attributes)
            unmatched_entities = set(find_unmatched_entities(menu_text, matched_target_str))
            matched_weighted_result.append(matched_score)
            record_str = "{}\t{}\t{:.2}\n".format(
                menu['name'],
                matched_target_str,
                matched_score
            )
            # write outputs to different record files
            if len(unmatched_entities) == 0:
                totalmatched_record_file.write(record_str)
                totalmatched_record_file.flush()
            elif all_in_set(unmatched_entities, attributes['type']):
                type_record_file.write(record_str)
                type_record_file.flush()
            elif all_in_set(unmatched_entities, attributes['cooking method'] | attributes['shape']):
                cooking_record_file.write(record_str)
                cooking_record_file.flush()
            elif all_in_set(unmatched_entities, attributes['taste'] | attributes['other']):
                style_record_file.write(record_str)
                style_record_file.flush()
            elif all_in_set(unmatched_entities,
                            attributes['other'] | attributes['shape'] | attributes['taste'] | attributes['type'] |
                            attributes['cooking method']):
                useless_record_file.write(record_str)
                useless_record_file.flush()
            else:
                ingredient_record_file.write(record_str)
                ingredient_record_file.flush()
            record_file.write(record_str)
            record_file.flush()
        except Exception as e:
            print(e)
    print(matched_weighted_result)
    draw_hist(matched_weighted_result, recipe_name)


if __name__ == '__main__':
    main()
