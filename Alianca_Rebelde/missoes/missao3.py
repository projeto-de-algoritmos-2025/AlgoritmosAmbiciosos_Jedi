# missoes/missao3.py
import tkinter as tk
from tkinter import ttk, messagebox, font as tkFont
from algoritmos.interval_scheduling import calcular_interval_scheduling_otimo # Corrigido o nome do módulo

class Missao3:
    def __init__(self, root, game_manager, content_frame_para_missao):
        self.root = root
        self.game_manager = game_manager
        self.base_content_frame = content_frame_para_missao # Já deve ser preto pelo GameManager

        # Cores do tema escuro (herdadas do GameManager)
        try:
            self.cor_fundo_base = self.game_manager.bg_color_dark
            self.cor_texto_principal = self.game_manager.fg_color_light
            self.cor_texto_titulo_missao = self.game_manager.title_color_accent # Vermelho Alaranjado
            self.cor_listbox_bg = "#101010" # Um cinza muito escuro para listboxes
            self.cor_listbox_fg = self.game_manager.fg_color_light
            self.cor_listbox_select_bg = "#004080" # Azul escuro para seleção
            self.cor_listbox_select_fg = "white"
        except AttributeError:
            print("AVISO Missao3: Cores do GameManager não encontradas. Usando fallbacks.")
            self.cor_fundo_base = "black"
            self.cor_texto_principal = "white"
            self.cor_texto_titulo_missao = "orangered"
            self.cor_listbox_bg = "black"
            self.cor_listbox_fg = "white"
            self.cor_listbox_select_bg = "blue"
            self.cor_listbox_select_fg = "white"


        # Fontes (acessando os objetos de fonte corretos do GameManager com _obj)
        try:
            self.narrative_font_obj = self.game_manager.narrative_font_obj
            self.button_font_obj = self.game_manager.button_font_obj # Para títulos de etapa
            self.item_font_obj = tkFont.Font(family=self.game_manager.default_font_family, size=10)
            self.header_font_obj = self.game_manager.header_font_obj # Para o título principal da missão
            self.status_label_font_obj = self.game_manager.small_bold_font_obj # Para labels menores
        except AttributeError:
            print("AVISO Missao3: Falha ao carregar fontes _obj do GameManager. Usando fallbacks.")
            default_family_fallback = "Arial"
            self.narrative_font_obj = tkFont.Font(family=default_family_fallback, size=12)
            self.button_font_obj = tkFont.Font(family=default_family_fallback, size=11, weight="bold")
            self.header_font_obj = tkFont.Font(family=default_family_fallback, size=20, weight="bold")
            self.status_label_font_obj = tkFont.Font(family=default_family_fallback, size=10, weight="bold")
            self.item_font_obj = tkFont.Font(family=default_family_fallback, size=10)
        
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
        self.ordenacao_escolhida_pelo_jogador_func = None # Renomeado para clareza
        self.ordenacao_escolhida_pelo_jogador_nome = None


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
        
        # Título da Missão
        tk.Label(self.base_content_frame, text="MISSÃO 3: Sincronia Secreta no Setor Arkanis", 
                 font=self.header_font_obj, fg=self.cor_texto_titulo_missao, bg=self.cor_fundo_base, pady=5).pack(pady=(0,15), fill=tk.X, padx=20)
        
        context_text_val = ( # Renomeado para evitar conflito
            "Comandante, a situação é crítica. O Império está prestes a consolidar seu controle sobre o Corredor de Arkanis, uma rota de hiperespaço vital para nossas operações de suprimento e fuga no Anel Externo. Se não agirmos AGORA, perderemos o setor por completo, isolando inúmeras células rebeldes.\n\n"
            "Nossos espiões Bothans arriscaram tudo para identificar várias vulnerabilidades Imperiais simultâneas – mas são janelas de oportunidade extremamente fugazes. Precisamos de um plano impecável para atingir o máximo de alvos sem sobrecarregar nossas poucas equipes de assalto disponíveis.\n\n"
            "Sua tarefa: analisar as operações propostas e selecionar o MAIOR NÚMERO POSSÍVEL de operações que NÃO SE SOBREPONHAM no tempo."
        )
        
        text_context_container = tk.Frame(self.base_content_frame, bg=self.cor_fundo_base)
        text_context_container.pack(pady=10, padx=30, fill=tk.X)
        text_widget = tk.Text(text_context_container, wrap=tk.WORD, height=10, relief=tk.FLAT, 
                              font=self.narrative_font_obj, padx=10, pady=10,
                              borderwidth=0, highlightthickness=0,
                              background=self.cor_fundo_base, fg=self.cor_texto_principal, insertbackground=self.cor_texto_principal)
        text_widget.insert(tk.END, context_text_val)
        text_widget.config(state=tk.DISABLED)
        text_widget.pack(fill=tk.X, expand=True)
        
        button_container = ttk.Frame(self.base_content_frame, style="Black.TFrame")
        button_container.pack(pady=20)
        ttk.Button(button_container, text="Iniciar Planejamento Tático...",
                   command=self.iniciar_etapa_ordenacao, style="Accent.Dark.TButton").pack()


    def iniciar_etapa_ordenacao(self):
        self._clear_mission_frame()
        self.plano_do_jogador = []
        self.ultimo_horario_fim_plano = -1
        self.dica_count_m3 = 0 
        self.erros_escolha_gulosa = 0
        self.primeira_falha_nesta_tentativa_m3 = True 
        self.lista_para_selecao = list(self.operacoes_base) 
        self.ordenacao_escolhida_pelo_jogador_func = None 
        self.ordenacao_escolhida_pelo_jogador_nome = None


        tk.Label(self.base_content_frame, text="Etapa 1: Estratégia de Ordenação", 
                 font=self.button_font_obj, fg=self.cor_texto_principal, bg=self.cor_fundo_base).pack(pady=10) # Usando tk.Label
        
        instrucoes_texto = (
            "Comandante, a ordem em que consideramos as operações é fundamental para uma estratégia gulosa eficaz.\n"
            "Qual critério de ordenação você acredita ser o mais promissor para esta tarefa de escalonamento?"
        )
        tk.Label(self.base_content_frame, text=instrucoes_texto, wraplength=700, justify=tk.CENTER, 
                 font=self.narrative_font_obj, fg=self.cor_texto_principal, bg=self.cor_fundo_base).pack(pady=10)

        botoes_frame = ttk.Frame(self.base_content_frame, style="Black.TFrame")
        botoes_frame.pack(pady=10)

        opcoes_ordenacao = [
            ("Ordenar por Início (mais cedo primeiro)", lambda x: x['inicio'], "Início Mais Cedo"),
            ("Ordenar por Fim (mais cedo primeiro)", lambda x: x['fim'], "Fim Mais Cedo"), 
            ("Ordenar por Duração (mais curta primeiro)", lambda x: x['fim'] - x['inicio'], "Duração Mais Curta"),
            ("Ordenar por Prioridade (maior primeiro)", lambda x: -x['prioridade'], "Maior Prioridade")
        ]

        for texto_btn, sort_key_func, nome_curto_estratgia in opcoes_ordenacao:
            # Usando estilo Dark.TButton para os botões de escolha
            btn = ttk.Button(botoes_frame, text=texto_btn, width=45, style="Dark.TButton",
                             command=lambda skf=sort_key_func, nome_est=nome_curto_estratgia: self.processar_escolha_ordenacao(skf, nome_est))
            btn.pack(pady=5)
        
        # Botão de dica também estilizado
        self.btn_dica_m3 = ttk.Button(botoes_frame, text="Pedir Conselho (Dica de Ordenação)", 
                                      command=lambda: self.mostrar_dica_selecao_is("ordenacao"), style="Dark.TButton")
        self.btn_dica_m3.pack(pady=10)


    def processar_escolha_ordenacao(self, sort_key_func_escolhida, nome_estrategia_escolhida):
        self.ordenacao_escolhida_pelo_jogador_func = sort_key_func_escolhida
        self.ordenacao_escolhida_pelo_jogador_nome = nome_estrategia_escolhida # Guarda o nome curto
        self.lista_para_selecao = sorted(list(self.operacoes_base), key=self.ordenacao_escolhida_pelo_jogador_func)
        
        mensagem_feedback = f"Entendido, Comandante. As operações foram ordenadas usando o critério: \"{self.ordenacao_escolhida_pelo_jogador_nome}\".\n\n"
        
        estrategia_correta_nome_curto = "Fim Mais Cedo" # A estratégia ótima
        if self.ordenacao_escolhida_pelo_jogador_nome == estrategia_correta_nome_curto:
            mensagem_feedback += "Esta é a estratégia de ordenação que garante o resultado ótimo para o algoritmo ganancioso padrão de Interval Scheduling. Excelente escolha!"
            messagebox.showinfo("Estratégia Selecionada", mensagem_feedback)
        else:
            mensagem_feedback += ("Esta é uma abordagem válida para explorar. Contudo, para o algoritmo ganancioso de Interval Scheduling que garante o ótimo, "
                                  "a ordenação por TEMPO DE TÉRMINO é a ideal. Fique atento às dicas se precisar de orientação para a estratégia mais eficaz.")
            messagebox.showwarning("Estratégia Registrada", mensagem_feedback)
            
        self.iniciar_etapa_selecao_iterativa()

    def iniciar_etapa_selecao_iterativa(self):
        self._clear_mission_frame()
        
        tk.Label(self.base_content_frame, text="Etapa 2: Seleção Gulosa Iterativa", 
                 font=self.button_font_obj, fg=self.cor_texto_principal, bg=self.cor_fundo_base).pack(pady=(10,5)) # Título da etapa
        
        self.status_label_m3 = tk.Label(self.base_content_frame, text=f"Operações ordenadas por '{self.ordenacao_escolhida_pelo_jogador_nome}'. Selecione a primeira para seu plano.", 
                                        font=self.narrative_font_obj, wraplength=700, justify=tk.CENTER,
                                        fg=self.cor_texto_principal, bg=self.cor_fundo_base)
        self.status_label_m3.pack(pady=5)

        main_interaction_frame = ttk.Frame(self.base_content_frame, style="Black.TFrame")
        main_interaction_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Para LabelFrame, precisamos de um estilo se quisermos fundo preto e texto branco no título
        s = ttk.Style()
        s.configure("Dark.TLabelframe", background=self.cor_fundo_base, bordercolor=self.cor_texto_principal)
        s.configure("Dark.TLabelframe.Label", background=self.cor_fundo_base, foreground=self.cor_texto_principal, font=self.status_label_font_obj)


        disponiveis_frame = ttk.LabelFrame(main_interaction_frame, text="Operações Disponíveis (Considerar em Ordem)", 
                                           padding=10, style="Dark.TLabelframe")
        disponiveis_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0,5))
        
        self.operacoes_disponiveis_listbox = tk.Listbox(disponiveis_frame, selectmode=tk.SINGLE, exportselection=False, 
                                                       height=12, font=self.item_font_obj,
                                                       bg=self.cor_listbox_bg, fg=self.cor_listbox_fg,
                                                       selectbackground=self.cor_listbox_select_bg,
                                                       selectforeground=self.cor_listbox_select_fg,
                                                       borderwidth=0, highlightthickness=0)
        self.operacoes_disponiveis_listbox.pack(fill=tk.BOTH, expand=True, pady=(0,5))
        self.operacoes_disponiveis_listbox.bind('<<ListboxSelect>>', self._on_op_disponivel_select)
        self._popular_lista_selecao() 

        self.btn_adicionar_op = ttk.Button(disponiveis_frame, text="Adicionar Selecionada ao Plano >>", 
                                           command=self.adicionar_operacao_ao_plano_interativo, state=tk.DISABLED, style="Dark.TButton")
        self.btn_adicionar_op.pack(pady=5)

        plano_frame = ttk.LabelFrame(main_interaction_frame, text="Seu Plano de Operações Atual", 
                                     padding=10, style="Dark.TLabelframe")
        plano_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5,0))
        self.plano_jogador_listbox = tk.Listbox(plano_frame, height=12, font=self.item_font_obj,
                                                bg=self.cor_listbox_bg, fg=self.cor_listbox_fg,
                                                selectbackground=self.cor_listbox_select_bg,
                                                selectforeground=self.cor_listbox_select_fg,
                                                borderwidth=0, highlightthickness=0)
        self.plano_jogador_listbox.pack(fill=tk.BOTH, expand=True, pady=(0,5))

        action_frame_bottom = ttk.Frame(self.base_content_frame, style="Black.TFrame")
        action_frame_bottom.pack(fill=tk.X, pady=10, padx=10)
        
        self.btn_dica_m3 = ttk.Button(action_frame_bottom, text="Pedir Dica (Seleção)", 
                                      command=lambda: self.mostrar_dica_selecao_is("selecao"), style="Dark.TButton")
        self.btn_dica_m3.pack(side=tk.LEFT)
        
        self.btn_finalizar_plano = ttk.Button(action_frame_bottom, text="Finalizar Plano", 
                                              command=self.avaliar_plano_final_jogador, 
                                              style="Accent.Dark.TButton", state=tk.DISABLED)
        self.btn_finalizar_plano.pack(side=tk.RIGHT)

    def _on_op_disponivel_select(self, event):
        # ... (como antes, mas verifica se os botões existem) ...
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
        except tk.TclError: 
             if self.btn_adicionar_op and self.btn_adicionar_op.winfo_exists(): self.btn_adicionar_op.config(state=tk.DISABLED)

    def _popular_lista_selecao(self):
        if not self.operacoes_disponiveis_listbox or not self.operacoes_disponiveis_listbox.winfo_exists(): return
        self.operacoes_disponiveis_listbox.delete(0, tk.END)
        
        for op_data in self.lista_para_selecao: 
            status = ""
            cor_fg_item = self.cor_listbox_fg # Cor padrão do texto da listbox
            if op_data in self.plano_do_jogador:
                status = " [NO PLANO]"
                cor_fg_item = "grey" # Cinza para itens no plano
            elif op_data['inicio'] < self.ultimo_horario_fim_plano:
                status = " [CONFLITA]"
                cor_fg_item = "salmon" # Um vermelho mais claro para conflito
            
            self.operacoes_disponiveis_listbox.insert(tk.END, f"{op_data['nome']} (I:{op_data['inicio']}-F:{op_data['fim']}){status}")
            idx = self.operacoes_disponiveis_listbox.size() - 1
            if status: 
                self.operacoes_disponiveis_listbox.itemconfig(idx, {'foreground': cor_fg_item})


    def adicionar_operacao_ao_plano_interativo(self):
        # ... (como antes, mas verifica se status_label_m3 existe) ...
        if not self.operacoes_disponiveis_listbox or not self.operacoes_disponiveis_listbox.curselection():
            messagebox.showwarning("Nenhuma Operação", "Selecione uma operação da lista para adicionar ao plano.")
            return
        idx_real_na_lista_ordenada = self.operacoes_disponiveis_listbox.curselection()[0]
        op_selecionada_pelo_jogador = self.lista_para_selecao[idx_real_na_lista_ordenada]
        if op_selecionada_pelo_jogador in self.plano_do_jogador:
            messagebox.showwarning("Já no Plano", "Esta operação já foi adicionada.")
            self._on_op_disponivel_select(None); return
        if op_selecionada_pelo_jogador['inicio'] < self.ultimo_horario_fim_plano:
            messagebox.showerror("Conflito!", f"'{op_selecionada_pelo_jogador['nome']}' conflita com o plano atual.")
            self.erros_escolha_gulosa +=1; self._on_op_disponivel_select(None); return
        op_gulosa_correta_nesta_etapa = None
        for op_candidata in self.lista_para_selecao: 
            if op_candidata not in self.plano_do_jogador and op_candidata['inicio'] >= self.ultimo_horario_fim_plano:
                op_gulosa_correta_nesta_etapa = op_candidata; break 
        if op_gulosa_correta_nesta_etapa and op_selecionada_pelo_jogador['id'] != op_gulosa_correta_nesta_etapa['id']:
            messagebox.showwarning("Escolha Questionável",
                                   f"Comandante, '{op_selecionada_pelo_jogador['nome']}' é compatível.\n"
                                   f"Porém, '{op_gulosa_correta_nesta_etapa['nome']}' (Fim: {op_gulosa_correta_nesta_etapa['fim']}) "
                                   f"seria a primeira compatível na lista ordenada atual. Lembre-se da estratégia gulosa ótima!")
            self.erros_escolha_gulosa += 1
        self.plano_do_jogador.append(op_selecionada_pelo_jogador)
        self.plano_jogador_listbox.insert(tk.END, f"{op_selecionada_pelo_jogador['nome']} (I:{op_selecionada_pelo_jogador['inicio']}-F:{op_selecionada_pelo_jogador['fim']})")
        self.ultimo_horario_fim_plano = op_selecionada_pelo_jogador['fim']
        self._popular_lista_selecao() 
        if self.status_label_m3 and self.status_label_m3.winfo_exists():
            self.status_label_m3.config(text=f"Plano atualizado. Última operação termina em {self.ultimo_horario_fim_plano}. Selecione a próxima ou finalize.")
        if self.btn_finalizar_plano and self.btn_finalizar_plano.winfo_exists(): self.btn_finalizar_plano.config(state=tk.NORMAL)
        if self.btn_adicionar_op and self.btn_adicionar_op.winfo_exists(): self.btn_adicionar_op.config(state=tk.DISABLED)

    def mostrar_dica_selecao_is(self, etapa_dica_atual): # Mudado para receber a etapa
        self.dica_count_m3 += 1
        dica_texto = ""
        # (Lógica de dica como na sua última versão, com a reordenação opcional)
        estrategia_correta_nome_curto = "Fim Mais Cedo" # A estratégia ótima
        ordenacao_atual_e_otima = (self.ordenacao_escolhida_pelo_jogador_nome == estrategia_correta_nome_curto)

        if etapa_dica_atual == "ordenacao": # Se a dica é para a etapa de ordenação
            dica_texto = ("DICA (Ordenação): Comandante, para maximizar o número de operações não conflitantes, "
                          "a experiência da Aliança sugere que ordenar as operações pelo seu **tempo de término mais cedo** "
                          "é a estratégia gulosa mais eficaz. Isso tende a liberar o 'recurso' (sua equipe de assalto) o mais rápido possível para a próxima tarefa.")
            if self.btn_dica_m3 and self.btn_dica_m3.winfo_exists():
                 self.btn_dica_m3.config(state=tk.DISABLED) # Desabilita dica de ordenação após uso

        elif etapa_dica_atual == "selecao": # Se a dica é para a etapa de seleção
            if self.dica_count_m3 == 1: # Ou um contador específico para esta etapa
                dica_texto = ("DICA 1 (Seleção): Com as operações ordenadas (idealmente por tempo de término):\n"
                              "1. Adicione a primeira operação da lista ao seu plano.\n"
                              "2. Ignore todas as operações que conflitam com a escolhida (começam antes do fim da última escolhida).\n"
                              "3. Da lista restante, escolha a PRÓXIMA operação que seja compatível e que esteja no topo da sua lista ordenada.\n"
                              "4. Repita.")
                if not ordenacao_atual_e_otima: # Se o jogador não escolheu a ordenação por Fim
                    dica_texto += ("\n\nALERTA: Sua ordenação atual por '" + str(self.ordenacao_escolhida_pelo_jogador_nome) + 
                                   "' pode não ser a ideal. A estratégia ótima usa 'Fim Mais Cedo'. "
                                   "Deseja REORDENAR agora pela estratégia ótima?")
                    if messagebox.askyesno("Dica: Reordenar Operações?", dica_texto, icon='question', parent=self.base_content_frame):
                        self.ordenacao_escolhida_pelo_jogador_func = lambda x: x['fim']
                        self.ordenacao_escolhida_pelo_jogador_nome = "Fim Mais Cedo"
                        self.lista_para_selecao = sorted(list(self.operacoes_base), key=self.ordenacao_escolhida_pelo_jogador_func)
                        self._popular_lista_selecao()
                        if self.status_label_m3 and self.status_label_m3.winfo_exists():
                            self.status_label_m3.config(text="Operações REORDENADAS por 'Fim Mais Cedo'. Continue selecionando.")
                        messagebox.showinfo("Reordenado", "A lista de operações foi reordenada pela estratégia ótima.", parent=self.base_content_frame)
                    dica_texto = "" # Limpa para não mostrar a mensagem padrão se reordenou
            elif self.dica_count_m3 >= 2: # Dica mais direta para o próximo passo
                op_gulosa_correta_para_dica = None
                for op_candidata in self.lista_para_selecao:
                    if op_candidata not in self.plano_do_jogador and op_candidata['inicio'] >= self.ultimo_horario_fim_plano:
                        op_gulosa_correta_para_dica = op_candidata; break
                if op_gulosa_correta_para_dica:
                    dica_texto = (f"DICA AVANÇADA: Considerando seu plano atual (último fim em {self.ultimo_horario_fim_plano}) "
                                  f"e a ordem atual da lista, a próxima operação ideal a selecionar seria '{op_gulosa_correta_para_dica['nome']}'.")
                else:
                    dica_texto = "DICA: Parece não haver mais operações compatíveis. Considere finalizar seu plano."
                if self.btn_dica_m3 and self.btn_dica_m3.winfo_exists(): self.btn_dica_m3.config(state=tk.DISABLED)
        
        if dica_texto: messagebox.showinfo("Conselho Estratégico", dica_texto, parent=self.base_content_frame)


    def _desabilitar_controles_missao3(self):
        # ... (como antes) ...
        if hasattr(self, 'btn_adicionar_op') and self.btn_adicionar_op and self.btn_adicionar_op.winfo_exists(): self.btn_adicionar_op.config(state=tk.DISABLED)
        if hasattr(self, 'btn_finalizar_plano') and self.btn_finalizar_plano and self.btn_finalizar_plano.winfo_exists(): self.btn_finalizar_plano.config(state=tk.DISABLED)
        if hasattr(self, 'btn_dica_m3') and self.btn_dica_m3 and self.btn_dica_m3.winfo_exists(): self.btn_dica_m3.config(state=tk.DISABLED)
        if hasattr(self, 'operacoes_disponiveis_listbox') and self.operacoes_disponiveis_listbox and self.operacoes_disponiveis_listbox.winfo_exists(): self.operacoes_disponiveis_listbox.config(state=tk.DISABLED) 


    def avaliar_plano_final_jogador(self):
        # ... (lógica de avaliação como na sua última versão, com pontuações e mensagens de Fulcrum) ...
        self._desabilitar_controles_missao3()
        solucao_otima_obj_list = calcular_interval_scheduling_otimo(self.operacoes_base)
        num_operacoes_jogador = len(self.plano_do_jogador)
        num_operacoes_otimo = len(solucao_otima_obj_list)
        ids_plano_jogador = {op['id'] for op in self.plano_do_jogador}
        ids_solucao_otima = {op['id'] for op in solucao_otima_obj_list}
        resultado_perfeito_em_composicao = (num_operacoes_jogador == num_operacoes_otimo and ids_plano_jogador == ids_solucao_otima)
        
        # Penalidade por falha na primeira tentativa
        penalidade_aplicada_nesta_rodada = False
        if not (resultado_perfeito_em_composicao and self.erros_escolha_gulosa == 0): # Se não for sucesso perfeito
            if self.primeira_falha_nesta_tentativa_m3:
                pontos_a_deduzir = -40
                self.game_manager.add_score(pontos_a_deduzir)
                messagebox.showwarning("Penalidade por Falha", f"Comandante, seu plano não foi o ideal. Uma penalidade de {abs(pontos_a_deduzir)} pontos de influência foi aplicada.", parent=self.base_content_frame)
                self.primeira_falha_nesta_tentativa_m3 = False
                penalidade_aplicada_nesta_rodada = True

        if resultado_perfeito_em_composicao and self.erros_escolha_gulosa == 0:
            pontos_ganhos = 300 
            self.game_manager.add_score(pontos_ganhos) 
            messagebox.showinfo("Plano Perfeito!", f"Coordenação impecável, Comandante! Você agendou {num_operacoes_jogador} operações... Você ganhou {pontos_ganhos} pontos...", parent=self.base_content_frame) # Texto completo
            self.game_manager.mission_completed("Missao3")
        elif resultado_perfeito_em_composicao and self.erros_escolha_gulosa > 0:
            pontos_ganhos = 200 
            self.game_manager.add_score(pontos_ganhos) 
            messagebox.showinfo("Plano Ótimo, Mas com Hesitação!", f"Comandante, seu plano final atingiu o máximo de {num_operacoes_jogador} operações! Contudo, {self.erros_escolha_gulosa} desvio(s) na estratégia... Você ganhou {pontos_ganhos} pontos.", parent=self.base_content_frame) # Texto completo
            self.game_manager.mission_completed("Missao3")
        else: 
            # Falha (resultado subótimo em número ou composição)
            if num_operacoes_jogador < num_operacoes_otimo:
                falha_msg1 = f"Fulcrum (voz grave): \"RZ-479, seu planejamento... executou apenas {num_operacoes_jogador} operações, quando poderíamos ter alcançado {num_operacoes_otimo}. Essa ineficiência custou caro... Perdemos bons agentes e informações valiosas...\"" # Texto completo
                falha_msg2_criativa = f"Fulcrum: \"Comandante, o Império explorou as brechas... Os {num_operacoes_otimo - num_operacoes_jogador} alvos de oportunidade que perdemos...\"" # Texto completo
            else: # num_operacoes_jogador == num_operacoes_otimo, mas ids diferentes ou erros no processo
                falha_msg1 = (f"Fulcrum: \"RZ-479, embora o número de operações ({num_operacoes_jogador}) pareça adequado, sua abordagem tática ou os desvios ({self.erros_escolha_gulosa} erros) são preocupantes...\"") # Texto completo
                falha_msg2_criativa = (f"Fulcrum: \"Sua capacidade de coordenar múltiplas frentes é notável... Desvios... podem ter consequências...\"") # Texto completo
            self.game_manager.mission_failed_options(self, falha_msg1, falha_msg2_criativa)


    def retry_mission(self):
        # O GameManager recriará a Missao3, chamando seu __init__ e depois iniciar_missao_contexto,
        # o que efetivamente reseta o estado interno da missão, incluindo self.primeira_falha_nesta_tentativa_m3.
        self.game_manager.set_game_state("START_MISSION_3")