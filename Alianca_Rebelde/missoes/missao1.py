# missoes/missao1.py
import tkinter as tk
from tkinter import ttk, messagebox, font as tkFont
import random # PARA VALORES ALEATÓRIOS
from algoritmos.knapsack_fracionario import calcular_solucao_otima_knapsack_fracionario

class Missao1:
    def __init__(self, root, game_manager, content_frame_para_missao):
        self.root = root
        self.game_manager = game_manager
        self.base_content_frame = content_frame_para_missao 

        # --- Define as cores primeiro ---
        # Cores para o tema escuro desta missão (pegando do GameManager se possível, ou fallback)
        try:
            self.cor_fundo_base = self.game_manager.bg_color_dark
            self.cor_texto_principal = self.game_manager.fg_color_light
            self.cor_texto_titulo_missao = self.game_manager.title_color_accent
        except AttributeError:
            print("AVISO Missao1: Cores base do GameManager não encontradas. Usando fallbacks.")
            self.cor_fundo_base = "black"
            self.cor_texto_principal = "white"
            self.cor_texto_titulo_missao = "orangered"

        self.cor_fundo_item_tabela = "#002b4d" # Azul escuro para as linhas da tabela
        self.cor_texto_tabela_item = self.cor_texto_principal # Branco ou cinza claro
        self.cor_texto_status_ok = "lime green"
        self.cor_texto_status_erro = "red"

        # --- Fontes (acessando os objetos de fonte corretos do GameManager com _obj) ---
        try:
            self.narrative_font_obj = self.game_manager.narrative_font_obj
            self.button_font_obj = self.game_manager.button_font_obj
            self.header_font_obj = self.game_manager.header_font_obj
            self.status_label_font_obj = self.game_manager.small_bold_font_obj
            
            default_family_for_local_fonts = "Arial" 
            if hasattr(self.game_manager, 'default_font_family'):
                default_family_for_local_fonts = self.game_manager.default_font_family

            self.item_font_obj = tkFont.Font(family=default_family_for_local_fonts, size=10)
            self.small_font_obj = tkFont.Font(family=default_family_for_local_fonts, size=9)
        except AttributeError:
            print("AVISO Missao1: Falha ao carregar fontes _obj do GameManager. Usando fallbacks locais para Missao1.")
            default_family_fallback = "Arial"
            self.narrative_font_obj = tkFont.Font(family=default_family_fallback, size=12)
            self.button_font_obj = tkFont.Font(family=default_family_fallback, size=11, weight="bold")
            self.header_font_obj = tkFont.Font(family=default_family_fallback, size=20, weight="bold") 
            self.status_label_font_obj = tkFont.Font(family=default_family_fallback, size=10, weight="bold")
            self.item_font_obj = tkFont.Font(family=default_family_fallback, size=10)
            self.small_font_obj = tkFont.Font(family=default_family_fallback, size=9)
        
        # "Moldes" dos suprimentos - apenas nomes e categorias para faixas de valores
        self.tipos_de_suprimentos = [
            {'nome_base': 'Kits Médicos de Combate', 'tag': 'vital'},
            {'nome_base': 'Componentes de Hiperdrive', 'tag': 'tecnologia_rara'},
            {'nome_base': 'Módulos de Decodificação', 'tag': 'inteligencia'},
            {'nome_base': 'Rações de Sobrevivência', 'tag': 'basico'},
            {'nome_base': 'Células de Energia (Blaster)', 'tag': 'armamento'},
            {'nome_base': 'Equip. de Camuflagem', 'tag': 'especial'},
            {'nome_base': 'Peças p/ Droides Astromec', 'tag': 'manutencao'},
            {'nome_base': 'Transmissores Subespaciais', 'tag': 'comunicacao'}
        ]
        
        # Estes serão definidos dinamicamente
        self.capacidade_maxima_transporte = 100.0 
        self.suprimentos_base = [] 
        
        self.player_carga_peso_atual = 0.0
        self.player_carga_importancia_atual = 0.0

        self.item_sliders = {} 
        self.item_labels_qtd = {}
        self.ratio_labels_widgets = [] 
        self.canvas_itens = None
        self.scrollable_frame_itens = None
        
        self.btn_dica = None
        self.btn_avaliar_carga = None

    def _gerar_suprimentos_aleatorios_e_capacidade(self):
        """Gera pesos e importâncias aleatórias para os suprimentos e uma capacidade de transporte."""
        self.suprimentos_base = []
        self.capacidade_maxima_transporte = float(random.randint(80, 150)) 
        for tipo_item in self.tipos_de_suprimentos:
            nome_completo = tipo_item['nome_base']
            tag = tipo_item['tag']
            if tag == 'vital':
                peso = round(random.uniform(15, 30), 1); importancia = round(random.uniform(peso * 12, peso * 20), 0); nome_completo += " (Vital)"
            elif tag == 'tecnologia_rara':
                peso = round(random.uniform(20, 40), 1); importancia = round(random.uniform(peso * 15, peso * 25), 0); nome_completo += " (Raro)"
            elif tag == 'inteligencia':
                peso = round(random.uniform(5, 15), 1); importancia = round(random.uniform(peso * 20, peso * 30), 0); nome_completo += " (Secreto)"
            elif tag == 'basico':
                peso = round(random.uniform(30, 60), 1); importancia = round(random.uniform(peso * 2, peso * 5), 0); nome_completo += " (Padrão)"
            elif tag == 'armamento':
                peso = round(random.uniform(10, 25), 1); importancia = round(random.uniform(peso * 8, peso * 15), 0); nome_completo += " (Ofensivo)"
            elif tag == 'especial':
                peso = round(random.uniform(5, 20), 1); importancia = round(random.uniform(peso * 10, peso * 18), 0); nome_completo += " (Tático)"
            elif tag == 'manutencao':
                peso = round(random.uniform(15, 35), 1); importancia = round(random.uniform(peso * 5, peso * 10), 0); nome_completo += " (Suporte)"
            elif tag == 'comunicacao':
                peso = round(random.uniform(8, 22), 1); importancia = round(random.uniform(peso * 12, peso * 20), 0); nome_completo += " (Seguro)"
            else: 
                peso = round(random.uniform(10, 50), 1); importancia = round(random.uniform(peso * 5, peso * 10), 0)
            self.suprimentos_base.append({'nome': nome_completo, 'importancia': importancia, 'peso_total': peso})
        print("--- Missão 1: Novos Suprimentos e Capacidade Gerados ---")
        print(f"Capacidade do Transporte: {self.capacidade_maxima_transporte}")
        print("---------------------------------------------------------")

    def _clear_mission_frame(self):
        if self.base_content_frame and self.base_content_frame.winfo_exists():
            for widget in self.base_content_frame.winfo_children():
                widget.destroy()

    def limpar_interface_missao_completa(self):
        if hasattr(self, 'canvas_itens') and self.canvas_itens:
            if self.canvas_itens.winfo_exists():
                self.canvas_itens.destroy()
            self.canvas_itens = None
        self._clear_mission_frame()

    def iniciar_missao_contexto(self):
        self._clear_mission_frame()
        self._gerar_suprimentos_aleatorios_e_capacidade()
        
        title_label = tk.Label(self.base_content_frame, text="MISSÃO 1: A Rota do Contrabando", 
                               font=self.header_font_obj, 
                               fg=self.cor_texto_titulo_missao, 
                               bg=self.cor_fundo_base,       
                               pady=5)
        title_label.pack(pady=(0,15), fill=tk.X, padx=20)

        context_text_val = (
            "Comandante, nossas células no setor de Atravis estão em situação crítica. Precisam urgentemente de suprimentos.\n"
            "Sua habilidade em otimização de carga será vital. Temos um transporte rápido, mas com capacidade limitada. "
            f"Desta vez, a capacidade do transporte é de {self.capacidade_maxima_transporte:.0f} unidades de carga.\n\n" 
            "Cada unidade conta. Cada ponto de importância pode ser a diferença para nossos operativos."
        )
        
        text_context_container = tk.Frame(self.base_content_frame, bg=self.cor_fundo_base)
        text_context_container.pack(pady=10, padx=30, fill=tk.X)

        text_widget = tk.Text(text_context_container, wrap=tk.WORD, height=7, relief=tk.FLAT, 
                              font=self.narrative_font_obj, padx=10, pady=10,
                              borderwidth=0, highlightthickness=0,
                              background=self.cor_fundo_base,      
                              foreground=self.cor_texto_principal, 
                              insertbackground=self.cor_texto_principal) 
        text_widget.insert(tk.END, context_text_val)
        text_widget.config(state=tk.DISABLED)
        text_widget.pack(fill=tk.X, expand=True)
        
        button_container = ttk.Frame(self.base_content_frame, style="Black.TFrame")
        button_container.pack(pady=20)
        ttk.Button(button_container, text="Analisar Suprimentos e Planejar Carga",
                   command=self.iniciar_knapsack_interativo, 
                   style="Accent.Dark.TButton").pack()


    def iniciar_knapsack_interativo(self):
        self._clear_mission_frame() 
        self.player_carga_peso_atual = 0.0
        self.player_carga_importancia_atual = 0.0
        self.item_sliders.clear()
        self.item_labels_qtd.clear()
        self.ratio_labels_widgets.clear()

        top_frame = ttk.Frame(self.base_content_frame, style="Black.TFrame")
        top_frame.pack(fill=tk.X, pady=(5,5), padx=10)
        
        ttk.Label(top_frame, text="Planejamento de Carga (Knapsack Fracionário)", 
                  font=self.button_font_obj, 
                  style="WhiteText.TLabel").pack(side=tk.LEFT, padx=(0,10))
        
        self.status_carga_label = ttk.Label(top_frame, text="", 
                                           font=self.status_label_font_obj, 
                                           style="WhiteText.TLabel") 
        self.status_carga_label.pack(side=tk.RIGHT)
        self._update_status_carga_label() 

        items_area_frame = ttk.Frame(self.base_content_frame, style="Black.TFrame")
        items_area_frame.pack(fill=tk.BOTH, expand=True, pady=5, padx=10)

        self.canvas_itens = tk.Canvas(items_area_frame, borderwidth=0, highlightthickness=0, bg=self.cor_fundo_base)
        self.scrollable_frame_itens = ttk.Frame(self.canvas_itens, style="Black.TFrame")  
        self.canvas_itens.create_window((0, 0), window=self.scrollable_frame_itens, anchor="nw", tags="scrollable_frame")
        self.scrollable_frame_itens.bind("<Configure>", self._on_frame_configure)
        
        scrollbar_itens = ttk.Scrollbar(items_area_frame, orient="vertical", command=self.canvas_itens.yview)
        self.canvas_itens.configure(yscrollcommand=scrollbar_itens.set)
        self.canvas_itens.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar_itens.pack(side=tk.RIGHT, fill=tk.Y)
        
        header_frame = ttk.Frame(self.scrollable_frame_itens, style="Black.TFrame")
        header_frame.pack(fill=tk.X, pady=(0,8), padx=0)
        
        col_widths = {'Suprimento': 33, 'Info': 20, 'Qtd': 23, 'Prioridade': 13}
        header_style = "WhiteText.TLabel" 

        ttk.Label(header_frame, text="Suprimento Disponível", font=self.status_label_font_obj, style=header_style, width=col_widths['Suprimento']).grid(row=0, column=0, padx=(5,0), sticky="w")
        ttk.Label(header_frame, text="Importância / Peso", font=self.status_label_font_obj, style=header_style, width=col_widths['Info']).grid(row=0, column=1, padx=5, sticky="w")
        ttk.Label(header_frame, text="Qtd. a Carregar", font=self.status_label_font_obj, style=header_style, width=col_widths['Qtd']).grid(row=0, column=2, padx=5, sticky="w")
        self.ratio_header_label = ttk.Label(header_frame, text="Prioridade (I/P)", font=self.status_label_font_obj, style=header_style, width=col_widths['Prioridade'])
        self.ratio_header_label.grid(row=0, column=3, padx=5, sticky="e")
        self.ratio_header_label.grid_remove()

        for i, item_data in enumerate(self.suprimentos_base):
            item_outer_frame = tk.Frame(self.scrollable_frame_itens, bg=self.cor_fundo_item_tabela, padx=5, pady=3)
            item_outer_frame.pack(fill=tk.X, pady=1, padx=0)

            tk.Label(item_outer_frame, text=item_data['nome'], width=col_widths['Suprimento']-2, font=self.item_font_obj, anchor="w", wraplength=200, 
                     bg=self.cor_fundo_item_tabela, fg=self.cor_texto_tabela_item).grid(row=0, column=0, pady=2, sticky="w")
            info_str = f"I: {item_data['importancia']:.0f}\nP: {item_data['peso_total']:.1f} kg" 
            tk.Label(item_outer_frame, text=info_str, width=col_widths['Info']-2, font=self.small_font_obj, justify=tk.LEFT, 
                     bg=self.cor_fundo_item_tabela, fg=self.cor_texto_tabela_item).grid(row=0, column=1, pady=2, sticky="w")

            slider_frame = tk.Frame(item_outer_frame, bg=self.cor_fundo_item_tabela) 
            slider_frame.grid(row=0, column=2, pady=2, sticky="ew")
            
            slider = ttk.Scale(slider_frame, from_=0, to=item_data['peso_total'], orient=tk.HORIZONTAL, length=110,
                               command=lambda val, idx=i: self._update_slider_label_and_carga(idx, float(val)))
            slider.set(0)
            slider.pack(side=tk.TOP, fill=tk.X, padx=(0,5))
            self.item_sliders[i] = slider

            label_qtd = tk.Label(slider_frame, text="0.0 kg", font=self.small_font_obj, width=10, anchor="center",
                                 bg=self.cor_fundo_item_tabela, fg=self.cor_texto_tabela_item)
            label_qtd.pack(side=tk.BOTTOM, fill=tk.X)
            self.item_labels_qtd[i] = label_qtd 
            
            imp_p_ratio = (item_data['importancia'] / item_data['peso_total']) if item_data['peso_total'] > 0 else float('inf')
            ratio_label_widget = tk.Label(item_outer_frame, text=f"{imp_p_ratio:.2f}", font=self.item_font_obj, width=col_widths['Prioridade'], anchor="e",
                                          bg=self.cor_fundo_item_tabela, fg=self.cor_texto_tabela_item)
            ratio_label_widget.grid(row=0, column=3, pady=2, sticky="e")
            ratio_label_widget.grid_remove() 
            self.ratio_labels_widgets.append(ratio_label_widget)

            item_outer_frame.columnconfigure(0, weight=3) 
            item_outer_frame.columnconfigure(1, weight=2) 
            item_outer_frame.columnconfigure(2, weight=2) 
            item_outer_frame.columnconfigure(3, weight=1)

        action_frame = ttk.Frame(self.base_content_frame, style="Black.TFrame")
        action_frame.pack(fill=tk.X, pady=(15,10), padx=10)
        
        self.btn_dica = ttk.Button(action_frame, text="Pedir Dica (Priorização)", command=self.mostrar_dica_knapsack, style="Dark.TButton")
        self.btn_dica.pack(side=tk.LEFT, padx=(0,10))
        
        self.btn_avaliar_carga = ttk.Button(action_frame, text="Confirmar Carga e Avaliar", command=self.avaliar_knapsack_player, style="Accent.Dark.TButton")
        self.btn_avaliar_carga.pack(side=tk.RIGHT)

        self.base_content_frame.update_idletasks() 
        self._on_frame_configure(None)
        # print("DEBUG Missao1: Knapsack UI populated (Modo Escuro).") # Seu comentário original

    def _on_frame_configure(self, event):
        if self.canvas_itens and self.canvas_itens.winfo_exists() and hasattr(self, 'scrollable_frame_itens') and self.scrollable_frame_itens.winfo_exists(): 
            self.canvas_itens.configure(scrollregion=self.canvas_itens.bbox("all"))

    def _update_slider_label_and_carga(self, item_index, slider_value):
        peso_selecionado = round(float(slider_value), 1)
        if item_index >= len(self.suprimentos_base): 
            print(f"AVISO: item_index {item_index} fora do alcance para suprimentos_base.")
            return
        if item_index not in self.item_labels_qtd or item_index not in self.item_sliders:
            print(f"AVISO: item_index {item_index} não encontrado nos dicionários de UI.")
            return 
        if self.item_labels_qtd[item_index].winfo_exists():
            self.item_labels_qtd[item_index].config(text=f"{peso_selecionado:.1f} kg")
        
        self.player_carga_peso_atual = 0.0
        self.player_carga_importancia_atual = 0.0
        for idx, item_data in enumerate(self.suprimentos_base):
            if idx in self.item_sliders and self.item_sliders[idx].winfo_exists(): 
                peso_deste_item_no_slider = round(float(self.item_sliders[idx].get()), 1)
                if peso_deste_item_no_slider > 0:
                    if item_data['peso_total'] > 0:
                        fracao = peso_deste_item_no_slider / item_data['peso_total']
                        importancia_deste_item = fracao * item_data['importancia']
                    else: 
                        importancia_deste_item = item_data['importancia'] if peso_deste_item_no_slider > 0 else 0
                    self.player_carga_peso_atual += peso_deste_item_no_slider
                    self.player_carga_importancia_atual += importancia_deste_item
        self._update_status_carga_label()

    def _update_status_carga_label(self):
        if self.player_carga_peso_atual > self.capacidade_maxima_transporte:
            cor_texto_status = self.cor_texto_status_erro 
        else:
            cor_texto_status = self.cor_texto_status_ok 

        capacidade_restante = self.capacidade_maxima_transporte - self.player_carga_peso_atual
        
        status_texto = (f"Carga: {self.player_carga_peso_atual:.1f} / {self.capacidade_maxima_transporte:.0f} kg "
                        f"(Restante: {capacidade_restante:.1f} kg)\n"
                        f"Importância Total: {self.player_carga_importancia_atual:.0f}")
        
        if hasattr(self, 'status_carga_label') and self.status_carga_label and self.status_carga_label.winfo_exists():
             self.status_carga_label.config(text=status_texto, foreground=cor_texto_status)

    def _desabilitar_controles_missao1(self):
        if self.btn_dica and self.btn_dica.winfo_exists(): self.btn_dica.config(state=tk.DISABLED)
        if self.btn_avaliar_carga and self.btn_avaliar_carga.winfo_exists(): self.btn_avaliar_carga.config(state=tk.DISABLED)
        for i_slider in self.item_sliders.values():
            if i_slider.winfo_exists(): i_slider.config(state=tk.DISABLED)

    def mostrar_dica_knapsack(self):
        dica_texto = (
            "Comandante, para maximizar a importância da carga, analise quais suprimentos oferecem o maior retorno por cada unidade de peso.\n\n"
            "Itens com alta 'Importância por Peso' (Prioridade I/P) são geralmente mais eficientes.\n\n"
            "(As razões de Prioridade I/P foram agora reveladas na tabela ao lado de cada item para sua análise.)"
        )
        messagebox.showinfo("Dica da Rebelião", dica_texto)
        if hasattr(self, 'ratio_header_label') and self.ratio_header_label and self.ratio_header_label.winfo_exists() and not self.ratio_header_label.winfo_ismapped():
             self.ratio_header_label.grid() 
        for ratio_widget in self.ratio_labels_widgets:
            if ratio_widget.winfo_exists() and not ratio_widget.winfo_ismapped():
                 ratio_widget.grid() 
        if self.btn_dica and self.btn_dica.winfo_exists():
            self.btn_dica.config(state=tk.DISABLED)

    def avaliar_knapsack_player(self):
        self._desabilitar_controles_missao1() 
        if self.player_carga_peso_atual > self.capacidade_maxima_transporte:
            falha_excesso_msg1 = (f"SOBRECARGA CRÍTICA! Comandante, o peso da carga excede os limites estruturais do transporte em {self.player_carga_peso_atual - self.capacidade_maxima_transporte:.1f} unidades. Na tentativa de decolagem, a nave sofreu uma falha catastrófica. Missão fracassada.")
            falha_excesso_msg2_criativa = ("Relatório do Hangar: \"Comandante, tentamos... mas existe uma coisa chamada 'limite de peso'. O transporte não aguentou. Parece que a física venceu desta vez.\" Missão desastrosamente fracassada.")
            self.game_manager.mission_failed_options(self, falha_excesso_msg1, falha_excesso_msg2_criativa)
            return
        
        itens_para_algoritmo = [{'nome': i['nome'], 'importancia': i['importancia'], 'peso_total': i['peso_total']} for i in self.suprimentos_base]
        _, importancia_otima, _ = calcular_solucao_otima_knapsack_fracionario(itens_para_algoritmo, self.capacidade_maxima_transporte)
        percentual_do_otimo = (self.player_carga_importancia_atual / importancia_otima) * 100 if importancia_otima > 0 else (100 if self.player_carga_importancia_atual > 0 else 0)
        percentual_capacidade_usada = (self.player_carga_peso_atual / self.capacidade_maxima_transporte) * 100 if self.capacidade_maxima_transporte > 0 else 0

        if percentual_do_otimo >= 96 and self.player_carga_peso_atual <= self.capacidade_maxima_transporte and percentual_capacidade_usada >= 70:
            self.game_manager.add_score(100) 
            messagebox.showinfo("Sucesso na Carga!", f"Excelente planejamento, Comandante!\nSua carga tem importância {self.player_carga_importancia_atual:.0f} e peso {self.player_carga_peso_atual:.1f} kg.\n(Eficiência: {percentual_do_otimo:.1f}% da importância ótima possível).\n\nOs suprimentos foram enviados!")
            self.game_manager.mission_completed("Missao1")
        else:
            falha_ineficiente_msg1 = (f"ANÁLISE DE CARGA NEGATIVA. Comandante, os suprimentos, embora dentro da capacidade, não atingiram o nível de importância estratégica necessário. As células de Atravis receberam ajuda, mas não o suficiente. Missão fracassada.\n(Sua carga: I:{self.player_carga_importancia_atual:.0f}, P:{self.player_carga_peso_atual:.1f} kg. Importância ótima possível: {importancia_otima:.0f})")
            falha_ineficiente_msg2_criativa = ("Feedback de Atravis (sarcástico): \"Obrigado pelos... 'suprimentos', Comandante. Ainda precisamos desesperadamente de itens mais... prioritários. Valeu a tentativa.\" Missão fracassada.")
            self.game_manager.mission_failed_options(self, falha_ineficiente_msg1, falha_ineficiente_msg2_criativa)

    def retry_mission(self):
        print("Missao1: retry_mission chamada. Resetando estado para START_MISSION_1.")
        self.game_manager.set_game_state("START_MISSION_1")