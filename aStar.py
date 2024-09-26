import heapq
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
import matplotlib.pyplot as plt
import networkx as nx
import urllib.parse
import time

class Graph:

    def __init__(self, target):
        self.graph = defaultdict(list)
        self.target = target
        self.exploredEdges = []  # Store explored edges
        self.edge_cost = {}  # To store the cost for each explored edge

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
                        self.edge_cost[(self.getWikiTitle(node), self.getWikiTitle(adjacent))] = fScore[adjacent] * 1.5 # Store edge cost

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
    def visualizeGraph(self, pathEdges, threshold=5, maxEdges=300):
        G = nx.DiGraph()

        # To store start and end nodes to make red
        start_end_nodes = set()

        for start, end in pathEdges:
            start_node = self.getWikiTitle(start)
            end_node = self.getWikiTitle(end)
            G.add_node(start_node)  # Add start node
            G.add_node(end_node)    # Add end node
            start_end_nodes.add(start_node)
            start_end_nodes.add(end_node)

        edgeCount = 0
        for edge in self.exploredEdges:
            edge_cost = self.edge_cost.get(edge, float('inf'))
            if maxEdges is not None and edgeCount >= maxEdges:
                break
            if threshold is None or edge_cost < threshold:
                G.add_edge(edge[0], edge[1])
                edgeCount += 1
                
        
        # Layout for visual appearance
        plt.figure(figsize=(10, 8))
        pos = nx.spring_layout(G)

        node_colors = []
        for node in G.nodes:
            if node in start_end_nodes:
                # Final path
                node_colors.append('red')
            else:
                node_colors.append('lightblue')

        # Draws graph without labels
        nx.draw(G, pos, with_labels=False, node_size=150, node_color=node_colors, edge_color='lightgray') # Uncomment for all edges
        # nx.draw(G, pos, with_labels=True, node_size=300, node_color='lightblue', font_size=10, font_weight='bold', edge_color='gray') # Comment out for all edges

        # Draws final path edges in red
        path_edges_to_draw = [(self.getWikiTitle(start), self.getWikiTitle(end)) for start, end in pathEdges] 
        nx.draw_networkx_edges(G, pos, edgelist=path_edges_to_draw, edge_color='red', width=1.5)

        # Adds node labels
        labels = {node: node for node in G.nodes}
        for node, label in labels.items():
            font_color = 'black' if node in start_end_nodes else 'dimgray'
            font_weight = 'bold' if node in start_end_nodes else 'normal'
            nx.draw_networkx_labels(G, pos, labels={node: label}, font_color=font_color, font_weight=font_weight, font_size=5)

        plt.show()