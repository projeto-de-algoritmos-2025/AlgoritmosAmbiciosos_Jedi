# missoes/minigame_rpg_kruskal.py
import tkinter as tk
from tkinter import ttk, messagebox, font as tkFont # Adicionado tkFont
from algoritmos.union_find import UnionFind # Importa a estrutura UnionFind

class MinigameKruskalContraAtaque:
    def __init__(self, root, game_manager, content_frame, recompensa_sucesso, id_escolha_rpg):
        self.root = root
        self.game_manager = game_manager
        self.base_content_frame = content_frame # Já deve estar com estilo "Black.TFrame"
        self.recompensa_sucesso = recompensa_sucesso
        self.id_escolha_rpg = id_escolha_rpg

        # Cores do tema escuro (herdadas do GameManager)
        try:
            self.cor_fundo_minigame = self.game_manager.bg_color_dark
            self.cor_texto_narrativa = self.game_manager.fg_color_light
            self.cor_titulo_minigame = self.game_manager.title_color_accent # Vermelho Alaranjado
            self.cor_texto_info_kruskal = "#B0E0E6" # Azul claro para infos do Kruskal
        except AttributeError:
            print("AVISO MinigameKruskal: Cores do GameManager não encontradas. Usando fallbacks.")
            self.cor_fundo_minigame = "black"
            self.cor_texto_narrativa = "white"
            self.cor_titulo_minigame = "orangered"
            self.cor_texto_info_kruskal = "lightblue"

        # Fontes (herdadas do GameManager)
        try:
            self.header_font_obj = self.game_manager.header_font_obj
            self.narrative_font_obj = self.game_manager.narrative_font_obj
            self.button_font_obj = self.game_manager.button_font_obj
            self.small_bold_font_obj = self.game_manager.small_bold_font_obj
        except AttributeError:
            print("AVISO MinigameKruskal: Fontes do GameManager não encontradas. Usando fallbacks.")
            default_family_fallback = "Arial"
            self.header_font_obj = tkFont.Font(family=default_family_fallback, size=18, weight="bold")
            self.narrative_font_obj = tkFont.Font(family=default_family_fallback, size=11)
            self.button_font_obj = tkFont.Font(family=default_family_fallback, size=10, weight="bold")
            self.small_bold_font_obj = tkFont.Font(family=default_family_fallback, size=9, weight="bold")

        # Cenário: Conectar postos táticos para o contra-ataque
        self.postos_taticos = {'P1', 'P2', 'P3', 'CentralCom', 'TorreVigia'} 
        self.conexoes_disponiveis_base = [ 
            {'u': 'P1', 'v': 'P2', 'custo': 10}, {'u': 'P1', 'v': 'CentralCom', 'custo': 5}, 
            {'u': 'P1', 'v': 'TorreVigia', 'custo': 20}, {'u': 'P2', 'v': 'CentralCom', 'custo': 8}, 
            {'u': 'P2', 'v': 'P3', 'custo': 12}, {'u': 'P3', 'v': 'CentralCom', 'custo': 6}, 
            {'u': 'P3', 'v': 'TorreVigia', 'custo': 15}, {'u': 'CentralCom', 'v': 'TorreVigia', 'custo': 4}
        ]
        self.num_nos_objetivo = len(self.postos_taticos)

        # Estado do algoritmo de Kruskal
        self.arestas_ordenadas = []
        self.indice_aresta_atual = 0
        self.mst_construida_jogador = [] 
        self.union_find_jogador = UnionFind(list(self.postos_taticos)) # Passa a lista de nós
        self.total_custo_jogador = 0
        self.dicas_usadas = 0
        self.erros_ciclo = 0 

        # Referências UI
        self.info_label = None
        self.aresta_atual_label = None
        self.mst_label = None
        self.custo_label = None
        self.componentes_label = None # Para mostrar os componentes/conjuntos
        self.btn_sim_ciclo = None
        self.btn_nao_ciclo = None
        self.btn_dica_kruskal = None

    def _clear_minigame_frame(self):
        if self.base_content_frame and self.base_content_frame.winfo_exists():
            for widget in self.base_content_frame.winfo_children():
                widget.destroy()

    def iniciar_minigame_interface(self):
        self._clear_minigame_frame()

        # Resetar estado para retries
        self.arestas_ordenadas = sorted(self.conexoes_disponiveis_base, key=lambda x: x['custo'])
        self.indice_aresta_atual = 0
        self.mst_construida_jogador = []
        self.union_find_jogador.reset(list(self.postos_taticos)) # Reseta a estrutura UnionFind
        self.total_custo_jogador = 0
        self.dicas_usadas = 0
        self.erros_ciclo = 0

        # Título do Minigame
        title_label = tk.Label(self.base_content_frame, text="Minigame: Rede de Contra-Ataque (Kruskal)", 
                               font=self.header_font_obj, 
                               fg=self.cor_titulo_minigame, 
                               bg=self.cor_fundo_minigame)
        title_label.pack(pady=(0,15), fill=tk.X, padx=20)

        narrativa_inicial = (
            "Comandante, para nosso contra-ataque ser eficaz, precisamos ativar uma rede de comunicação segura e de baixo custo entre nossos postos táticos.\n"
            "Use o Algoritmo de Kruskal: considere as conexões (arestas) da mais barata para a mais cara.\n"
            "Adicione uma conexão à rede APENAS SE ela NÃO FORMAR UM CICLO com as conexões já existentes."
        )
        narrativa_label_ui = tk.Label(self.base_content_frame, text=narrativa_inicial, 
                                   wraplength=700, justify=tk.CENTER, 
                                   font=self.narrative_font_obj, 
                                   fg=self.cor_texto_narrativa, 
                                   bg=self.cor_fundo_minigame)
        narrativa_label_ui.pack(pady=10, padx=20)


        # --- Display do Estado do Algoritmo ---
        estado_frame = tk.Frame(self.base_content_frame, bg=self.cor_fundo_minigame, pady=5)
        estado_frame.pack(pady=10, fill=tk.X, padx=20)

        self.aresta_atual_label = tk.Label(estado_frame, text="", font=self.small_bold_font_obj, 
                                           fg=self.cor_texto_info_kruskal, bg=self.cor_fundo_minigame, justify=tk.LEFT)
        self.aresta_atual_label.pack(anchor="w")
        
        self.mst_label = tk.Label(estado_frame, text="Rede Ativada (MST): Nenhuma", font=self.small_bold_font_obj, 
                                  wraplength=700, fg=self.cor_texto_info_kruskal, bg=self.cor_fundo_minigame, justify=tk.LEFT)
        self.mst_label.pack(anchor="w")
        
        self.custo_label = tk.Label(estado_frame, text="Custo Total da Rede: 0", font=self.small_bold_font_obj,
                                    fg=self.cor_texto_info_kruskal, bg=self.cor_fundo_minigame, justify=tk.LEFT)
        self.custo_label.pack(anchor="w")

        self.componentes_label = tk.Label(estado_frame, text="Componentes Conectados: (Inicial)", font=self.small_bold_font_obj,
                                    wraplength=700, fg=self.cor_texto_info_kruskal, bg=self.cor_fundo_minigame, justify=tk.LEFT)
        self.componentes_label.pack(anchor="w")
        self._atualizar_display_componentes() # Atualiza o display inicial dos componentes


        # --- Área de Interação Principal (Decisão sobre Ciclo) ---
        self.info_label = tk.Label(self.base_content_frame, text="Aguardando sua análise...", 
                                   font=self.narrative_font_obj, fg=self.cor_texto_narrativa, bg=self.cor_fundo_minigame)
        self.info_label.pack(pady=10)

        decisao_frame = ttk.Frame(self.base_content_frame, style="Black.TFrame") # ttk.Frame para botões estilizados
        decisao_frame.pack(pady=10)
        self.btn_sim_ciclo = ttk.Button(decisao_frame, text="Sim (Forma Ciclo - Descartar)", 
                                        command=lambda: self.processar_decisao_jogador(True), style="Dark.TButton")
        self.btn_sim_ciclo.pack(side=tk.LEFT, padx=10)
        self.btn_nao_ciclo = ttk.Button(decisao_frame, text="Não (Não Forma Ciclo - Adicionar)", 
                                         command=lambda: self.processar_decisao_jogador(False), style="Accent.Dark.TButton")
        self.btn_nao_ciclo.pack(side=tk.LEFT, padx=10)
        
        # --- Botão de Dica ---
        action_frame_bottom = ttk.Frame(self.base_content_frame, style="Black.TFrame")
        action_frame_bottom.pack(fill=tk.X, pady=15, padx=20)
        self.btn_dica_kruskal = ttk.Button(action_frame_bottom, text="Pedir Dica (Kruskal)", command=self.dar_dica_kruskal, style="Dark.TButton")
        self.btn_dica_kruskal.pack(side=tk.LEFT)

        self.apresentar_proxima_aresta()

    def _atualizar_display_componentes(self):
        if not (self.componentes_label and self.componentes_label.winfo_exists()): return
        
        componentes_dict = {}
        for no in self.union_find_jogador.parent: # Itera sobre os nós que a UF conhece
            raiz = self.union_find_jogador.find(no)
            if raiz not in componentes_dict:
                componentes_dict[raiz] = []
            componentes_dict[raiz].append(no)
        
        componentes_str = "Componentes: " + "; ".join([f"{{{', '.join(sorted(comp))}}}" for comp in componentes_dict.values()])
        self.componentes_label.config(text=componentes_str)


    def apresentar_proxima_aresta(self):
        # Verifica se o minigame deve terminar
        if self.indice_aresta_atual >= len(self.arestas_ordenadas) or \
           len(self.mst_construida_jogador) >= self.num_nos_objetivo - 1:
            self.finalizar_minigame()
            return

        aresta_data = self.arestas_ordenadas[self.indice_aresta_atual]
        u, v, custo = aresta_data['u'], aresta_data['v'], aresta_data['custo']
        
        if self.aresta_atual_label and self.aresta_atual_label.winfo_exists():
            self.aresta_atual_label.config(text=f"Próxima Conexão (menor custo): {u} <-> {v} (Custo: {custo})")
        if self.info_label and self.info_label.winfo_exists():
            self.info_label.config(text=f"Adicionar a conexão ({u}-{v}) formaria um ciclo na sua rede atual?")
        
        if self.btn_sim_ciclo and self.btn_sim_ciclo.winfo_exists(): self.btn_sim_ciclo.config(state=tk.NORMAL)
        if self.btn_nao_ciclo and self.btn_nao_ciclo.winfo_exists(): self.btn_nao_ciclo.config(state=tk.NORMAL)
        self._atualizar_display_componentes()


    def processar_decisao_jogador(self, jogador_acha_que_forma_ciclo):
        if self.indice_aresta_atual >= len(self.arestas_ordenadas): # Segurança
            self.finalizar_minigame()
            return

        aresta_data = self.arestas_ordenadas[self.indice_aresta_atual]
        u, v, custo = aresta_data['u'], aresta_data['v'], aresta_data['custo']

        realmente_forma_ciclo = self.union_find_jogador.conectados(u, v)

        if jogador_acha_que_forma_ciclo == realmente_forma_ciclo:
            messagebox.showinfo("Análise Correta!", "Sua análise sobre o ciclo está correta, Comandante.")
            if not realmente_forma_ciclo: # Se NÃO forma ciclo E o jogador disse NÃO (correto)
                self.union_find_jogador.union(u, v)
                self.mst_construida_jogador.append(aresta_data)
                self.total_custo_jogador += custo
                if self.mst_label and self.mst_label.winfo_exists():
                    self.mst_label.config(text=f"Rede Ativada (MST): {self.formatar_mst_string()}")
                if self.custo_label and self.custo_label.winfo_exists():
                    self.custo_label.config(text=f"Custo Total da Rede: {self.total_custo_jogador}")
        else:
            self.erros_ciclo += 1
            feedback_erro = "Análise Incorreta, Comandante! "
            if realmente_forma_ciclo: 
                feedback_erro += f"Adicionar ({u}-{v}) TERIA formado um ciclo, pois '{u}' e '{v}' já estão conectados na sua rede atual."
            else: 
                feedback_erro += f"Adicionar ({u}-{v}) NÃO formaria um ciclo. Era uma conexão segura para adicionar à rede."
            messagebox.showwarning("Erro na Análise de Ciclo", feedback_erro + f"\nVocê cometeu {self.erros_ciclo} erro(s) na detecção de ciclo.")
            # Poderia adicionar uma pequena penalidade de pontos aqui por erro, se quisesse.

        self.indice_aresta_atual += 1
        self.apresentar_proxima_aresta() # Chama para a próxima aresta ou finaliza

    def formatar_mst_string(self):
        if not self.mst_construida_jogador:
            return "Nenhuma conexão ativada."
        return ", ".join([f"({a['u']}-{a['v']} C:{a['custo']})" for a in self.mst_construida_jogador])


    def finalizar_minigame(self):
        if self.btn_sim_ciclo and self.btn_sim_ciclo.winfo_exists(): self.btn_sim_ciclo.config(state=tk.DISABLED)
        if self.btn_nao_ciclo and self.btn_nao_ciclo.winfo_exists(): self.btn_nao_ciclo.config(state=tk.DISABLED)
        if self.btn_dica_kruskal and self.btn_dica_kruskal.winfo_exists(): self.btn_dica_kruskal.config(state=tk.DISABLED)
        
        num_arestas_esperadas_mst = self.num_nos_objetivo - 1
        # O sucesso aqui é definido por ter o número correto de arestas E poucos erros de julgamento de ciclo
        sucesso = (len(self.mst_construida_jogador) == num_arestas_esperadas_mst and self.erros_ciclo <= 1) 
        # Poderíamos também calcular o custo ótimo da MST e comparar, mas o processo é mais importante aqui.

        if sucesso:
            msg = (f"Rede de Contra-Ataque estabelecida com sucesso!\n"
                   f"Conexões Ativadas: {len(self.mst_construida_jogador)} (de {num_arestas_esperadas_mst} esperadas para uma rede completa)\n"
                   f"Custo Total da Rede: {self.total_custo_jogador}\n"
                   f"Erros na detecção de ciclo: {self.erros_ciclo}\n"
                   "Sua precisão foi fundamental para otimizar nossos recursos, Comandante!")
            messagebox.showinfo("Sucesso no Minigame Kruskal!", msg)
            self.game_manager.handle_minigame_rpg_result(True, self.id_escolha_rpg, self.recompensa_sucesso)
        else:
            msg_falha = "Falha ao estabelecer a Rede de Contra-Ataque de forma ótima.\n"
            if len(self.mst_construida_jogador) != num_arestas_esperadas_mst:
                msg_falha += f"Sua rede ativou {len(self.mst_construida_jogador)} conexões, mas {num_arestas_esperadas_mst} eram necessárias para conectar todos os postos sem redundância.\n"
            if self.erros_ciclo > 1:
                msg_falha += f"Você cometeu {self.erros_ciclo} erros na detecção de ciclos, o que pode ter levado a uma rede ineficiente ou incompleta."
            messagebox.showerror("Falha no Minigame Kruskal", msg_falha)
            self.game_manager.handle_minigame_rpg_result(False, self.id_escolha_rpg)

    def dar_dica_kruskal(self):
        self.dicas_usadas += 1
        dica_texto = ""
        # ... (Textos das dicas como antes) ...
        if self.dicas_usadas == 1:
            dica_texto = ("DICA 1: O Algoritmo de Kruskal constrói a Árvore Geradora Mínima (MST) adicionando arestas (conexões) uma por uma. "
                          "Comece sempre pela conexão de MENOR CUSTO que ainda não foi considerada.")
        elif self.dicas_usadas == 2 and self.indice_aresta_atual < len(self.arestas_ordenadas):
            aresta_data = self.arestas_ordenadas[self.indice_aresta_atual]
            u, v, _ = aresta_data['u'], aresta_data['v'], aresta_data['custo']
            # Simula a verificação de ciclo para a dica
            uf_temp = UnionFind(list(self.postos_taticos))
            for mst_aresta in self.mst_construida_jogador:
                uf_temp.union(mst_aresta['u'], mst_aresta['v'])
            conectados = uf_temp.conectados(u,v)

            dica_texto = (f"DICA 2: Para a conexão atual ({u}-{v}), pergunte-se: '{u}' e '{v}' já estão conectados através da 'Rede Ativada' que você construiu até agora? "
                          f"Se sim, adicionar esta conexão formaria um ciclo e deve ser evitada.\n"
                          f"(Análise interna para esta conexão: Eles {'JÁ ESTÃO' if conectados else 'NÃO ESTÃO'} conectados por outras arestas na sua MST parcial).")
        else:
            dica_texto = "DICA EXTRA: Mantenha o foco! Ordene por custo. Evite ciclos. Conecte todos os postos com o menor custo total."
        
        messagebox.showinfo("Dica - Rede Kruskal", dica_texto)
        if self.dicas_usadas >= 2 and self.btn_dica_kruskal and self.btn_dica_kruskal.winfo_exists():
            self.btn_dica_kruskal.config(state=tk.DISABLED)
            
    def retry_mission(self): 
        print(f"MinigameKruskal: retry_mission chamada para {self.id_escolha_rpg}")
        self.iniciar_minigame_interface() # Reinicia a UI e o estado do minigame