
import pandas as pd

def build_id2res_dict_from_file(path):
    id2res_dict = {}
    res_data = pd.read_csv(path, error_bad_lines=False, encoding='utf-8')
    for i, res in res_data.iterrows():
        id2res_dict[res['restaurant_id']] = res['name']
    return id2res_dict



