# algoritmos/grafo_bfs.py
from collections import deque

def bfs_caminho_mais_curto(grafo, inicio, fim):
    """
    Encontra o caminho mais curto entre dois nós em um grafo usando BFS.

    Args:
        grafo (dict): Representação do grafo como lista de adjacências.
                      Ex: {'A': ['B', 'C'], 'B': ['A', 'D'], ...}
        inicio (str): Nó inicial.
        fim (str): Nó final.

    Returns:
        list: Uma lista de nós representando o caminho mais curto, ou None se não houver caminho.
    """
    if inicio == fim:
        return [inicio]
    if inicio not in grafo or fim not in grafo:
        return None

    fila = deque([(inicio, [inicio])])  # Armazena (nó_atual, caminho_ate_aqui)
    visitados = {inicio}

    while fila:
        no_atual, caminho_atual = fila.popleft()

        for vizinho in grafo.get(no_atual, []):
            if vizinho == fim:
                return caminho_atual + [vizinho]
            if vizinho not in visitados:
                visitados.add(vizinho)
                fila.append((vizinho, caminho_atual + [vizinho]))
    
    return None # Caminho não encontrado