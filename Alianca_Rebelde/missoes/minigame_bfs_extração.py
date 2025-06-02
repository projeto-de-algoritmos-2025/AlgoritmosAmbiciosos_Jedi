# missoes/minigame_bfs_extração.py
import tkinter as tk
from tkinter import ttk, messagebox, font as tkFont 
from collections import deque # Para a fila do BFS
# Se você tiver o algoritmo BFS em um arquivo separado e quiser usá-lo para referência/validação:
# from algoritmos.grafo_bfs import bfs_caminho_mais_curto 

class MinigameBFSExtracao:
    def __init__(self, root, game_manager, content_frame, recompensa_sucesso, id_escolha_rpg):
        self.root = root
        self.game_manager = game_manager
        self.base_content_frame = content_frame # Este já é um ttk.Frame com estilo "Black.TFrame" do GameManager
        self.recompensa_sucesso = recompensa_sucesso
        self.id_escolha_rpg = id_escolha_rpg

        # Cores do tema escuro (herdadas do GameManager)
        try:
            self.cor_fundo_minigame = self.game_manager.bg_color_dark
            self.cor_texto_narrativa = self.game_manager.fg_color_light
            self.cor_titulo_minigame_bfs = self.game_manager.title_color_accent # CORRIGIDO: Nome consistente
            self.cor_texto_info_bfs = "#B0E0E6" # Um azul claro (PowderBlue) para infos do BFS
        except AttributeError:
            print("AVISO MinigameBFS: Cores do GameManager não encontradas. Usando fallbacks.")
            self.cor_fundo_minigame = "black"
            self.cor_texto_narrativa = "white"
            self.cor_titulo_minigame_bfs = "orangered" # Fallback
            self.cor_texto_info_bfs = "lightblue"

        # Fontes (herdadas do GameManager)
        try:
            self.header_font_obj = self.game_manager.header_font_obj
            self.narrative_font_obj = self.game_manager.narrative_font_obj
            self.button_font_obj = self.game_manager.button_font_obj
            self.small_bold_font_obj = self.game_manager.small_bold_font_obj
        except AttributeError:
            print("AVISO MinigameBFS: Fontes do GameManager não encontradas. Usando fallbacks.")
            default_family_fallback = "Arial"
            self.header_font_obj = tkFont.Font(family=default_family_fallback, size=18, weight="bold") 
            self.narrative_font_obj = tkFont.Font(family=default_family_fallback, size=11)
            self.button_font_obj = tkFont.Font(family=default_family_fallback, size=10, weight="bold")
            self.small_bold_font_obj = tkFont.Font(family=default_family_fallback, size=9, weight="bold")


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
        # self.pais_bfs = None # Removido pois o caminho está na fila
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
        self._reset_estado_bfs() 

        # Título do Minigame
        title_label = tk.Label(self.base_content_frame, text="Minigame: Rota de Extração (BFS)", 
                               font=self.header_font_obj, 
                               fg=self.cor_titulo_minigame_bfs, # <<< USA A VARIÁVEL CORRETA
                               bg=self.cor_fundo_minigame)
        title_label.pack(pady=(0,15), fill=tk.X, padx=20)

        narrativa_inicial = (
            f"Comandante, a Patrulha Eco está no '{self.ponto_inicial}'. O resgate será no '{self.ponto_final}'.\n"
            "Precisamos encontrar a rota com o menor número de paradas (setores) intermediários.\n"
            "Use a Busca em Largura (BFS) para explorar o mapa camada por camada, seguindo as instruções."
        )
        narrativa_label = tk.Label(self.base_content_frame, text=narrativa_inicial, 
                                   wraplength=700, justify=tk.CENTER, 
                                   font=self.narrative_font_obj, 
                                   fg=self.cor_texto_narrativa, 
                                   bg=self.cor_fundo_minigame)
        narrativa_label.pack(pady=10, padx=20)

        # --- Área de Informações do BFS ---
        info_bfs_container = tk.Frame(self.base_content_frame, bg=self.cor_fundo_minigame, pady=5)
        info_bfs_container.pack(pady=10, fill=tk.X, padx=20)

        self.camada_info_label = tk.Label(info_bfs_container, text="", font=self.small_bold_font_obj, 
                                          fg=self.cor_texto_info_bfs, bg=self.cor_fundo_minigame, justify=tk.LEFT)
        self.camada_info_label.pack(anchor="w")
        self.fila_label = tk.Label(info_bfs_container, text="", font=self.small_bold_font_obj, 
                                   fg=self.cor_texto_info_bfs, bg=self.cor_fundo_minigame, justify=tk.LEFT)
        self.fila_label.pack(anchor="w")
        self.visitados_label = tk.Label(info_bfs_container, text="", font=self.small_bold_font_obj, 
                                        fg=self.cor_texto_info_bfs, bg=self.cor_fundo_minigame, justify=tk.LEFT)
        self.visitados_label.pack(anchor="w")
        
        # --- Área de Interação Principal ---
        self.info_label = tk.Label(self.base_content_frame, text="", 
                                   font=self.narrative_font_obj, wraplength=700, justify=tk.CENTER,
                                   fg=self.cor_texto_narrativa, bg=self.cor_fundo_minigame)
        self.info_label.pack(pady=10, padx=20)
        
        # --- Botões de Ação do Minigame ---
        action_frame_minigame = ttk.Frame(self.base_content_frame, style="Black.TFrame")
        action_frame_minigame.pack(pady=15, fill=tk.X, padx=20)

        self.btn_dica_minigame = ttk.Button(action_frame_minigame, text="Pedir Dica (BFS)", 
                                            command=self.dar_dica_bfs, style="Dark.TButton")
        self.btn_dica_minigame.pack(side=tk.LEFT, padx=(0,10))
        
        self.btn_proxima_etapa = ttk.Button(action_frame_minigame, text="Iniciar Exploração BFS", 
                                            command=self.proxima_etapa_bfs, style="Accent.Dark.TButton")
        self.btn_proxima_etapa.pack(side=tk.RIGHT)

        self.atualizar_display_estado_bfs()

    def atualizar_display_estado_bfs(self, mensagem_info_principal=""):
        if not (hasattr(self, 'fila_label') and self.fila_label and self.fila_label.winfo_exists()): # Checagem de segurança
            return 

        nos_na_fila_para_display = [item[0] for item in self.fila_bfs] 
        self.fila_label.config(text=f"Fila de Exploração: {nos_na_fila_para_display}")
        self.visitados_label.config(text=f"Locais Visitados: {', '.join(sorted(list(self.visitados)))}")
        self.camada_info_label.config(text=f"Profundidade/Camada Atual (da expansão): {self.camada_atual_num}")

        if not self.btn_proxima_etapa or not self.btn_proxima_etapa.winfo_exists(): return # Botão pode não existir ainda

        if not self.fila_bfs: 
            if self.ponto_final in self.visitados and self.caminho_encontrado_jogador:
                 self.info_label.config(text=f"Ponto de extração alcançado! Rota: {' -> '.join(self.caminho_encontrado_jogador)}")
                 self.btn_proxima_etapa.config(text="Confirmar Rota (Sucesso)", command=self.finalizar_minigame_bfs_sucesso, style="Accent.Dark.TButton")
            else: 
                self.info_label.config(text="Fila de exploração vazia e ponto de extração não alcançado.")
                self.btn_proxima_etapa.config(text="Finalizar (Falha na Rota)", command=self.finalizar_minigame_bfs_falha, style="Dark.TButton")
            return
        
        no_a_expandir, _ = self.fila_bfs[0]
        if mensagem_info_principal:
            self.info_label.config(text=mensagem_info_principal)
        else:
            self.info_label.config(text=f"Próximo local a ser expandido da fila: '{no_a_expandir}'.\nClique em 'Expandir' para processá-lo.")
        
        self.btn_proxima_etapa.config(text=f"Expandir '{no_a_expandir}'", command=self.proxima_etapa_bfs, style="Accent.Dark.TButton")


    def proxima_etapa_bfs(self):
        if not self.fila_bfs:
            if self.ponto_final in self.visitados and self.caminho_encontrado_jogador:
                self.finalizar_minigame_bfs_sucesso()
            else:
                self.finalizar_minigame_bfs_falha()
            return

        no_atual, caminho_ate_no_atual = self.fila_bfs.popleft()
        self.camada_atual_num = len(caminho_ate_no_atual) - 1 

        mensagem_etapa = f"Expandindo '{no_atual}' (na profundidade {self.camada_atual_num}).\nVizinhos diretos: {', '.join(self.grafo_mapa.get(no_atual, []))}\n"
        novos_adicionados_fila = []

        for vizinho in self.grafo_mapa.get(no_atual, []):
            if vizinho not in self.visitados:
                self.visitados.add(vizinho)
                novo_caminho = caminho_ate_no_atual + [vizinho]
                self.fila_bfs.append((vizinho, novo_caminho))
                novos_adicionados_fila.append(vizinho)
                
                if vizinho == self.ponto_final:
                    self.caminho_encontrado_jogador = novo_caminho # Armazena o caminho encontrado
                    mensagem_etapa += f"Ponto de Extração '{self.ponto_final}' alcançado! Rota: {' -> '.join(self.caminho_encontrado_jogador)}."
                    self.atualizar_display_estado_bfs(mensagem_etapa) # Atualiza o display com a mensagem
                    if self.btn_proxima_etapa and self.btn_proxima_etapa.winfo_exists(): # Verifica se o botão ainda existe
                        self.btn_proxima_etapa.config(text="Confirmar Rota Encontrada!", command=self.finalizar_minigame_bfs_sucesso, style="Accent.Dark.TButton")
                    return 

        if novos_adicionados_fila:
            mensagem_etapa += f"Vizinhos não visitados ('{', '.join(novos_adicionados_fila)}') foram adicionados ao fim da fila."
        else:
            mensagem_etapa += f"Nenhum vizinho novo (não visitado) encontrado a partir de '{no_atual}'."
        
        self.atualizar_display_estado_bfs(mensagem_etapa)


    def finalizar_minigame_bfs_sucesso(self):
        if self.caminho_encontrado_jogador:
            msg = (f"Rota de extração encontrada e confirmada!\n"
                   f"Caminho: {' -> '.join(self.caminho_encontrado_jogador)}\n"
                   f"Número de etapas: {len(self.caminho_encontrado_jogador) - 1}\n\n"
                   "Você guiou a Patrulha Eco com sucesso, Comandante!")
            messagebox.showinfo("Sucesso no Minigame!", msg)
            self.game_manager.handle_minigame_rpg_result(True, self.id_escolha_rpg, self.recompensa_sucesso)
        else: 
            self.finalizar_minigame_bfs_falha("Erro interno: Sucesso chamado sem rota definida.")


    def finalizar_minigame_bfs_falha(self, mensagem_adicional=""):
        msg_falha = "Não foi possível encontrar uma rota para o ponto de extração ou a exploração não foi ótima."
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
        print(f"MinigameBFS: retry_mission chamada para {self.id_escolha_rpg}")
        self.iniciar_minigame_interface()