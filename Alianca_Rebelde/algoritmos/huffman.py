from collections import Counter
import heapq 

class NoHuffman:
    def __init__(self, char, freq):
        self.char = char
        self.freq = freq
        self.esquerda = None
        self.direita = None

    def __lt__(self, other):
        return self.freq < other.freq

def construir_arvore_huffman(texto):
    contador = Counter(texto)
    heap = [NoHuffman(char, freq) for char, freq in contador.items()]
    heapq.heapify(heap)

    while len(heap) > 1:
        no1 = heapq.heappop(heap)
        no2 = heapq.heappop(heap)
        novo = NoHuffman(None, no1.freq + no2.freq)
        novo.esquerda = no1
        novo.direita = no2
        heapq.heappush(heap, novo)

    return heap[0] if heap else None

def gerar_codigos_huffman(raiz, prefixo="", codigos=None):
    if codigos is None:
        codigos = {}
    if raiz:
        if raiz.char is not None:
            codigos[raiz.char] = prefixo
        gerar_codigos_huffman(raiz.esquerda, prefixo + "0", codigos)
        gerar_codigos_huffman(raiz.direita, prefixo + "1", codigos)
    return codigos

