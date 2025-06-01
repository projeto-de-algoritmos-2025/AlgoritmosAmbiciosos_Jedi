def calcular_schedule_edf_e_lmax(tarefas_base):
    
    if not tarefas_base:
        return 0, []

    # Ordena as tarefas pelo prazo final (dj) - Earliest Deadline First
    tarefas_ordenadas_edf = sorted(tarefas_base, key=lambda x: x['dj'])

    tempo_corrente = 0
    lmax_final = 0
    cronograma_detalhado = []

    for tarefa in tarefas_ordenadas_edf:
        inicio_tarefa = tempo_corrente
        fim_tarefa = inicio_tarefa + tarefa['tj']
        atraso = max(0, fim_tarefa - tarefa['dj'])

        lmax_final = max(lmax_final, atraso)

        cronograma_detalhado.append({
            'nome': tarefa.get('nome', tarefa.get('id', 'Tarefa Desconhecida')), # Usa nome ou id
            'id': tarefa.get('id', tarefa.get('nome', 'ID Desconhecido')),
            'tj': tarefa['tj'],
            'dj': tarefa['dj'],
            'sj': inicio_tarefa,
            'fj': fim_tarefa,
            'atraso_j': atraso
        })

        tempo_corrente = fim_tarefa # Próxima tarefa começa quando esta termina

    return lmax_final, cronograma_detalhado
    