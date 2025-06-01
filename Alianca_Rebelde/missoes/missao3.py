import tkinter as tk
from tkinter import ttk, messagebox, font as tkFont
from algoritmos.interval_scheduling import calcular_interval_scheduling_otimo

class Missao3:
    def __init__(self, root, game_manager, content_frame_para_missao):
        self.root = root
        self.game_manager = game_manager
        self.base_content_frame = content_frame_para_missao

        # Fontes
        self.narrative_font = self.game_manager.narrative_font
        self.button_font = self.game_manager.button_font
        self.item_font = tkFont.Font(family="Arial", size=10)
        self.header_font = self.game_manager.header_font
        self.status_label_font = self.game_manager.small_bold_font
        
        self.operacoes_base = [
            {'nome': "Intrusão Servidor Central (Coruscant)", 'inicio': 0, 'fim': 3, 'id': 'OpX1', 'prioridade': 90},
            {'nome': "Extração VIP (Nal Hutta)", 'inicio': 2, 'fim': 5, 'id': 'OpX2', 'prioridade': 70},
            {'nome': "Sabotagem Fábrica de Droides (Geonosis)", 'inicio': 1, 'fim': 4, 'id': 'OpX3', 'prioridade': 80},
            {'nome': "Escolta Comboio Suprimentos (Kashyyyk)", 'inicio': 4, 'fim': 8, 'id': 'OpX4', 'prioridade': 60},
            {'nome': "Reconhecimento Rota Secreta (Bespin)", 'inicio': 6, 'fim': 9, 'id': 'OpX5', 'prioridade': 75},
            {'nome': "Desativar Canhão Planetário (Hoth)", 'inicio': 7, 'fim': 10, 'id': 'OpX6', 'prioridade': 95},
            {'nome': "Interceptar Mensageiro Imperial (Ord Mantell)", 'inicio': 9, 'fim': 12, 'id': 'OpX7', 'prioridade': 50},
            {'nome': "Estabelecer Ponto de Observação (Tatooine)", 'inicio': 5, 'fim': 7, 'id': 'OpX8', 'prioridade': 40}
        ]
        
        self.lista_para_selecao = [] 
        self.plano_do_jogador = []
        self.ultimo_horario_fim_plano = -1
        self.dica_count_m3 = 0
        self.erros_escolha_gulosa = 0
        self.primeira_falha_nesta_tentativa_m3 = True 
        self.ordenacao_escolhida_pelo_jogador = None

        self.operacoes_disponiveis_listbox = None
        self.plano_jogador_listbox = None
        self.btn_adicionar_op = None
        self.btn_finalizar_plano = None
        self.btn_dica_m3 = None
        self.status_label_m3 = None

    def _clear_mission_frame(self):
        if self.base_content_frame and self.base_content_frame.winfo_exists():
            for widget in self.base_content_frame.winfo_children():
                widget.destroy()

    def limpar_interface_missao_completa(self):
        self._clear_mission_frame()

    def iniciar_missao_contexto(self):
        self._clear_mission_frame()
        
        ttk.Label(self.base_content_frame, text="MISSÃO 3: Sincronia Secreta no Setor Arkanis", font=self.header_font).pack(pady=10)
        context_text = (
            "Comandante, a situação é crítica. O Império está prestes a consolidar seu controle sobre o Corredor de Arkanis, uma rota de hiperespaço vital para nossas operações de suprimento e fuga no Anel Externo. Se não agirmos AGORA, perderemos o setor por completo, isolando inúmeras células rebeldes.\n\n"
            "Nossos espiões Bothans arriscaram tudo para identificar várias vulnerabilidades Imperiais simultâneas – mas são janelas de oportunidade extremamente fugazes. Precisamos de um plano impecável para atingir o máximo de alvos sem sobrecarregar nossas poucas equipes de assalto disponíveis.\n\n"
            "Sua tarefa: analisar as operações propostas e selecionar o MAIOR NÚMERO POSSÍVEL de operações que NÃO SE SOBREPONHAM no tempo."
        )
        text_widget = tk.Text(self.base_content_frame, wrap=tk.WORD, height=10, relief=tk.FLAT, 
                              background=self.root.cget('bg'), font=self.narrative_font, padx=10, pady=10)
        text_widget.insert(tk.END, context_text)
        text_widget.config(state=tk.DISABLED)
        text_widget.pack(pady=15, padx=10, fill=tk.X)
        ttk.Button(self.base_content_frame, text="Iniciar Planejamento Tático...",
                   command=self.iniciar_etapa_ordenacao, style="Accent.TButton").pack(pady=20)

    def iniciar_etapa_ordenacao(self):
        self._clear_mission_frame()
        self.plano_do_jogador = []
        self.ultimo_horario_fim_plano = -1
        self.dica_count_m3 = 0 
        self.erros_escolha_gulosa = 0
        self.primeira_falha_nesta_tentativa_m3 = True 
        self.lista_para_selecao = list(self.operacoes_base) 
        self.ordenacao_escolhida_pelo_jogador = None 

        ttk.Label(self.base_content_frame, text="Etapa 1: Estratégia de Ordenação", font=self.game_manager.button_font).pack(pady=10)
        
        instrucoes_texto = (
            "Comandante, a ordem em que consideramos as operações é fundamental para uma estratégia gulosa eficaz.\n"
            "Qual critério de ordenação você acredita ser o mais promissor para esta tarefa de escalonamento?"
        )
        ttk.Label(self.base_content_frame, text=instrucoes_texto, wraplength=700, justify=tk.CENTER, font=self.narrative_font).pack(pady=10)

        botoes_frame = ttk.Frame(self.base_content_frame)
        botoes_frame.pack(pady=10)

        opcoes_ordenacao = [
            ("Ordenar por Início (mais cedo primeiro)", lambda x: x['inicio'], "Início Mais Cedo"),
            ("Ordenar por Fim (mais cedo primeiro)", lambda x: x['fim'], "Fim Mais Cedo"), 
            ("Ordenar por Duração (mais curta primeiro)", lambda x: x['fim'] - x['inicio'], "Duração Mais Curta"),
            ("Ordenar por Prioridade (maior primeiro)", lambda x: -x['prioridade'], "Maior Prioridade")
        ]

        for texto_btn, sort_key_func, nome_curto_estratgia in opcoes_ordenacao:
            btn = ttk.Button(botoes_frame, text=texto_btn, width=45,
                             command=lambda skf=sort_key_func, nome_est=nome_curto_estratgia: self.processar_escolha_ordenacao(skf, nome_est))
            btn.pack(pady=5)

    def processar_escolha_ordenacao(self, sort_key_func_escolhida, nome_estrategia_escolhida):
        self.ordenacao_escolhida_pelo_jogador = sort_key_func_escolhida
        self.lista_para_selecao = sorted(self.operacoes_base, key=self.ordenacao_escolhida_pelo_jogador)
        
        mensagem_feedback = f"Entendido, Comandante. As operações foram ordenadas usando o critério: \"{nome_estrategia_escolhida}\".\n\n"
        
        estrategia_correta_nome_curto = "Fim Mais Cedo"
        if nome_estrategia_escolhida == estrategia_correta_nome_curto:
            mensagem_feedback += "Esta é a estratégia de ordenação que garante o resultado ótimo para o algoritmo ganancioso padrão de Interval Scheduling. Excelente escolha!"
            messagebox.showinfo("Estratégia Selecionada", mensagem_feedback)
        else:
            mensagem_feedback += ("Esta é uma abordagem válida para explorar, mas lembre-se que diferentes estratégias de ordenação podem levar a diferentes níveis de eficiência. "
                                  "A estratégia gulosa ótima clássica para este problema utiliza outro critério. Fique atento às dicas se precisar.")
            messagebox.showwarning("Estratégia Selecionada", mensagem_feedback)
            
        self.iniciar_etapa_selecao_iterativa()

    def iniciar_etapa_selecao_iterativa(self):
        self._clear_mission_frame()
        
        ttk.Label(self.base_content_frame, text="Etapa 2: Seleção Gulosa Iterativa", font=self.button_font).pack(pady=(10,5))
        self.status_label_m3 = ttk.Label(self.base_content_frame, text="Analise a lista de operações (ordenada conforme sua escolha) e selecione a primeira para seu plano.", font=self.narrative_font, wraplength=700, justify=tk.CENTER)
        self.status_label_m3.pack(pady=5)

        main_interaction_frame = ttk.Frame(self.base_content_frame)
        main_interaction_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        disponiveis_frame = ttk.LabelFrame(main_interaction_frame, text="Operações Disponíveis (Considerar em Ordem)", padding=10)
        disponiveis_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0,5))
        
        self.operacoes_disponiveis_listbox = tk.Listbox(disponiveis_frame, selectmode=tk.SINGLE, exportselection=False, height=12, font=self.item_font)
        self.operacoes_disponiveis_listbox.pack(fill=tk.BOTH, expand=True, pady=(0,5))
        self.operacoes_disponiveis_listbox.bind('<<ListboxSelect>>', self._on_op_disponivel_select)
        self._popular_lista_selecao() 

        self.btn_adicionar_op = ttk.Button(disponiveis_frame, text="Adicionar Selecionada ao Plano >>", command=self.adicionar_operacao_ao_plano_interativo, state=tk.DISABLED)
        self.btn_adicionar_op.pack(pady=5)

        plano_frame = ttk.LabelFrame(main_interaction_frame, text="Seu Plano de Operações Atual", padding=10)
        plano_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5,0))
        self.plano_jogador_listbox = tk.Listbox(plano_frame, height=12, font=self.item_font)
        self.plano_jogador_listbox.pack(fill=tk.BOTH, expand=True, pady=(0,5))

        action_frame_bottom = ttk.Frame(self.base_content_frame)
        action_frame_bottom.pack(fill=tk.X, pady=10, padx=10)
        
        self.btn_dica_m3 = ttk.Button(action_frame_bottom, text="Pedir Dica (Seleção)", command=self.mostrar_dica_selecao_is)
        self.btn_dica_m3.pack(side=tk.LEFT)
        
        self.btn_finalizar_plano = ttk.Button(action_frame_bottom, text="Finalizar Plano (Não há mais compatíveis)", command=self.avaliar_plano_final_jogador, style="Accent.TButton", state=tk.DISABLED)
        self.btn_finalizar_plano.pack(side=tk.RIGHT)

    def _on_op_disponivel_select(self, event):
        if not self.operacoes_disponiveis_listbox or not self.operacoes_disponiveis_listbox.curselection():
            if self.btn_adicionar_op and self.btn_adicionar_op.winfo_exists(): self.btn_adicionar_op.config(state=tk.DISABLED)
            return
        
        try:
            idx_na_listbox = self.operacoes_disponiveis_listbox.curselection()[0]
            if idx_na_listbox < len(self.lista_para_selecao):
                op_selecionada_preview = self.lista_para_selecao[idx_na_listbox]
                if op_selecionada_preview in self.plano_do_jogador or op_selecionada_preview['inicio'] < self.ultimo_horario_fim_plano:
                    if self.btn_adicionar_op and self.btn_adicionar_op.winfo_exists(): self.btn_adicionar_op.config(state=tk.DISABLED)
                else:
                    if self.btn_adicionar_op and self.btn_adicionar_op.winfo_exists(): self.btn_adicionar_op.config(state=tk.NORMAL)
            else:
                if self.btn_adicionar_op and self.btn_adicionar_op.winfo_exists(): self.btn_adicionar_op.config(state=tk.DISABLED)
        except tk.TclError: # Caso a listbox seja destruída enquanto o evento é processado
             if self.btn_adicionar_op and self.btn_adicionar_op.winfo_exists(): self.btn_adicionar_op.config(state=tk.DISABLED)


    def _popular_lista_selecao(self):
        if not self.operacoes_disponiveis_listbox or not self.operacoes_disponiveis_listbox.winfo_exists(): return
        self.operacoes_disponiveis_listbox.delete(0, tk.END)
        
        for op_data in self.lista_para_selecao: 
            status = ""
            cor_fg = "black" 
            if op_data in self.plano_do_jogador:
                status = " [NO PLANO]"
                cor_fg = "slate gray"
            elif op_data['inicio'] < self.ultimo_horario_fim_plano:
                status = " [CONFLITA]"
                cor_fg = "indian red"
            
            self.operacoes_disponiveis_listbox.insert(tk.END, f"{op_data['nome']} (I:{op_data['inicio']}-F:{op_data['fim']}){status}")
            idx = self.operacoes_disponiveis_listbox.size() - 1
            if status: 
                self.operacoes_disponiveis_listbox.itemconfig(idx, {'foreground': cor_fg})

    def adicionar_operacao_ao_plano_interativo(self):
        if not self.operacoes_disponiveis_listbox or not self.operacoes_disponiveis_listbox.curselection():
            messagebox.showwarning("Nenhuma Operação", "Selecione uma operação da lista para adicionar ao plano.")
            return
        
        idx_real_na_lista_ordenada = self.operacoes_disponiveis_listbox.curselection()[0]
        op_selecionada_pelo_jogador = self.lista_para_selecao[idx_real_na_lista_ordenada]

        if op_selecionada_pelo_jogador in self.plano_do_jogador:
            messagebox.showwarning("Já no Plano", "Esta operação já foi adicionada ao seu plano.")
            self._on_op_disponivel_select(None)
            return

        if op_selecionada_pelo_jogador['inicio'] < self.ultimo_horario_fim_plano:
            messagebox.showerror("Conflito de Horário!", 
                                 f"A operação '{op_selecionada_pelo_jogador['nome']}' (início: {op_selecionada_pelo_jogador['inicio']}) "
                                 f"conflita com a última operação do seu plano (que termina em: {self.ultimo_horario_fim_plano}).")
            self.erros_escolha_gulosa +=1 
            self._on_op_disponivel_select(None) 
            return

        op_gulosa_correta_nesta_etapa = None
        for op_candidata in self.lista_para_selecao: 
            if op_candidata not in self.plano_do_jogador and op_candidata['inicio'] >= self.ultimo_horario_fim_plano:
                op_gulosa_correta_nesta_etapa = op_candidata
                break 
        
        if op_gulosa_correta_nesta_etapa and op_selecionada_pelo_jogador['id'] != op_gulosa_correta_nesta_etapa['id']:
            messagebox.showwarning("Escolha Questionável",
                                   f"Comandante, sua escolha '{op_selecionada_pelo_jogador['nome']}' é compatível.\n"
                                   f"No entanto, considerando a ordem atual das operações, a operação '{op_gulosa_correta_nesta_etapa['nome']}' "
                                   f"(Fim: {op_gulosa_correta_nesta_etapa['fim']}) "
                                   f"seria a primeira opção compatível a ser considerada para uma estratégia gulosa ótima.\n"
                                   "Lembre-se: priorizar a operação que termina mais cedo (na lista ordenada) geralmente leva ao melhor resultado geral.")
            self.erros_escolha_gulosa += 1
        
        self.plano_do_jogador.append(op_selecionada_pelo_jogador)
        self.plano_jogador_listbox.insert(tk.END, f"{op_selecionada_pelo_jogador['nome']} (I:{op_selecionada_pelo_jogador['inicio']}-F:{op_selecionada_pelo_jogador['fim']})")
        self.ultimo_horario_fim_plano = op_selecionada_pelo_jogador['fim']
        
        self._popular_lista_selecao() 
        self.status_label_m3.config(text=f"Plano atualizado. Última operação termina em {self.ultimo_horario_fim_plano}. Selecione a próxima ou finalize.")
        if self.btn_finalizar_plano and self.btn_finalizar_plano.winfo_exists():
            self.btn_finalizar_plano.config(state=tk.NORMAL)
        if self.btn_adicionar_op and self.btn_adicionar_op.winfo_exists():
            self.btn_adicionar_op.config(state=tk.DISABLED)


    def mostrar_dica_selecao_is(self):
        self.dica_count_m3 += 1
        dica_texto = ""
        # Verifica se a ordenação atual é a ótima (por tempo de fim)
        lista_ordenada_otima = sorted(self.operacoes_base, key=lambda x: x['fim'])
        ordenacao_atual_e_otima = (self.lista_para_selecao == lista_ordenada_otima)

        if self.dica_count_m3 == 1:
            dica_texto = ("DICA 1 (Estratégia Geral): Para maximizar o número de operações, a estratégia gulosa envolve:\n"
                          "1. ORDENAR todas as operações disponíveis por um critério específico.\n"
                          "2. ITERATIVAMENTE, selecionar a primeira operação da lista ordenada que seja compatível com as já selecionadas.")
            if not ordenacao_atual_e_otima:
                dica_texto += ("\n\nALERTA: Sua ordenação atual NÃO é a ideal (ordenar por tempo de término mais cedo). "
                               "Isso pode levar a um resultado subótimo. Deseja REORDENAR pela estratégia comprovadamente ótima?")
                if messagebox.askyesno("Dica: Reordenar Operações?", dica_texto):
                    self.ordenacao_escolhida_pelo_jogador = lambda x: x['fim'] # Define como se o jogador tivesse escolhido
                    self.lista_para_selecao = sorted(self.operacoes_base, key=self.ordenacao_escolhida_pelo_jogador)
                    self._popular_lista_selecao()
                    self.status_label_m3.config(text="Operações REORDENADAS por 'Fim Mais Cedo'. Continue selecionando.")
                    messagebox.showinfo("Reordenado", "A lista de operações foi reordenada pela estratégia ótima (Fim Mais Cedo).")
                dica_texto = "" 
                    
        elif self.dica_count_m3 == 2:
            op_gulosa_correta_para_dica = None
            for op_candidata in self.lista_para_selecao: # self.lista_para_selecao JÁ ESTÁ ORDENADA
                if op_candidata not in self.plano_do_jogador and op_candidata['inicio'] >= self.ultimo_horario_fim_plano:
                    op_gulosa_correta_para_dica = op_candidata
                    break
            if op_gulosa_correta_para_dica:
                dica_texto = (f"DICA 2 (Próximo Passo Ganancioso): Considerando seu plano atual (último fim em {self.ultimo_horario_fim_plano}) e a ORDEM ATUAL da lista, "
                              f"a próxima operação ideal a ser selecionada seria '{op_gulosa_correta_para_dica['nome']}' "
                              f"(I:{op_gulosa_correta_para_dica['inicio']}, Fim: {op_gulosa_correta_para_dica['fim']}).")
            else:
                dica_texto = "DICA 2: Parece que não há mais operações compatíveis com seu plano atual na lista. Talvez seja hora de finalizar."
        else:
            dica_texto = "DICA EXTRA: Continue aplicando a regra de 'escolher a primeira atividade compatível da lista (considerando a ordenação atual) que começa após o término da última atividade adicionada ao seu plano.'"
        
        if dica_texto: 
            messagebox.showinfo("Dica - Seleção Gulosa", dica_texto)
        
        if self.dica_count_m3 >= 2 and self.btn_dica_m3 and self.btn_dica_m3.winfo_exists():
            self.btn_dica_m3.config(state=tk.DISABLED)


    def _desabilitar_controles_missao3(self):
        if hasattr(self, 'btn_adicionar_op') and self.btn_adicionar_op and self.btn_adicionar_op.winfo_exists():
            self.btn_adicionar_op.config(state=tk.DISABLED)
        if hasattr(self, 'btn_finalizar_plano') and self.btn_finalizar_plano and self.btn_finalizar_plano.winfo_exists():
            self.btn_finalizar_plano.config(state=tk.DISABLED)
        if hasattr(self, 'btn_dica_m3') and self.btn_dica_m3 and self.btn_dica_m3.winfo_exists():
            self.btn_dica_m3.config(state=tk.DISABLED)
        if hasattr(self, 'operacoes_disponiveis_listbox') and self.operacoes_disponiveis_listbox and self.operacoes_disponiveis_listbox.winfo_exists():
            self.operacoes_disponiveis_listbox.config(state=tk.DISABLED) 


    def avaliar_plano_final_jogador(self):
        self._desabilitar_controles_missao3()

        solucao_otima_obj_list = calcular_interval_scheduling_otimo(self.operacoes_base)
        num_operacoes_jogador = len(self.plano_do_jogador)
        num_operacoes_otimo = len(solucao_otima_obj_list)
        ids_plano_jogador = {op['id'] for op in self.plano_do_jogador}
        ids_solucao_otima = {op['id'] for op in solucao_otima_obj_list}

        # Determina se o resultado é ótimo em número E composição
        resultado_perfeito_em_composicao = (num_operacoes_jogador == num_operacoes_otimo and ids_plano_jogador == ids_solucao_otima)
        
        # Verifica se a ordenação escolhida pelo jogador era a ótima
        ordenacao_foi_otima = (self.ordenacao_escolhida_pelo_jogador == (lambda x: x['fim']))

        if not resultado_perfeito_em_composicao and num_operacoes_jogador < num_operacoes_otimo: 
            if self.primeira_falha_nesta_tentativa_m3:
                pontos_a_deduzir = -40
                self.game_manager.add_score(pontos_a_deduzir)
                messagebox.showwarning("Penalidade por Falha", f"Comandante, seu plano não foi o ótimo. Uma penalidade de {abs(pontos_a_deduzir)} pontos de influência foi aplicada.")
                self.primeira_falha_nesta_tentativa_m3 = False
            
            falha_msg1 = f"Fulcrum (com voz grave): \"RZ-479, seu planejamento para o setor Arkanis foi... inadequado. Você executou apenas {num_operacoes_jogador} operações, quando poderíamos ter alcançado {num_operacoes_otimo}. Essa ineficiência custou caro. Uma de nossas equipes de infiltração, que dependia de uma sabotagem que NÃO foi incluída no seu plano, foi comprometida. Perdemos bons agentes e informações valiosas hoje por causa dessa falha.\""
            falha_msg2_criativa = f"Fulcrum: \"Comandante, o Império explorou as brechas que seu plano deixou no setor Arkanis. Os {num_operacoes_otimo - num_operacoes_jogador} alvos de oportunidade que perdemos permitiram ao inimigo reforçar suas posições. A Rebelião não pode se dar a esse luxo. Espero que esta lição seja aprendida.\""
            self.game_manager.mission_failed_options(self, falha_msg1, falha_msg2_criativa)

        elif resultado_perfeito_em_composicao and self.erros_escolha_gulosa == 0:
            pontos_ganhos = 300 
            self.game_manager.add_score(pontos_ganhos) 
            messagebox.showinfo("Plano Perfeito!",
                                f"Coordenação impecável, Comandante! Você agendou {num_operacoes_jogador} operações de forma ótima, seguindo a estratégia gulosa perfeitamente.\n"
                                f"Você ganhou {pontos_ganhos} pontos de influência!\n"
                                "Todas as ações foram executadas com sucesso no setor Arkanis, um duro golpe contra o Império!")
            self.game_manager.mission_completed("Missao3")
        
        elif resultado_perfeito_em_composicao and self.erros_escolha_gulosa > 0:
            pontos_ganhos = 200 
            self.game_manager.add_score(pontos_ganhos) 
            messagebox.showinfo("Plano Ótimo, Mas com Hesitação!",
                                f"Comandante, seu plano final atingiu o número máximo de {num_operacoes_jogador} operações! No entanto, você cometeu {self.erros_escolha_gulosa} desvio(s) ao aplicar a estratégia gulosa durante o planejamento. "
                                f"A precisão tática é vital, mas o resultado final ainda é um sucesso estratégico. Você ganhou {pontos_ganhos} pontos de influência.")
            self.game_manager.mission_completed("Missao3")
        
        else: 
            if self.primeira_falha_nesta_tentativa_m3:
                pontos_a_deduzir = -40
                self.game_manager.add_score(pontos_a_deduzir)
                messagebox.showwarning("Penalidade por Falha", f"Comandante, seu plano não seguiu a estratégia ótima. Uma penalidade de {abs(pontos_a_deduzir)} pontos de influência foi aplicada.")
                self.primeira_falha_nesta_tentativa_m3 = False

            falha_msg1 = (f"Fulcrum: \"RZ-479, embora o número de operações ({num_operacoes_jogador}) possa parecer adequado, sua abordagem tática ou os desvios da estratégia ótima padrão "
                          f"({self.erros_escolha_gulosa} erros de processo) são preocupantes. Essa inconsistência pode gerar riscos imprevistos e perdas de informação. "
                          "Precisamos de execuções impecáveis.\"")
            falha_msg2_criativa = (f"Fulcrum: \"Sua capacidade de coordenar múltiplas frentes é notável. No entanto, a *forma* como chegamos ao resultado importa. "
                                 "Desvios da doutrina tática padrão, mesmo que pareçam levar a um bom número de sucessos parciais, podem ter consequências não intencionais para a segurança de nossas células e a integridade da informação coletada.\"")
            self.game_manager.mission_failed_options(self, falha_msg1, falha_msg2_criativa)


    def retry_mission(self):
        self.game_manager.set_game_state("START_MISSION_3")