def replace_all(text, l):
    for t in l:
        text = text.replace(t[0], t[1])
    return text


def is_included(a,b):
    """
    Return 0 if a is included in b
    Return -1 if a intersects b but a not included in b and b not included in a
    Return 1 else
    """
    if a[1] >= b[1] and a[2] <= b[2]:
        return 0
    elif a[1] > b[1] and a[2] > b[2] or a[1] < b[1] and a[2] < b[2]:
        return -1
    else:
        return 1
