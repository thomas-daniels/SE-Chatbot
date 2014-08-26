from bs4 import BeautifulSoup
import requests

def GetAssociatedWord(w):
    r = requests.get("http://wordassociations.net/search?q=%s" % w)
    soup = BeautifulSoup(r.text)
    _list = soup.find_all("ul")
    if _list is None or len(_list) < 3:
        return None
    else:
        return _list[2].contents[0].contents[0].contents[0].lower()
        