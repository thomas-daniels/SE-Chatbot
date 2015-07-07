import os


def fixed_font_to_normal(text):
    text = text.replace('\r\n', '\n')
    lines = text.splitlines()
    lines[0] = "    " + lines[0]
    normalized_lines = [x[4:] for x in lines]
    return os.linesep.join(normalized_lines)


def is_fixed_font(text):
    text = text.replace('\r\n', '\n')
    lines = text.splitlines()
    first_line = True
    for l in lines:
        if first_line:
            first_line = False
            continue
        if not l.startswith("    "):
            return False
    return True
