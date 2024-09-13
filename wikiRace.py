import aiohttp
import asyncio
import requests
import sys
import time
from bs4 import BeautifulSoup
# from bfs import Graph
from aStar import Graph
from concurrent.futures import ThreadPoolExecutor, as_completed

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
        # self.graph = Graph(self.title(end))

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
                    # self.graph.addEdge(self.getTitle(self.session, self.current), self.getTitle(self.session, fullLink))
                    self.links.append(fullLink)
                    self.visited.add(fullLink)

        self.count += 1

        if self.links:
            self.current = self.links.pop(0)
            if self.count % 5 == 0:
                print("Checking for matches...")
                # self.bfs()
                self.aStar()
            
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
    
    # def parseCategories(self, soup):
    #     cats = set()
    #     object = soup.find(id="mw-normal-catlinks")
    #     items = object.find_all('li')
    #     if items:
    #         for li in items:
    #             cats.add(li.text.strip())
    #     return cats
            
    """
    Calls BFS algorithm and prints out the path
    """
    def bfs(self):
        ret = self.graph.bfs(self.start, self.end)
        if ret != False:
            path = [self.title(link) for link in ret]
            print(path)

            endTime = time.time()  # End timing after completing the search
            elapsedTime = endTime - self.startTime
            print(f"Time alloted: {elapsedTime:.2f} seconds")
            sys.exit()
    
    """
    Calls A* search algorithm and prints out the path
    """
    def aStar(self):
        ret = self.graph.search(self.start, self.end)
        # ret = future.result() if future else None
        if ret != False and ret != None:
            path = [self.title(link) for link in ret]
            print(path)

            endTime = time.time()  # End timing after completing the search
            elapsedTime = endTime - self.startTime
            print(f"Time alloted: {elapsedTime:.2f} seconds")

            # Visualize the search graph after the path is found
            pathEdges = [(ret[i], ret[i + 1]) for i in range(len(ret) - 1)]
            self.graph.visualizeGraph(pathEdges)

            sys.exit()

    """
    Runs the program using asynchronous threading
    """
    async def run(self):
        async with aiohttp.ClientSession() as session:
            self.session = session
            self.target = await self.getTitle(session, self.end)

            self.startTime = time.time()  # Start timing before beginning the search

            await self.getHyperLinks()

"""
Checks if a Wikipedia link is valid by checking the HTTP status code
"""
def linkValid(link):
    response = requests.get(link)
    return response.status_code == 200

"""
Converts a Wikipedia page title to a Wikipedia link
"""
def titleToLink(title):
    formattedTitle = title.strip().lower().capitalize().replace(" ", "_")
    return f"https://en.wikipedia.org/wiki/{formattedTitle}"

"""
Receives user input for start and end articles
"""
def userInput():
    start = input("Enter start wiki page title: ")
    startLink = titleToLink(start)
    if(not linkValid(startLink)):
        print(startLink, " is invalid\n")
        userInput()
        sys.exit

    end = input("Enter end wiki page title: ")
    endLink = titleToLink(end)
    if(not linkValid(endLink)):
        print(endLink, " is invalid\n")
        userInput()
        sys.exit

    print("\nStart: ", startLink, "\nEnd: ", endLink, "\n")
    time.sleep(1)
    
    path = Wiki(titleToLink(start), titleToLink(end))
    asyncio.run(path.run())

# userInput()

start = "https://en.wikipedia.org/wiki/Whale_shark"
end = "https://en.wikipedia.org/wiki/Cosmopolitan_distribution"

whaleShark = Wiki(start, end)
asyncio.run(whaleShark.run())