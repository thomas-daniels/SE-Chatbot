import thread
import requests
import random
import urllib
from Module import Command

translation_languages = ["auto", "en", "fr", "nl", "de", "he", "ru", "el", "pt", "es", "fi", "af", "sq", "ar", "hy", "az", "eu", "be", "bn", "bs", "bg", "ca", "ceb", "zh-CN", "hr", "cs", "da",
                         "eo", "et", "tl", "gl", "ka", "gu", "ht", "ha", "hi", "hmn", "hu", "is", "ig", "id", "ga", "it", "ja", "jw", "kn", "km", "ko", "lo", "la", "lv", "lt", "mk", "ms"
                         "mt", "mi", "mr", "mn", "ne", "no", "fa", "pl", "pa", "ro", "sr", "sk", "sl", "so", "sw", "sv", "ta", "te", "th", "tr", "uk", "ur", "vi", "cy", "yi", "yo", "zu"]
end_lang = None
translation_chain_going_on = False
translation_switch_going_on = False


def command_translationchain(cmd, bot, args, msg, event):
    global translation_languages
    global translation_chain_going_on
    if event.user.id not in bot.owner_ids:
        return "The `translationchain` command is a command that posts many messages and it does not post all messages, and causes that some messages that have to be posted after the chain might not be posted, so it is an owner-only command now."
    if len(args) < 4:
        return "Not enough arguments."
    try:
        translation_count = int(args[0])
    except ValueError:
        return "Invalid arguments."
    if translation_count < 1:
        return "Invalid arguments."
    if not translation_chain_going_on:
        if not args[1] in translation_languages or not args[2] in translation_languages:
            return "Language not in list. If the language is supported, ping ProgramFOX and he will add it."
        translation_chain_going_on = True
        thread.start_new_thread(translationchain, (bot, args[3], args[1], args[2], translation_count))
        return "Translation chain started. Translation made by [Google Translate](https://translate.google.com). Some messages in the chain might not be posted due to a reason I don't know."
    else:
        return "There is already a translation chain going on."


def command_translationswitch(cmd, bot, args, msg, event):
    global translation_switch_going_on
    global translation_languages
    if event.user.id not in bot.owner_ids:
        return "The `translationswitch` command is a command that posts many messages and it does not post all messages, and causes that some messages that have to be posted after the chain might not be posted, so it is an owner-only command now."
    if translation_switch_going_on:
        return "There is already a translation switch going on."
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
    if not args[1] in translation_languages or not args[2] in translation_languages:
        return "Language not in list. If the language is supported, ping ProgramFOX and he will add it."
    translation_switch_going_on = True
    thread.start_new_thread(translationswitch, (bot, args[3], args[1], args[2], translation_count))
    return "Translation switch started. Translation made by [Google Translate](https://translate.google.com). Some messages in the switch might not be posted due to a reason I don't know."


def command_translate(cmd, bot, args, msg, event):
    global translation_languages
    if len(args) < 3:
        return "Not enough arguments."
    if args[0] == args[1]:
        return "There's no point in having the same input language as output language."
    if not args[0] in translation_languages or not args[1] in translation_languages:
        return "Language not in list. If the language is supported, ping ProgramFOX and he will add it."
    return translate(args[2], args[0], args[1])


def translationchain(bot, text, start_lang, end_lang, translation_count):
    global translation_languages
    global translation_chain_going_on
    i = 0
    curr_lang = start_lang
    next_lang = None
    curr_text = text
    choices = list(translation_languages)
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
        result = translate(curr_text, curr_lang, next_lang)
        curr_text = result
        bot.room.send_message("Translate %s-%s: %s" % (curr_lang, next_lang, result))
        i += 1
    final_result = translate(curr_text, next_lang, end_lang)
    bot.room.send_message("Final translation result (%s-%s): %s" % (next_lang, end_lang, final_result))
    translation_chain_going_on = False


def translationswitch(bot, text, lang1, lang2, translation_count):
    global translation_switch_going_on
    i = 1
    curr_text = text
    while i <= translation_count:
        if (i % 2) == 0:
            lang_order = (lang2, lang1)
        else:
            lang_order = (lang1, lang2)
        curr_text = translate(curr_text, lang_order[0], lang_order[1])
        msg_text = "Translate %s-%s: %s" if i != translation_count else "Final result (%s-%s): %s"
        bot.room.send_message(msg_text % (lang_order + (curr_text,)))
        i += 1
    translation_switch_going_on = False


def translate(text, start_lang, end_lang):
    translate_url = "https://translate.google.com/translate_a/single?client=t&sl=%s&tl=%s&hl=en&dt=bd&dt=ex&dt=ld&dt=md&dt=qc&dt=rw&dt=rm&dt=ss&dt=t&dt=at&dt=sw&ie=UTF-8&oe=UTF-8&prev=btn&srcrom=1&ssel=0&tsel=0&q=%s" % (start_lang, end_lang, urllib.quote_plus(text.encode("utf-8")))
    r = requests.get(translate_url)
    unparsed_json = r.text.split("],[\"\",,", 1)[0].split("]]", 1)[0][3:]
    return parse(unparsed_json)


def parse(json):
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


def trans_arg_parsing(full_cmd):
    cmd_args = full_cmd.split(' ')
    args = cmd_args[1:]
    to_translate = " ".join(args[2:])
    args = args[:2]
    args.append(to_translate)
    return args


def transcs_arg_parsing(full_cmd):
    cmd_args = full_cmd.split(' ')
    args = cmd_args[1:]
    to_translate = " ".join(args[3:])
    args = args[:3]
    args.append(to_translate)
    return args


commands = [
    Command('translate', command_translate, "Translates text using [Google Translate](https://translate.google.com). Syntax: `>>translate input_lang output_lang Text to translate.`. `input_lang` and `output_lang` are language codes such as `en`, `fr` and `auto`.", False, False, False, trans_arg_parsing),
    Command('translationchain', command_translationchain, "Owner-only command. Creates a chain of translations using [Google Translate](https://translate.google.com). Syntax: `>>translationchain steps_number input_lang output_lang Text to translate.`", False, True, False, transcs_arg_parsing),
    Command('translationswitch', command_translationswitch, "Owner-only command. Creates a chain of translations using [Google Translate](https://translate.google.com), consisting of two languages. Syntax: `>>translationswitch steps_number lang1 lang2 Text to translate.`", False, True, False, transcs_arg_parsing)
]
