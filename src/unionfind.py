class UnionFind:
    def __init__(self):
        self.parent = {}
    
    def find(self, x):
        if x not in self.parent.keys(): 
            self.parent[x] = x
        a = self.parent[x]
        if a != x:
            root = self.find(a)
            self.parent[x] = root
            return root
        return x
    
    def union(self, x, y):
        px = self.find(x)
        py = self.find(y)
        self.parent[px] = py