from bs4 import BeautifulSoup
import requests
import random
import re


def GetAssociatedWord(w, latest_words):
    r = requests.get("http://wordassociations.net/search?q=%s" % w)
    soup = BeautifulSoup(r.text)
    found_words = []
    sections = soup.find_all("div", class_ = re.compile("(NOUN|ADJECTIVE|VERB|ADVERB)-SECTION"))
    for section in sections:
        list_items = section.find_all("li")
        for li in list_items:
            found_words.append(li.getText().lower())
    if len(found_words) < 1:
        return (None, False)
    else:
        i = 0
        already_tried = []
        x = 0
        while x < len(found_words):
            i = random.randint(0, len(found_words) - 1)
            if i in already_tried:
                x -= 1
                continue
            already_tried.append(i)
            associated_word = found_words[i]
            if not associated_word in latest_words:
                return (associated_word, True)
            x += 1
        return (None, True)
        