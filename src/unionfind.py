class UnionFind:
    def __init__(self):
        self.parent = {}
        self.rank = {}
    
    def find(self, x):
        if x not in self.parent.keys(): 
            self.parent[x] = x
            self.rank[x] = 0
        a = self.parent[x]
        if a != x:
            root = self.find(a)
            self.parent[x] = root
            return root
        return x
    
    def union(self, x, y):
        px = self.find(x)
        py = self.find(y)
        if self.rank[px] > self.rank[py]:
            self.parent[py] = px
        elif self.rank[px] < self.rank[py]:
            self.parent[px] = py
        else:
            self.parent[px] = py
            self.rank[py] += 1