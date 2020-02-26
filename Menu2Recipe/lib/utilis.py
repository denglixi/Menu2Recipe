def all_in_set(sources, targets):
    """
    determine whether all elements of sources in set targets
    :param sources:
    :param targets:
    :return:
    """
    if len(sources) == 0:
        return False
    for s in sources:
        if s not in targets:
            return False
    return True
