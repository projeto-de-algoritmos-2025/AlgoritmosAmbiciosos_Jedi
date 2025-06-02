import tkinter as tk
from tkinter import ttk, messagebox, font as tkFont
import heapq 

from algoritmos.interval_partitioning import calcular_interval_partitioning_otimo 

class Missao5:
    def __init__(self, root, game_manager, content_frame_para_missao):
        self.root = root
        self.game_manager = game_manager
        self.base_content_frame = content_frame_para_missao # estilo "Black.TFrame"

        # Cores do tema escuro (herdadas do GameManager)
        try:
            self.cor_fundo_base = self.game_manager.bg_color_dark
            self.cor_texto_principal = self.game_manager.fg_color_light
            self.cor_texto_titulo_missao = self.game_manager.title_color_accent
            self.cor_listbox_bg = "#101010" 
            self.cor_listbox_fg = self.game_manager.fg_color_light
            self.cor_listbox_select_bg = "#004080" 
            self.cor_listbox_select_fg = "white"
            self.cor_texto_info = "#B0E0E6" 
        except AttributeError:
            print("AVISO Missao5: Cores do GameManager não encontradas. Usando fallbacks.")
            self.cor_fundo_base = "black"
            self.cor_texto_principal = "white"
            self.cor_texto_titulo_missao = "orangered"
            self.cor_listbox_bg = "black"
            self.cor_listbox_fg = "white"
            self.cor_listbox_select_bg = "blue"
            self.cor_listbox_select_fg = "white"
            self.cor_texto_info = "lightblue"

        # Fontes (acessando os objetos de fonte corretos do GameManager com _obj)
        try:
            self.narrative_font_obj = self.game_manager.narrative_font_obj
            self.button_font_obj = self.game_manager.button_font_obj
            self.item_font_obj = tkFont.Font(family=self.game_manager.default_font_family, size=10)
            self.header_font_obj = self.game_manager.header_font_obj
            self.status_label_font_obj = self.game_manager.small_bold_font_obj
        except AttributeError:
            print("AVISO Missao5: Falha ao carregar fontes _obj do GameManager. Usando fallbacks.")
            default_family_fallback = "Arial"
            self.narrative_font_obj = tkFont.Font(family=default_family_fallback, size=12)
            self.button_font_obj = tkFont.Font(family=default_family_fallback, size=11, weight="bold")
            self.header_font_obj = tkFont.Font(family=default_family_fallback, size=20, weight="bold")
            self.status_label_font_obj = tkFont.Font(family=default_family_fallback, size=10, weight="bold")
            self.item_font_obj = tkFont.Font(family=default_family_fallback, size=10)

        
        # Dados da Missão: Janelas de Vigilância (nome, inicio, fim)
        self.janelas_vigilancia_base_original = [
            {'nome': "Patrulha Setor Alpha-7", 'inicio': 1, 'fim': 4, 'id': 'JV1'},
            {'nome': "Monitoramento Rota Bryx-Corellia", 'inicio': 2, 'fim': 5, 'id': 'JV2'},
            {'nome': "Vigilância Posto Imperial Gamma", 'inicio': 0, 'fim': 3, 'id': 'JV3'},
            {'nome': "Observação Frota Inimiga (Ponto K)", 'inicio': 4, 'fim': 7, 'id': 'JV4'},
            {'nome': "Escaneamento Corredor de Contrabando", 'inicio': 3, 'fim': 6, 'id': 'JV5'},
            {'nome': "Análise de Sinais (Nebulosa Xylos)", 'inicio': 6, 'fim': 8, 'id': 'JV6'},
            {'nome': "Segurança Ponto de Encontro Delta", 'inicio': 7, 'fim': 9, 'id': 'JV7'}
        ]
        self.janelas_vigilancia_base = list(self.janelas_vigilancia_base_original)

        # Estado da Missão
        self._reset_mission_state()

        # Referências UI
        self.lista_janelas_pendentes_listbox = None
        self.atribuicoes_listbox = None
        self.esquadroes_status_label = None
        self.btn_processar_janela = None
        self.btn_dica_m5_ordenacao = None 
        self.btn_dica_m5_atribuicao = None 


    def _clear_mission_frame(self):
        if self.base_content_frame and self.base_content_frame.winfo_exists():
            for widget in self.base_content_frame.winfo_children():
                widget.destroy()

    def limpar_interface_missao_completa(self):
        self._clear_mission_frame()

    def _reset_mission_state(self):
        self.janelas_vigilancia_base = list(self.janelas_vigilancia_base_original) 
        self.janelas_ordenadas_para_processar = []
        self.atribuicoes_jogador = {} 
        self.esquadroes_em_uso_heap_jogador = [] 
        self.num_esquadroes_jogador = 0
        self.primeira_falha_nesta_tentativa_m5 = True
        self.dica_count_m5 = 0
        self.estrategia_ordenacao_escolhida_m5_nome = None

    def iniciar_missao_contexto(self):
        self._clear_mission_frame()
        self._reset_mission_state()
        
        # Título da Missão
        tk.Label(self.base_content_frame, text="MISSÃO 5: Olhos no Setor Bryx", 
                 font=self.header_font_obj, fg=self.cor_texto_titulo_missao, bg=self.cor_fundo_base, pady=5).pack(pady=(0,15), fill=tk.X, padx=20)
        
        context_text_val = ( 
            "Fulcrum: \"Comandante, sua coordenação em Kessel foi vital. Agora, uma nova frente se abre. "
            "O Império está discretamente expandindo sua rede de sensores e patrulhas no Setor Bryx, uma área que acreditávamos ser de baixa prioridade para eles. "
            "Isso pode indicar uma nova rota de abastecimento imperial ou a preparação para uma ofensiva surpresa.\n\n"
            "Precisamos de vigilância constante sobre múltiplas 'janelas de tempo' para monitorar essas movimentações. Nossos recursos de patrulha (esquadrões de reconhecimento e droides sonda) são escassos.\n"
            "Sua missão: Atribuir o MENOR NÚMERO POSSÍVEL de esquadrões para cobrir todas as janelas de vigilância necessárias. Um esquadrão pode iniciar uma nova tarefa assim que a anterior for concluída.\""
        )
        
        text_context_container = tk.Frame(self.base_content_frame, bg=self.cor_fundo_base)
        text_context_container.pack(pady=10, padx=30, fill=tk.X)
        text_widget = tk.Text(text_context_container, wrap=tk.WORD, height=12, relief=tk.FLAT, 
                              font=self.narrative_font_obj, padx=10, pady=10,
                              borderwidth=0, highlightthickness=0,
                              background=self.cor_fundo_base, fg=self.cor_texto_principal, insertbackground=self.cor_texto_principal)
        text_widget.insert(tk.END, context_text_val)
        text_widget.config(state=tk.DISABLED)
        text_widget.pack(fill=tk.X, expand=True)
        
        button_container = ttk.Frame(self.base_content_frame, style="Black.TFrame")
        button_container.pack(pady=20)
        ttk.Button(button_container, text="Analisar Janelas de Vigilância...",
                   command=self.iniciar_etapa_ordenacao_m5, style="Accent.Dark.TButton").pack()

    def iniciar_etapa_ordenacao_m5(self):
        self._clear_mission_frame()
        
        tk.Label(self.base_content_frame, text="Etapa 1: Estratégia de Ordenação (Interval Partitioning)", 
                 font=self.button_font_obj, fg=self.cor_texto_principal, bg=self.cor_fundo_base).pack(pady=10)
        
        info_janelas_container = tk.Frame(self.base_content_frame, bg=self.cor_fundo_base, pady=5)
        info_janelas_container.pack(pady=5, padx=20, fill=tk.X)
        info_janelas_str = "JANELAS DE VIGILÂNCIA REQUERIDAS (Nome | Início | Fim):\n"
        for jv in sorted(self.janelas_vigilancia_base, key=lambda x: x['nome']):
            info_janelas_str += f"- {jv['nome']} (Início: {jv['inicio']}, Fim: {jv['fim']})\n"
        tk.Label(info_janelas_container, text=info_janelas_str, justify=tk.LEFT, 
                 font=self.item_font_obj, fg=self.cor_texto_info, bg=self.cor_fundo_base).pack(anchor="w")
        
        instrucoes_texto = ("Comandante, a ordem em que consideramos estas janelas para atribuir esquadrões é crucial "
                            "para minimizar o número total de esquadrões que precisaremos mobilizar. Qual critério de ordenação você sugere?")
        tk.Label(self.base_content_frame, text=instrucoes_texto, wraplength=700, justify=tk.CENTER, 
                 font=self.narrative_font_obj, fg=self.cor_texto_principal, bg=self.cor_fundo_base).pack(pady=10)

        botoes_frame = ttk.Frame(self.base_content_frame, style="Black.TFrame")
        botoes_frame.pack(pady=10)

        opcoes = [
            ("Ordenar por Início da Vigilância (mais cedo primeiro)", lambda x: x['inicio'], "Início Mais Cedo"), 
            ("Ordenar por Fim da Vigilância (mais cedo primeiro)", lambda x: x['fim'], "Fim Mais Cedo"),
            ("Ordenar por Duração (mais curta primeiro)", lambda x: x['fim'] - x['inicio'], "Duração Mais Curta")
        ]
        for texto_btn, sort_key_func, nome_curto_est in opcoes:
            btn = ttk.Button(botoes_frame, text=texto_btn, width=50, style="Dark.TButton",
                             command=lambda skf=sort_key_func, nome_est=nome_curto_est: self.processar_escolha_ordenacao_m5(skf, nome_est))
            btn.pack(pady=5)
        
        self.btn_dica_m5_ordenacao = ttk.Button(botoes_frame, text="Pedir Conselho (Dica de Ordenação)", 
                                                command=lambda: self.dar_dica_m5("ordenacao"), style="Dark.TButton")
        self.btn_dica_m5_ordenacao.pack(pady=10)

    def processar_escolha_ordenacao_m5(self, sort_key_func_escolhida, nome_curto_estrategia_escolhida):
        self.estrategia_ordenacao_escolhida_m5_nome = nome_curto_estrategia_escolhida
        self.janelas_ordenadas_para_processar = sorted(list(self.janelas_vigilancia_base), key=sort_key_func_escolhida)
        
        estrategia_correta_nome_curto = "Início Mais Cedo"
        if self.estrategia_ordenacao_escolhida_m5_nome == estrategia_correta_nome_curto:
            messagebox.showinfo("Estratégia Confirmada", 
                                f"Fulcrum: \"Excelente, Comandante. '{self.estrategia_ordenacao_escolhida_m5_nome}' é a abordagem correta para o problema de Particionamento de Intervalos. Isso nos permitirá atribuir recursos de forma eficiente.\"")
        else:
            messagebox.showwarning("Estratégia Registrada",
                                   f"Fulcrum: \"Sua escolha de '{self.estrategia_ordenacao_escolhida_m5_nome}' foi registrada, Comandante. Lembre-se, a ordem de processamento pode impactar diretamente quantos esquadrões precisaremos. O protocolo padrão sugere 'Início Mais Cedo'. Veremos o resultado da sua abordagem.\"")
        self.iniciar_etapa_atribuicao_m5()

    def iniciar_etapa_atribuicao_m5(self):
        self._clear_mission_frame()
        self.atribuicoes_jogador = {}
        self.esquadroes_em_uso_heap_jogador = [] 
        self.num_esquadroes_jogador = 0

        tk.Label(self.base_content_frame, text="Etapa 2: Atribuição de Esquadrões de Vigilância", 
                 font=self.button_font_obj, fg=self.cor_texto_principal, bg=self.cor_fundo_base).pack(pady=10)
        
        top_info_frame = tk.Frame(self.base_content_frame, bg=self.cor_fundo_base)
        top_info_frame.pack(fill=tk.X, pady=5, padx=10)
        self.esquadroes_status_label = tk.Label(top_info_frame, text=f"Esquadrões Utilizados: {self.num_esquadroes_jogador}", 
                                                font=self.status_label_font_obj, fg=self.cor_texto_info, bg=self.cor_fundo_base)
        self.esquadroes_status_label.pack(side=tk.LEFT, padx=5)

        listas_frame_container = tk.Frame(self.base_content_frame, bg=self.cor_fundo_base)
        listas_frame_container.pack(fill=tk.BOTH, expand=True, pady=5, padx=10)

        s = ttk.Style() # Para configurar o TLabelframe.Label para o modo escuro
        s.configure("Dark.TLabelframe", background=self.cor_fundo_base, bordercolor=self.cor_texto_info, relief=tk.GROOVE)
        s.configure("Dark.TLabelframe.Label", background=self.cor_fundo_base, foreground=self.cor_texto_principal, font=self.status_label_font_obj)


        pendentes_frame = ttk.LabelFrame(listas_frame_container, text=f"Janelas Pendentes (Ordem: {self.estrategia_ordenacao_escolhida_m5_nome})", 
                                         padding=5, style="Dark.TLabelframe")
        pendentes_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0,5))
        self.lista_janelas_pendentes_listbox = tk.Listbox(pendentes_frame, height=10, font=self.item_font_obj, exportselection=False,
                                                          bg=self.cor_listbox_bg, fg=self.cor_listbox_fg,
                                                          selectbackground=self.cor_listbox_select_bg,
                                                          selectforeground=self.cor_listbox_select_fg,
                                                          borderwidth=0, highlightthickness=0)
        self.lista_janelas_pendentes_listbox.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        self._popular_lista_janelas_pendentes_ui()

        atrib_frame = ttk.LabelFrame(listas_frame_container, text="Atribuições de Esquadrões Realizadas", 
                                     padding=5, style="Dark.TLabelframe")
        atrib_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5,0))
        self.atribuicoes_listbox = tk.Listbox(atrib_frame, height=10, font=self.item_font_obj,
                                              bg=self.cor_listbox_bg, fg=self.cor_listbox_fg,
                                              selectbackground=self.cor_listbox_select_bg,
                                              selectforeground=self.cor_listbox_select_fg,
                                              borderwidth=0, highlightthickness=0)
        self.atribuicoes_listbox.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)

        action_frame_bottom = ttk.Frame(self.base_content_frame, style="Black.TFrame")
        action_frame_bottom.pack(fill=tk.X, pady=(15,10), padx=10)

        self.btn_dica_m5_atribuicao = ttk.Button(action_frame_bottom, text="Pedir Dica (Atribuição)", 
                                                 command=lambda: self.dar_dica_m5("atribuicao"), style="Dark.TButton")
        self.btn_dica_m5_atribuicao.pack(side=tk.LEFT)
        
        self.btn_processar_janela = ttk.Button(action_frame_bottom, text="Processar Próxima Janela de Vigilância", 
                                              command=self.processar_proxima_janela_interativo, style="Accent.Dark.TButton")
        self.btn_processar_janela.pack(side=tk.RIGHT)
        
        if not self.janelas_ordenadas_para_processar: 
             self._finalizar_atribuicao_m5()

    def _popular_lista_janelas_pendentes_ui(self):
        if not self.lista_janelas_pendentes_listbox or not self.lista_janelas_pendentes_listbox.winfo_exists(): return
        self.lista_janelas_pendentes_listbox.delete(0, tk.END)
        for idx, jv in enumerate(self.janelas_ordenadas_para_processar): 
            self.lista_janelas_pendentes_listbox.insert(tk.END, f"{idx+1}. {jv['nome']} (I:{jv['inicio']}, F:{jv['fim']})")


    def processar_proxima_janela_interativo(self):
        if not self.janelas_ordenadas_para_processar:
            self._finalizar_atribuicao_m5(); return
        intervalo_atual = self.janelas_ordenadas_para_processar.pop(0)
        nome_janela, inicio_janela, fim_janela = intervalo_atual['nome'], intervalo_atual['inicio'], intervalo_atual['fim']
        id_esquadrao_atribuido = 0; acao_realizada_texto = ""
        if self.esquadroes_em_uso_heap_jogador and self.esquadroes_em_uso_heap_jogador[0][0] <= inicio_janela:
            _fim_recurso_anterior, id_recurso_reutilizado = heapq.heappop(self.esquadroes_em_uso_heap_jogador)
            self.atribuicoes_jogador[nome_janela] = id_recurso_reutilizado
            heapq.heappush(self.esquadroes_em_uso_heap_jogador, (fim_janela, id_recurso_reutilizado))
            id_esquadrao_atribuido = id_recurso_reutilizado
            acao_realizada_texto = f"Janela '{nome_janela}' (I:{inicio_janela}-F:{fim_janela}) atribuída ao Esq. {id_esquadrao_atribuido} (reutilizado, livre às {int(_fim_recurso_anterior)})."
        else:
            self.num_esquadroes_jogador += 1; id_novo_recurso = self.num_esquadroes_jogador
            self.atribuicoes_jogador[nome_janela] = id_novo_recurso
            heapq.heappush(self.esquadroes_em_uso_heap_jogador, (fim_janela, id_novo_recurso))
            id_esquadrao_atribuido = id_novo_recurso
            acao_realizada_texto = f"Janela '{nome_janela}' (I:{inicio_janela}-F:{fim_janela}) atribuída ao NOVO Esq. {id_esquadrao_atribuido}."
        self.atribuicoes_listbox.insert(tk.END, f"{nome_janela} -> Esq. {id_esquadrao_atribuido}")
        self.atribuicoes_listbox.see(tk.END)
        if self.esquadroes_status_label and self.esquadroes_status_label.winfo_exists():
            self.esquadroes_status_label.config(text=f"Esquadrões Utilizados: {self.num_esquadroes_jogador}")
        self._popular_lista_janelas_pendentes_ui() 
        messagebox.showinfo("Atribuição Realizada", acao_realizada_texto, parent=self.base_content_frame)
        if not self.janelas_ordenadas_para_processar: self._finalizar_atribuicao_m5()


    def _finalizar_atribuicao_m5(self):
        messagebox.showinfo("Planejamento Concluído", "Todas as janelas cobertas. Avaliando eficiência...", parent=self.base_content_frame)
        if self.btn_processar_janela and self.btn_processar_janela.winfo_exists():
            self.btn_processar_janela.config(state=tk.NORMAL, text="Avaliar Alocação Final", command=self.avaliar_plano_final_m5)
        if self.btn_dica_m5_atribuicao and self.btn_dica_m5_atribuicao.winfo_exists(): self.btn_dica_m5_atribuicao.config(state=tk.DISABLED)


    def avaliar_plano_final_m5(self):
        if hasattr(self, 'btn_processar_janela') and self.btn_processar_janela.winfo_exists(): self.btn_processar_janela.config(state=tk.DISABLED)
        if hasattr(self, 'btn_dica_m5_atribuicao') and self.btn_dica_m5_atribuicao.winfo_exists(): self.btn_dica_m5_atribuicao.config(state=tk.DISABLED)
        intervalos_para_otimo = sorted(list(self.janelas_vigilancia_base_original), key=lambda x: x['inicio'])
        num_esquadroes_otimo, _ = calcular_interval_partitioning_otimo(intervalos_para_otimo)
        print(f"DEBUG M5: Esquadrões Jogador: {self.num_esquadroes_jogador}, Ótimo: {num_esquadroes_otimo}, Estratégia: {self.estrategia_ordenacao_escolhida_m5_nome}")

        if self.num_esquadroes_jogador == num_esquadroes_otimo:
            pontos_ganhos = 80 
            estrategia_correta = "Início Mais Cedo"
            if self.estrategia_ordenacao_escolhida_m5_nome != estrategia_correta:
                messagebox.showwarning("Resultado Inesperado", f"Comandante, você usou {self.num_esquadroes_jogador} esquadrões (ótimo!), mas sua estratégia '{self.estrategia_ordenacao_escolhida_m5_nome}' não é a padrão ('{estrategia_correta}'). Desta vez funcionou...", parent=self.base_content_frame)
            else:
                 pontos_ganhos += 20; messagebox.showinfo("Alocação Perfeita!", f"Excelente! Mínimo de {self.num_esquadroes_jogador} esquadrões, seguindo a estratégia ótima! +{pontos_ganhos} pontos.", parent=self.base_content_frame)
            self.game_manager.add_score(pontos_ganhos); self.game_manager.mission_completed("Missao5")
        else: 
            if self.primeira_falha_nesta_tentativa_m5:
                self.game_manager.add_score(-50); messagebox.showwarning("Penalidade", f"Alocação não foi eficiente. Penalidade de 50 pontos.", parent=self.base_content_frame); self.primeira_falha_nesta_tentativa_m5 = False
            falha_msg1 = (f"Fulcrum: \"RZ-479, sua alocação usou {self.num_esquadroes_jogador} esquadrões. Era possível com {num_esquadroes_otimo} usando '{self.estrategia_ordenacao_escolhida_m5_nome}'. Recursos desperdiçados.\"")
            falha_msg2_criativa = ("Fulcrum: \"Comandante, cada esquadrão extra é um risco. Eficiência é sobrevivência.\"")
            self.game_manager.mission_failed_options(self, falha_msg1, falha_msg2_criativa)


    def dar_dica_m5(self, etapa_dica): 
        self.dica_count_m5 += 1; dica_texto = ""
        if etapa_dica == "ordenacao":
            if self.dica_count_m5 == 1: dica_texto = ("DICA: Para minimizar recursos no Particionamento de Intervalos, a ordem de considerar as janelas é crucial. Pense em qual encaixar primeiro para maximizar a reutilização.")
            elif self.dica_count_m5 >= 2:
                dica_texto = ("DICA AVANÇADA: A estratégia gulosa padrão é ordenar as janelas pelo HORÁRIO DE INÍCIO.")
                if self.btn_dica_m5_ordenacao and self.btn_dica_m5_ordenacao.winfo_exists(): self.btn_dica_m5_ordenacao.config(text="Aplicar Ordenação por Início", command=self.forcar_ordenacao_inicio_com_dica)
        elif etapa_dica == "atribuicao":
            dica_texto = "DICA: Com as janelas ordenadas (por início), para cada uma: 1. Verifique se algum esquadrão já usado está livre. 2. Se sim, use-o (o que ficou livre mais cedo é ideal). 3. Se não, aloque um novo."
            if self.btn_dica_m5_atribuicao and self.btn_dica_m5_atribuicao.winfo_exists(): self.btn_dica_m5_atribuicao.config(state=tk.DISABLED)
        if dica_texto: messagebox.showinfo("Conselho Estratégico", dica_texto, parent=self.base_content_frame)


    def forcar_ordenacao_inicio_com_dica(self):
        messagebox.showinfo("Estratégia Corrigida", "Fulcrum: \"Sábia decisão. Lista reordenada por 'Início Mais Cedo'.\"", parent=self.base_content_frame)
        self.estrategia_ordenacao_escolhida_m5_nome = "Início Mais Cedo"
        self.janelas_ordenadas_para_processar = sorted(list(self.janelas_vigilancia_base), key=lambda x: x['inicio'])
        if self.btn_dica_m5_ordenacao and self.btn_dica_m5_ordenacao.winfo_exists(): self.btn_dica_m5_ordenacao.config(state=tk.DISABLED) 
        self.iniciar_etapa_atribuicao_m5() 


    def retry_mission(self):
        self.game_manager.set_game_state("START_MISSION_5")