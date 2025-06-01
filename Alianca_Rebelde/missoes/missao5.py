import tkinter as tk
from tkinter import ttk, messagebox, font as tkFont
import heapq 

from algoritmos.interval_partitioning import calcular_interval_partitioning_otimo

class Missao5:
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
        self.btn_dica_m5 = None

    def _clear_mission_frame(self):
        if self.base_content_frame and self.base_content_frame.winfo_exists():
            for widget in self.base_content_frame.winfo_children():
                widget.destroy()

    def limpar_interface_missao_completa(self):
        self._clear_mission_frame()

    def _reset_mission_state(self):
        self.janelas_vigilancia_base = list(self.janelas_vigilancia_base_original) # Recarrega
        self.janelas_ordenadas_para_processar = []
        self.atribuicoes_jogador = {} # {nome_janela: id_esquadrao}
        self.esquadroes_em_uso_heap_jogador = [] # Min-heap: (tempo_fim, id_esquadrao)
        self.num_esquadroes_jogador = 0
        self.primeira_falha_nesta_tentativa_m5 = True
        self.dica_count_m5 = 0
        self.estrategia_ordenacao_escolhida_m5_nome = None

    def iniciar_missao_contexto(self):
        self._clear_mission_frame()
        self._reset_mission_state()
        
        ttk.Label(self.base_content_frame, text="MISSÃO 5: Olhos no Setor Bryx", font=self.header_font).pack(pady=10)
        context_text = (
            "Fulcrum: \"Comandante, sua coordenação em Kessel foi vital. Agora, uma nova frente se abre. "
            "O Império está discretamente expandindo sua rede de sensores e patrulhas no Setor Bryx, uma área que acreditávamos ser de baixa prioridade para eles. "
            "Isso pode indicar uma nova rota de abastecimento imperial ou a preparação para uma ofensiva surpresa.\n\n"
            "Precisamos de vigilância constante sobre múltiplas 'janelas de tempo' para monitorar essas movimentações. Nossos recursos de patrulha (esquadrões de reconhecimento e droides sonda) são escassos.\n"
            "Sua missão: Atribuir o MENOR NÚMERO POSSÍVEL de esquadrões para cobrir todas as janelas de vigilância necessárias. Um esquadrão pode iniciar uma nova tarefa assim que a anterior for concluída.\""
        )
        text_widget = tk.Text(self.base_content_frame, wrap=tk.WORD, height=12, relief=tk.FLAT, 
                              background=self.root.cget('bg'), font=self.narrative_font, padx=10, pady=10)
        text_widget.insert(tk.END, context_text)
        text_widget.config(state=tk.DISABLED)
        text_widget.pack(pady=15, padx=10, fill=tk.X)
        ttk.Button(self.base_content_frame, text="Analisar Janelas de Vigilância...",
                   command=self.iniciar_etapa_ordenacao_m5, style="Accent.TButton").pack(pady=20)

    def iniciar_etapa_ordenacao_m5(self):
        self._clear_mission_frame()
        
        ttk.Label(self.base_content_frame, text="Etapa 1: Estratégia de Ordenação (Interval Partitioning)", font=self.button_font).pack(pady=10)
        
        info_janelas_str = "JANELAS DE VIGILÂNCIA REQUERIDAS (Nome | Início | Fim):\n"
        for jv in sorted(self.janelas_vigilancia_base, key=lambda x: x['nome']):
            info_janelas_str += f"- {jv['nome']} (Início: {jv['inicio']}, Fim: {jv['fim']})\n"
        
        ttk.Label(self.base_content_frame, text=info_janelas_str, justify=tk.LEFT, font=self.item_font).pack(pady=10, anchor="w", padx=20)
        
        instrucoes_texto = ("Comandante, a ordem em que consideramos estas janelas para atribuir esquadrões é crucial "
                            "para minimizar o número total de esquadrões que precisaremos mobilizar. Qual critério de ordenação você sugere?")
        ttk.Label(self.base_content_frame, text=instrucoes_texto, wraplength=700, justify=tk.CENTER, font=self.narrative_font).pack(pady=10)

        botoes_frame = ttk.Frame(self.base_content_frame)
        botoes_frame.pack(pady=10)

        opcoes = [
            ("Ordenar por Início da Vigilância (mais cedo primeiro)", lambda x: x['inicio'], "Início Mais Cedo"), # Correta
            ("Ordenar por Fim da Vigilância (mais cedo primeiro)", lambda x: x['fim'], "Fim Mais Cedo"),
            ("Ordenar por Duração (mais curta primeiro)", lambda x: x['fim'] - x['inicio'], "Duração Mais Curta")
        ]
        for texto_btn, sort_key_func, nome_curto_est in opcoes:
            btn = ttk.Button(botoes_frame, text=texto_btn, width=50,
                             command=lambda skf=sort_key_func, nome_est=nome_curto_est: self.processar_escolha_ordenacao_m5(skf, nome_est))
            btn.pack(pady=5)
        
        self.btn_dica_m5 = ttk.Button(botoes_frame, text="Pedir Conselho (Dica de Ordenação)", command=lambda: self.dar_dica_m5("ordenacao"))
        self.btn_dica_m5.pack(pady=10)

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
        # Reseta para a etapa de atribuição
        self.atribuicoes_jogador = {}
        self.esquadroes_em_uso_heap_jogador = [] # Min-heap: (tempo_fim, id_esquadrao)
        self.num_esquadroes_jogador = 0

        ttk.Label(self.base_content_frame, text="Etapa 2: Atribuição de Esquadrões de Vigilância", font=self.button_font).pack(pady=10)
        
        # --- Frames para layout ---
        top_info_frame = ttk.Frame(self.base_content_frame)
        top_info_frame.pack(fill=tk.X, pady=5, padx=10)
        self.esquadroes_status_label = ttk.Label(top_info_frame, text=f"Esquadrões Utilizados: {self.num_esquadroes_jogador}", font=self.status_label_font)
        self.esquadroes_status_label.pack(side=tk.LEFT, padx=5)

        listas_frame = ttk.Frame(self.base_content_frame)
        listas_frame.pack(fill=tk.BOTH, expand=True, pady=5, padx=10)

        pendentes_frame = ttk.LabelFrame(listas_frame, text=f"Janelas Pendentes (Ordem: {self.estrategia_ordenacao_escolhida_m5_nome})", padding=5)
        pendentes_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0,5))
        self.lista_janelas_pendentes_listbox = tk.Listbox(pendentes_frame, height=10, font=self.item_font, exportselection=False)
        self.lista_janelas_pendentes_listbox.pack(fill=tk.BOTH, expand=True)
        self._popular_lista_janelas_pendentes_ui()

        atrib_frame = ttk.LabelFrame(listas_frame, text="Atribuições de Esquadrões Realizadas", padding=5)
        atrib_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5,0))
        self.atribuicoes_listbox = tk.Listbox(atrib_frame, height=10, font=self.item_font)
        self.atribuicoes_listbox.pack(fill=tk.BOTH, expand=True)

        action_frame_bottom = ttk.Frame(self.base_content_frame)
        action_frame_bottom.pack(fill=tk.X, pady=(15,10), padx=10)

        self.btn_dica_m5_atribuicao = ttk.Button(action_frame_bottom, text="Pedir Dica (Atribuição)", command=lambda: self.dar_dica_m5("atribuicao"))
        self.btn_dica_m5_atribuicao.pack(side=tk.LEFT)
        
        self.btn_processar_janela = ttk.Button(action_frame_bottom, text="Processar Próxima Janela de Vigilância", 
                                              command=self.processar_proxima_janela_interativo, style="Accent.TButton")
        self.btn_processar_janela.pack(side=tk.RIGHT)
        
        if not self.janelas_ordenadas_para_processar: # Se a lista estiver vazia
             self._finalizar_atribuicao_m5()

    def _popular_lista_janelas_pendentes_ui(self):
        if not self.lista_janelas_pendentes_listbox or not self.lista_janelas_pendentes_listbox.winfo_exists(): return
        self.lista_janelas_pendentes_listbox.delete(0, tk.END)
        for idx, jv in enumerate(self.janelas_ordenadas_para_processar): # Mostra o que resta
            self.lista_janelas_pendentes_listbox.insert(tk.END, f"{idx+1}. {jv['nome']} (I:{jv['inicio']}, F:{jv['fim']})")

    def processar_proxima_janela_interativo(self):
        if not self.janelas_ordenadas_para_processar:
            self._finalizar_atribuicao_m5()
            return

        intervalo_atual = self.janelas_ordenadas_para_processar.pop(0) # Pega e remove o primeiro
        nome_janela = intervalo_atual['nome']
        inicio_janela = intervalo_atual['inicio']
        fim_janela = intervalo_atual['fim']
        
        id_esquadrao_atribuido = 0
        acao_realizada_texto = ""

        if self.esquadroes_em_uso_heap_jogador and self.esquadroes_em_uso_heap_jogador[0][0] <= inicio_janela:
            # Reutiliza um esquadrão
            _fim_recurso_anterior, id_recurso_reutilizado = heapq.heappop(self.esquadroes_em_uso_heap_jogador)
            self.atribuicoes_jogador[nome_janela] = id_recurso_reutilizado
            heapq.heappush(self.esquadroes_em_uso_heap_jogador, (fim_janela, id_recurso_reutilizado))
            id_esquadrao_atribuido = id_recurso_reutilizado
            acao_realizada_texto = f"Janela '{nome_janela}' (I:{inicio_janela}-F:{fim_janela}) atribuída ao Esquadrão {id_esquadrao_atribuido} (reutilizado, terminou tarefa anterior em {_fim_recurso_anterior})."
        else:
            # Aloca um novo esquadrão
            self.num_esquadroes_jogador += 1
            id_novo_recurso = self.num_esquadroes_jogador
            self.atribuicoes_jogador[nome_janela] = id_novo_recurso
            heapq.heappush(self.esquadroes_em_uso_heap_jogador, (fim_janela, id_novo_recurso))
            id_esquadrao_atribuido = id_novo_recurso
            acao_realizada_texto = f"Janela '{nome_janela}' (I:{inicio_janela}-F:{fim_janela}) atribuída ao NOVO Esquadrão {id_esquadrao_atribuido}."

        # Atualiza UI
        self.atribuicoes_listbox.insert(tk.END, f"{nome_janela} -> Esq. {id_esquadrao_atribuido}")
        self.atribuicoes_listbox.see(tk.END)
        self.esquadroes_status_label.config(text=f"Esquadrões Utilizados: {self.num_esquadroes_jogador}")
        self._popular_lista_janelas_pendentes_ui() 
        messagebox.showinfo("Atribuição Realizada", acao_realizada_texto)

        if not self.janelas_ordenadas_para_processar: 
            self._finalizar_atribuicao_m5()

    def _finalizar_atribuicao_m5(self):
        messagebox.showinfo("Planejamento de Vigilância Concluído", "Todas as janelas de vigilância foram cobertas. Vamos avaliar a eficiência da sua alocação de esquadrões.")
        if self.btn_processar_janela and self.btn_processar_janela.winfo_exists():
            self.btn_processar_janela.config(state=tk.NORMAL, text="Avaliar Alocação de Esquadrões")
            self.btn_processar_janela.config(command=self.avaliar_plano_final_m5)
        if self.btn_dica_m5_atribuicao and self.btn_dica_m5_atribuicao.winfo_exists():
            self.btn_dica_m5_atribuicao.config(state=tk.DISABLED)

    def avaliar_plano_final_m5(self):
        if hasattr(self, 'btn_processar_janela') and self.btn_processar_janela and self.btn_processar_janela.winfo_exists():
             self.btn_processar_janela.config(state=tk.DISABLED)
        if hasattr(self, 'btn_dica_m5_atribuicao') and self.btn_dica_m5_atribuicao and self.btn_dica_m5_atribuicao.winfo_exists():
            self.btn_dica_m5_atribuicao.config(state=tk.DISABLED)

        # Calcula a solução ótima usando os dados base originais e a ordenação correta (por início)
        intervalos_para_otimo = sorted(list(self.janelas_vigilancia_base_original), key=lambda x: x['inicio'])
        num_esquadroes_otimo, _ = calcular_interval_partitioning_otimo(intervalos_para_otimo)

        print(f"DEBUG M5: Esquadrões Jogador: {self.num_esquadroes_jogador}, Esquadrões Ótimo: {num_esquadroes_otimo}")
        print(f"DEBUG M5: Estratégia de Ordenação do Jogador: {self.estrategia_ordenacao_escolhida_m5_nome}")

        # Sucesso se o jogador usou o número ótimo de esquadrões
        if self.num_esquadroes_jogador == num_esquadroes_otimo:
            pontos_ganhos = 80 # Pontuação base para sucesso
            estrategia_correta = "Início Mais Cedo"
            if self.estrategia_ordenacao_escolhida_m5_nome != estrategia_correta:
                messagebox.showwarning("Resultado Inesperado",
                                       f"Comandante, você usou {self.num_esquadroes_jogador} esquadrões, que é o ótimo! "
                                       f"No entanto, sua estratégia de ordenação '{self.estrategia_ordenacao_escolhida_m5_nome}' não é a padrão ( '{estrategia_correta}'). "
                                       "Desta vez funcionou, mas para garantir a eficiência em todos os cenários, o protocolo é crucial.")
            else:
                 pontos_ganhos += 20 # Bônus por usar a estratégia correta e obter o ótimo
                 messagebox.showinfo("Alocação Perfeita!",
                                f"Excelente uso de recursos, Comandante! Você utilizou o mínimo de {self.num_esquadroes_jogador} esquadrões, seguindo a estratégia ótima.\n"
                                "Nossa vigilância no Setor Bryx será eficaz e discreta.")

            self.game_manager.add_score(pontos_ganhos)
            self.game_manager.mission_completed("Missao5")
        else: # Jogador usou mais esquadrões que o necessário
            if self.primeira_falha_nesta_tentativa_m5:
                self.game_manager.add_score(-50)
                messagebox.showwarning("Penalidade por Ineficiência", f"Comandante, sua alocação não foi a mais eficiente. Penalidade de 50 pontos aplicada.")
                self.primeira_falha_nesta_tentativa_m5 = False
            
            falha_msg1 = (f"Fulcrum (analítico): \"RZ-479, sua alocação para o Setor Bryx utilizou {self.num_esquadroes_jogador} esquadrões. "
                          f"Nossas simulações indicam que era possível cobrir todas as janelas com apenas {num_esquadroes_otimo} esquadrões.\n"
                          f"A estratégia de ordenação '{self.estrategia_ordenacao_escolhida_m5_nome}' que você aplicou não foi a ideal. "
                          "Essa diferença representa um desperdício de recursos que poderiam ser vitais em outra frente.\"")
            falha_msg2_criativa = ("Fulcrum: \"Comandante, cada esquadrão extra que mobilizamos desnecessariamente é um risco adicional de exposição e um dreno em nossos recursos já limitados. "
                                   "A eficiência não é apenas um objetivo, é sobrevivência para a Aliança. Precisamos otimizar cada decisão.\"")
            self.game_manager.mission_failed_options(self, falha_msg1, falha_msg2_criativa)

    def dar_dica_m5(self, etapa_dica):
        self.dica_count_m5 += 1
        dica_texto = ""
        
        if etapa_dica == "ordenacao":
            if self.dica_count_m5 == 1:
                dica_texto = ("DICA - Ordenação para Particionamento:\n"
                              "Comandante, para minimizar o número de 'salas' (ou esquadrões, no nosso caso) em que precisamos dividir os 'cursos' (janelas de vigilância), "
                              "a ordem em que consideramos as janelas é crucial. Pense em qual janela você deve tentar encaixar primeiro para maximizar a chance de reutilizar um esquadrão.")
            elif self.dica_count_m5 >= 2:
                dica_texto = ("DICA AVANÇADA - Ordenação por Início:\n"
                              "A estratégia gulosa padrão para Interval Partitioning é ordenar as janelas de vigilância pelo seu HORÁRIO DE INÍCIO (da mais cedo para a mais tarde). "
                              "Isso permite processar as tarefas sequencialmente e tomar decisões de alocação informadas.")
                if self.btn_dica_m5 and hasattr(self.btn_dica_m5, 'winfo_exists') and self.btn_dica_m5.winfo_exists(): # Verifica se o botão ainda existe
                    self.btn_dica_m5.config(text="Aplicar Ordenação por Início (Recomendado)", 
                                            command=self.forcar_ordenacao_inicio_com_dica)
        
        elif etapa_dica == "atribuicao":
            if self.dica_count_m5 <= 2: # Se as dicas de ordenação não foram todas usadas
                 dica_texto = ("DICA - Atribuição de Esquadrões:\n"
                               "Com as janelas ordenadas (idealmente por início), para cada uma:\n"
                               "1. Verifique se algum esquadrão já utilizado estará livre ANTES ou NO MOMENTO do início desta janela.\n"
                               "2. Se SIM, atribua a janela a um desses esquadrões (idealmente, o que ficou livre mais cedo).\n"
                               "3. Se NÃO, aloque um NOVO esquadrão para esta janela.")
            else: # Dica mais avançada ou repetida
                 dica_texto = ("DICA EXTRA - Min-Heap:\n"
                               "Para gerenciar eficientemente os esquadrões que ficam livres, uma estrutura de dados chamada 'min-heap' é frequentemente usada, "
                               "armazenando os horários de término dos esquadrões em uso. Isso permite encontrar rapidamente o esquadrão que termina sua tarefa atual mais cedo.")
            if self.btn_dica_m5_atribuicao and self.btn_dica_m5_atribuicao.winfo_exists():
                self.btn_dica_m5_atribuicao.config(state=tk.DISABLED)

        if dica_texto: messagebox.showinfo("Conselho Estratégico de Fulcrum", dica_texto)

    def forcar_ordenacao_inicio_com_dica(self):
        messagebox.showinfo("Estratégia Corrigida",
                            "Fulcrum: \"Decisão acertada, Comandante. A lista de janelas de vigilância será agora ordenada por 'Início Mais Cedo' para seu planejamento.\"")
        self.estrategia_ordenacao_escolhida_m5_nome = "Início Mais Cedo"
        self.janelas_ordenadas_para_processar = sorted(list(self.janelas_vigilancia_base), key=lambda x: x['inicio'])
        
        if self.btn_dica_m5 and hasattr(self.btn_dica_m5, 'winfo_exists') and self.btn_dica_m5.winfo_exists():
            self.btn_dica_m5.config(state=tk.DISABLED) 
        
        self.iniciar_etapa_atribuicao_m5() # Prossegue para a atribuição com a lista correta

    def retry_mission(self):
        self.game_manager.set_game_state("START_MISSION_5")
