from __future__ import division


def unique_sorted(s):
    return ''.join(sorted(set(s)))


def did_you_mean(given, cmd_name_list):
    highest_ranked = ("", 0)
    given = unique_sorted(given.lower())
    for name in cmd_name_list:
        nameu = unique_sorted(name)
        score = 0
        for c in given:
            if c in nameu:
                score += 1
        if score >= len(name) / 2 and score > highest_ranked[1]:
            highest_ranked = (name, score)
    if highest_ranked[1] == 0:
        return None
    else:
        return highest_ranked[0]
