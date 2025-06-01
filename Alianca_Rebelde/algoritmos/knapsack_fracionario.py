def calcular_solucao_otima_knapsack_fracionario(itens_disponiveis, capacidade_maxima):

    itens_com_razao = []
    for item_original in itens_disponiveis: 
        # Trabalha com uma cópia para evitar modificar a lista original se ela for usada em outro lugar
        item = item_original.copy() 
        
        if item['peso_total'] > 0:
            razao = item['importancia'] / item['peso_total'] 
        else:
            razao = float('inf') if item['importancia'] > 0 else 0 
        
        item['razao'] = razao
        itens_com_razao.append(item)

    itens_ordenados = sorted(itens_com_razao, key=lambda x: x['razao'], reverse=True)

    mochila_otima = []
    peso_atual_mochila = 0
    importancia_atual_mochila = 0 # Mudado de valor_atual_mochila

    for item_processado in itens_ordenados:
        if peso_atual_mochila >= capacidade_maxima:
            break 

        peso_disponivel_do_item = item_processado['peso_total']
        # importancia_total_do_item_disponivel = item_processado['importancia']

        if peso_atual_mochila + peso_disponivel_do_item <= capacidade_maxima:
            peso_a_pegar = peso_disponivel_do_item
            importancia_ganha = item_processado['importancia'] 
            
            mochila_otima.append({
                'nome': item_processado['nome'],
                'peso_pego': peso_a_pegar,
                'importancia_pega': importancia_ganha, # Nome da chave consistente
                'fracao_pega': 1.0
            })
            peso_atual_mochila += peso_a_pegar
            importancia_atual_mochila += importancia_ganha
        else:
            peso_restante_na_mochila = capacidade_maxima - peso_atual_mochila
            if peso_restante_na_mochila > 0 and item_processado['peso_total'] > 0:
                fracao_a_pegar = peso_restante_na_mochila / item_processado['peso_total']
                peso_a_pegar = peso_restante_na_mochila
                importancia_ganha = fracao_a_pegar * item_processado['importancia'] 
                
                mochila_otima.append({
                    'nome': item_processado['nome'],
                    'peso_pego': peso_a_pegar,
                    'importancia_pega': importancia_ganha, 
                    'fracao_pega': fracao_a_pegar
                })
                peso_atual_mochila += peso_a_pegar
                importancia_atual_mochila += importancia_ganha
            break 

    return mochila_otima, importancia_atual_mochila, peso_atual_mochila