from bs4 import BeautifulSoup
# from bfs import Graph
from aStar import Graph
from concurrent.futures import ThreadPoolExecutor, as_completed
import aiohttp
import asyncio
import requests
import sys

class Wiki():
    """
    Gets the start and end pages and creates a BFS graph to search for the end page
    """
    def __init__(self, start, end):
        self.page = requests.get(start)
        self.soup = BeautifulSoup(self.page.content, 'html.parser')

        self.start = start
        self.target = None

        self.current = start
        self.end = end

        self.graph = Graph(self.end)

        self.count = 0
        self.links = []
        self.visited = set()  # Track visited pages
    
    """
    Makes a GET request to specified URL using a specific session to handle multiple HTTP requests at once
    """
    async def fetch(self, session, url):
        async with session.get(url) as response:
            return await response.text()
    
    """
    Returns the title of a Wikipedia article -- THREADED
    """
    async def getTitle(self, session, link):
        content = await self.fetch(session, link)
        soup = BeautifulSoup(content, 'html.parser')
        items = soup.find_all(class_="firstHeading")
        
        result = items[0]
        return result.text.strip()
    
    """
    Returns the title of a Wikipedia article -- UNTHREADED
    """
    def title(self, link):
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
    async def getHyperLinks(self):
        print("Currently searching " + await self.getTitle(self.session, self.current))
        self.visited.add(self.current)

        content = await self.fetch(self.session, self.current)
        soup = BeautifulSoup(content, 'html.parser')
        object = soup.find(id="mw-content-text")
        items = object.find_all('a')

        with ThreadPoolExecutor(max_workers=20) as executor:
            futures = [executor.submit(self.processLink, item) for item in items]

            for future in as_completed(futures):
                fullLink = future.result()
                if fullLink and fullLink not in self.visited:
                    self.graph.addEdge(self.current, fullLink)
                    self.links.append(fullLink)

        self.count += 1

        if self.links:
            self.current = self.links.pop(0)
            if self.count % 2 == 0:
                # self.bfs()
                self.aStar()
                print("Checking for matches...")
            
            await self.getHyperLinks()

    """
    Processes a hyperlink to get the full link
    Only returns link if it's not a reference link (outside articles, serial numbers)
    """
    def processLink(self, item):
        output = item.prettify()
        split = output.splitlines()
        text = split[1].strip()

        chars = set('0123456789[@_!#$%^&*<>?/\|}{~:]')
        if not any((c in chars) for c in text):
            link = item.get('href')
            if link and '/wiki' in link and 'https' not in link:
                fullLink = 'https://en.wikipedia.org' + link
                return fullLink
        return None
            
    """
    Calls BFS algorithm and prints out the path
    """
    def bfs(self):
        ret = self.graph.bfs(self.start, self.end)
        if ret != False:
            path = [self.title(link) for link in ret]
            print(path)
            sys.exit()
    
    def aStar(self):
        ret = self.graph.aStar(self.start, self.end)
        if ret != False:
            path = [self.title(link) for link in ret]
            print(path)
            sys.exit()

    """
    Runs the program using asynchronous threading
    """
    async def run(self):
        async with aiohttp.ClientSession() as session:
            self.session = session
            self.target = await self.getTitle(session, self.end)
            await self.getHyperLinks()

start = "https://en.wikipedia.org/wiki/Whale_shark"
end = "https://en.wikipedia.org/wiki/Flying_fish"

whaleShark = Wiki(start, end)
asyncio.run(whaleShark.run())