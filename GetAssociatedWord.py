from bs4 import BeautifulSoup
import requests

def GetAssociatedWord(w, latest_words):
    r = requests.get("http://wordassociations.net/search?q=%s" % w)
    soup = BeautifulSoup(r.text)
    _list = soup.find_all("ul")
    if _list is None or len(_list) < 3:
        return None
    else:
        i = 0
        while True:
            associated_word = _list[2].contents[i].contents[0].contents[0].lower()
            if not associated_word in latest_words:
                return associated_word
            i += 1
        