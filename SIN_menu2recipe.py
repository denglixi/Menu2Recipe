'''
menu to recipe mapping for singapore food.
'''
import os
from concurrent.futures import ProcessPoolExecutor, as_completed
from functools import wraps


import jieba
import pandas as pd

from lib.CHN_entity_match import entity_match, find_unmatched_entities
from lib.text_search import text_search_fully_match
from lib.utilis import all_in_set
from lib.visulization import draw_hist
from lib.restaurant import build_id2res_dict_from_file


def text_search_fully_match_with_resid(func, res_id, *args, **kwargs):
    matched_score, matched_target, matched_voc_list, menu_str, matched_idx = func(*args, **kwargs)
    return res_id, matched_score, matched_target, matched_voc_list, menu_str, matched_idx


def multiprocess_main():
    # Initialization
    # menu
    menu_path = './sources/Singapore/sample_menu_sg.csv'
    menu_data = pd.read_csv(menu_path, error_bad_lines=False, encoding='utf-8')
    menu_data.drop_duplicates('name', 'first', True)
    print('len of menu: {}'.format(len(menu_data)))

    # recipe
    recipe_food_composition_path = './sources/Singapore/food_sg.csv'
    recipe_food_composition_data = pd.read_csv(recipe_food_composition_path, error_bad_lines=False, encoding='utf-8')
    recipe_food_composition_data.drop_duplicates('display_name', 'first', True)
    recipe_food_composition_data = [x['display_name'].split(" ") for _, x in recipe_food_composition_data.iterrows()]

    #restaurant
    res_file = './sources/Singapore/sample_restaurant_sg.csv'
    id2res_dict = build_id2res_dict_from_file(res_file)

    # saving setting
    recipe_data = recipe_food_composition_data
    suffix_str = 'drop_duplicates'
    recipe_name = 'food_composition'
    save_dir_name = '{}_{}_{}'.format(recipe_name, len(recipe_data), suffix_str)
    print("length of recipes: {}".format(len(recipe_data)))

    output_save_dir = 'outputs/match_record_{}'.format(save_dir_name)
    if not os.path.exists(output_save_dir):
        os.makedirs(output_save_dir)
    record_file = open(os.path.join(output_save_dir, 'all.csv'), 'w', encoding='utf-8')
    error_file = open(os.path.join(output_save_dir, 'error_menu.txt'), 'w', encoding='utf-8')
    total_matched_record_file = open(os.path.join(output_save_dir, 'total_matched.csv'), 'w', encoding='utf-8')
    type_record_file = open('outputs/match_record_{}/type.csv'.format(save_dir_name), 'w', encoding='utf-8')
    cooking_record_file = open('outputs/match_record_{}/cooking.csv'.format(save_dir_name), 'w', encoding='utf-8')
    useless_record_file = open('outputs/match_record_{}/useless.csv'.format(save_dir_name), 'w', encoding='utf-8')
    style_record_file = open('outputs/match_record_{}/style.csv'.format(save_dir_name), 'w', encoding='utf-8')
    ingredient_record_file = open('outputs/match_record_{}/ingredient.csv'.format(save_dir_name), 'w', encoding='utf-8')
    unknown_record_file = open('outputs/match_record_{}/unknown.csv'.format(save_dir_name), 'w', encoding='utf-8')
    # visualization
    matched_weighted_result = []
    # multi processing setting
    procsss_pool = ProcessPoolExecutor(max_workers=60)
    fs_list = []

    # set up multiprocess pool
    for menu_idx, menu in menu_data.iterrows():
        if menu_idx % 200 == 0:
            print(menu_idx)
        try:
            # try exception for some menu are wrong
            menu_text = menu['name']
            menu_text_splited = menu_text.split(" ")
            #a = process_pool_func(text_search_fully_match,menu['restaurant_id'],  menu_text_splited, recipe_data)
            fs_list.append(procsss_pool.submit(text_search_fully_match_with_resid,
                                               text_search_fully_match,
                                               menu['restaurant_id'],
                                               menu_text_splited,
                                               recipe_data
                                               ))
        except Exception as e:
            print(e)

    # get results from pool
    unmatched_uncategoried_entities = []
    fs_count = 0
    for feature in as_completed(fs_list):
        fs_count += 1
        if fs_count % 20 == 0:
            print(fs_count)
        res_id, matched_score, matched_target, matched_voc_list, menu_str, matched_idx = feature.result()
        #unmatched_entities = set(find_unmatched_entities(menu_text, matched_target_str))
        #matched_weighted_result.append(matched_score)
        res_name = id2res_dict[res_id]

        record_str = "{}\t{}\t{}\t{:.2}\n".format(
            res_name,
            menu_str,
            matched_target,
            float(matched_score)
        )

        # write outputs to different record files
        record_file.write(record_str)
        record_file.flush()

    print(matched_weighted_result)
    draw_hist(matched_weighted_result, save_dir_name)


if __name__ == '__main__':
    # main()
    multiprocess_main()
