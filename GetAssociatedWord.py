from bs4 import BeautifulSoup
import requests
import random

def GetAssociatedWord(w, latest_words):
    r = requests.get("http://wordassociations.net/search?q=%s" % w)
    soup = BeautifulSoup(r.text)
    _list = soup.find_all("ul")
    if _list is None or len(_list) < 3:
        return (None, False)
    else:
        i = 0
        word_list_contents = _list[2].contents
        already_tried = []
        x = 0
        while x < len(word_list_contents):
            i = random.randint(0, len(word_list_contents) - 1)
            if i in already_tried:
                x -= 1
                continue
            already_tried.append(i)
            associated_word = _list[2].contents[i].contents[0].contents[0].lower()
            if not associated_word in latest_words:
                return (associated_word, True)
            x += 1
        return (None, True)
        