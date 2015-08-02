#!/usr/bin/env python

from Chatbot import Chatbot
from ExceptHook import *
from Config import Config

sys.excepthook = uncaught_exception
install_thread_excepthook()
bot = Chatbot()
config_data = {}
additional_general_config = {}
args_length = len(sys.argv)
if "-c" in sys.argv:
    config_index = sys.argv.index("-c") + 1
    if args_length <= config_index:
        sys.exit("Error: no configuration name provided after the -c argument.")
    config_name = sys.argv[config_index]
    if config_name in Config.Configurations:
        config_data = Config.Configurations[config_name]
    else:
        sys.exit("Error: configuration not found.")
if "-s" in sys.argv:
    site_index = sys.argv.index("-s") + 1
    if args_length <= site_index:
        sys.exit("Error: no site provided after the -s argument.")
    config_data["site"] = sys.argv[site_index]
if "-r" in sys.argv:
    room_index = sys.argv.index("-r") + 1
    if args_length <= room_index:
        sys.exit("Error: no room number provided after the -r argument.")
    config_data["room"] = int(sys.argv[room_index])
if "-e" in sys.argv:
    email_index = sys.argv.index("-e") + 1
    if args_length <= email_index:
        sys.exit("Error: no email address provided after the -e argument.")
    additional_general_config["email"] = sys.argv[email_index]
if "-p" in sys.argv:
    password_index = sys.argv.index("-p") + 1
    if args_length <= password_index:
        sys.exit("Error: no password provided after the -p argument.")
    additional_general_config["password"] = sys.argv[password_index]
if "-f" in sys.argv:
    prefix_index = sys.argv.index("-f") + 1
    if args_length <= prefix_index:
        sys.exit("Error: no prefix provided after the -f argument.")
    additional_general_config["prefix"] = sys.argv[prefix_index]
if "-m" in sys.argv:
    message_index = sys.argv.index("-m") + 1
    if args_length <= message_index:
        sys.exit("Error: no message provided after the -m argument.")
    additional_general_config["message"] = sys.argv[message_index]

bot.main(config_data, additional_general_config)
