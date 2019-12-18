def text_search_fully_match(source, targets):
    """
    :param source: list of voc string
    :param targets: list of list of voc string
    :return:
    """
    matched_idx = -1
    matched_voc_list = []
    matched_len = 0
    matched_target = ""
    matched_score = 0
    for i, target_text in enumerate(targets):
        temp_matched_count, temp_matched_voc_list = vocabulary_match(source, target_text)
        total_voc_lens = len(source) + len(target_text)
        temp_matched_score = temp_matched_count * 2 / total_voc_lens
        if temp_matched_score > matched_score:
            matched_score = temp_matched_score
            matched_target = " ".join(target_text)
            matched_voc_list = temp_matched_voc_list
    menu_str = " ".join(source)

    return matched_score, matched_target, matched_voc_list, menu_str


def find_unmatched_vocabularies(source, target):
    sources = source.split(" ")
    targets = target.split(" ")
    unmatched_entities = []
    for entity in sources:
        matched_idx, matched_text, matched_len, matched_target = text_search_fully_match(entity, targets)
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


def vocabulary_match(sources, targets):
    matched_count = 0
    matched_voc_list = []
    for s_v in sources:
        for t_v in targets:
            if s_v == t_v:
                matched_count += 1
                matched_voc_list.append(s_v)
    return matched_count, matched_voc_list


def text_search_lcs(source, targets):
    """
    Given a source str, search the most matched string in the target set by longest Common Subsequence algorithm
    :param source: a source string
    :param targets: a string iterable set
    :return:
    """
    matched_idx = -1
    matched_text = ""
    matched_len = 0
    matched_target = ""
    matched_percentage = 0
    for i, target_text in enumerate(targets):
        temp_matched_len, temp_matched_text = find_lcsubstr(source, target_text)
        temp_percentage = (temp_matched_len / len(source) + temp_matched_len / len(target_text)) / 2
        # if temp_matched_len > matched_len:
        if temp_percentage > matched_percentage:
            matched_percentage = temp_percentage
            matched_len = temp_matched_len
            matched_text = temp_matched_text
            matched_idx = i
            matched_target = target_text
    return matched_idx, matched_text, matched_len, matched_target


def find_lcsubstr(s1, s2):
    """
    find longest substring between two string
    :param s1:
    :param s2:
    :return:
    """
    m = [[0 for i in range(len(s2) + 1)] for j in range(len(s1) + 1)]  # 生成0矩阵，为方便后续计算，比字符串长度多了一列
    mmax = 0  # 最长匹配的长度
    p = 0  # 最长匹配对应在s1中的最后一位
    for i in range(len(s1)):
        for j in range(len(s2)):
            if s1[i] == s2[j]:
                m[i + 1][j + 1] = m[i][j] + 1
                if m[i + 1][j + 1] > mmax:
                    mmax = m[i + 1][j + 1]
                    p = i + 1
    return mmax, s1[p - mmax:p]
