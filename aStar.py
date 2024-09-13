import heapq
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
import matplotlib.pyplot as plt
import networkx as nx
import urllib.parse

class Graph:

    def __init__(self, target):
        self.graph = defaultdict(list)
        self.target = target
        self.exploredEdges = []  # Store explored edges

    """
    Adds edge to a graph
    """
    def addEdge(self, current, next):
        self.graph[current].append(next)

    """
    Heuristic function to estimate the distance from the current node to the target
    """
    def heuristic(self, node, end):
        # Placeholder heuristic: title lengths
        return abs(len(node) - len(end))

    """
    Backtraces to find and return path
    """
    def backtrace(self, parent, start, end):
        path = [end]
        # self.exploredEdges = []  # Clear explored edges
        while path[-1] != start:
            currentNode = path[-1]
            if currentNode in parent:
                parentNode = parent[currentNode]
                # self.exploredEdges.append((self.getWikiTitle(parentNode), self.getWikiTitle(currentNode)))  # Store the edge
                path.append(parentNode)
            else:
                print(f"Error: Parent of node {currentNode} not found. Aborting path reconstruction.")
                return False  # Return False if the path cannot be completed
        path.reverse()
        return path
    
    """
    A* search algorithm implementation
    Uses threading to speed up search
    """
    def search(self, start, end, use_threading=False):
        def aStar():
            parent = {}
            gScore = {start: 0}
            fScore = {start: self.heuristic(start, end)}
            openSet = []
            heapq.heappush(openSet, (fScore[start], start))

            while openSet:
                _, node = heapq.heappop(openSet)

                if node == end:
                    return self.backtrace(parent, start, end)

                for adjacent in self.graph.get(node, []):
                    tentativeGScore = gScore[node] + 1  # Assume each edge has a weight of 1

                    if adjacent not in gScore or tentativeGScore < gScore[adjacent]:
                        parent[adjacent] = node
                        gScore[adjacent] = tentativeGScore
                        fScore[adjacent] = tentativeGScore + self.heuristic(adjacent, end)
                        heapq.heappush(openSet, (fScore[adjacent], adjacent))

                        self.exploredEdges.append((self.getWikiTitle(node), self.getWikiTitle(adjacent)))

            return False

        if use_threading:
            with ThreadPoolExecutor(max_workers=10) as executor:
                future = executor.submit(aStar)
                return future
        else:
            # Run without threading
            return aStar()
        
    def getWikiTitle(self, link):
        # Remove the first part of the URL and decode any URL-encoded characters
        if "/wiki/" in link:
            title_part = link.split("/wiki/")[1]  # Extract everything after /wiki/
            title = urllib.parse.unquote(title_part)  # Decode URL encoding
            title = title.replace("_", " ")  # Replace underscores with spaces
            return title
        return None  # If the link doesn't have /wiki/, return None

    """
    Visualizes the search graph using NetworkX
    """
    def visualizeGraph(self, pathEdges):
        G = nx.DiGraph()  # Create a directed graph

        for edge in self.exploredEdges:
            G.add_edge(edge[0], edge[1])
        
        plt.figure(figsize=(10, 8))
        pos = nx.spring_layout(G, k=5, scale=300, center=[0,0], iterations=5)  # Layout for visual appearance

        nx.draw(G, pos, with_labels=True, node_size=150, node_color='lightblue', font_size=5, font_weight='bold', edge_color='gray')

        path_edges_to_draw = [(self.getWikiTitle(start), self.getWikiTitle(end)) for start, end in pathEdges]
        nx.draw_networkx_edges(G, pos, edgelist=path_edges_to_draw, edge_color='red', width=2.5)

        plt.show()