import tkinter as tk
from tkinter import ttk, messagebox, font as tkFont
from algoritmos.scheduling_minimize_lateness import calcular_schedule_edf_e_lmax

class Missao4:
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
        
        # --- CONJUNTO DE DADOS PARA OS GRUPOS DE EXTRAÇÃO ---
        self.grupos_extracao_base_original = [ 
            # Nome, tj (tempo de processo), dj (prazo), id (para rastrear)
            {'nome': "Extração Alfa (Informante Urgente)", 'tj': 1, 'dj': 3,  'id': 'A'},
            {'nome': "Resgate Bravo (Cientista Chave)",    'tj': 8, 'dj': 10, 'id': 'B'},
            {'nome': "Coleta Charlie (Dados Imperiais)",  'tj': 4, 'dj': 12, 'id': 'C'},
            {'nome': "Sabotagem Delta (Fábrica de Armas)",'tj': 6, 'dj': 18, 'id': 'D'},
            {'nome': "Apoio Echo (Célula Rebelde Local)", 'tj': 3, 'dj': 7,  'id': 'E'}
        ]

        self.grupos_extracao_base = list(self.grupos_extracao_base_original) 
        self.tempo_total_limite_frota_imperial = sum(g['tj'] for g in self.grupos_extracao_base) + 5 

        # Estado da Missão
        self._reset_mission_state() # Chama o reset no init

        # Referências UI
        self.lista_pendentes_listbox = None
        self.timeline_listbox = None
        self.lmax_label = None
        self.tempo_op_label = None
        self.btn_agendar_proximo = None
        self.btn_dica_m4_ordenacao = None
        self.btn_dica_m4_agendamento = None

    def _clear_mission_frame(self):
        if self.base_content_frame and self.base_content_frame.winfo_exists():
            for widget in self.base_content_frame.winfo_children():
                widget.destroy()

    def limpar_interface_missao_completa(self):
        self._clear_mission_frame()

    def _reset_mission_state(self):
        """Reseta o estado interno da missão para uma nova tentativa ou início."""
        self.grupos_extracao_base = list(self.grupos_extracao_base_original) # Recarrega os dados base
        self.lista_ordenada_pelo_jogador = []
        self.plano_extracao_jogador = [] 
        self.tempo_atual_operacao = 0
        self.lmax_jogador = 0
        self.primeira_falha_nesta_tentativa_m4 = True
        self.dica_count_m4 = 0 
        self.estrategia_ordenacao_escolhida_nomecurto = None
        self.estrategia_ordenacao_escolhida_func = None


    def iniciar_missao_contexto(self):
        self._clear_mission_frame()
        self._reset_mission_state() 
        
        ttk.Label(self.base_content_frame, text="MISSÃO 4: Contagem Regressiva em Kessel", font=self.header_font).pack(pady=10)
        context_text = (
            f"Comandante RZ-479, emergência Nível Alfa no sistema Kessel! Operativos infiltrados instigaram uma rebelião em massa como distração para uma fuga planejada de prisioneiros políticos e cientistas vitais para a Aliança.\n\n"
            f"O Império respondeu rápido. Uma frota de bloqueio chegará em {self.tempo_total_limite_frota_imperial} unidades de tempo. Temos UMA nave de extração rápida, processando uma tarefa de resgate por vez.\n"
            "Cada grupo de resgate tem um tempo de preparo e extração (tj) e um prazo final crítico (dj) antes que sua rota de fuga seja cortada.\n\n"
            "Sua missão: Agendar as extrações para MINIMIZAR O ATRASO MÁXIMO de qualquer grupo. Vidas e o futuro da Aliança dependem da sua precisão."
        )
        text_widget = tk.Text(self.base_content_frame, wrap=tk.WORD, height=11, relief=tk.FLAT, 
                              background=self.root.cget('bg'), font=self.narrative_font, padx=10, pady=10)
        text_widget.insert(tk.END, context_text)
        text_widget.config(state=tk.DISABLED)
        text_widget.pack(pady=15, padx=10, fill=tk.X)
        ttk.Button(self.base_content_frame, text="Analisar Protocolos de Extração...",
                   command=self.iniciar_etapa_estrategia_ordenacao, style="Accent.TButton").pack(pady=20)

    def iniciar_etapa_estrategia_ordenacao(self):
        self._clear_mission_frame()
        self.lista_ordenada_pelo_jogador = [] 
        self.plano_extracao_jogador = []
        self.tempo_atual_operacao = 0
        self.lmax_jogador = 0
        self.estrategia_ordenacao_escolhida_nomecurto = None
        self.estrategia_ordenacao_escolhida_func = None


        ttk.Label(self.base_content_frame, text="Etapa 1: Estratégia de Priorização", font=self.button_font).pack(pady=10)
        
        info_grupos_str = "GRUPOS PARA EXTRAÇÃO (Nome | Processo (tj) | Prazo (dj)):\n"
        for g in sorted(self.grupos_extracao_base, key=lambda x: x['nome']): 
            info_grupos_str += f"- {g['nome']} (tj: {g['tj']}, dj: {g['dj']})\n"
        
        ttk.Label(self.base_content_frame, text=info_grupos_str, justify=tk.LEFT, font=self.item_font).pack(pady=10, anchor="w", padx=20)
        
        instrucoes_texto = ("Comandante, a ordem em que processamos estes grupos é crucial para minimizar o atraso máximo. "
                            "Qual estratégia de priorização você recomenda para esta situação crítica?")
        ttk.Label(self.base_content_frame, text=instrucoes_texto, wraplength=700, justify=tk.CENTER, font=self.narrative_font).pack(pady=10)

        botoes_frame = ttk.Frame(self.base_content_frame)
        botoes_frame.pack(pady=10)

        # Adicionado critério de desempate para 'Menor Folga' (menor dj, depois menor tj)
        opcoes = [
            ("Processar Extrações Mais Rápidas Primeiro (menor tj)", lambda x: x['tj'], "Menor tj"),
            ("Priorizar Prazos Mais Cedos Primeiro (menor dj)", lambda x: x['dj'], "Menor dj (EDF)"), 
            ("Atender Grupos com Menor 'Folga' Primeiro (menor dj - tj)", lambda x: (x['dj'] - x['tj'], x['dj'], x['tj']), "Menor Folga")
        ]
        for texto_btn, sort_key_func, nome_curto_est in opcoes:
            btn = ttk.Button(botoes_frame, text=texto_btn, width=50,
                             command=lambda skf=sort_key_func, nome_est=nome_curto_est: self.processar_escolha_estrategia(skf, nome_est))
            btn.pack(pady=5)
        
        self.btn_dica_m4_ordenacao = ttk.Button(botoes_frame, text="Pedir Conselho a Fulcrum (Dica de Ordenação)", command=lambda: self.dar_dica_m4("ordenacao"))
        self.btn_dica_m4_ordenacao.pack(pady=10)

    def processar_escolha_estrategia(self, sort_key_func_escolhida, nome_curto_estrategia_escolhida):
        self.estrategia_ordenacao_escolhida_func = sort_key_func_escolhida
        self.estrategia_ordenacao_escolhida_nomecurto = nome_curto_estrategia_escolhida
        
        # Cria uma cópia para ordenar, mantendo a original intacta para o cálculo do ótimo
        self.lista_ordenada_pelo_jogador = sorted(list(self.grupos_extracao_base), key=self.estrategia_ordenacao_escolhida_func)
        
        estrategia_correta_nome_curto = "Menor dj (EDF)" # A estratégia ótima
        if self.estrategia_ordenacao_escolhida_nomecurto == estrategia_correta_nome_curto:
            messagebox.showinfo("Estratégia Confirmada", 
                                f"Fulcrum: \"Correto, Comandante. '{self.estrategia_ordenacao_escolhida_nomecurto}' (Priorizar Prazos Mais Cedos) é a doutrina padrão da Aliança para minimizar o atraso máximo. Uma escolha sólida. Prossiga com a montagem do cronograma.\"")
        else:
            messagebox.showwarning("Estratégia Registrada",
                                   f"Fulcrum: \"Entendido, Comandante. Você escolheu '{self.estrategia_ordenacao_escolhida_nomecurto}'. Uma abordagem... taticamente divergente. "
                                   "Lembre-se que o protocolo padrão da Aliança para minimizar o atraso máximo é focar nos prazos mais urgentes. "
                                   "Sua escolha pode ter consequências diretas no resultado da missão. Prossiga com a montagem do cronograma com base na sua estratégia.\"")
        self.iniciar_etapa_construcao_cronograma()

    def iniciar_etapa_construcao_cronograma(self):
        self._clear_mission_frame()
        # Reseta o plano do jogador
        self.plano_extracao_jogador = []
        self.tempo_atual_operacao = 0
        self.lmax_jogador = 0
        
        # Usa a lista que foi ordenada pela estratégia do jogador
        self.lista_pendente_para_agendar_ui = list(self.lista_ordenada_pelo_jogador)

        ttk.Label(self.base_content_frame, text="Etapa 2: Construção do Cronograma de Extração", font=self.button_font).pack(pady=10)

        top_info_frame = ttk.Frame(self.base_content_frame)
        top_info_frame.pack(fill=tk.X, pady=5, padx=10)
        self.tempo_op_label = ttk.Label(top_info_frame, text=f"Tempo da Operação: {self.tempo_atual_operacao}", font=self.status_label_font)
        self.tempo_op_label.pack(side=tk.LEFT, padx=5)
        self.lmax_label = ttk.Label(top_info_frame, text=f"Atraso Máximo Atual: {self.lmax_jogador}", font=self.status_label_font)
        self.lmax_label.pack(side=tk.RIGHT, padx=5)

        listas_frame = ttk.Frame(self.base_content_frame)
        listas_frame.pack(fill=tk.BOTH, expand=True, pady=5, padx=10)

        pendentes_frame = ttk.LabelFrame(listas_frame, text=f"Grupos Pendentes (Sua Ordem: {self.estrategia_ordenacao_escolhida_nomecurto})", padding=5)
        pendentes_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0,5))
        self.lista_pendentes_listbox = tk.Listbox(pendentes_frame, height=10, font=self.item_font, exportselection=False)
        self.lista_pendentes_listbox.pack(fill=tk.BOTH, expand=True)
        self._popular_lista_pendentes_ui()

        plano_exec_frame = ttk.LabelFrame(listas_frame, text="Cronograma de Extração Formado", padding=5)
        plano_exec_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5,0))
        self.timeline_listbox = tk.Listbox(plano_exec_frame, height=10, font=self.item_font)
        self.timeline_listbox.pack(fill=tk.BOTH, expand=True)

        action_frame_bottom = ttk.Frame(self.base_content_frame)
        action_frame_bottom.pack(fill=tk.X, pady=(15,10), padx=10)

        self.btn_dica_m4_agendamento = ttk.Button(action_frame_bottom, text="Pedir Dica (Agendamento)", command=lambda: self.dar_dica_m4("agendamento"))
        self.btn_dica_m4_agendamento.pack(side=tk.LEFT)
        
        self.btn_agendar_proximo = ttk.Button(action_frame_bottom, text="Agendar Próximo Grupo da Lista", 
                                              command=self.agendar_proximo_grupo_interativo, style="Accent.TButton")
        self.btn_agendar_proximo.pack(side=tk.RIGHT)
        
        if not self.lista_pendente_para_agendar_ui: # Se, por acaso, a lista já estiver vazia
             self._finalizar_construcao_cronograma()

    def _popular_lista_pendentes_ui(self):
        if not self.lista_pendentes_listbox or not self.lista_pendentes_listbox.winfo_exists(): return
        self.lista_pendentes_listbox.delete(0, tk.END)
        for idx, grupo in enumerate(self.lista_pendente_para_agendar_ui):
            self.lista_pendentes_listbox.insert(tk.END, f"{idx+1}. {grupo['nome']} (tj:{grupo['tj']}, dj:{grupo['dj']})")

    def agendar_proximo_grupo_interativo(self):
        if not self.lista_pendente_para_agendar_ui:
            self._finalizar_construcao_cronograma()
            return

        grupo_a_agendar = self.lista_pendente_para_agendar_ui.pop(0) 
        
        tj = grupo_a_agendar['tj']
        dj = grupo_a_agendar['dj']
        
        sj = self.tempo_atual_operacao
        fj = sj + tj
        atraso_j = max(0, fj - dj)
        
        self.plano_extracao_jogador.append({
            'nome': grupo_a_agendar['nome'], 'id': grupo_a_agendar['id'], 
            'tj': tj, 'dj': dj, 'sj': sj, 'fj': fj, 'atraso_j': atraso_j
        })
        
        self.tempo_atual_operacao = fj 
        self.lmax_jogador = max(self.lmax_jogador, atraso_j)

        self.timeline_listbox.insert(tk.END, f"{grupo_a_agendar['nome']}: Início {sj}, Fim {fj} (Prazo {dj}, Atraso {atraso_j})")
        self.timeline_listbox.see(tk.END) 
        if self.tempo_op_label and self.tempo_op_label.winfo_exists():
            self.tempo_op_label.config(text=f"Tempo da Operação: {self.tempo_atual_operacao}")
        if self.lmax_label and self.lmax_label.winfo_exists():
            self.lmax_label.config(text=f"Atraso Máximo Atual: {self.lmax_jogador}")
        self._popular_lista_pendentes_ui() 

        if not self.lista_pendente_para_agendar_ui: 
            self._finalizar_construcao_cronograma()

    def _finalizar_construcao_cronograma(self):
        messagebox.showinfo("Cronograma Montado", "Todos os grupos foram processados conforme sua estratégia. Vamos avaliar o resultado.")
        if self.btn_agendar_proximo and self.btn_agendar_proximo.winfo_exists():
            self.btn_agendar_proximo.config(state=tk.NORMAL, text="Avaliar Cronograma Final")
            self.btn_agendar_proximo.config(command=self.avaliar_cronograma_final)
        if self.btn_dica_m4_agendamento and self.btn_dica_m4_agendamento.winfo_exists():
            self.btn_dica_m4_agendamento.config(state=tk.DISABLED)

    def avaliar_cronograma_final(self):
        if hasattr(self, 'btn_agendar_proximo') and self.btn_agendar_proximo and self.btn_agendar_proximo.winfo_exists():
             self.btn_agendar_proximo.config(state=tk.DISABLED)
        if hasattr(self, 'btn_dica_m4_agendamento') and self.btn_dica_m4_agendamento and self.btn_dica_m4_agendamento.winfo_exists():
            self.btn_dica_m4_agendamento.config(state=tk.DISABLED)

        # --- PRINTS DE DEPURAÇÃO DETALHADOS ---
        print("\n" + "="*40)
        print("INÍCIO AVALIAÇÃO CRONOGRAMA FINAL (MISSÃO 4)")
        print(f"  Estratégia de Ordenação Escolhida: {self.estrategia_ordenacao_escolhida_nomecurto}")
        print("  Cronograma Montado pelo Jogador (self.plano_extracao_jogador):")
        if not self.plano_extracao_jogador: print("    PLANO DO JOGADOR ESTÁ VAZIO!")
        for i, item_p in enumerate(self.plano_extracao_jogador):
            print(f"    {i+1}. Nome: {item_p.get('nome', 'N/A')}, tj: {item_p.get('tj', 'N/A')}, dj: {item_p.get('dj', 'N/A')}, sj: {item_p.get('sj', 'N/A')}, fj: {item_p.get('fj', 'N/A')}, Atraso_j: {item_p.get('atraso_j', 'N/A')}")
        print(f"  Lmax do Jogador (calculado durante agendamento): {self.lmax_jogador}")
        print(f"  Tempo Total da Operação do Jogador: {self.tempo_atual_operacao}")
        
        lmax_otimo_calculado, cronograma_otimo_detalhado = calcular_schedule_edf_e_lmax(list(self.grupos_extracao_base_original)) 
        print(f"\n  Lmax Ótimo Calculado (via EDF): {lmax_otimo_calculado}")
        print(f"  Cronograma Ótimo EDF Detalhado:")
        for i, item_o in enumerate(cronograma_otimo_detalhado):
            print(f"    {i+1}. Nome: {item_o.get('nome', 'N/A')}, tj: {item_o.get('tj', 'N/A')}, dj: {item_o.get('dj', 'N/A')}, sj: {item_o.get('sj', 'N/A')}, fj: {item_o.get('fj', 'N/A')}, Atraso_j: {item_o.get('atraso_j', 'N/A')}")
        print("="*40 + "\n")
        # --- FIM DOS PRINTS DE DEPURAÇÃO ---

        if self.tempo_atual_operacao > self.tempo_total_limite_frota_imperial:
            if self.primeira_falha_nesta_tentativa_m4:
                self.game_manager.add_score(-60) 
                messagebox.showwarning("Penalidade por Falha Crítica", f"Comandante, suas operações levaram {self.tempo_atual_operacao} u.t., excedendo o limite de {self.tempo_total_limite_frota_imperial}! Fomos detectados! Penalidade de 60 pontos.")
                self.primeira_falha_nesta_tentativa_m4 = False
            falha_msg1 = (f"ALERTA MÁXIMO! Comandante, seu cronograma de extração levou {self.tempo_atual_operacao} u.t., "
                          f"excedendo o limite de {self.tempo_total_limite_frota_imperial} antes da chegada da frota de bloqueio Imperial! "
                          "Nossa nave de extração foi apanhada! Missão fracassada, consequências severas!")
            falha_msg2_criativa = ("Os sensores de longo alcance disparam! Contatos hostis múltiplos saltando do hiperespaço! "
                                   "É a frota de bloqueio! Tarde demais... \"Preparem-se para o impacto!\" - foi a última transmissão da nave de extração. "
                                   "Uma falha catastrófica, Comandante.")
            self.game_manager.mission_failed_options(self, falha_msg1, falha_msg2_criativa)
            return

        # Condição de Sucesso: Lmax do jogador é igual ao Lmax ótimo calculado pela EDF.
        if self.lmax_jogador == lmax_otimo_calculado: 
            self.game_manager.add_score(300) 
            messagebox.showinfo("Extração Bem-Sucedida!",
                                f"Excelente coordenação, Comandante! Seu cronograma resultou em um Atraso Máximo de {self.lmax_jogador}.\n"
                                f"Este é o resultado ótimo possível, igualando a estratégia EDF (Lmax: {lmax_otimo_calculado}).\n"
                                "Todas as equipes cruciais foram extraídas com o mínimo de exposição. Um grande dia para a Aliança! Você ganhou 300 pontos.")
            self.game_manager.mission_completed("Missao4")
        else: # Lmax do jogador foi pior que o ótimo
            if self.primeira_falha_nesta_tentativa_m4:
                self.game_manager.add_score(-60)
                messagebox.showwarning("Penalidade por Plano Subótimo", f"Comandante, seu cronograma resultou em Atraso Máximo de {self.lmax_jogador}, mas o ótimo era {lmax_otimo_calculado}. Penalidade de 60 pontos aplicada.")
                self.primeira_falha_nesta_tentativa_m4 = False
            
            grupo_mais_atrasado_jogador_nome = "Um dos grupos prioritários"
            maior_atraso_real_jogador = self.lmax_jogador 
            if self.plano_extracao_jogador:
                try:
                    grupos_com_lmax = [g for g in self.plano_extracao_jogador if g['atraso_j'] == self.lmax_jogador]
                    if grupos_com_lmax:
                        grupo_mais_atrasado_jogador_nome = grupos_com_lmax[0]['nome']
                except (ValueError, KeyError): pass # Em caso de erro ao buscar nome

            falha_msg1 = (f"Fulcrum (com voz grave): \"RZ-479, seu planejamento para Kessel resultou em um Atraso Máximo de {self.lmax_jogador}. "
                          f"A estratégia ótima (EDF) teria nos dado um atraso de apenas {lmax_otimo_calculado}.\n"
                          f"Essa diferença foi crítica. O grupo '{grupo_mais_atrasado_jogador_nome}', que sofreu um atraso de {maior_atraso_real_jogador} sob seu plano, foi interceptado por patrulhas imperiais. Perdemos contato e tememos o pior. Nossos agentes confiavam em você.\"")
            falha_msg2_criativa = (f"Fulcrum: \"Comandante, a precisão em operações como esta é a diferença entre a vida e a morte. "
                                   f"Sua programação expôs desnecessariamente nossos ativos devido à estratégia de ordenação '{self.estrategia_ordenacao_escolhida_nomecurto}'. "
                                   "Perdemos recursos valiosos hoje porque um grupo específico atrasou demais e sua rota de fuga foi comprometida. "
                                   "A falta de otimização... custa caro.\"")
            self.game_manager.mission_failed_options(self, falha_msg1, falha_msg2_criativa)


    def dar_dica_m4(self, etapa_dica): 
        self.dica_count_m4 += 1 
        dica_texto = ""
        
        if etapa_dica == "ordenacao":
            if self.dica_count_m4 == 1:
                dica_texto = ("DICA - Estratégia de Priorização:\n"
                              "Comandante, para minimizar o *atraso máximo* de um conjunto de tarefas, a teoria de escalonamento "
                              "sugere focar em uma propriedade específica das tarefas. Qual delas você acha que impede que *qualquer uma* das tarefas se atrase demais?")
            elif self.dica_count_m4 >= 2:
                dica_texto = ("DICA AVANÇADA - Ordenação EDF:\n"
                              "A estratégia ótima comprovada é 'Earliest Deadline First' (EDF) - Prazo Mais Cedo Primeiro. "
                              "Sempre processe a tarefa disponível com o prazo final mais próximo. Isso tende a 'tirar da frente' as tarefas que venceriam antes.")
                if self.btn_dica_m4_ordenacao and self.btn_dica_m4_ordenacao.winfo_exists():
                    self.btn_dica_m4_ordenacao.config(text="Aplicar Estratégia EDF (Recomendado)", 
                                                      command=self.forcar_ordenacao_edf_com_dica)
        
        elif etapa_dica == "agendamento":
            dica_texto = "DICA - Construção do Cronograma:\nApós ordenar os grupos pela sua estratégia escolhida, adicione-os ao cronograma um por um, NESSA ORDEM. Não deixe tempo ocioso. O tempo da operação avança conforme cada grupo é processado."
            if self.btn_dica_m4_agendamento and self.btn_dica_m4_agendamento.winfo_exists(): # Desabilita após uma dica de agendamento
                self.btn_dica_m4_agendamento.config(state=tk.DISABLED)


        if dica_texto: messagebox.showinfo("Conselho de Fulcrum", dica_texto)


    def forcar_ordenacao_edf_com_dica(self):
        messagebox.showinfo("Estratégia Corrigida",
                            "Fulcrum: \"Sábia decisão, Comandante. A lista de operações será agora ordenada por 'Prazo Mais Cedo Primeiro' para seu planejamento.\"")
        self.estrategia_ordenacao_escolhida_nomecurto = "Menor dj (EDF)" # Atualiza o nome da estratégia
        self.estrategia_ordenacao_escolhida_func = lambda x: x['dj'] # Atualiza a função chave
        self.lista_ordenada_pelo_jogador = sorted(list(self.grupos_extracao_base), key=self.estrategia_ordenacao_escolhida_func)
        
        if self.btn_dica_m4_ordenacao and self.btn_dica_m4_ordenacao.winfo_exists():
            self.btn_dica_m4_ordenacao.config(state=tk.DISABLED) #
        
        self.iniciar_etapa_construcao_cronograma() 


    def retry_mission(self):
        self.game_manager.set_game_state("START_MISSION_4")