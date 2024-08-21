from bs4 import BeautifulSoup
from bfs import Graph
import requests

class Wiki():
    """
    Gets the start and end pages and creates a BFS graph to search for the end page
    """
    def __init__(self, start, end):
        # Start wiki page
        self.startPage = requests.get(start)
        self.startSoup = BeautifulSoup(self.startPage.content, 'html.parser')

        self.start = self.getTitle(start)
        self.target = self.getTitle(end)

        self.current = start
        self.end = end

        self.graph = Graph(self.end)
    
    """
    Returns the title of a Wikipedia article
    """
    def getTitle(self, link):
        page = requests.get(link)
        soup = BeautifulSoup(page.content, 'html.parser')

        items = soup.find_all(class_="firstHeading")
        result = items[0]

        output = result.prettify()
        split = output.splitlines()
        title = split[2].strip()
        return title
    
    """
    Gets all hyperlinks from the Wikipedia article
    Only gets other Wikipedia links and ignores footnotes and references
    """
    def getHyperLinks(self):
        object = self.startSoup.find(id="mw-content-text")
        items = object.find_all('a')
        for item in items:
            output = item.prettify()
            split = output.splitlines()
            text = split[1].strip()

            chars = set('0123456789[@_!#$%^&*<>?/\|}{~:]')
            if not any((c in chars) for c in text):
                link = item.get('href')
                if '/wiki' in link and 'https' not in link:
                    fullLink = 'https://en.wikipedia.org' + link
                    self.graph.addEdge(self.current, fullLink)
        
    def search(self):
        ret = self.graph.bfs(self.current, self.end)
        path = []
        for link in ret:
            title = self.getTitle(link)
            path.append(title)
        
        print(path)

start = "https://en.wikipedia.org/wiki/Whale_shark"
end = "https://en.wikipedia.org/wiki/Baleen_whale"

whaleShark = Wiki(start, end)
whaleShark.getHyperLinks()
whaleShark.search()