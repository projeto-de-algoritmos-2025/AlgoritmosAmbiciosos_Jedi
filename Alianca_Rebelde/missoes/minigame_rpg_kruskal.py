import tkinter as tk
from tkinter import ttk, messagebox
from algoritmos.union_find import UnionFind # Importa a estrutura UnionFind

class MinigameKruskalContraAtaque:
    def __init__(self, root, game_manager, content_frame, recompensa_sucesso, id_escolha_rpg):
        self.root = root
        self.game_manager = game_manager
        self.base_content_frame = content_frame
        self.recompensa_sucesso = recompensa_sucesso
        self.id_escolha_rpg = id_escolha_rpg

        # Cenário: Conectar postos táticos para o contra-ataque
        self.postos_taticos = {'P1', 'P2', 'P3', 'CentralCom', 'TorreVigia'} # Nós do grafo
        self.conexoes_disponiveis = [ # Arestas: (no1, no2, custo)
            ('P1', 'P2', 10), ('P1', 'CentralCom', 5), ('P1', 'TorreVigia', 20),
            ('P2', 'CentralCom', 8), ('P2', 'P3', 12),
            ('P3', 'CentralCom', 6), ('P3', 'TorreVigia', 15),
            ('CentralCom', 'TorreVigia', 4)
        ]
        self.num_nos_objetivo = len(self.postos_taticos) # Número de nós que precisam estar conectados

        # Estado do algoritmo de Kruskal
        self.arestas_ordenadas = []
        self.indice_aresta_atual = 0
        self.mst_construida_jogador = [] 
        self.union_find_jogador = UnionFind(self.postos_taticos)
        self.total_custo_jogador = 0
        self.dicas_usadas = 0
        self.erros_ciclo = 0 

        self.info_label = None
        self.aresta_atual_label = None
        self.mst_label = None
        self.custo_label = None
        self.btn_sim_ciclo = None
        self.btn_nao_ciclo = None
        self.btn_dica_kruskal = None

    def _clear_minigame_frame(self):
        if self.base_content_frame and self.base_content_frame.winfo_exists():
            for widget in self.base_content_frame.winfo_children():
                widget.destroy()

    def iniciar_minigame_interface(self):
        self._clear_minigame_frame()

        self.arestas_ordenadas = sorted(self.conexoes_disponiveis, key=lambda x: x[2])
        self.indice_aresta_atual = 0
        self.mst_construida_jogador = []
        self.union_find_jogador.reset(self.postos_taticos) 
        self.total_custo_jogador = 0
        self.dicas_usadas = 0
        self.erros_ciclo = 0

        title_label = ttk.Label(self.base_content_frame, text="Minigame: Rede de Contra-Ataque (Kruskal)", font=self.game_manager.header_font)
        title_label.pack(pady=10)

        narrativa_inicial = (
            "Comandante, para nosso contra-ataque ser eficaz, precisamos ativar uma rede de comunicação segura e de baixo custo entre nossos postos táticos.\n"
            "Use o Algoritmo de Kruskal: considere as conexões (arestas) da mais barata para a mais cara.\n"
            "Adicione uma conexão à rede APENAS SE ela NÃO FORMAR UM CICLO com as conexões já existentes."
        )
        ttk.Label(self.base_content_frame, text=narrativa_inicial, wraplength=700, justify=tk.CENTER, font=self.game_manager.narrative_font).pack(pady=10)

        # --- Display do Estado do Algoritmo ---
        estado_frame = ttk.Frame(self.base_content_frame, padding=5)
        estado_frame.pack(pady=10, fill=tk.X)

        self.aresta_atual_label = ttk.Label(estado_frame, text="", font=self.game_manager.small_bold_font)
        self.aresta_atual_label.pack(anchor="w")
        self.mst_label = ttk.Label(estado_frame, text="Rede Ativada (MST): Nenhuma", font=self.game_manager.small_bold_font, wraplength=700)
        self.mst_label.pack(anchor="w")
        self.custo_label = ttk.Label(estado_frame, text="Custo Total da Rede: 0", font=self.game_manager.small_bold_font)
        self.custo_label.pack(anchor="w")

        # --- Área de Interação Principal (Decisão sobre Ciclo) ---
        self.info_label = ttk.Label(self.base_content_frame, text="Aguardando sua análise...", font=self.game_manager.narrative_font)
        self.info_label.pack(pady=10)

        decisao_frame = ttk.Frame(self.base_content_frame)
        decisao_frame.pack(pady=10)
        self.btn_sim_ciclo = ttk.Button(decisao_frame, text="Sim (Forma Ciclo - Descartar)", command=lambda: self.processar_decisao_jogador(True))
        self.btn_sim_ciclo.pack(side=tk.LEFT, padx=10)
        self.btn_nao_ciclo = ttk.Button(decisao_frame, text="Não (Não Forma Ciclo - Adicionar)", command=lambda: self.processar_decisao_jogador(False), style="Accent.TButton")
        self.btn_nao_ciclo.pack(side=tk.LEFT, padx=10)
        
        # --- Botão de Dica ---
        self.btn_dica_kruskal = ttk.Button(self.base_content_frame, text="Pedir Dica (Kruskal)", command=self.dar_dica_kruskal)
        self.btn_dica_kruskal.pack(pady=15)

        self.apresentar_proxima_aresta()

    def apresentar_proxima_aresta(self):
        if self.indice_aresta_atual >= len(self.arestas_ordenadas) or len(self.mst_construida_jogador) >= self.num_nos_objetivo - 1:
            self.finalizar_minigame()
            return

        aresta = self.arestas_ordenadas[self.indice_aresta_atual]
        u, v, custo = aresta
        self.aresta_atual_label.config(text=f"Considerando conexão: {u} <-> {v} (Custo: {custo})")
        self.info_label.config(text=f"Adicionar a conexão ({u}-{v}) formaria um ciclo na rede atual?")
        
        # Habilita botões de decisão
        self.btn_sim_ciclo.config(state=tk.NORMAL)
        self.btn_nao_ciclo.config(state=tk.NORMAL)

    def processar_decisao_jogador(self, jogador_acha_que_forma_ciclo):
        aresta = self.arestas_ordenadas[self.indice_aresta_atual]
        u, v, custo = aresta

        # Verifica a realidade (usando Union-Find)
        realmente_forma_ciclo = self.union_find_jogador.conectados(u, v)

        if jogador_acha_que_forma_ciclo == realmente_forma_ciclo:
            messagebox.showinfo("Análise Correta!", "Sua análise sobre o ciclo está correta.")
            if not realmente_forma_ciclo: # Se não forma ciclo (e o jogador acertou dizendo não), adiciona à MST
                self.union_find_jogador.union(u, v)
                self.mst_construida_jogador.append(aresta)
                self.total_custo_jogador += custo
                self.mst_label.config(text=f"Rede Ativada (MST): {self.formatar_mst_string()}")
                self.custo_label.config(text=f"Custo Total da Rede: {self.total_custo_jogador}")
        else:
            self.erros_ciclo += 1
            feedback_erro = "Análise Incorreta! "
            if realmente_forma_ciclo: # Jogador disse NÃO, mas formava
                feedback_erro += f"Adicionar ({u}-{v}) TERIA formado um ciclo, pois já existe um caminho entre eles."
            else: # Jogador disse SIM, mas não formava
                feedback_erro += f"Adicionar ({u}-{v}) NÃO formaria um ciclo. Era seguro adicionar."
            messagebox.showwarning("Erro na Análise", feedback_erro + f"\nVocê cometeu {self.erros_ciclo} erro(s) na detecção de ciclo.")

        self.indice_aresta_atual += 1
        self.apresentar_proxima_aresta()

    def formatar_mst_string(self):
        if not self.mst_construida_jogador:
            return "Nenhuma"
        return ", ".join([f"({a[0]}-{a[1]} C:{a[2]})" for a in self.mst_construida_jogador])


    def finalizar_minigame(self):
        # Desabilita botões de decisão
        self.btn_sim_ciclo.config(state=tk.DISABLED)
        self.btn_nao_ciclo.config(state=tk.DISABLED)
        if self.btn_dica_kruskal and self.btn_dica_kruskal.winfo_exists():
            self.btn_dica_kruskal.config(state=tk.DISABLED)
        
        num_arestas_esperadas = self.num_nos_objetivo - 1
        sucesso = (len(self.mst_construida_jogador) == num_arestas_esperadas and self.erros_ciclo <= 1) 

        if sucesso:
            msg = (f"Rede de Contra-Ataque estabelecida com sucesso!\n"
                   f"Conexões Ativadas: {len(self.mst_construida_jogador)}\n"
                   f"Custo Total da Rede: {self.total_custo_jogador}\n"
                   "Sua precisão foi fundamental, Comandante!")
            messagebox.showinfo("Sucesso no Minigame!", msg)
            self.game_manager.handle_minigame_rpg_result(True, self.id_escolha_rpg, self.recompensa_sucesso)
        else:
            msg_falha = "Falha ao estabelecer a Rede de Contra-Ataque.\n"
            if len(self.mst_construida_jogador) != num_arestas_esperadas:
                msg_falha += f"A rede formada não conectou todos os postos corretamente (esperadas {num_arestas_esperadas} conexões, você ativou {len(self.mst_construida_jogador)}).\n"
            if self.erros_ciclo > 1:
                msg_falha += f"Você cometeu {self.erros_ciclo} erros na detecção de ciclos, comprometendo a eficiência da rede."
            messagebox.showerror("Falha no Minigame", msg_falha)
            self.game_manager.handle_minigame_rpg_result(False, self.id_escolha_rpg)

    def dar_dica_kruskal(self):
        self.dicas_usadas += 1
        dica_texto = ""
        if self.dicas_usadas == 1:
            dica_texto = ("DICA 1: Kruskal constrói a Árvore Geradora Mínima (MST) adicionando arestas uma por uma, "
                          "sempre a de MENOR CUSTO primeiro, DESDE QUE não forme um ciclo com as arestas já escolhidas.")
        elif self.dicas_usadas == 2:
            aresta = self.arestas_ordenadas[self.indice_aresta_atual]
            u, v, _ = aresta
            conectados = self.union_find_jogador.conectados(u,v)
            dica_texto = (f"DICA 2: Para a aresta atual ({u}-{v}), verifique se já existe um caminho entre '{u}' e '{v}' "
                          f"usando as conexões já na sua 'Rede Ativada'.\n"
                          f"(Análise interna: '{u}' e '{v}' atualmente {'ESTÃO' if conectados else 'NÃO ESTÃO'} no mesmo componente conectado).")
        else:
            dica_texto = "DICA EXTRA: Continue considerando as arestas em ordem de custo. Se uma aresta conecta dois componentes já unidos, ela forma um ciclo e deve ser descartada."
        
        messagebox.showinfo("Dica - Kruskal", dica_texto)
        if self.dicas_usadas >= 2 and self.btn_dica_kruskal and self.btn_dica_kruskal.winfo_exists():
            self.btn_dica_kruskal.config(state=tk.DISABLED)
            
    def retry_mission(self): 
        self.iniciar_minigame_interface() 
