def calcular_paradas_reabastecimento(capacidade_combustivel, breakpoints):
    """
    Calcula as paradas de reabastecimento usando o algoritmo ambicioso.

    Args:
        capacidade_combustivel: A capacidade máxima de combustível da nave.
        breakpoints: Uma lista ordenada das distâncias das estações de reabastecimento
                     a partir do ponto inicial, incluindo 0 e a distância total.

    Returns:
        Uma lista dos índices das estações de reabastecimento onde a parada é necessária,
        ou None se não for possível alcançar o destino.
    """
    paradas = []
    combustivel_atual = capacidade_combustivel
    localizacao_atual = 0

    n = len(breakpoints) - 1 # Índice do destino

    while localizacao_atual < breakpoints[n]:
        # Encontra a estação de reabastecimento mais distante que pode ser alcançada
        proxima_parada_potencial_indice = -1
        for i in range(1, n + 1):
            if breakpoints[i] <= localizacao_atual + combustivel_atual:
                proxima_parada_potencial_indice = i
            else:
                break

        # Se nenhuma estação de reabastecimento pode ser alcançada
        if proxima_parada_potencial_indice == -1:
            return None # Não é possível alcançar o destino

        # Se a próxima parada potencial é o destino, chegamos
        if breakpoints[proxima_parada_potencial_indice] == breakpoints[n]:
            localizacao_atual = breakpoints[n]
            break

        # Se a próxima parada potencial não é o destino, precisamos reabastecer lá
        paradas.append(proxima_parada_potencial_indice)
        combustivel_atual -= (breakpoints[proxima_parada_potencial_indice] - localizacao_atual)
        localizacao_atual = breakpoints[proxima_parada_potencial_indice]
        combustivel_atual = capacidade_combustivel # Reabastece completamente

        # Segurança contra loops infinitos (se a configuração for impossível)
        if len(paradas) > 2 * len(breakpoints):
            return None

    return paradas

# Exemplo de uso:
capacidade = 10
pontos = [0, 2, 5, 8, 12, 15] # 0 é o início, 15 é o fim
paradas_necessarias = calcular_paradas_reabastecimento(capacidade, pontos)

if paradas_necessarias is not None:
    print("Paradas de reabastecimento nos pontos:", [pontos[i] for i in paradas_necessarias])
else:
    print("Não é possível completar a rota com a capacidade de combustível dada.")