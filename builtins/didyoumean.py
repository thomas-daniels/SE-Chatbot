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


def on_bot_load(bot):
    orig_method = bot.command

    def command_with_didyoumean(cmd, msg, event):
        result = orig_method(cmd, msg, event)
        if result == "Command not found.":
            dym = did_you_mean(cmd.split(' ')[0].lower(), [command.name for command in bot.modules.list_commands()])
            if dym is None:
                return "Command not found."
            else:
                return "Command not found. Did you mean: `%s`?" % dym
        else:
            return result

    bot.command = command_with_didyoumean

commands = []