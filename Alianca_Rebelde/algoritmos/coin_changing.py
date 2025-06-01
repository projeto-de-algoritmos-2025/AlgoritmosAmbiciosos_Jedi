# algoritmos/coin_changing_guloso.py

def calcular_troco(denominacoes_disponiveis, valor_a_pagar):
    
    if valor_a_pagar < 0:
        return None, -1 # Não pode pagar valor negativo

    # Ordena as denominações da maior para a menor
    denominacoes_ordenadas = sorted(denominacoes_disponiveis, reverse=True)
    
    cedulas_usadas = {}
    numero_total_de_cedulas = 0
    valor_restante = valor_a_pagar

    for den_valor in denominacoes_ordenadas:
        if den_valor <= 0: # Ignora denominações inválidas
            continue
        
        if valor_restante >= den_valor:
            quantidade_desta_cedula = valor_restante // den_valor
            cedulas_usadas[den_valor] = quantidade_desta_cedula
            valor_restante -= quantidade_desta_cedula * den_valor
            numero_total_de_cedulas += quantidade_desta_cedula
            
        if valor_restante == 0:
            break # Valor exato alcançado

    if valor_restante == 0:
        return cedulas_usadas, numero_total_de_cedulas
    else:
        # O algoritmo não conseguiu formar o valor exato com as denominações
        return None, -1