# contains commands which do not depend on any variables in the WordAssociationChatbot class
import random
import sys
from datetime import datetime


def command_alive(args, msg, event):
    return "Yes, I'm alive."


def command_random(args, msg, event):
    return str(random.random())


def command_randomint(args, msg, event):
    if len(args) == 0:
        return str(random.randint(0, sys.maxint))
    if len(args) == 1:
        max_ = -1
        try:
            max_ = int(args[0])
        except ValueError:
            return "Invalid arguments."
        min_ = 0
        if min_ > max_:
            return "Min cannot be greater than max."
        return str(random.randint(min_, max_))
    if len(args) == 2:
        min_ = -1
        max_ = -1
        try:
            min_ = int(args[0])
            max_ = int(args[1])
        except ValueError:
            return "Invalid arguments."
        if min_ > max_:
            return "Min cannot be greater than max."
        return str(random.randint(min_, max_))
    return "Too many arguments."


def command_randomchoice(args, msg, event):
    if len(args) < 1:
        return "Not enough arguments."
    return random.choice(args)


def command_shuffle(args, msg, event):
    if len(args) < 1:
        return "Not enough arguments."
    list_to_shuffle = list(args)
    random.shuffle(list_to_shuffle)
    return " ".join(list_to_shuffle)


def command_utc(args, msg, event):
    return datetime.utcnow().ctime()


def command_xkcdrandomnumber(args, msg, event):
    return "[4 // Chosen by fair dice roll. Guaranteed to be random.](http://xkcd.com/221/)"


def command_xkcd(args, msg, event):
    if len(args) < 1:
        return "Not enough arguments."
    id_ = -1
    try:
        id_ = int(args[0])
    except:
        return "Invalid arguments."
    return "http://xkcd.com/%i/" % id_
