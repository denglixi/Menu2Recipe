import pandas as pd
import json
import re

def read_attribute_from_csv(attribute_path):
    attribute_data = pd.read_csv(attribute_path, error_bad_lines=False, encoding='utf-8')
    attribute_data = attribute_data[:6000]

    # id, source, food name, entity, shape, taste, cooking method, other, type
    attr_entity_set = set()
    attr_entity = attribute_data['entity']
    for entities in attr_entity:
        try:
            entities = re.split('[,，]', entities)
            for e in entities:
                attr_entity_set.add(e)
        except:
            continue
    attr_entity = attr_entity_set

    attr_entity = list(attr_entity)
    attr_shape = list(set(attribute_data['shape']))
    attr_taste = list(set(attribute_data['taste']))
    attr_cook = list(set(attribute_data['cooking method']))
    attr_other = list(set(attribute_data['other']) | {'大', '小', '大份', '小份', '大杯', '小杯', '(', ')', '（', '）'})
    attr_type = list(set(attribute_data['type']))

    # attr_shape = set(attribute_data['shape'])
    # attr_taste = set(attribute_data['taste'])
    # attr_cook = set(attribute_data['cooking method'])
    # attr_other = set(attribute_data['other']) | {'大', '小', '大份', '小份', '大杯', '小杯', '(', ')', '（', '）'}
    # attr_type = set(attribute_data['type'])

    attributes = {'entity': attr_entity,
                  'shape': attr_shape,
                  'taste': attr_taste,
                  'cooking method': attr_cook,
                  'other': attr_other,
                  'type': attr_type}
    return attributes

def write_attribute_to_json(attributes):
    attribute_json_path = './sources/attributes.json'
    with open(attribute_json_path, 'w', encoding='utf-8') as f:
        json.dump(attributes, f, ensure_ascii=False)

def load_attribute_from_json(attr_json_path):
    with open(attr_json_path, 'r', encoding='utf-8') as f:
        attributes = json.load(f)
        for k in attributes:
            attributes[k] = set(attributes[k])
    return attributes

if __name__ == '__main__':
    attribute_path = './sources/Attribute/recipe_attribute.csv'
    attributes = read_attribute_from_csv(attribute_path)
    write_attribute_to_json(attributes)