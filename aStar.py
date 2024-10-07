import heapq
import matplotlib.pyplot as plt
import networkx as nx
import urllib.parse
import requests
from bs4 import BeautifulSoup
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor

class Graph:

    def __init__(self, target):
        self.graph = defaultdict(list)
        self.target = target
        self.exploredEdges = []  # Store explored edges
        self.edgeCost = {}  # To store the cost for each explored edge

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
        # return abs(len(node) - len(end))
        str1 = node.replace('https://en.wikipedia.org', '')
        str2 = end.replace('https://en.wikipedia.org', '')
        h = self.longestCommonSubstr(str1, str2)
    
        # Return -h since A* minimizes cost
        return -h
    
    def longestCommonSubstr(self, str1, str2):
        m, n = len(str1), len(str2)
        table = [[0] * (n + 1) for _ in range(m + 1)]
        longest = 0
        
        for i in range(1, m + 1):
            for j in range(1, n + 1):
                if str1[i - 1] == str2[j - 1]:
                    table[i][j] = table[i - 1][j - 1] + 1
                    longest = max(longest, table[i][j])
        
        return longest
    
    """
    Backtraces to find and return path
    """
    def backtrace(self, parent, start, end):
        path = [end]
        # self.exploredEdges = []  # Clear explored edges -- comment out to show all edges
        while path[-1] != start:
            currentNode = path[-1]
            if currentNode in parent:
                parentNode = parent[currentNode]
                # self.exploredEdges.append((self.getWikiTitle(parentNode), self.getWikiTitle(currentNode)))  # Store the edge -- comment out to show all edges
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
    def search(self, start, end, use_threading=True):
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
                        self.edgeCost[(self.getWikiTitle(node), self.getWikiTitle(adjacent))] = fScore[adjacent] * 1.5 # Store edge cost

            return False

        if use_threading:
            with ThreadPoolExecutor(max_workers=20) as executor:
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
    def visualizeGraph(self, pathEdges, path, allotedTime, threshold=5, maxEdges=300):
        G = nx.DiGraph()

        # To store start and end nodes to make red
        startEndNodes =[]

        # Getting count of nodes
        nodeCount = 0
        for edge in self.exploredEdges:
            nodeCount += 1

        for start, end in pathEdges:
            startNode = self.getWikiTitle(start)
            endNode = self.getWikiTitle(end)
            G.add_node(startNode)  # Add start node
            G.add_node(endNode)    # Add end node
            startEndNodes.append(startNode)
            startEndNodes.append(endNode)

        # Adds nodes to graph -- only nodes below a threshold number and up to a max count
        edgeCount = 0
        for edge in self.exploredEdges:
            edgeCost = self.edgeCost.get(edge, float('inf'))
            if maxEdges is not None and edgeCount >= maxEdges:
                break
            if threshold is None or edgeCost < threshold:
                G.add_edge(edge[0], edge[1])
                edgeCount += 1
                
        
        # Layout for visual appearance
        plt.figure(figsize=(10, 8))
        pos = nx.spring_layout(G)

        nodeColors = []
        for node in G.nodes:
            if node in startEndNodes:
                # Final path
                nodeColors.append('red')
            else:
                nodeColors.append('lightblue')

        # Draws graph without labels
        nx.draw(G, pos, with_labels=False, node_size=150, node_color=nodeColors, edge_color='lightgray') # Uncomment for all edges

        # Draws final path edges in red
        pathEdgesToDraw = [(self.getWikiTitle(start), self.getWikiTitle(end)) for start, end in pathEdges] 
        nx.draw_networkx_edges(G, pos, edgelist=pathEdgesToDraw, edge_color='red', width=1.5)

        # Adds node labels
        labels = {node: node for node in G.nodes}
        for node, label in labels.items():
            fontColor = 'black' if node in startEndNodes else 'dimgray'
            fontWeight = 'bold' if node in startEndNodes else 'normal'
            nx.draw_networkx_labels(G, pos, labels={node: label}, font_color=fontColor, font_weight=fontWeight, font_size=5)

        plt.suptitle(f"Wiki Race: {path}\n{nodeCount} articles explored, {maxEdges} articles displayed | Search Time: {allotedTime:.2f} seconds", fontsize='small')
        plt.show()