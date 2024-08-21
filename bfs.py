from collections import defaultdict

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
    Backtraces to find and return path
    """
    def backtrace(self, parent, start, end):
        path = [end]
        while path[-1] != start:
            path.append(parent[path[-1]])
        path.reverse()
        return path
    
    """
    Searches for end node using breadth-first search
    Maintains map from parents to children to backtrace once end is found to return full path
    """
    def bfs(self, start, end):
        parent = {}
        queue = []
        queue.append(start)

        while queue:
            node = queue.pop(0)
            if node == end:
                return self.backtrace(parent, start, end)
            for adjacent in self.graph.get(node, []):
                if node not in queue :
                    parent[adjacent] = node # <<<<< record its parent 
                    queue.append(adjacent)
        
        return False