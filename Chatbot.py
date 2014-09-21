#!/usr/bin/env python

import chatexchange.client
import chatexchange.events
import getpass
import re
from GetAssociatedWord import GetAssociatedWord
from HTMLParser import HTMLParser
import thread
import time
import random
import requests
import urllib
import logging.handlers
import os.path
import sys
from SpellManager import SpellManager
import pickle

class WordAssociationBot:
    
    def main(self):
        self.room = None
        self.client = None
        self.owner_id = 229438 # change this into your ID
        self.owner_name = "ProgramFOX" # change this into your name
        self.enabled = True
        self.running = True
        self.waiting_time = -1
        self.current_word_to_reply_to = ""
        self.latest_words = []
        self.in_shadows_den = False
        self.translation_languages = [ "auto", "en", "fr", "nl", "de", "he", "ru", "el", "pt", "es", "fi", "af", "sq", "ar", "hy", "az", "eu", "be", "bn", "bs", "bg", "ca", "ceb", "zh-CN", "hr", "cs", "da",
                                       "eo", "et", "tl", "gl", "ka", "gu", "ht", "ha", "hi", "hmn", "hu", "is", "ig", "id", "ga", "it", "ja", "jw", "kn", "km", "ko", "lo", "la", "lv", "lt", "mk", "ms"
                                       "mt", "mi", "mr", "mn", "ne", "no", "fa", "pl", "pa", "ro", "sr", "sk", "sl", "so", "sw", "sv", "ta", "te", "th", "tr", "uk", "ur", "vi", "cy", "yi", "yo", "zu" ]
        self.end_lang = None
        self.translation_chain_going_on = False
        self.translation_switch_going_on = False
        self.spell_manager = SpellManager()
        self.links = []
        self.banned = {}
        self.site = ""
        self.setup_logging()
        self.msg_id_no_reply_found = -1
        self.commands = { 
            'translationchain': self.command_translationchain,
            'translationswitch': self.command_translationswitch,
            'translate': self.command_translate,
            'random': self.command_random,
            'randomint': self.command_randomint,
            'randomchoice': self.command_randomchoice,
            'shuffle': self.command_shuffle,
            'listcommands': self.command_listcommands,
            'help': self.command_help
        }
        self.shadows_den_specific_commands = {
            'time': self.command_time,
            'viewspells': self.command_viewspells,
            'link': self.command_link,
            'removelink': self.command_removelink,
            'reply': self.command_reply
        }
        self.owner_commands = {
            'stop': self.command_stop,
            'disable': self.command_disable,
            'enable': self.command_enable,
            'award': self.command_award,
            'emptyqueue': self.command_emptyqueue,
            'ban': self.command_ban,
            'unban': self.command_unban 
        }
        self.spell_manager.init()
        in_den = raw_input("Does the bot run in Shadow's Den? (y/n) ").lower()
        if in_den == "y":
            self.in_shadows_den = True
        elif in_den == "n":
            self.in_shadows_den = False
        else:
            self.in_shadows_den = False
            print("Invalid input; assumed 'no'")
        self.site = raw_input("Site: ")
        room_number = int(raw_input("Room number: "))
        email = raw_input("Email address: ")
        password = getpass.getpass("Password: ")
        
        if os.path.isfile("config.txt"):
            f = open("config.txt", "r")
            self.waiting_time = int(f.read());
            f.close()
        else:
            f = open("config.txt", "w")
            f.write("20")
            f.close()
            
        if os.path.isfile("linkedWords.txt"):
            with open("linkedWords.txt", "r") as f:
                self.links = pickle.load(f)
        if os.path.isfile("bannedUsers.txt"):
            with open("bannedUsers.txt", "r") as f:
                self.banned = pickle.load(f)

        self.client = chatexchange.client.Client(self.site)
        self.client.login(email, password)
        
        self.spell_manager.c = self.client
    
        self.room = self.client.get_room(room_number)
        self.room.join()
        bot_message = "Bot started with waiting time set to %i seconds." % self.waiting_time if self.in_shadows_den else "Bot started."
        self.room.send_message(bot_message)
        self.room.watch(self.on_event)
            
        thread.start_new_thread(self.scheduled_empty_queue, ())
        
        while self.running:
            inputted = raw_input("<< ")
            if inputted.startswith("$") and len(inputted) > 2:
                command_in = inputted[2:]
                command_out = self.command(command_in, None, None)
                if command_out != False and command_out is not None:
                    print command_out
                if inputted[1] == "+":
                    self.room.send_message("%s" % command_out)
            else:
                self.room.send_message(inputted)
                    
    
    def setup_logging(self):
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
                    
    def scheduled_empty_queue(self):
        while self.running:
            time.sleep(15 * 60)
            awarded = self.spell_manager.empty_queue()
            for s in awarded:
                if self.room is not None:
                    self.room.send_message(s)
                else:
                    print s
            
    def reply_word(self, message, wait, orig_word):
        self.current_word_to_reply_to = orig_word
        if wait and self.waiting_time > 0:
            time.sleep(self.waiting_time)
        if self.current_word_to_reply_to != orig_word:
            return
        word_tuple = self.find_associated_word(orig_word, message)
        word = word_tuple[0]
        word_found = word_tuple[1]
        #if word == self.current_word_to_reply:
            #if word is not None:
            #    message.reply(word);
            #else:
            #    self.room.send_message("No associated word found for %s" % orig_word)
        if word is None and not word_found:
            self.room.send_message("No associated word found for %s." % orig_word)
            self.msg_id_no_reply_found = message.id
        elif word is None and word_found:
            self.room.send_message("Associated words found for %s, but all of them have been posted in the latest 10 messages." % orig_word)
            self.msg_id_no_reply_found = -1
        else:
            self.msg_id_no_reply_found = -1
            message.reply(word)

    def on_event(self, event, client):
        if self.in_shadows_den:
            self.spell_manager.check_spells(event)
        should_return = False
        if not self.enabled:
            should_return = True
        if (not self.enabled) and event.user.id == self.owner_id and event.message.content.startswith("&gt;&gt;"):
            should_return = False
        if not self.running:
            should_return = True
        if not isinstance(event, chatexchange.events.MessagePosted):
            should_return = True
        if should_return:
            return
        
        message = event.message

        if event.user.id == self.client.get_me().id:
            return
        
        h = HTMLParser()
        content = h.unescape(message.content_source)
        if not content.startswith(">>translat"):
            content = re.sub(r"\[(.+?)\]\(.+?\)", r"\1", content)
            content = re.sub(r"\(.+?\)", "", content)
        content = re.sub(r"\s+", " ", content)
        content = content.strip()
        parts = content.split(" ")
        if (not parts[0].startswith(">>")) and (len(parts) != 2 or not parts[0].startswith(":")) and (event.user.id != -2):
            return

        if self.in_shadows_den and parts[0].startswith(":") and re.compile("^:([0-9]+)$").search(parts[0]):
            c = parts[1]
            if re.compile("[^a-zA-Z0-9-]").search(c):
                return
            thread.start_new_thread(self.reply_word, (message, True, c))
            return
        
        if parts[0].startswith(">>"):
            if self.site in self.banned:
                if event.user.id in self.banned[self.site]:
                    return
            cmd_args = content[2:]
            if (not cmd_args.startswith("translat")) and re.compile("[^a-zA-Z0-9 _-]").search(cmd_args):
                message.reply("Command contains invalid characters.")
            else:
                output = self.command(cmd_args, message, event)
                if output != False and output is not None:
                    if len(output) > 500:
                        message.reply("Output would be longer than 500 characters (the limit), so only the first 500 characters are posted now.")
                        self.room.send_message(output[:500])
                    else:
                        message.reply(output)
            
    def find_associated_word(self, word, message):
            self.add_word_to_latest_words(word)
            get_word = GetAssociatedWord(word, self.latest_words)
            word_to_reply = get_word[0]
            word_found = get_word[1]
            if word_to_reply is None:
                found_links = self.find_links(word)
                valid_found_links = []
                if len(found_links) > 0:
                    word_found = True
                for link in found_links:
                    if not link in self.latest_words:
                        valid_found_links.append(link)
                if len(valid_found_links) > 0:
                    word_to_reply = random.choice(valid_found_links)
            if word_to_reply is not None:
                self.add_word_to_latest_words(word_to_reply)
            return (word_to_reply, word_found)
            #thread.start_new_thread(self.reply_word, (word_to_reply, message, True, word, word_found))
            
    def add_word_to_latest_words(self, word):
        self.latest_words.insert(0, word)
        if len(self.latest_words) > 10:
            self.latest_words.pop()
    

    def command(self, cmd, msg, event):
        cmd_args = cmd.split(' ')
        cmd_name = cmd_args[0]
        args = cmd_args[1:]
        if cmd_name == "translationchain" or cmd_name == "translationswitch":
            to_translate = " ".join(args[3:])
            args = args[:3]
            args.append(to_translate)
        elif cmd_name == "translate":
            to_translate = " ".join(args[2:])
            args = args[:2]
            args.append(to_translate)
        commands_to_use = self.commands.copy()
        if self.in_shadows_den:
            commands_to_use.update(self.shadows_den_specific_commands)
        if cmd_name in commands_to_use:
            return commands_to_use[cmd_name](args, msg, event)

        elif cmd_name in self.owner_commands:
            if msg is None or event.user.id == self.owner_id:
                return self.owner_commands[cmd_name](args, msg, event)
            else:
                return "You don't have the privilege to execute this command."
        else:
            return "Command not found."
    
    def command_time(self, args, msg, event):
        if len(args) > 0:
            try:
                new_time = int(args[0])
                if new_time > -1:
                    self.waiting_time = new_time
                    f = open("config.txt", "w")
                    f.write(str(self.waiting_time))
                    f.close()
                    return "Waiting time set to %s %s." % (args[0], ("seconds" if new_time != 1 else "second"))
                else:
                    return "Given argument has to be a positive integer."
            except ValueError:
                return "Given argument is not a valid integer."
        else:
            return "Command does not have enough arguments."
                
    def command_stop(self, args, msg, event):
        self.enabled = False
        self.running = False
        if msg is not None:
            msg.reply("Bot terminated.")
        self.client.logout()
        return False
        
    def command_disable(self, args, msg, event):
        self.enabled = False
        return "Bot disabled, run >>enable to enable it again."
        
    def command_enable(self, args, msg, event):
        self.enabled = True
        return "Bot enabled."
    
    def command_award(self, args, msg, event):
        spell_id = -1
        user_id = -1
        add_to_queue = False
        if len(args) < 3:
            return "Not enough arguments."
        try:
            spell_id = int(args[0])
            user_id = int(args[1])
        except ValueError:
            return "Not a valid id."
        if args[2] == "-n":
            add_to_queue = False
        elif args[2] == "-q":
            add_to_queue = True
        else:
            return "Invalid arguments."
        return self.spell_manager.award(spell_id, user_id, add_to_queue)
        
    def command_viewspells(self, args, msg, event):
        if len(args) < 1:
            return "Not enough arguments."
        user_id = -1
        try:
            user_id = int(args[0])
        except ValueError:
            return "Invalid arguments."
        try:
            spells = self.spell_manager.view_spells(user_id)
            return spells
        except:
            return "An error occurred."
    
    def command_emptyqueue(self, args, msg, event):
        awarded = self.spell_manager.empty_queue()
        for s in awarded:
            if self.room is not None:
                self.room.send_message(s)
            else:
                print s
    
    def command_random(self, args, msg, event):
        return str(random.random())
    
    def command_randomint(self, args, msg, event):
        if len(args) == 0:
            return str(random.randint(0, sys.maxint))
        if len(args) == 1:
            max_ = -1
            try:
                max_ = int(args[0])
            except ValueError:
                return "Invalid arguments."
            min_ = -sys.maxint - 1
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
    
    def command_randomchoice(self, args, msg, event):
        if len(args) < 1:
            return "Not enough arguments."
        return random.choice(args)
    
    def command_shuffle(self, args, msg, event):
        if len(args) < 1:
            return "Not enough arguments."
        list_to_shuffle = list(args)
        random.shuffle(list_to_shuffle)
        return " ".join(list_to_shuffle)
    
    def command_ban(self, args, msg, event):
        banned_user = -1
        try:
            banned_user = int(args[0])
        except ValueError:
            return "Invalid arguments."
        if not self.site in self.banned:
            self.banned[self.site] = []
        if not banned_user in self.banned[self.site]:
            self.banned[self.site].append(banned_user)
        else:
            return "Already banned."
        with open("bannedUsers.txt", "w") as f:
            pickle.dump(self.banned, f)
        user_name = self.client.get_user(banned_user).name.replace(" ", "")
        return "User @%s has been banned from using the commands." % user_name
            
    def command_unban(self, args, msg, event):
        banned_user = -1
        try:
            banned_user = int(args[0])
        except ValueError:
            return "Invalid arguments."
        if not self.site in self.banned:
            return "Not banned."
        if not banned_user in self.banned[self.site]:
            return "Not banned."
        self.banned[self.site].remove(banned_user)
        with open("bannedUsers.txt", "w") as f:
            pickle.dump(self.banned, f)
        user_name = self.client.get_user(banned_user).name.replace(" ", "")
        return "User @%s has been unbanned." % user_name
    
    def command_listcommands(self, args, msg, event):
        command_keys = self.commands.keys()
        if self.in_shadows_den:
            command_keys += self.shadows_den_specific_commands.keys()
        return "Commands: %s" % (", ".join(command_keys),)
    
    def command_help(self, args, msg, event):
        return "I'm FOX 9000, ProgramFOX's chatbot. You can find the source code [on GitHub](https://github.com/ProgramFOX/SE-Chatbot). You can get a list of all commands by running >>listcommands"
                
    def command_link(self, args, msg, event):
        if len(args) != 2:
            return "2 arguments expected, %i given." % len(args)
        if self.links_contain((args[0].replace("_", " "), args[1].replace("_", " "))):
            return "Link is already added."
        self.links.append((args[0].replace("_", " "), args[1].replace("_", " ")))
        with open("linkedWords.txt", "w") as f:
            pickle.dump(self.links, f)
        return "Link added."
    
    def command_reply(self, args, msg, event):
        if len(args) < 1:
            return "Not enough arguments."
        msg_id_to_reply_to = -1
        try:
            msg_id_to_reply_to = int(args[0])
        except ValueError:
            if args[0] == "recent":
                msg_id_to_reply_to = self.msg_id_no_reply_found
            else:
                return "Invalid arguments."
            if msg_id_to_reply_to == -1:
                return "'recent' has a value of -1, which is not a valid message ID. Please provide an explicit ID."
        msg_to_reply_to = chatexchange.messages.Message(msg_id_to_reply_to, self.client)
        content = msg_to_reply_to.content_source
        content = re.sub(r"\[(.+?)\]\(.+?\)", r"\1", content)
        content = re.sub(r"\(.+?\)", "", content)
        content = re.sub(r"\s+", " ", content)
        content = content.strip()
        parts = content.split(" ")
        msg_does_not_qualify = "Message does not qualify as a message that belongs to the word association game."
        if len(parts) != 2:
            return msg_does_not_qualify
        if not re.compile("^:([0-9]+)$").search(parts[0]):
            return msg_does_not_qualify
        if re.compile("[^a-zA-Z0-9-]").search(parts[1]):
            return "Word contains invalid characters."
        self.reply_word(msg_to_reply_to, False, parts[1])
        return None

    def command_removelink(self, args, msg, event):
        if len(args) < 2:
            return "Not enough arguments."
        return self.remove_link(args[0], args[1])
    
    def links_contain(self, item):
        for link in self.links:
            lowercase_link = (link[0].lower(), link[1].lower())
            if item[0].lower() in lowercase_link and item[1].lower() in lowercase_link:
                return True
        return False
    
    def find_links(self, item):
        results = []
        for link in self.links:
            lowercase_link = (link[0].lower(), link[1].lower())
            lowercase_item = item.lower()
            if lowercase_item in lowercase_link:
                i = lowercase_link.index(lowercase_item)
                associated_index = 0 if i == 1 else 1
                results.append(link[associated_index])
        return results
    
    def remove_link(self, item0, item1):
        for i, link in enumerate(self.links):
            lowercase_link = (link[0].lower(), link[1].lower())
            if item0.lower() in lowercase_link and item1.lower() in lowercase_link:
                self.links.pop(i)
                with open("linkedWords.txt", "w") as f:
                    pickle.dump(self.links, f)
                return "Link removed."
        return "No link found."

    def command_translationchain(self, args, msg, event):
        if event.user.id != self.owner_id:
            return "The `translationchain` command is a command that posts many messages and it does not post all messages, and causes that some messages that have to be posted after the chain might not be posted, so it is an owner-only command now."
        translation_count = -1
        if len(args) < 4:
            return "Not enough arguments."
        try:
            translation_count = int(args[0])
        except ValueError:
            return "Invalid arguments."
        if translation_count < 1:
            return "Invalid arguments."
        if not self.translation_chain_going_on:
            if not args[1] in self.translation_languages or not args[2] in self.translation_languages:
                return "Language not in list. If the language is supported, ping ProgramFOX and he will add it."
            self.translation_chain_going_on = True
            thread.start_new_thread(self.translationchain, (args[3], args[1], args[2], translation_count))
            return "Translation chain started. Translation made by [Google Translate](https://translate.google.com). Some messages in the chain might not be posted due to a reason I don't know."
        else:
            return "There is already a translation chain going on."
        
    def command_translationswitch(self, args, msg, event):
        if event.user.id != self.owner_id:
            return "The `translationswitch` command is a command that posts many messages and it does not post all messages, and causes that some messages that have to be posted after the chain might not be posted, so it is an owner-only command now."
        if self.translation_switch_going_on:
            return "There is already a translation switch going on."
        translation_count = -1
        if len(args) < 4:
            return "Not enough arguments."
        try:
            translation_count = int(args[0])
        except ValueError:
            return "Invalid arguments."
        if translation_count < 2:
            return "Invalid arguments."
        if (translation_count % 2) == 1:
            return "Translation count has to be an even number."
        if not args[1] in self.translation_languages or not args[2] in self.translation_languages:
            return "Language not in list. If the language is supported, ping ProgramFOX and he will add it."
        self.translation_switch_going_on = True
        thread.start_new_thread(self.translationswitch, (args[3], args[1], args[2], translation_count))
        return "Translation switch started. Translation made by [Google Translate](https://translate.google.com). Some messages in the switch might not be posted due to a reason I don't know."
        
    def command_translate(self, args, msg, event):
        if len(args) < 3:
            return "Not enough arguments."
        if args[0] == args[1]:
            return "There's no point in having the same input language as output language."
        if not args[0] in self.translation_languages or not args[1] in self.translation_languages:
            return "Language not in list. If the language is supported, ping ProgramFOX and he will add it."
        return self.translate(args[2], args[0], args[1])

    def translationchain(self, text, start_lang, end_lang, translation_count):
        i = 0
        curr_lang = start_lang
        next_lang = None
        curr_text = text
        choices = list(self.translation_languages)
        if start_lang == end_lang:
            choices.remove(start_lang)
        else:
            choices.remove(start_lang)
            choices.remove(end_lang)
        while i < translation_count - 1:
            if next_lang is not None:
                curr_lang = next_lang
            while True:
                next_lang = random.choice(choices)
                if next_lang != curr_lang:
                    break
            result = self.translate(curr_text, curr_lang, next_lang)
            curr_text = result
            self.room.send_message("Translate %s-%s: %s" % (curr_lang, next_lang, result))
            i += 1
        final_result = self.translate(curr_text, next_lang, end_lang)
        self.room.send_message("Final translation result (%s-%s): %s" % (next_lang, end_lang, final_result))
        self.translation_chain_going_on = False
        
    def translationswitch(self, text, lang1, lang2, translation_count):
        i = 1
        curr_text = text
        while i <= translation_count:
            if (i % 2) == 0:
                lang_order = (lang2, lang1)
            else:
                lang_order = (lang1, lang2)
            curr_text = self.translate(curr_text, lang_order[0], lang_order[1])
            msg_text = "Translate %s-%s: %s" if i != translation_count else "Final result (%s-%s): %s"
            self.room.send_message(msg_text % (lang_order + (curr_text,)))
            i += 1
        self.translation_switch_going_on = False
    
    def translate(self, text, start_lang, end_lang):
        translate_url = "https://translate.google.com/translate_a/single?client=t&sl=%s&tl=%s&hl=en&dt=bd&dt=ex&dt=ld&dt=md&dt=qc&dt=rw&dt=rm&dt=ss&dt=t&dt=at&dt=sw&ie=UTF-8&oe=UTF-8&prev=btn&srcrom=1&ssel=0&tsel=0&q=%s" % (start_lang, end_lang, urllib.quote_plus(text.encode("utf-8")))
        r = requests.get(translate_url)
        unparsed_json = r.text.split("],[\"\",,", 1)[0].split("]]", 1)[0][3:]
        #print unparsed_json
        #parsed_json = json.loads(unparsed_json)
        #result_parts = []
        #for json_arr in parsed_json:
        #    result_parts.append(json_arr[0])
        #return " ".join(result_parts)
        return self.parse(unparsed_json)
    
    def parse(self, json):
        is_open = False
        is_backslash = False
        is_translation = True
        all_str = []
        curr_str = []
        for c in json:
            if c != '"' and not is_open:
                continue
            elif c == '"' and not is_open:
                is_open = True
            elif c == '\\':
                is_backslash = not is_backslash
                if is_translation:
                    curr_str.append(c)
            elif c == '"' and is_open and not is_backslash:
                is_open = False
                if is_translation:
                    s = "".join(curr_str).replace("\\\\", "\\").replace("\\\"", "\"")
                    all_str.append(s)
                curr_str = []
                is_backslash = False
                is_translation = not is_translation
            else:
                is_backslash = False
                if is_translation:
                    curr_str.append(c)
        return " ".join(all_str)
            

if __name__ == '__main__':
    bot = WordAssociationBot()
    bot.main()
