import os
from concurrent.futures import ProcessPoolExecutor, as_completed

import jieba
import pandas as pd

from lib.attribute import read_attribute_from_csv, load_attribute_from_json
from lib.dataload import load_recipe_jieba_date, merge_all_json
from lib.CHN_entity_match import entity_match, find_unmatched_entities
from lib.jieba_config import add_voc_by_attribute
from lib.utilis import all_in_set
from lib.visulization import draw_hist


def multiprocess_main():
    # Initialization
    # menu
    menu_path = './sources/Menu/sample_menu_cleaned2.csv'
    menu_data = pd.read_csv(menu_path, error_bad_lines=False, encoding='utf-8')

    # attribute
    attribute_path = './sources/Attribute/recipe_attribute.csv'
    add_voc_by_attribute(attribute_path)
    attributes = read_attribute_from_csv(attribute_path)
    attribute_json_path = './sources/Attribute/attributes.json'
    attributes = load_attribute_from_json(attribute_json_path)

    # recipe
    recipe_jieba_path = './sources/recipe/recipe_name_jieba.xlsx'
    # recipe_jieba_path = './sources/recipe/recipe_name_jieba_exclude_meishijie.xlsx'
    recipe_jieba_data = load_recipe_jieba_date(recipe_jieba_path)
    # get the jieba results
    recipe_jieba_data = [x[1].split('/') for x in recipe_jieba_data]
    recipe_jieba_data = recipe_jieba_data[1:]

    meishijie_recipe_path = './sources/recipe/meishiji'
    meishijie_recipe_data = merge_all_json(meishijie_recipe_path)
    meishijie_recipe_data = [list(jieba.cut(x['name'], cut_all=False)) for x in meishijie_recipe_data]

    # saving setting
    recipe_data = meishijie_recipe_path
    suffix_str = 'exclude_useless_attri'
    recipe_name = 'meishijie_' \
                  '{}_{}'.format(len(recipe_data), suffix_str)
    print("length of recipes: {}".format(len(recipe_data)))

    output_save_dir = 'outputs/match_record_{}'.format(recipe_name)
    if not os.path.exists(output_save_dir):
        os.makedirs(output_save_dir)
    record_file = open(os.path.join(output_save_dir, 'all.csv'), 'w', encoding='utf-8')
    error_file = open(os.path.join(output_save_dir, 'error_menu.txt'), 'w', encoding='utf-8')
    totalmatched_record_file = open(os.path.join(output_save_dir, 'totalmatched.csv'), 'w', encoding='utf-8')
    type_record_file = open('outputs/match_record_{}/type.csv'.format(recipe_name), 'w', encoding='utf-8')
    cooking_record_file = open('outputs/match_record_{}/cooking.csv'.format(recipe_name), 'w', encoding='utf-8')
    useless_record_file = open('outputs/match_record_{}/useless.csv'.format(recipe_name), 'w', encoding='utf-8')
    style_record_file = open('outputs/match_record_{}/style.csv'.format(recipe_name), 'w', encoding='utf-8')
    ingredient_record_file = open('outputs/match_record_{}/ingredient.csv'.format(recipe_name), 'w', encoding='utf-8')
    unknown_record_file = open('outputs/match_record_{}/unknown.csv'.format(recipe_name), 'w', encoding='utf-8')
    # visualization
    matched_weighted_result = []
    # multi processing setting
    procsss_pool = ProcessPoolExecutor()
    fs_list = []

    # set up multiprocess pool
    for menu_idx, menu in menu_data.iterrows():
        if menu_idx % 200 == 0:
            print(menu_idx)
        try:
            # try exception for some menu are wrong
            menu_text = menu['name']
            menu_text_splited = list(jieba.cut(menu_text, cut_all=False))
            fs_list.append(procsss_pool.submit(entity_match,
                                               menu_text_splited,
                                               recipe_data,
                                               attributes))
        except Exception as e:
            print(e)

    # get results from pool

    unmatched_uncategoried_entities = []

    fs_count = 0
    for feature in as_completed(fs_list):
        fs_count += 1
        if fs_count % 20 == 0:
            print(fs_count)
        matched_score, matched_target_idx, matched_target_str, menu_text = feature.result()
        unmatched_entities = set(find_unmatched_entities(menu_text, matched_target_str))
        matched_weighted_result.append(matched_score)
        record_str = "{}\t{}\t{:.2}\n".format(
            menu_text,
            matched_target_str,
            float(matched_score)
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
        elif all_in_set(unmatched_entities, attributes['entity']):
            ingredient_record_file.write(record_str)
            ingredient_record_file.flush()
        else:
            unmatched_entities_str = " ".join(unmatched_entities)
            record_str = "{}\t{}\t{:.2}\t{}\n".format(
                menu_text,
                matched_target_str,
                float(matched_score), unmatched_entities_str)
            unknown_record_file.write(record_str)
            unknown_record_file.flush()
        record_file.write(record_str)
        record_file.flush()

    print(matched_weighted_result)
    draw_hist(matched_weighted_result, recipe_name)


if __name__ == '__main__':
    # main()
    multiprocess_main()
