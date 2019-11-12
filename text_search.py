
def text_search(source, target):
    """
    Given a source str, search the most matched string in the target set
    :param source: a source string
    :param target: a string iterable set
    :return:
    """
    matched_idx = -1
    matched_text = ""
    matched_len = 0
    matched_target = ""
    matched_percentage = 0
    for i, target_text in enumerate(target):
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
