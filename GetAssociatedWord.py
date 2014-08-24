from bs4 import BeautifulSoup
import requests

def GetAssociatedWord(w):
    r = requests.get("http://wordassociations.net/search?q=%s" % w)
    soup = BeautifulSoup(r.text)
    # found = soup.select("div.section:nth-child(1) > ul:nth-child(2) > li:nth-child(1) > a:nth-child(1)")
    _list = soup.find_all("ul")
    # print found
    if _list is None or len(_list) < 3:
        return "No associated word found."
    else:
        #return list.contents[0].contents[0]
        return _list[2].contents[0].contents[0].contents[0].lower()
        # return str(len(list))
        