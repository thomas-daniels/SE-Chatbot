from Module import Command
import time
import os
import SaveIO
from ChatExchange.chatexchange.messages import Message
from ChatExchange.chatexchange.events import MessagePosted

save_subdir = 'admin'


def command_stop(cmd, bot, args, msg, event):
    bot.bot_stopping()
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
    global command_banned_users
    global banned_users
    try:
        banned_user = int(args[0])
    except ValueError:
        return "Invalid arguments."
    try:
        user_name = bot.client.get_user(banned_user).name.replace(" ", "")
    except:
        return "Could not fetch user; please check whether the user exists."
    if len(args) > 1:
        command = args[1]
        if command not in command_banned_users:
            command_banned_users[command] = [ ]
        if banned_user not in command_banned_users[command]:
            command_banned_users[command].append(banned_user)
            SaveIO.save(command_banned_users, save_subdir, 'command_banned_users')
            return "User @%s has been banned from using >>%s." % (user_name, command)
        else:
            return "Already banned."
    if bot.site not in banned_users:
        banned_users[bot.site] = []
    if banned_user not in banned_users[bot.site]:
        banned_users[bot.site].append(banned_user)
    else:
        return "Already banned."
    SaveIO.save(banned_users, save_subdir, 'banned_users')
    return "User @%s has been banned." % user_name


def command_unban(cmd, bot, args, msg, event):
    global banned_users
    global command_banned_users
    try:
        banned_user = int(args[0])
    except ValueError:
        return "Invalid arguments."
    try:
        user_name = bot.client.get_user(banned_user).name.replace(" ", "")
    except:
        return "Could not fetch user; please check whether the user exists."
    if len(args) > 1:
        command = args[1]
        if command in command_banned_users and banned_user in command_banned_users[command]:
            command_banned_users[command].remove(banned_user)
            if len(command_banned_users[command])==0:
                del command_banned_users[command]
            SaveIO.save(command_banned_users, save_subdir, 'command_banned_users')
            return "User @%s has been unbanned from using >>%s." % (user_name, command)
        else:
            return "Not banned"
    else:
        if bot.site not in banned_users:
            return "Not banned."
        if banned_user not in banned_users[bot.site]:
            return "Not banned."
        banned_users[bot.site].remove(banned_user)
        SaveIO.save(banned_users, save_subdir, 'banned_users')
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
    Command('ban', command_ban, "Owner-only command. Bans a user from using the bot. Syntax: `>>ban user_id [command]`", False, True),
    Command('unban', command_unban, "Owner-only command. Unbans a banned user. Syntax: `>>unban user_id` [command]", False, True),
    Command('delete', command_delete, "Only for privileged users. Deletes a message of the bot. Syntax: `>>delete msg_id` or `<reply> !delete!`", True, True)
]

command_banned_users = { }
banned_users = { }

def command_ban_deco(func):
    global command_banned_users
    def check_banned(cmd, msg, event, *args, **kwargs):
        cmd_args = cmd.split(' ')
        cmd_name = cmd_args[0].lower()
        if cmd_name not in command_banned_users or event.user.id not in command_banned_users[cmd_name]:
            return func(cmd, msg, event, *args, **kwargs)
        else:
            return "You have been banned from using that command."
    return check_banned

def ban_deco(func, bot):
    global banned_users
    def check_banned(event, client, *args, **kwargs):
        if isinstance(event, MessagePosted) and bot.site in banned_users \
                and event.user.id in banned_users[bot.site]:
            return
        else:
            return func(event, client, *args, **kwargs)
    return check_banned

def on_bot_load(bot):
    global command_banned_users
    global banned_users
    bot.command = command_ban_deco(bot.command)
    bot.on_event = ban_deco(bot.on_event, bot)
    command_banned_users = SaveIO.load(save_subdir, 'command_banned_users')
    banned_users = SaveIO.load(save_subdir, 'banned_users')