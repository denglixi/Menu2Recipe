import jieba
import pandas as pd

from lib.dataload import load_recipe_jieba_date, merge_all_json
from lib.CHN_entity_match import entity_match, find_unmatched_entities
from lib.attribute import read_attribute_from_csv, load_attribute_from_json
from lib.text_search import text_search_fully_match


def Chinese_food_ingredient_recognition(food_name):
    # set menu, recipe and attirbute.
    menu = food_name

    meishijie_recipe_path = './sources/recipe/meishiji'
    meishijie_recipe_data = merge_all_json(meishijie_recipe_path)
    meishijie_recipe_name_data = [list(jieba.cut(x['name'], cut_all=False)) for x in meishijie_recipe_data]

    attribute_json_path = './sources/Attribute/attributes.json'
    attributes = load_attribute_from_json(attribute_json_path)

    _, id, _, _  = entity_match(menu, meishijie_recipe_name_data, attributes)
    ingredients = meishijie_recipe_data[id]['ingredients']
    #print(ingredients)
    return ingredients

def Singpore_food_ingredint_recognition(food_name):
    """
    :param food_name:
    :return:
    The recipe data of Singapore food lacks ingredient information so this function return recipe data.
    """

    menu_text_splited = food_name.split(" ")
    # recipe
    recipe_food_composition_path = './sources/Singapore/food_sg.csv'
    recipe_food_composition_data = pd.read_csv(recipe_food_composition_path, error_bad_lines=False, encoding='utf-8')
    recipe_food_composition_data.drop_duplicates('display_name', 'first', True)
    recipe_food_composition_name_data = [x['display_name'].split(" ") for _, x in recipe_food_composition_data.iterrows()]

    _, _, _, _, id = text_search_fully_match(menu_text_splited, recipe_food_composition_name_data)
    matched_recipe = recipe_food_composition_data.iloc[id]
    return matched_recipe


def main():
    ingredient = Chinese_food_ingredient_recognition('紫菜蛋花汤')
    print(ingredient)
    recipe = Singpore_food_ingredint_recognition('fried rice')
    print(recipe)

if __name__ == "__main__":
    main()