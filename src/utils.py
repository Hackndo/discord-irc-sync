def replace_all(text, l):
    for t in l:
        text = text.replace(t[0], t[1])
    return text