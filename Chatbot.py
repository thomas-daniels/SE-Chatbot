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

class WordAssociationBot:

    room = None
    client = None
    commands = {}
    owner_commands = {}
    owner_id = 88521 # change this into your ID
    owner_name = "ProgramFOX" # change this into your name
    enabled = True
    running = True
    waiting_time = -1
    current_word_to_reply = ""
    spellManager = SecretSpells()
    def main(self):
        self.commands = { 
            'time': self.command_time,
            'viewspells': self.command_viewspells
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
            
    def reply_word(self, word, message, wait):
        if wait and self.waiting_time > 0:
            time.sleep(self.waiting_time)
        if word == self.current_word_to_reply:
            message.reply(word);

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
        parts = content.split(" ")
        if (not parts[0].startswith(">>")) and (len(parts) != 2 or not parts[0].startswith("@")):
            return
        
        if parts[0].startswith(">>"):
            cmd_args = content[2:]
            if re.compile("[^a-zA-Z0-9 -]").search(cmd_args):
                #self.room.send_message(":%s Command contains invalid characters" % message._message_id)
                message.reply("Command contains invalid characters")
            else:
                output = self.command(cmd_args, message, event)
                if output != False and output is not None:
                    message.reply(output)
        elif parts[0].startswith("@"):
            c = parts[1]
            if re.compile("[^a-zA-Z0-9-]").search(c):
                return
            #self.room.send_message(":%s %s" % (message._message_id, GetAssociatedWord(c)))
            word_to_reply = GetAssociatedWord(c)
            self.current_word_to_reply = word_to_reply
            thread.start_new_thread(self.reply_word, (word_to_reply, message, True))
    

    def command(self, cmd, msg, event):
        cmd_args = cmd.split(' ')
        cmd_name = cmd_args[0]
        args = cmd_args[1:]
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

if __name__ == '__main__':
    bot = WordAssociationBot()
    bot.main()