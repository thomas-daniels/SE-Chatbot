from Module import Command
import random
import sys


def command_random(cmd, bot, args, msg, event):
    return str(random.random())


def command_randomint(cmd, bot, args, msg, event):
    if len(args) == 0:
        return str(random.randint(0, sys.maxint))
    if len(args) == 1:
        try:
            max_ = int(args[0])
        except ValueError:
            return "Invalid arguments."
        min_ = 0
        if min_ > max_:
            return "Min cannot be greater than max."
        return str(random.randint(min_, max_))
    if len(args) == 2:
        try:
            min_ = int(args[0])
            max_ = int(args[1])
        except ValueError:
            return "Invalid arguments."
        if min_ > max_:
            return "Min cannot be greater than max."
        return str(random.randint(min_, max_))
    return "Too many arguments."


def command_randomchoice(cmd, bot, args, msg, event):
    if len(args) < 1:
        return "Not enough arguments."
    return random.choice(args)


def command_shuffle(cmd, bot, args, msg, event):
    if len(args) < 1:
        return "Not enough arguments."
    list_to_shuffle = list(args)
    random.shuffle(list_to_shuffle)
    return " ".join(list_to_shuffle)

commands = [
    Command('random', command_random, "Returns a random floating-point number. Syntax: `>>random`", False, False),
    Command('randomint', command_randomint, "Returns a random integer. Syntax: `>>randomint [ [ min ] max ]`", False, False),
    Command('randomchoice', command_randomchoice, "Randomly chooses an item from a given list. Syntax: `>>randomchoice listitem1 listitem2 listitem3 ...`", False, False),
    Command('shuffle', command_shuffle, "Shuffles a list of given items. Syntax: `>>shuffle listitem1 listitem2 listitem3 ...`", False, False)
]
