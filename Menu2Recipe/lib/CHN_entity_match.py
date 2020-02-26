import jieba

from lib.text_search import text_search_lcs


def find_unmatched_entities(sources, targets):
    sources = list(jieba.cut(sources, cut_all=False))
    targets = list(jieba.cut(targets, cut_all=False))
    unmatched_entities = []
    for entity in sources:
        matched_idx, matched_text, matched_len, matched_target = text_search_lcs(entity, targets)
        if matched_len != len(entity) or matched_len != len(matched_target):
            if len(entity) != 0:
                unmatched_entities.append(entity)
            if len(matched_target) != 0:
                unmatched_entities.append(matched_target)

    for entity in targets:
        matched_idx, matched_text, matched_len, matched_target = text_search_lcs(entity, sources)
        if matched_len != len(entity) or matched_len != len(matched_target):
            if len(entity) != 0:
                unmatched_entities.append(entity)
            if len(matched_target) != 0:
                unmatched_entities.append(matched_target)
    return unmatched_entities


def entity_match(source_entities, target_entities_list, attributes):
    """
    match source entities to target lists of eneities
    :param source_entities: a list of entities.
    :param target_entities_list: a list of list of entities
    :param attributes:
    :return:
    """
    max_matched_score = 0
    matched_target_idx = -1
    matched_target_str = ''
    attribute_uncount_set = attributes['other'] | attributes['shape'] | attributes['taste'] | attributes['type'] | \
                            attributes['cooking method']
    # Debug
    source_str = "".join(source_entities)
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

        # exclude empty target
        if target_len == 0:
            continue

        # calculate the match score for each source entities, i.e. each food
        matched_score = 0

        for source_entity in source_entities:
            if len(source_entity) == 0:
                continue
            matched_idx, matched_text, matched_len, matched_target = text_search_lcs(source_entity, target_entities)
            # increase the matched score of meat ingredients
            meat_match_len = 0

            if len(matched_text) > 0:
                _, _, meat_match_len, _ = text_search_lcs(matched_text, ['猪', '鸭', '鱼', '肉', '牛', '羊', '虾'])
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

    return max_matched_score, matched_target_idx, matched_target_str, source_str
