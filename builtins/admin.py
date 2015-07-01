from Module import Command
import time
import os
import pickle
from ChatExchange.chatexchange.messages import Message


def command_stop(cmd, bot, args, msg, event):
    bot.enabled = False
    bot.running = False
    if msg is not None:
        msg.reply("Bot terminated.")
        time.sleep(2)
    bot.room.leave()
    bot.client.logout()
    time.sleep(5)
    os._exit(0)


def command_disable(cmd, bot, args, msg, event):
    bot.enabled = False
    return "Bot disabled, run >>enable to enable it again."


def command_enable(cmd, bot, args, msg, event):
    bot.enabled = True
    return "Bot enabled."


def command_ban(cmd, bot, args, msg, event):
    try:
        banned_user = int(args[0])
    except ValueError:
        return "Invalid arguments."
    try:
        user_name = bot.client.get_user(banned_user).name.replace(" ", "")
    except:
        return "Could not fetch user; please check whether the user exists."
    if not bot.site in bot.banned:
        bot.banned[bot.site] = []
    if not banned_user in bot.banned[bot.site]:
        bot.banned[bot.site].append(banned_user)
    else:
        return "Already banned."
    with open("bannedUsers.txt", "w") as f:
        pickle.dump(bot.banned, f)
    return "User @%s has been banned." % user_name


def command_unban(cmd, bot, args, msg, event):
    try:
        banned_user = int(args[0])
    except ValueError:
        return "Invalid arguments."
    try:
        user_name = bot.client.get_user(banned_user).name.replace(" ", "")
    except:
        return "Could not fetch user; please check whether the user exists."
    if not bot.site in bot.banned:
        return "Not banned."
    if not banned_user in bot.banned[bot.site]:
        return "Not banned."
    bot.banned[bot.site].remove(banned_user)
    with open("bannedUsers.txt", "w") as f:
        pickle.dump(bot.banned, f)
    return "User @%s has been unbanned." % user_name


def command_delete(cmd, bot, args, msg, event):
    if len(args) == 0:
        return "Not enough arguments."
    try:
        message_id = int(args[0])
    except:
        return "Invalid arguments."
    message_to_delete = Message(message_id, bot.client)
    try:
        message_to_delete.delete()
    except:
        pass

commands = [
    Command('stop', command_stop, "Owner-only command. Stops the bot. Syntax: `>>stop`", False, True),
    Command('disable', command_disable, "Owner-only command. Disables the bot. Syntax: `>>disable`", False, True),
    Command('enable', command_enable, "Owner-only command. Enables the bot when it is disabled. Syntax: `>>enable`", False, True),
    Command('ban', command_ban, "Owner-only command. Bans a user from using the bot. Syntax: `>>ban user_id`", False, True),
    Command('unban', command_unban, "Owner-only command. Unbans a banned user. Syntax: `>>unban user_id`", False, True),
    Command('delete', command_delete, "Only for privileged users. Deletes a message of the bot. Syntax: `>>delete msg_id` or `<reply> !delete!`", True, True)
]