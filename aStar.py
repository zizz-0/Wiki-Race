import heapq
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor

class Graph:

    def __init__(self, target):
        self.graph = defaultdict(list)
        self.target = target

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
        while path[-1] != start:
            path.append(parent[path[-1]])
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

            return False

        if use_threading:
            with ThreadPoolExecutor(max_workers=10) as executor:
                future = executor.submit(aStar)
                return future
        else:
            # Run directly without threading for comparison
            return aStar()