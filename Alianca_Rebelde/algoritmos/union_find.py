class UnionFind:
    def __init__(self, nos=None):
  
        self.parent = {}
        self.rank = {} # Para otimização de união por rank
        if nos:
            for no in nos:
                self.add_no(no)

    def add_no(self, no):
        if no not in self.parent:
            self.parent[no] = no
            self.rank[no] = 0

    def find(self, no):
        if no not in self.parent: # Adiciona o nó se ele for encontrado pela primeira vez (ex: em uma aresta)
            self.add_no(no)

        if self.parent[no] == no:
            return no
        # Compressão de caminho
        self.parent[no] = self.find(self.parent[no])
        return self.parent[no]

    def union(self, no1, no2):
        if no1 not in self.parent: self.add_no(no1)
        if no2 not in self.parent: self.add_no(no2)

        raiz1 = self.find(no1)
        raiz2 = self.find(no2)

        if raiz1 != raiz2:
            if self.rank[raiz1] < self.rank[raiz2]:
                self.parent[raiz1] = raiz2
            elif self.rank[raiz1] > self.rank[raiz2]:
                self.parent[raiz2] = raiz1
            else:
                self.parent[raiz2] = raiz1
                self.rank[raiz1] += 1
            return True # União bem-sucedida
        return False 

    def conectados(self, no1, no2):
        if no1 not in self.parent or no2 not in self.parent:
            return False 
        return self.find(no1) == self.find(no2)

    def reset(self, nos=None):
        self.parent.clear()
        self.rank.clear()
        if nos:
            for no in nos:
                self.add_no(no)
