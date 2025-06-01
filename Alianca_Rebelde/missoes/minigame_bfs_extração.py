import tkinter as tk
from tkinter import ttk, messagebox
from collections import deque # Para a fila do BFS

class MinigameBFSExtracao:
    def __init__(self, root, game_manager, content_frame, recompensa_sucesso, id_escolha_rpg):
        self.root = root
        self.game_manager = game_manager
        self.base_content_frame = content_frame
        self.recompensa_sucesso = recompensa_sucesso
        self.id_escolha_rpg = id_escolha_rpg

        self.grafo_mapa = {
            'Posto Avançado Alpha': ['Corredor Norte', 'Duto de Ventilação Leste'],
            'Corredor Norte': ['Posto Avançado Alpha', 'Sala de Controle', 'Arsenal'],
            'Duto de Ventilação Leste': ['Posto Avançado Alpha', 'Arsenal'],
            'Sala de Controle': ['Corredor Norte', 'Ponto de Extração Sierra'],
            'Arsenal': ['Corredor Norte', 'Duto de Ventilação Leste', 'Ponto de Extração Sierra'],
            'Ponto de Extração Sierra': ['Sala de Controle', 'Arsenal'] 
        }
        self.ponto_inicial = 'Posto Avançado Alpha'
        self.ponto_final = 'Ponto de Extração Sierra'
        
        # Estado do BFS
        self.fila_bfs = None
        self.visitados = None
        self.pais_bfs = None
        self.caminho_encontrado_jogador = None
        self.dicas_usadas = 0
        self.camada_atual_num = 0

        # Referências de UI
        self.info_label = None
        self.fila_label = None
        self.visitados_label = None
        self.camada_info_label = None 
        self.btn_proxima_etapa = None
        self.btn_dica_minigame = None

    def _clear_minigame_frame(self):
        if self.base_content_frame and self.base_content_frame.winfo_exists():
            for widget in self.base_content_frame.winfo_children():
                widget.destroy()

    def _reset_estado_bfs(self):
        self.camada_atual_num = 0
        self.fila_bfs = deque([(self.ponto_inicial, [self.ponto_inicial])]) # (nó, caminho_até_ele)
        self.visitados = {self.ponto_inicial}
        self.caminho_encontrado_jogador = None
        self.dicas_usadas = 0


    def iniciar_minigame_interface(self):
        self._clear_minigame_frame()
        self._reset_estado_bfs() # Reseta o estado do BFS

        title_label = ttk.Label(self.base_content_frame, text="Minigame: Rota de Extração (BFS)", font=self.game_manager.header_font)
        title_label.pack(pady=10)

        narrativa_inicial = (
            f"Comandante, a Patrulha Eco está no '{self.ponto_inicial}'. O resgate será no '{self.ponto_final}'.\n"
            "Precisamos encontrar a rota com o menor número de paradas (setores) intermediários.\n"
            "Use a Busca em Largura (BFS) para explorar o mapa camada por camada."
        )
        ttk.Label(self.base_content_frame, text=narrativa_inicial, wraplength=700, justify=tk.CENTER, font=self.game_manager.narrative_font).pack(pady=10)

        info_bfs_frame = ttk.Frame(self.base_content_frame, padding=5)
        info_bfs_frame.pack(pady=10, fill=tk.X)

        self.camada_info_label = ttk.Label(info_bfs_frame, text="", font=self.game_manager.small_bold_font)
        self.camada_info_label.pack(anchor="w")
        self.fila_label = ttk.Label(info_bfs_frame, text="", font=self.game_manager.small_bold_font)
        self.fila_label.pack(anchor="w")
        self.visitados_label = ttk.Label(info_bfs_frame, text="", font=self.game_manager.small_bold_font)
        self.visitados_label.pack(anchor="w")
        
        self.info_label = ttk.Label(self.base_content_frame, text="", font=self.game_manager.narrative_font, wraplength=700, justify=tk.CENTER)
        self.info_label.pack(pady=10)
        
        action_frame_minigame = ttk.Frame(self.base_content_frame)
        action_frame_minigame.pack(pady=20, fill=tk.X)

        self.btn_dica_minigame = ttk.Button(action_frame_minigame, text="Pedir Dica (Como funciona o BFS?)", command=self.dar_dica_bfs)
        self.btn_dica_minigame.pack(side=tk.LEFT, padx=10)
        
        self.btn_proxima_etapa = ttk.Button(action_frame_minigame, text="Iniciar Exploração BFS", command=self.proxima_etapa_bfs, style="Accent.TButton")
        self.btn_proxima_etapa.pack(side=tk.RIGHT, padx=10)

        self.atualizar_display_estado_bfs()

    def atualizar_display_estado_bfs(self, mensagem_info_principal=""):
        # Atualiza as labels de Fila e Visitados
        nos_na_fila_para_display = [item[0] for item in self.fila_bfs] # Mostra apenas os nós, não os caminhos
        self.fila_label.config(text=f"Fila de Exploração (BFS): {nos_na_fila_para_display}")
        self.visitados_label.config(text=f"Locais Já Visitados: {', '.join(sorted(list(self.visitados)))}")
        self.camada_info_label.config(text=f"Profundidade/Camada Atual (nós na fila): {self.camada_atual_num}")


        # Lógica para o botão principal e a mensagem de informação
        if not self.fila_bfs: # Fila vazia
            if self.ponto_final in self.visitados and self.caminho_encontrado_jogador: # Já achou e processou
                 self.info_label.config(text=f"Ponto de extração alcançado! Rota: {' -> '.join(self.caminho_encontrado_jogador)}")
                 self.btn_proxima_etapa.config(text="Confirmar Rota (Sucesso)", command=self.finalizar_minigame_bfs_sucesso)
            else:
                self.info_label.config(text="Fila de exploração vazia e ponto de extração não alcançado.")
                self.btn_proxima_etapa.config(text="Finalizar (Falha na Rota)", command=self.finalizar_minigame_bfs_falha)
            return
        
        # Se a fila não está vazia
        no_a_expandir, _ = self.fila_bfs[0]
        if mensagem_info_principal:
            self.info_label.config(text=mensagem_info_principal)
        else:
            self.info_label.config(text=f"Próximo local a ser expandido da fila: '{no_a_expandir}'.\nVamos identificar seus vizinhos não visitados.")
        
        self.btn_proxima_etapa.config(text=f"Expandir '{no_a_expandir}'", command=self.proxima_etapa_bfs)


    def proxima_etapa_bfs(self):
        if not self.fila_bfs:
            if self.ponto_final in self.visitados and self.caminho_encontrado_jogador:
                self.finalizar_minigame_bfs_sucesso()
            else:
                self.finalizar_minigame_bfs_falha()
            return

        no_atual, caminho_ate_no_atual = self.fila_bfs.popleft()
        self.camada_atual_num = len(caminho_ate_no_atual) -1 

        mensagem_etapa = f"Expandindo '{no_atual}' (Camada {self.camada_atual_num}). Vizinhos: {', '.join(self.grafo_mapa.get(no_atual, []))}\n"
        novos_adicionados_fila = []

        for vizinho in self.grafo_mapa.get(no_atual, []):
            if vizinho not in self.visitados:
                self.visitados.add(vizinho)
                novo_caminho = caminho_ate_no_atual + [vizinho]
                self.fila_bfs.append((vizinho, novo_caminho))
                novos_adicionados_fila.append(vizinho)
                
                if vizinho == self.ponto_final:
                    self.caminho_encontrado_jogador = novo_caminho
                    mensagem_etapa += f"Ponto de Extração '{self.ponto_final}' alcançado! Rota: {' -> '.join(self.caminho_encontrado_jogador)}."
                    self.atualizar_display_estado_bfs(mensagem_etapa)
                    self.btn_proxima_etapa.config(text="Confirmar Rota Encontrada!", command=self.finalizar_minigame_bfs_sucesso)
                    return 

        if novos_adicionados_fila:
            mensagem_etapa += f"Vizinhos não visitados adicionados à fila: {', '.join(novos_adicionados_fila)}."
        else:
            mensagem_etapa += "Nenhum vizinho novo (não visitado) encontrado para adicionar à fila."
        
        self.atualizar_display_estado_bfs(mensagem_etapa)


    def finalizar_minigame_bfs_sucesso(self):
        if self.caminho_encontrado_jogador:
            msg = (f"Rota de extração encontrada e confirmada!\n"
                   f"Caminho: {' -> '.join(self.caminho_encontrado_jogador)}\n"
                   f"Número de etapas: {len(self.caminho_encontrado_jogador) - 1}\n\n"
                   "Você guiou a Patrulha Eco com sucesso!")
            messagebox.showinfo("Sucesso no Minigame!", msg)
            self.game_manager.handle_minigame_rpg_result(True, self.id_escolha_rpg, self.recompensa_sucesso)
        else: 
            # Fallback, caso seja chamado indevidamente sem um caminho
            self.finalizar_minigame_bfs_falha("Erro interno: Sucesso chamado sem rota definida.")


    def finalizar_minigame_bfs_falha(self, mensagem_adicional=""):
        msg_falha = "Não foi possível encontrar uma rota ótima para o ponto de extração ou a exploração falhou."
        if mensagem_adicional:
            msg_falha += "\n" + mensagem_adicional
        messagebox.showerror("Falha no Minigame de Rota", msg_falha)
        self.game_manager.handle_minigame_rpg_result(False, self.id_escolha_rpg)

    def dar_dica_bfs(self):
        self.dicas_usadas += 1
        dica_texto = ""
        if self.dicas_usadas == 1:
            dica_texto = ("DICA 1: O BFS (Busca em Largura) explora o grafo camada por camada. "
                          "Ele usa uma FILA (Primeiro que Entra, Primeiro que Sai) para controlar os locais a visitar.\n"
                          "Comece com o local inicial na fila. A cada etapa, pegue o primeiro da fila, "
                          "adicione todos os seus vizinhos (que ainda não foram visitados) ao FIM da fila.")
        elif self.dicas_usadas == 2:
            dica_texto = ("DICA 2: Continue o processo até que o Ponto de Extração seja o próximo a sair da fila, ou até a fila ficar vazia. "
                          "O BFS garante que o primeiro caminho encontrado para o destino é um dos mais curtos (em número de 'saltos').")
        else:
            dica_texto = "DICA EXTRA: Observe a 'Fila de Exploração' e os 'Locais Já Visitados' para decidir seu próximo movimento conceitual. O jogo automatiza a expansão quando você clica no botão."
        
        messagebox.showinfo("Dica - Rota BFS", dica_texto)
        if self.dicas_usadas >= 2 and self.btn_dica_minigame and self.btn_dica_minigame.winfo_exists():
            self.btn_dica_minigame.config(state=tk.DISABLED)
            
    def retry_mission(self): 
        self.iniciar_minigame_interface() 