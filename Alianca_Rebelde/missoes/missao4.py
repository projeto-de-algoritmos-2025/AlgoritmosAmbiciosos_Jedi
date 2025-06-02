import tkinter as tk
from tkinter import ttk, messagebox, font as tkFont
import random 
from algoritmos.scheduling_minimize_lateness import calcular_schedule_edf_e_lmax

class Missao4:
    def __init__(self, root, game_manager, content_frame_para_missao):
        self.root = root
        self.game_manager = game_manager
        self.base_content_frame = content_frame_para_missao # Já deve estar com estilo "Black.TFrame"

        # Cores do tema escuro (herdadas do GameManager)
        try:
            self.cor_fundo_base = self.game_manager.bg_color_dark
            self.cor_texto_principal = self.game_manager.fg_color_light
            self.cor_texto_titulo_missao = self.game_manager.title_color_accent
            self.cor_listbox_bg = "#1A1A1A" # Um cinza bem escuro para fundos de listbox
            self.cor_listbox_fg = self.game_manager.fg_color_light
            self.cor_listbox_select_bg = "#004080" 
            self.cor_listbox_select_fg = "white"
            self.cor_texto_info = "#B0E0E6" # Azul claro para informações de status
        except AttributeError:
            print("AVISO Missao4: Cores do GameManager não encontradas. Usando fallbacks.")
            self.cor_fundo_base = "black"
            self.cor_texto_principal = "white"
            self.cor_texto_titulo_missao = "orangered"
            self.cor_listbox_bg = "#101010"
            self.cor_listbox_fg = "white"
            self.cor_listbox_select_bg = "blue"
            self.cor_listbox_select_fg = "white"
            self.cor_texto_info = "lightblue"


        # Fontes (acessando os objetos de fonte corretos do GameManager com _obj)
        try:
            self.narrative_font_obj = self.game_manager.narrative_font_obj
            self.button_font_obj = self.game_manager.button_font_obj
            self.header_font_obj = self.game_manager.header_font_obj
            self.status_label_font_obj = self.game_manager.small_bold_font_obj # Para labels menores e em negrito
            self.small_bold_font_obj = self.game_manager.small_bold_font_obj # <<< DEFINIDO CORRETAMENTE
            
            default_family_for_local_fonts = "Arial" 
            if hasattr(self.game_manager, 'default_font_family'):
                default_family_for_local_fonts = self.game_manager.default_font_family
            self.item_font_obj = tkFont.Font(family=default_family_for_local_fonts, size=10)
        except AttributeError:
            print("AVISO Missao4: Falha ao carregar fontes _obj do GameManager. Usando fallbacks.")
            default_family_fallback = "Arial"
            self.narrative_font_obj = tkFont.Font(family=default_family_fallback, size=12)
            self.button_font_obj = tkFont.Font(family=default_family_fallback, size=11, weight="bold")
            self.header_font_obj = tkFont.Font(family=default_family_fallback, size=20, weight="bold")
            self.status_label_font_obj = tkFont.Font(family=default_family_fallback, size=10, weight="bold")
            self.small_bold_font_obj = tkFont.Font(family=default_family_fallback, size=10, weight="bold") # Fallback
            self.item_font_obj = tkFont.Font(family=default_family_fallback, size=10)
        
        # --- CONJUNTO DE DADOS PARA OS GRUPOS DE EXTRAÇÃO ---
        self.grupos_extracao_base_original = [ 
            {'nome': "Extração Alfa (Informante Urgente)", 'tj': 1, 'dj': 3,  'id': 'A'},
            {'nome': "Resgate Bravo (Cientista Chave)",    'tj': 8, 'dj': 10, 'id': 'B'},
            {'nome': "Coleta Charlie (Dados Imperiais)",  'tj': 4, 'dj': 12, 'id': 'C'},
            {'nome': "Sabotagem Delta (Fábrica de Armas)",'tj': 6, 'dj': 18, 'id': 'D'},
            {'nome': "Apoio Echo (Célula Rebelde Local)", 'tj': 3, 'dj': 7,  'id': 'E'}
        ] # Este conjunto de dados é projetado para diferenciar estratégias
        self.grupos_extracao_base = list(self.grupos_extracao_base_original) 
        self.tempo_total_limite_frota_imperial = sum(g['tj'] for g in self.grupos_extracao_base) + random.randint(3, 7) # Tempo total + uma pequena folga aleatória

        # Estado da Missão
        self._reset_mission_state() 

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
        self.grupos_extracao_base = list(self.grupos_extracao_base_original) 
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
        
        # Título da Missão
        tk.Label(self.base_content_frame, text="MISSÃO 4: Contagem Regressiva em Kessel", 
                 font=self.header_font_obj, fg=self.cor_texto_titulo_missao, bg=self.cor_fundo_base, pady=5).pack(pady=(0,15), fill=tk.X, padx=20)
        
        context_text_val = (
            f"Comandante RZ-479, emergência Nível Alfa no sistema Kessel! Operativos infiltrados instigaram uma rebelião em massa como distração para uma fuga planejada de prisioneiros políticos e cientistas vitais para a Aliança.\n\n"
            f"O Império respondeu rápido. Uma frota de bloqueio chegará em {self.tempo_total_limite_frota_imperial} unidades de tempo. Temos UMA nave de extração rápida, processando uma tarefa de resgate por vez.\n"
            "Cada grupo de resgate tem um tempo de preparo e extração (tj) e um prazo final crítico (dj) antes que sua rota de fuga seja cortada.\n\n"
            "Sua missão: Agendar as extrações para MINIMIZAR O ATRASO MÁXIMO de qualquer grupo. Vidas e o futuro da Aliança dependem da sua precisão."
        )
        
        text_context_container = tk.Frame(self.base_content_frame, bg=self.cor_fundo_base)
        text_context_container.pack(pady=10, padx=30, fill=tk.X)
        text_widget = tk.Text(text_context_container, wrap=tk.WORD, height=11, relief=tk.FLAT, 
                              font=self.narrative_font_obj, padx=10, pady=10,
                              borderwidth=0, highlightthickness=0,
                              background=self.cor_fundo_base, fg=self.cor_texto_principal, insertbackground=self.cor_texto_principal)
        text_widget.insert(tk.END, context_text_val)
        text_widget.config(state=tk.DISABLED)
        text_widget.pack(fill=tk.X, expand=True)
        
        button_container = ttk.Frame(self.base_content_frame, style="Black.TFrame")
        button_container.pack(pady=20)
        ttk.Button(button_container, text="Analisar Protocolos de Extração...",
                   command=self.iniciar_etapa_estrategia_ordenacao, style="Accent.Dark.TButton").pack()

    def iniciar_etapa_estrategia_ordenacao(self):
        self._clear_mission_frame()
        self.lista_ordenada_pelo_jogador = [] 
        self.plano_extracao_jogador = []
        self.tempo_atual_operacao = 0
        self.lmax_jogador = 0
        # self.estrategia_ordenacao_escolhida_nomecurto = None # Mantém a estratégia da tentativa anterior se for um retry da etapa de construção
        # self.estrategia_ordenacao_escolhida_func = None  # ou reseta se quiser que o jogador escolha de novo sempre


        tk.Label(self.base_content_frame, text="Etapa 1: Estratégia de Priorização", 
                 font=self.button_font_obj, fg=self.cor_texto_principal, bg=self.cor_fundo_base).pack(pady=10)
        
        info_grupos_container = tk.Frame(self.base_content_frame, bg=self.cor_fundo_base, pady=5)
        info_grupos_container.pack(pady=5, padx=20, fill=tk.X)
        info_grupos_str = "GRUPOS PARA EXTRAÇÃO (Nome | Processo (tj) | Prazo (dj)):\n"
        for g in sorted(self.grupos_extracao_base, key=lambda x: x['nome']): 
            info_grupos_str += f"- {g['nome']} (tj: {g['tj']}, dj: {g['dj']})\n"
        tk.Label(info_grupos_container, text=info_grupos_str, justify=tk.LEFT, 
                 font=self.item_font_obj, fg=self.cor_texto_info, bg=self.cor_fundo_base).pack(anchor="w")
        
        instrucoes_texto = ("Comandante, a ordem em que processamos estes grupos é crucial para minimizar o atraso máximo. "
                            "Qual estratégia de priorização você recomenda para esta situação crítica?")
        tk.Label(self.base_content_frame, text=instrucoes_texto, wraplength=700, justify=tk.CENTER, 
                 font=self.narrative_font_obj, fg=self.cor_texto_principal, bg=self.cor_fundo_base).pack(pady=10)

        botoes_frame = ttk.Frame(self.base_content_frame, style="Black.TFrame")
        botoes_frame.pack(pady=10)

        opcoes = [
            ("Processar Extrações Mais Rápidas Primeiro (menor tj)", lambda x: x['tj'], "Menor tj"),
            ("Priorizar Prazos Mais Cedos Primeiro (menor dj)", lambda x: x['dj'], "Menor dj (EDF)"), 
            ("Atender Grupos com Menor 'Folga' Primeiro (menor dj - tj)", lambda x: (x['dj'] - x['tj'], x['dj'], x['tj']), "Menor Folga")
        ]
        for texto_btn, sort_key_func, nome_curto_est in opcoes:
            btn = ttk.Button(botoes_frame, text=texto_btn, width=50, style="Dark.TButton",
                             command=lambda skf=sort_key_func, nome_est=nome_curto_est: self.processar_escolha_estrategia(skf, nome_est))
            btn.pack(pady=5)
        
        self.btn_dica_m4_ordenacao = ttk.Button(botoes_frame, text="Pedir Conselho a Fulcrum (Dica de Ordenação)", 
                                                command=lambda: self.dar_dica_m4("ordenacao"), style="Dark.TButton")
        self.btn_dica_m4_ordenacao.pack(pady=10)

    def processar_escolha_estrategia(self, sort_key_func_escolhida, nome_curto_estrategia_escolhida):
        self.estrategia_ordenacao_escolhida_func = sort_key_func_escolhida
        self.estrategia_ordenacao_escolhida_nomecurto = nome_curto_estrategia_escolhida
        self.lista_ordenada_pelo_jogador = sorted(list(self.grupos_extracao_base), key=self.estrategia_ordenacao_escolhida_func)
        estrategia_correta_nome_curto = "Menor dj (EDF)" 
        if self.estrategia_ordenacao_escolhida_nomecurto == estrategia_correta_nome_curto:
            messagebox.showinfo("Estratégia Confirmada", f"Fulcrum: \"Correto, Comandante. '{self.estrategia_ordenacao_escolhida_nomecurto}' é a doutrina padrão... Prossiga.\"")
        else:
            messagebox.showwarning("Estratégia Registrada", f"Fulcrum: \"Entendido, Comandante. Você escolheu '{self.estrategia_ordenacao_escolhida_nomecurto}'. Uma abordagem... taticamente divergente... Prossiga com sua estratégia.\"")
        self.iniciar_etapa_construcao_cronograma()


    def iniciar_etapa_construcao_cronograma(self):
        self._clear_mission_frame()
        self.plano_extracao_jogador = []
        self.tempo_atual_operacao = 0
        self.lmax_jogador = 0
        self.lista_pendente_para_agendar_ui = list(self.lista_ordenada_pelo_jogador)

        tk.Label(self.base_content_frame, text="Etapa 2: Construção do Cronograma de Extração", 
                 font=self.button_font_obj, fg=self.cor_texto_principal, bg=self.cor_fundo_base).pack(pady=10)

        top_info_frame = tk.Frame(self.base_content_frame, bg=self.cor_fundo_base)
        top_info_frame.pack(fill=tk.X, pady=5, padx=10)
        self.tempo_op_label = tk.Label(top_info_frame, text=f"Tempo da Operação: {self.tempo_atual_operacao}", 
                                       font=self.status_label_font_obj, fg=self.cor_texto_info, bg=self.cor_fundo_base)
        self.tempo_op_label.pack(side=tk.LEFT, padx=5)
        self.lmax_label = tk.Label(top_info_frame, text=f"Atraso Máximo Atual: {self.lmax_jogador}", 
                                   font=self.status_label_font_obj, fg=self.cor_texto_info, bg=self.cor_fundo_base)
        self.lmax_label.pack(side=tk.RIGHT, padx=5)

        listas_frame_container = tk.Frame(self.base_content_frame, bg=self.cor_fundo_base)
        listas_frame_container.pack(fill=tk.BOTH, expand=True, pady=5, padx=10)

        # Usando tk.LabelFrame com cores explícitas
        s = ttk.Style() # Para configurar o TLabelframe.Label
        s.configure("DarkFG.TLabelframe.Label", foreground=self.cor_texto_principal, background=self.cor_fundo_base, font=self.small_bold_font_obj)

        pendentes_frame = ttk.LabelFrame(listas_frame_container, text=f"Grupos Pendentes (Ordem: {self.estrategia_ordenacao_escolhida_nomecurto})", 
                                         padding=5, style="Dark.TLabelframe") # Precisa do estilo Dark.TLabelframe
        pendentes_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0,5))
        self.lista_pendentes_listbox = tk.Listbox(pendentes_frame, height=10, font=self.item_font_obj, exportselection=False,
                                                  bg=self.cor_listbox_bg, fg=self.cor_listbox_fg,
                                                  selectbackground=self.cor_listbox_select_bg,
                                                  selectforeground=self.cor_listbox_select_fg,
                                                  borderwidth=0, highlightthickness=0)
        self.lista_pendentes_listbox.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        self._popular_lista_pendentes_ui()

        plano_exec_frame = ttk.LabelFrame(listas_frame_container, text="Cronograma de Extração Formado", 
                                          padding=5, style="Dark.TLabelframe")
        plano_exec_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5,0))
        self.timeline_listbox = tk.Listbox(plano_exec_frame, height=10, font=self.item_font_obj,
                                           bg=self.cor_listbox_bg, fg=self.cor_listbox_fg,
                                           selectbackground=self.cor_listbox_select_bg,
                                           selectforeground=self.cor_listbox_select_fg,
                                           borderwidth=0, highlightthickness=0)
        self.timeline_listbox.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)

        action_frame_bottom = ttk.Frame(self.base_content_frame, style="Black.TFrame")
        action_frame_bottom.pack(fill=tk.X, pady=(15,10), padx=10)

        self.btn_dica_m4_agendamento = ttk.Button(action_frame_bottom, text="Pedir Dica (Agendamento)", 
                                                  command=lambda: self.dar_dica_m4("agendamento"), style="Dark.TButton")
        self.btn_dica_m4_agendamento.pack(side=tk.LEFT)
        
        self.btn_agendar_proximo = ttk.Button(action_frame_bottom, text="Agendar Próximo Grupo da Lista", 
                                              command=self.agendar_proximo_grupo_interativo, style="Accent.Dark.TButton")
        self.btn_agendar_proximo.pack(side=tk.RIGHT)
        
        if not self.lista_pendente_para_agendar_ui:
             self._finalizar_construcao_cronograma()

    def _popular_lista_pendentes_ui(self):
        if not self.lista_pendentes_listbox or not self.lista_pendentes_listbox.winfo_exists(): return
        self.lista_pendentes_listbox.delete(0, tk.END)
        for idx, grupo in enumerate(self.lista_pendente_para_agendar_ui):
            self.lista_pendentes_listbox.insert(tk.END, f"{idx+1}. {grupo['nome']} (tj:{grupo['tj']}, dj:{grupo['dj']})")


    def agendar_proximo_grupo_interativo(self):
        if not self.lista_pendente_para_agendar_ui:
            self._finalizar_construcao_cronograma(); return
        grupo_a_agendar = self.lista_pendente_para_agendar_ui.pop(0) 
        tj, dj = grupo_a_agendar['tj'], grupo_a_agendar['dj']
        sj = self.tempo_atual_operacao
        fj = sj + tj
        atraso_j = max(0, fj - dj)
        self.plano_extracao_jogador.append({'nome': grupo_a_agendar['nome'], 'id': grupo_a_agendar['id'], 'tj': tj, 'dj': dj, 'sj': sj, 'fj': fj, 'atraso_j': atraso_j})
        self.tempo_atual_operacao = fj 
        self.lmax_jogador = max(self.lmax_jogador, atraso_j)
        self.timeline_listbox.insert(tk.END, f"{grupo_a_agendar['nome']}: Início {sj}, Fim {fj} (Prazo {dj}, Atraso {atraso_j})")
        self.timeline_listbox.see(tk.END) 
        if self.tempo_op_label and self.tempo_op_label.winfo_exists(): self.tempo_op_label.config(text=f"Tempo da Operação: {self.tempo_atual_operacao}")
        if self.lmax_label and self.lmax_label.winfo_exists(): self.lmax_label.config(text=f"Atraso Máximo Atual: {self.lmax_jogador}")
        self._popular_lista_pendentes_ui() 
        if not self.lista_pendente_para_agendar_ui: self._finalizar_construcao_cronograma()


    def _finalizar_construcao_cronograma(self):
        messagebox.showinfo("Cronograma Montado", "Todos os grupos foram processados conforme sua estratégia. Vamos avaliar o resultado.", parent=self.base_content_frame)
        if self.btn_agendar_proximo and self.btn_agendar_proximo.winfo_exists():
            self.btn_agendar_proximo.config(state=tk.NORMAL, text="Avaliar Cronograma Final", command=self.avaliar_cronograma_final)
        if self.btn_dica_m4_agendamento and self.btn_dica_m4_agendamento.winfo_exists(): self.btn_dica_m4_agendamento.config(state=tk.DISABLED)


    def avaliar_cronograma_final(self):
        if hasattr(self, 'btn_agendar_proximo') and self.btn_agendar_proximo and self.btn_agendar_proximo.winfo_exists(): self.btn_agendar_proximo.config(state=tk.DISABLED)
        if hasattr(self, 'btn_dica_m4_agendamento') and self.btn_dica_m4_agendamento and self.btn_dica_m4_agendamento.winfo_exists(): self.btn_dica_m4_agendamento.config(state=tk.DISABLED)
        print("\n" + "="*40); print("INÍCIO AVALIAÇÃO CRONOGRAMA FINAL (MISSÃO 4)") 
        print(f"  Estratégia Escolhida: {self.estrategia_ordenacao_escolhida_nomecurto}")
        print(f"  Lmax Jogador: {self.lmax_jogador}"); 
        lmax_otimo_calculado, _ = calcular_schedule_edf_e_lmax(list(self.grupos_extracao_base_original)) 
        print(f"  Lmax Ótimo EDF: {lmax_otimo_calculado}"); print("="*40 + "\n")

        if self.tempo_atual_operacao > self.tempo_total_limite_frota_imperial:
            if self.primeira_falha_nesta_tentativa_m4:
                self.game_manager.add_score(-60); messagebox.showwarning("Penalidade", f"Tempo limite excedido! Penalidade de 60 pontos.", parent=self.base_content_frame); self.primeira_falha_nesta_tentativa_m4 = False
            falha_msg1 = (f"ALERTA MÁXIMO! Seu cronograma levou {self.tempo_atual_operacao} u.t., excedendo o limite! Nave apanhada!")
            falha_msg2_criativa = ("Sensores disparam! Frota de bloqueio! \"Preparem-se para o impacto!\" - Falha catastrófica.")
            self.game_manager.mission_failed_options(self, falha_msg1, falha_msg2_criativa); return
        if self.lmax_jogador == lmax_otimo_calculado: 
            self.game_manager.add_score(300); messagebox.showinfo("Extração Bem-Sucedida!", f"Excelente! Atraso Máximo: {self.lmax_jogador} (Ótimo: {lmax_otimo_calculado}). +300 pontos.", parent=self.base_content_frame)
            self.game_manager.mission_completed("Missao4")
        else: 
            if self.primeira_falha_nesta_tentativa_m4:
                self.game_manager.add_score(-60); messagebox.showwarning("Penalidade", f"Cronograma subótimo. Lmax: {self.lmax_jogador} (Ótimo: {lmax_otimo_calculado}). Penalidade de 60 pontos.", parent=self.base_content_frame); self.primeira_falha_nesta_tentativa_m4 = False
            grupo_mais_atrasado_nome = max(self.plano_extracao_jogador, key=lambda x:x['atraso_j'])['nome'] if self.plano_extracao_jogador else "um grupo"
            falha_msg1 = (f"Fulcrum: \"RZ-479, seu plano resultou em Lmax {self.lmax_jogador}. O ótimo era {lmax_otimo_calculado}. O grupo '{grupo_mais_atrasado_nome}' foi interceptado!\"")
            falha_msg2_criativa = (f"Fulcrum: \"Sua estratégia '{self.estrategia_ordenacao_escolhida_nomecurto}' nos custou caro. Precisão salva vidas.\"")
            self.game_manager.mission_failed_options(self, falha_msg1, falha_msg2_criativa)

    def dar_dica_m4(self, etapa_dica): 
        self.dica_count_m4 += 1; dica_texto = ""
        if etapa_dica == "ordenacao":
            if self.dica_count_m4 == 1: dica_texto = ("DICA: Para minimizar o atraso máximo, considere qual propriedade das tarefas é mais crítica.")
            elif self.dica_count_m4 >= 2:
                dica_texto = ("DICA AVANÇADA: 'Earliest Deadline First' (EDF) - Prazo Mais Cedo Primeiro é a estratégia ótima.")
                if self.btn_dica_m4_ordenacao and self.btn_dica_m4_ordenacao.winfo_exists(): self.btn_dica_m4_ordenacao.config(text="Aplicar EDF", command=self.forcar_ordenacao_edf_com_dica)
        elif etapa_dica == "agendamento":
            dica_texto = "DICA: Após ordenar, adicione os grupos nessa ordem. Não deixe tempo ocioso."
            if self.btn_dica_m4_agendamento and self.btn_dica_m4_agendamento.winfo_exists(): self.btn_dica_m4_agendamento.config(state=tk.DISABLED)
        if dica_texto: messagebox.showinfo("Conselho de Fulcrum", dica_texto, parent=self.base_content_frame)


    def forcar_ordenacao_edf_com_dica(self):
        messagebox.showinfo("Estratégia Corrigida", "Fulcrum: \"Sábia decisão. Lista reordenada por 'Prazo Mais Cedo Primeiro'.\"", parent=self.base_content_frame)
        self.estrategia_ordenacao_escolhida_nomecurto = "Menor dj (EDF)"
        self.estrategia_ordenacao_escolhida_func = lambda x: x['dj']
        self.lista_ordenada_pelo_jogador = sorted(list(self.grupos_extracao_base), key=self.estrategia_ordenacao_escolhida_func)
        if self.btn_dica_m4_ordenacao and self.btn_dica_m4_ordenacao.winfo_exists(): self.btn_dica_m4_ordenacao.config(state=tk.DISABLED) 
        self.iniciar_etapa_construcao_cronograma() 

    def retry_mission(self):
        self.game_manager.set_game_state("START_MISSION_4")