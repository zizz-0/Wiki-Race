from bs4 import BeautifulSoup
from bfs import Graph
import requests
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed

class Wiki():
    """
    Gets the start and end pages and creates a BFS graph to search for the end page
    """
    def __init__(self, start, end):
        # Start wiki page
        self.page = requests.get(start)
        self.soup = BeautifulSoup(self.page.content, 'html.parser')

        self.start = start
        self.target = self.getTitle(end)

        self.current = start
        self.end = end

        self.graph = Graph(self.end)

        self.count = 0
        self.links = []
        self.visited = set()  # Track visited pages
    
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
        print("Currently searching " + self.getTitle(self.current))
        self.visited.add(self.current)

        object = self.soup.find(id="mw-content-text")
        items = object.find_all('a')
        for item in items:
            output = item.prettify()
            split = output.splitlines()
            text = split[1].strip()

            chars = set('0123456789[@_!#$%^&*<>?/\|}{~:]')
            if not any((c in chars) for c in text):
                link = item.get('href')
                if link and'/wiki' in link and 'https' not in link:
                    fullLink = 'https://en.wikipedia.org' + link
                    if fullLink not in self.visited:
                        self.graph.addEdge(self.current, fullLink)
                        self.links.append(fullLink)

        # if self.links:
        self.count += 1

        if self.links[0] not in self.visited:
            self.current = self.links[0]

        self.links.pop(0)

        self.page = requests.get(self.current)
        self.soup = BeautifulSoup(self.page.content, 'html.parser')

        if self.count % 2 == 0:
            self.search()
            print("Checking for matches...")
        
        self.getHyperLinks()
            
    """
    Calls BFS algorithm and prints out the path
    """
    def search(self):
        ret = self.graph.bfs(self.start, self.end)
        if ret != False:
            path = [self.getTitle(link) for link in ret]
            print(path)
            sys.exit()

start = "https://en.wikipedia.org/wiki/Whale_shark"
end = "https://en.wikipedia.org/wiki/Cetacea"

whaleShark = Wiki(start, end)
whaleShark.getHyperLinks()