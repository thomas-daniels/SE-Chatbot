#!/usr/bin/env python

import chatexchange.client
import chatexchange.events
import getpass
import re
from GetAssociatedWord import GetAssociatedWord
from SecretSpells import *
from HTMLParser import HTMLParser
import thread
import time
import random
import math
from bs4 import BeautifulSoup
import requests
import urllib

class WordAssociationBot:

    room = None
    client = None
    commands = {}
    owner_commands = {}
    owner_id = 229438 # change this into your ID
    owner_name = "ProgramFOX" # change this into your name
    enabled = True
    running = True
    waiting_time = -1
    current_word_to_reply = ""
    translation_languages = [ "en", "fr", "nl", "de", "he", "ru", "el", "pt", "es", "fi" ]
    current_translation_languages_order = None
    translation_count = -1
    curr_translation = -1
    end_lang = None
    translation_chain_going_on = False
    spellManager = SecretSpells()
    def main(self):
        self.commands = { 
            'time': self.command_time,
            'viewspells': self.command_viewspells,
            'translationchain': self.command_translationchain
        }
        self.owner_commands = {
            'stop': self.command_stop,
            'disable': self.command_disable,
            'enable': self.command_enable,
            'award': self.command_award,
            'emptyqueue': self.command_emptyqueue      
        }
        self.spellManager.init()
        site = raw_input("Site: ")
        room_number = int(raw_input("Room number: "))
        email = raw_input("Email address: ")
        password = getpass.getpass("Password: ")
        
        f = open("config.txt", "r")
        self.waiting_time = int(f.read());
        f.close()

        self.client = chatexchange.client.Client(site)
        self.client.login(email, password)
        
        self.spellManager.c = self.client
    
        self.room = self.client.get_room(room_number)
        self.room.join()
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
                    
    def scheduled_empty_queue(self):
        while self.running:
            time.sleep(15 * 60)
            awarded = self.spellManager.empty_queue()
            for s in awarded:
                if self.room is not None:
                    self.room.send_message(s)
                else:
                    print s
            
    def reply_word(self, word, message, wait, orig_word):
        if wait and self.waiting_time > 0:
            time.sleep(self.waiting_time)
        if word == self.current_word_to_reply:
            if word is not None:
                message.reply(word);
            else:
                self.room.send_message("No associated word found for %s" % orig_word)

    def on_event(self, event, client):
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
        content = h.unescape(message.content)
        content = re.sub("\(.+?\)", "", content)
        content = re.sub("\s+", " ", content)
        content = content.strip()
        parts = content.split(" ")
        if (not parts[0].startswith(">>")) and (len(parts) != 2 or not parts[0].startswith("@")) and (event.user.id != -2):
            return
        
        if parts[0].startswith(">>"):
            cmd_args = content[2:]
            if (not cmd_args.startswith("translat")) and re.compile("[^a-zA-Z0-9 -]").search(cmd_args):
                #self.room.send_message(":%s Command contains invalid characters" % message._message_id)
                message.reply("Command contains invalid characters")
            else:
                output = self.command(cmd_args, message, event)
                if output != False and output is not None:
                    if len(output) > 500:
                        message.reply("Output would be longer than 500 characters (the limit), so only the first 500 characters are posted now.")
                        self.room.send_message(output[:500])
                    else:
                        message.reply(output)
        elif parts[0].startswith("@"):
            c = parts[1]
            if re.compile("[^a-zA-Z0-9-]").search(c):
                return
            #self.room.send_message(":%s %s" % (message._message_id, GetAssociatedWord(c)))
            word_to_reply = GetAssociatedWord(c)
            self.current_word_to_reply = word_to_reply
            thread.start_new_thread(self.reply_word, (word_to_reply, message, True, c))
        """elif event.user.id == -2 and self.current_translation_languages_order is not None:
            if self.curr_lang >= self.translation_count:
                self.room.send_message("translate %s: %s" % (self.end_lang, message.content))
                self.end_lang = None
                self.curr_lang = -1
                self.current_translation_languages_order = None
                self.translation_count = -1
            else:
                self.room.send_message("translate %s: %s" % (self.current_translation_languages_order[self.curr_lang], message.content))
                self.curr_lang += 1"""
    

    def command(self, cmd, msg, event):
        cmd_args = cmd.split(' ')
        cmd_name = cmd_args[0]
        args = cmd_args[1:]
        if cmd_name == "translationchain":
            to_translate = " ".join(args[3:])
            args = args[:3]
            args.append(to_translate)
        if cmd_name in self.commands:
            return self.commands[cmd_name](args, msg, event)

        elif cmd_name in self.owner_commands:
            if msg is None or event.user.id == self.owner_id:
                return self.owner_commands[cmd_name](args, msg, event)
            else:
                return "You don't have the privilege to execute this command"
        else:
            return "Command not found"
    
    def command_time(self, args, msg, event):
        if len(args) > 0:
            #self.room.send_message(":%s Time command executed: %s" % (msg_id, args[0]))
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
            # self.room.send_message("%s Command does not have enough arguments" % msg_id)
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
        return self.spellManager.award(spell_id, user_id, add_to_queue)
        
    def command_viewspells(self, args, msg, event):
        if len(args) < 1:
            return "Not enough arguments."
        user_id = -1
        try:
            user_id = int(args[0])
        except ValueError:
            return "Invalid arguments."
        return self.spellManager.view_spells(user_id)
    
    def command_emptyqueue(self, args, msg, event):
        awarded = self.spellManager.empty_queue()
        for s in awarded:
            if self.room is not None:
                self.room.send_message(s)
            else:
                print s

    def command_translationchain(self, args, msg, event):
        translation_count = -1
        if len(args) < 4:
            return "Not enough arguments."
        try:
            translation_count = int(args[0])
        except ValueError:
            return "Invalid arguments."
        if translation_count < 1:
            return "Invalid arguments."
        #if self.current_translation_languages_order is None:
        if not self.translation_chain_going_on:
            #self.current_translation_languages_order = list(self.translation_languages)
            if not args[1] in self.translation_languages or not args[2] in self.translation_languages:
                return "Language not in list. If the language is supported, ping ProgramFOX and he will add it."
            #mul = int(math.ceil(self.translation_count / float(len(self.translation_languages))))
            #self.current_translation_languages_order = self.current_translation_languages_order * mul
            #random.shuffle(self.current_translation_languages_order)
            #self.current_translation_languages_order = self.current_translation_languages_order[:self.translation_count]
            #self.avoid_consecutive_duplicates()
            #self.room.send_message("translate %s: %s" % (self.current_translation_languages_order[0], args[0]))
            #self.curr_lang = 1
            #self.end_lang = args[1]
            self.translation_chain_going_on = True
            thread.start_new_thread(self.translationchain, (args[3], args[1], args[2], translation_count))
            return "Translation chain started. Translation made by [Google Translate](https://translate.google.com)"
        else:
            return "There is already a translation chain going on."
        
    def translationchain(self, text, start_lang, end_lang, translation_count):
        i = 0
        curr_lang = start_lang
        next_lang = None
        curr_text = text
        choices = list(self.translation_languages)
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
    
    def translate(self, text, start_lang, end_lang):
        translate_url = "https://translate.google.com/translate_a/single?client=t&sl=%s&tl=%s&hl=en&dt=bd&dt=ex&dt=ld&dt=md&dt=qc&dt=rw&dt=rm&dt=ss&dt=t&dt=at&dt=sw&ie=UTF-8&oe=UTF-8&prev=btn&srcrom=1&ssel=0&tsel=0&q=%s" % (start_lang, end_lang, urllib.quote_plus(text.encode("utf-8")))
        #r = requests.get("https://translate.google.com/#%s/%s/%s" % (start_lang, end_lang, text))
        #r = requests.post("https://translate.google.com/translate_t", post_data)
        r = requests.get(translate_url)
        #soup = BeautifulSoup(r.text)
        #result = soup.find("span", { "id": "result_box" }).text
        result = r.text.split(",", 1)[0][4:][:-1]
        #result = re.match('\[\[\["(.+)",', content).group(1)
        return result
        
    '''def avoid_consecutive_duplicates(self):
        max_ = len(self.current_translation_languages_order) - 1
        i = 0
        while self.has_consecutive_duplicates(self.current_translation_languages_order):
            while i < len(self.current_translation_languages_order):
                if i != max_:
                    next_ = i + 1
                    next_next = -1
                    if i == max_ - 1:
                        next_next = 0
                    else:
                        next_next = i + 2
                    a = self.current_translation_languages_order[i]
                    b = self.current_translation_languages_order[next_]
                    c = self.current_translation_languages_order[next_next]
                    if a == b:
                        self.current_translation_languages_order[next_] = c
                        self.current_translation_languages_order[next_next] = b
                i += 1
            
    def has_consecutive_duplicates(self, l):
        i = 0
        max_ = len(l) - 1
        while i < len(l):
            if i != max_:
                if l[i] == l[i + 1]:
                    return True
            i += 1
        return False'''
        

if __name__ == '__main__':
    bot = WordAssociationBot()
    bot.main()