import heapq

def calcular_interval_partitioning_otimo(intervalos_propostos):
    
    if not intervalos_propostos:
        return 0, {}

    # Adiciona o índice original para rastreamento ou para usar como ID único 
    
    # Ordena os intervalos pelo tempo de início
    intervalos_ordenados = sorted(intervalos_propostos, key=lambda x: x['inicio'])

    atribuicoes = {}  
    
    # Min-heap para armazenar tuplas: (tempo_de_fim_do_recurso, id_do_recurso_disponivel)
    recursos_em_uso_heap = [] 
    
    numero_de_recursos_alocados = 0 # Contador para dar IDs aos novos recursos

    for intervalo_atual in intervalos_ordenados:
        nome_intervalo = intervalo_atual['nome']
        inicio_intervalo = intervalo_atual['inicio']
        fim_intervalo = intervalo_atual['fim']

        if recursos_em_uso_heap and recursos_em_uso_heap[0][0] <= inicio_intervalo:
            # Existe um recurso que já terminou sua tarefa anterior antes ou no momento
            _fim_recurso_anterior, id_recurso_reutilizado = heapq.heappop(recursos_em_uso_heap)
            
            atribuicoes[nome_intervalo] = id_recurso_reutilizado
            # Adiciona este recurso de volta ao heap com seu novo tempo de término
            heapq.heappush(recursos_em_uso_heap, (fim_intervalo, id_recurso_reutilizado))
        else:
            # Nenhum recurso existente está livre. Precisa alocar um novo.
            numero_de_recursos_alocados += 1
            id_novo_recurso = numero_de_recursos_alocados # Esquadrão 1, Esquadrão 2, etc.
            
            atribuicoes[nome_intervalo] = id_novo_recurso
            # Adiciona este novo recurso ao heap
            heapq.heappush(recursos_em_uso_heap, (fim_intervalo, id_novo_recurso))
            
    # O número mínimo de recursos é o total de recursos que precisamos alocar
    return numero_de_recursos_alocados, atribuicoes
