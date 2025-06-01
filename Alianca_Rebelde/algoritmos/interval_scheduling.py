def calcular_interval_scheduling_otimo(atividades_propostas):
    
    if not atividades_propostas:
        return []

    # Ordena as atividades pelo tempo de término (crescente)
    atividades_ordenadas = sorted(atividades_propostas, key=lambda x: x['fim'])

    plano_de_operacoes_otimo = []
    
    if atividades_ordenadas:
        # Seleciona a primeira atividade (a que termina mais cedo)
        ultima_operacao_no_plano = atividades_ordenadas[0]
        plano_de_operacoes_otimo.append(ultima_operacao_no_plano)

        # Itera sobre as atividades restantes
        for i in range(1, len(atividades_ordenadas)):
            operacao_atual = atividades_ordenadas[i]
            if operacao_atual['inicio'] >= ultima_operacao_no_plano['fim']:
                plano_de_operacoes_otimo.append(operacao_atual)
                ultima_operacao_no_plano = operacao_atual
                
    return plano_de_operacoes_otimo