import os


def fixed_font_to_normal(text):
    text = text.replace('\r\n', '\n')
    lines = text.splitlines()
    normalized_lines = [x[4:] for x in lines]
    return os.linesep.join(normalized_lines)
