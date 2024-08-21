# import required modules
from bs4 import BeautifulSoup
import requests

class Wiki():
    """
    Initializes a Wikipedia page given a link
    """
    def __init__(self, link):
        # get URL
        self.page = requests.get(link)

        # scrape webpage
        self.soup = BeautifulSoup(self.page.content, 'html.parser')
    
    """
    Prints the title of the Wikipedia article
    """
    def getTitle(self):
        # find tags
        items = self.soup.find_all(class_="firstHeading")
        result = items[0]

        # display tags
        output = result.prettify()
        split = output.splitlines()
        title = split[2].strip()
        print(title)
    
    """
    Gets all hyperlinks from the Wikipedia article
    Only gets other Wikipedia links and ignores footnotes and references
    """
    def getHyperLinks(self):
        object = self.soup.find(id="mw-content-text")
        items = object.find_all('a')
        for item in items:
            output = item.prettify()
            split = output.splitlines()
            text = split[1].strip()

            chars = set('0123456789[@_!#$%^&*<>?/\|}{~:]')
            if not any((c in chars) for c in text):
                link = item.get('href')
                if '/wiki' in link and 'https' not in link:
                    print(link)

whaleShark = Wiki("https://en.wikipedia.org/wiki/Whale_shark")
whaleShark.getTitle()
whaleShark.getHyperLinks()