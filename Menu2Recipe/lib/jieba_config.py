import pandas as pd
import jieba


def add_voc_by_attribute(path):
    attribute_data = pd.read_csv(path, error_bad_lines=False, encoding='utf-8')
    # id,source,food name,entity,shape,taste,cooking method,other,type
    for attr_key in ['shape', 'taste', 'cooking method', 'other', 'type']:  # eclude 'entity'
        attr_entity = set(attribute_data[attr_key])
        for entity in attr_entity:
            if type(entity) is not str:
                continue
            jieba.add_word(entity)
