from ChatExchange.chatexchange.client import Client
from ChatExchange.chatexchange.events import MessagePosted
import getpass
import re
from HTMLParser import HTMLParser
import logging.handlers
import os
import os.path
import sys
import pickle
from Config import Config
import ModuleManifest
from Module import MetaModule
from nocharcheck import no_char_check


class Chatbot:
    def __init__(self):
        self.room = None
        self.client = None
        self.privileged_users = []
        self.owners = []
        self.owner_name = ""
        self.chatbot_name = ""
        self.enabled = True
        self.running = True
        self.translation_languages = ["auto", "en", "fr", "nl", "de", "he", "ru", "el", "pt", "es", "fi", "af", "sq", "ar", "hy", "az", "eu", "be", "bn", "bs", "bg", "ca", "ceb", "zh-CN", "hr", "cs", "da",
                                      "eo", "et", "tl", "gl", "ka", "gu", "ht", "ha", "hi", "hmn", "hu", "is", "ig", "id", "ga", "it", "ja", "jw", "kn", "km", "ko", "lo", "la", "lv", "lt", "mk", "ms"
                                      "mt", "mi", "mr", "mn", "ne", "no", "fa", "pl", "pa", "ro", "sr", "sk", "sl", "so", "sw", "sv", "ta", "te", "th", "tr", "uk", "ur", "vi", "cy", "yi", "yo", "zu"]
        self.end_lang = None
        self.translation_chain_going_on = False
        self.translation_switch_going_on = False
        self.banned = {}
        self.site = ""
        self.msg_id_no_reply_found = -1
        self.owner_ids = []
        self.privileged_user_ids = []
        self.modules = MetaModule(ModuleManifest.module_file_names, self)

    def main(self, config_data, additional_general_config):
        if "owners" in Config.General:
            self.owners = Config.General["owners"]
        else:
            sys.exit("Error: no owners found. Please update Config.py.")
        if "privileged_users" in config_data:
            self.privileged_users = config_data["privileged_users"]
        if "owner_name" in Config.General:
            self.owner_name = Config.General["owner_name"]
        else:
            sys.exit("Error: no owner name found. Please update Config.py.")
        if "chatbot_name" in Config.General:
            self.chatbot_name = Config.General["chatbot_name"]
        else:
            sys.exit("Error: no chatbot name found. Please update Config.py.")
        # self.setup_logging() # if you want to have logging, un-comment this line
        if "site" in config_data:
            self.site = config_data["site"]
            print("Site: %s" % self.site)
        else:
            self.site = raw_input("Site: ")
        for o in self.owners:
            if self.site in o:
                self.owner_ids.append(o[self.site])
        if len(self.owner_ids) < 1:
            sys.exit("Error: no owners found for this site: %s." % self.site)
        for p in self.privileged_users:
            if self.site in p:
                self.privileged_user_ids.append(p[self.site])
        if "room" in config_data:
            room_number = config_data["room"]
            print("Room number: %i" % room_number)
        else:
            room_number = int(raw_input("Room number: "))
        if "email" in Config.General:
            email = Config.General["email"]
        elif "email" in additional_general_config:
            email = additional_general_config["email"]
        else:
            email = raw_input("Email address: ")
        if "password" in Config.General: # I would not recommend to store the password in Config.py
            password = Config.General["password"]
        elif "password" in additional_general_config:
            password = additional_general_config["password"]
        else:
            password = getpass.getpass("Password: ")

        if os.path.isfile("bannedUsers.txt"):
            with open("bannedUsers.txt", "r") as f:
                self.banned = pickle.load(f)

        self.client = Client(self.site)
        self.client.login(email, password)
    
        self.room = self.client.get_room(room_number)
        self.room.join()
        bot_message = "Bot started."
        self.room.send_message(bot_message)
        self.room.watch_socket(self.on_event)
        
        while self.running:
            inputted = raw_input("<< ")
            if inputted.strip() == "":
                continue
            if inputted.startswith("$") and len(inputted) > 2:
                command_in = inputted[2:]
                command_out = self.command(command_in, None, None)
                if command_out != False and command_out is not None:
                    print command_out
                    if inputted[1] == "+":
                        self.room.send_message("%s" % command_out)
            else:
                self.room.send_message(inputted)

    def setup_logging(self): # logging method taken from ChatExchange/examples/chat.py
        logger = logging.getLogger(__name__)
        logging.basicConfig(level=logging.INFO)
        logger.setLevel(logging.DEBUG)

        # In addition to the basic stderr logging configured globally
        # above, we'll use a log file for chatexchange.client.
        wrapper_logger = logging.getLogger('chatexchange.client')
        wrapper_handler = logging.handlers.TimedRotatingFileHandler(
           filename='client.log',
            when='midnight', delay=True, utc=True, backupCount=7,
        )
        wrapper_handler.setFormatter(logging.Formatter(
            "%(asctime)s: %(levelname)s: %(threadName)s: %(message)s"
        ))
        wrapper_logger.addHandler(wrapper_handler)

    def on_event(self, event, client):
        watchers = self.modules.get_event_watchers()
        for w in watchers:
            w(event, client, self)
        should_return = False
        if not self.enabled:
            should_return = True
        if isinstance(event, MessagePosted) and (not self.enabled) and event.user.id in self.owner_ids and event.message.content.startswith("&gt;&gt;"):
            should_return = False
        if not self.running:
            should_return = True
        if not isinstance(event, MessagePosted):
            should_return = True
        if isinstance(event, MessagePosted) and self.site in self.banned \
                and event.user.id in self.banned[self.site]:
            should_return = True
        if should_return:
            return
        
        message = event.message
        h = HTMLParser()
        content = h.unescape(message.content_source)

        if event.user.id == self.client.get_me().id:
            return

        content = re.sub(r"^>>\s+", ">>", content)
        content = re.sub(r"\s+", " ", content)
        content = content.strip()
        parts = content.split(" ")
        if not parts[0].startswith(">>") and (len(parts) != 2 or not parts[0].startswith(":")):
            return
        
        if len(parts) == 2 and parts[1] == "!delete!" and parts[0].startswith(":"):
            try:
                if event.user.id in self.privileged_user_ids or event.user.id in self.owner_ids:
                    msg_id_to_delete = int(parts[0][1:])
                    self.client.get_message(msg_id_to_delete).delete()
            except:
                pass
        
        if parts[0].startswith(">>"):
            cmd_args = content[2:]
            if (not cmd_args.split(" ")[0] in no_char_check) and event.user.id not in self.owner_ids and re.compile("[^a-zA-Z0-9 _-]").search(cmd_args):
                message.reply("Command contains invalid characters.")
                return
            output = self.command(cmd_args, message, event)
            if output != False and output is not None:
                if len(output) > 500:
                    message.reply("Output would be longer than 500 characters (the limit), so only the first 500 characters are posted now.")
                    self.room.send_message(output[:500])
                else:
                    message.reply(output)

    def command(self, cmd, msg, event):
        cmd_args = cmd.split(' ')
        cmd_name = cmd_args[0].lower()
        args = cmd_args[1:]
        if cmd_name == "translationchain" or cmd_name == "translationswitch":
            to_translate = " ".join(args[3:])
            args = args[:3]
            args.append(to_translate)
        elif cmd_name == "translate":
            to_translate = " ".join(args[2:])
            args = args[:2]
            args.append(to_translate)
        r = self.modules.command(cmd_name, args, msg, event)
        if r is not False:
            return r
        else:
            return "Command not found."
