# missoes/missao7.py
import tkinter as tk
from tkinter import ttk, messagebox, font as tkFont
from algoritmos.huffman import construir_arvore_huffman, gerar_codigos_huffman # Seu import original

class Missao7:
    def __init__(self, root, game_manager, content_frame_para_missao):
        self.root = root
        self.game_manager = game_manager
        self.base_content_frame = content_frame_para_missao # Já deve ser preto pelo GameManager

        # Cores do tema escuro (herdadas do GameManager)
        try:
            self.cor_fundo_base = self.game_manager.bg_color_dark
            self.cor_texto_principal = self.game_manager.fg_color_light
            self.cor_texto_titulo_missao = self.game_manager.title_color_accent
            self.cor_texto_info = "#B0E0E6" # Azul claro para informações de status/listas
            self.cor_entry_bg = "#101010" # Fundo para campos de Entry
            self.cor_entry_fg = self.game_manager.fg_color_light
        except AttributeError:
            print("AVISO Missao7: Cores do GameManager não encontradas. Usando fallbacks.")
            self.cor_fundo_base = "black"
            self.cor_texto_principal = "white"
            self.cor_texto_titulo_missao = "orangered"
            self.cor_texto_info = "lightblue"
            self.cor_entry_bg = "black"
            self.cor_entry_fg = "white"

        # Fontes (acessando os objetos de fonte corretos do GameManager com _obj)
        # Mantendo a sua estrutura original de acesso às fontes, mas usando os nomes _obj
        try:
            self.narrative_font_obj = self.game_manager.narrative_font_obj
            self.button_font_obj = self.game_manager.button_font_obj
            self.header_font_obj = self.game_manager.header_font_obj
            # self.status_label_font_obj = self.game_manager.small_bold_font_obj # Se precisar
            
            default_family_for_local_fonts = "Arial" 
            if hasattr(self.game_manager, 'default_font_family'):
                default_family_for_local_fonts = self.game_manager.default_font_family
            self.item_font_obj = tkFont.Font(family=default_family_for_local_fonts, size=10)

        except AttributeError:
            print("AVISO Missao7: Falha ao carregar fontes _obj do GameManager. Usando fallbacks.")
            default_family_fallback = "Arial"
            self.narrative_font_obj = tkFont.Font(family=default_family_fallback, size=12)
            self.button_font_obj = tkFont.Font(family=default_family_fallback, size=11, weight="bold")
            self.header_font_obj = tkFont.Font(family=default_family_fallback, size=20, weight="bold")
            # self.status_label_font_obj = tkFont.Font(family=default_family_fallback, size=10, weight="bold")
            self.item_font_obj = tkFont.Font(family=default_family_fallback, size=10)
        
        self.codigos_gerados = {}
        self.mensagem_original = ""
        self.mensagem_codificada = "" # Para armazenar a string binária correta
        self.dica_count = 0 # Seu contador de dicas original

        # Referências UI
        self.input_mensagem = None
        self.input_codificada = None
        self.btn_validar = None # Para poder desabilitar
        self.btn_dica_m7 = None

    def _clear_frame(self): # Seu método original de limpeza
        if self.base_content_frame and self.base_content_frame.winfo_exists():
            for widget in self.base_content_frame.winfo_children():
                widget.destroy()

    # Adicionando para consistência com outras missões
    def limpar_interface_missao_completa(self):
        self._clear_frame()

    def iniciar_missao_contexto(self):
        self._clear_frame()
        self.dica_count = 0 # Reseta contador de dicas para a missão

        # Título da Missão
        tk.Label(self.base_content_frame, text="MISSÃO 7: Comunicação Segura", 
                 font=self.header_font_obj, fg=self.cor_texto_titulo_missao, bg=self.cor_fundo_base, pady=5).pack(pady=(0,15), fill=tk.X, padx=20)

        contexto = (
            "Fulcrum: \"Comandante, esta é possivelmente nossa transmissão mais crítica. Precisamos enviar um relatório consolidado de nossas operações recentes para o Alto Comando da Aliança. "
            "Os canais de comunicação estão sob vigilância imperial pesada, e qualquer mensagem longa ou não otimizada será certamente interceptada e decifrada.\n\n"
            "Sua tarefa é usar a Codificação de Huffman para compactar a mensagem o máximo possível. Após gerar os códigos binários para cada caractere, você deverá transcrever manualmente a mensagem original para sua forma codificada. "
            "A precisão é absoluta, cada bit conta para a segurança da nossa rede e o sucesso da Rebelião.\""
        )
        
        text_context_container = tk.Frame(self.base_content_frame, bg=self.cor_fundo_base)
        text_context_container.pack(pady=10, padx=30, fill=tk.X)
        texto_widget = tk.Text(text_context_container, wrap=tk.WORD, height=9, relief=tk.FLAT,
                                 font=self.narrative_font_obj, padx=10, pady=10,
                                 borderwidth=0, highlightthickness=0,
                                 background=self.cor_fundo_base, fg=self.cor_texto_principal, insertbackground=self.cor_texto_principal)
        texto_widget.insert(tk.END, contexto)
        texto_widget.config(state=tk.DISABLED)
        texto_widget.pack(fill=tk.X, expand=True)

        # Input da mensagem original
        input_frame = tk.Frame(self.base_content_frame, bg=self.cor_fundo_base)
        input_frame.pack(pady=10, padx=30, fill=tk.X)
        tk.Label(input_frame, text="Digite a mensagem a ser codificada (letras e espaços): ", 
                 font=self.narrative_font_obj, fg=self.cor_texto_principal, bg=self.cor_fundo_base).pack(anchor="w", pady=(5,0))
        self.input_mensagem = tk.Entry(input_frame, width=70, font=self.item_font_obj, 
                                       bg=self.cor_entry_bg, fg=self.cor_entry_fg, insertbackground=self.cor_entry_fg,
                                       relief=tk.FLAT, borderwidth=2)
        self.input_mensagem.pack(pady=5, fill=tk.X)

        button_container = ttk.Frame(self.base_content_frame, style="Black.TFrame")
        button_container.pack(pady=15)
        ttk.Button(button_container, text="Gerar Códigos Huffman e Prosseguir", 
                   command=self.gerar_codificacao, style="Accent.Dark.TButton").pack()

    def gerar_codificacao(self):
        # Seu método original, sem alterações na lógica
        self.mensagem_original = self.input_mensagem.get().strip().upper() # Convertendo para maiúsculas para consistência nos códigos
        if not self.mensagem_original:
            messagebox.showerror("Erro de Entrada", "A mensagem não pode estar vazia.", parent=self.base_content_frame)
            return
        if not all(c.isalpha() or c.isspace() for c in self.mensagem_original): # Permite espaços
            messagebox.showerror("Erro de Entrada", "Digite apenas letras e espaços na mensagem.", parent=self.base_content_frame)
            return
        
        # Remove múltiplos espaços e espaços no início/fim para a codificação real
        mensagem_para_codificar = ' '.join(self.mensagem_original.split())


        if not mensagem_para_codificar: # Se a mensagem só tinha espaços
             messagebox.showerror("Erro de Entrada", "A mensagem efetiva (sem múltiplos espaços) está vazia.", parent=self.base_content_frame)
             return


        try:
            raiz_huffman = construir_arvore_huffman(mensagem_para_codificar)
            if raiz_huffman is None: # Caso a mensagem tenha apenas 1 tipo de caractere (ou vazia após processamento)
                if len(set(mensagem_para_codificar)) == 1: # Mensagem com um único tipo de caractere
                    char_unico = list(set(mensagem_para_codificar))[0]
                    self.codigos_gerados = {char_unico: '0'} # Código arbitrário para caractere único
                else: # Deveria ser pego pelo 'if not mensagem_para_codificar'
                    messagebox.showerror("Erro na Geração de Códigos", "Não foi possível gerar códigos para a mensagem fornecida (ex: mensagem muito curta ou com apenas um tipo de caractere de forma problemática).", parent=self.base_content_frame)
                    return
            else:
                self.codigos_gerados = gerar_codigos_huffman(raiz_huffman)
            
            self.mensagem_codificada = ''.join(self.codigos_gerados.get(c, '') for c in mensagem_para_codificar) # Usa .get para evitar erro se um char não tiver código (não deve acontecer)
            self.mensagem_original_processada = mensagem_para_codificar # Guarda a versão que foi realmente codificada

        except Exception as e:
            messagebox.showerror("Erro na Geração de Códigos", f"Ocorreu um erro: {e}", parent=self.base_content_frame)
            return

        self.exibir_interface_codificacao()

    def exibir_interface_codificacao(self):
        self._clear_frame()

        tk.Label(self.base_content_frame, text="Códigos Gerados por Huffman:", 
                 font=self.button_font_obj, fg=self.cor_texto_principal, bg=self.cor_fundo_base).pack(pady=(5, 0))
        
        # Frame para os códigos com fundo preto
        codigos_display_frame = tk.Frame(self.base_content_frame, bg=self.cor_fundo_base, pady=5)
        codigos_display_frame.pack(pady=5, padx=20, fill=tk.X)

        # Mostra os códigos em colunas para melhor visualização
        col = 0
        max_cols = 3 # Número de colunas para exibir os códigos
        for char_code in sorted(self.codigos_gerados.items()):
            char, code = char_code
            tk.Label(codigos_display_frame, text=f"'{char}': {code}", 
                     font=self.item_font_obj, fg=self.cor_texto_info, bg=self.cor_fundo_base
                     ).grid(row=col // max_cols, column=col % max_cols, sticky="w", padx=10)
            col += 1
        
        tk.Label(self.base_content_frame, text=f"Mensagem original (processada): {self.mensagem_original_processada}", 
                 font=self.item_font_obj, fg=self.cor_texto_info, bg=self.cor_fundo_base, wraplength=700).pack(pady=(10, 5))

        instrucoes = "Agora, Comandante, transcreva manualmente a mensagem acima usando os códigos binários gerados. Não use espaços entre os códigos."
        tk.Label(self.base_content_frame, text=instrucoes, 
                 font=self.narrative_font_obj, wraplength=600, justify=tk.CENTER,
                 fg=self.cor_texto_principal, bg=self.cor_fundo_base).pack(pady=5)

        tk.Label(self.base_content_frame, text="Digite a mensagem codificada (em binário):", 
                 font=self.narrative_font_obj, fg=self.cor_texto_principal, bg=self.cor_fundo_base).pack(pady=(10,0))
        self.input_codificada = tk.Entry(self.base_content_frame, width=80, font=self.item_font_obj,
                                         bg=self.cor_entry_bg, fg=self.cor_entry_fg, insertbackground=self.cor_entry_fg,
                                         relief=tk.FLAT, borderwidth=2)
        self.input_codificada.pack(pady=5)

        botoes_frame = ttk.Frame(self.base_content_frame, style="Black.TFrame")
        botoes_frame.pack(pady=10)
        self.btn_validar = ttk.Button(botoes_frame, text="Validar Codificação", command=self.verificar_codificacao, style="Accent.Dark.TButton")
        self.btn_validar.pack(side=tk.LEFT, padx=5)
        self.btn_dica_m7 = ttk.Button(botoes_frame, text="Pedir Dica", command=self.mostrar_dica, style="Dark.TButton")
        self.btn_dica_m7.pack(side=tk.LEFT, padx=5)


    def verificar_codificacao(self):
        # Desabilitar botões após a tentativa
        if self.btn_validar and self.btn_validar.winfo_exists():
            self.btn_validar.config(state=tk.DISABLED)
        if self.btn_dica_m7 and self.btn_dica_m7.winfo_exists():
            self.btn_dica_m7.config(state=tk.DISABLED)


        tentativa_jogador = self.input_codificada.get().strip().replace(" ", "") # Remove espaços
        
        # Validação se a entrada contém apenas 0s e 1s
        if not all(c in '01' for c in tentativa_jogador) and tentativa_jogador: # Permite string vazia para não dar erro antes
            messagebox.showerror("Entrada Inválida", "Sua mensagem codificada deve conter apenas 0s e 1s.", parent=self.base_content_frame)
            if self.btn_validar and self.btn_validar.winfo_exists(): self.btn_validar.config(state=tk.NORMAL) # Reabilita para nova tentativa
            if self.btn_dica_m7 and self.btn_dica_m7.winfo_exists(): self.btn_dica_m7.config(state=tk.NORMAL)
            return

        correta_codificada = self.mensagem_codificada

        if tentativa_jogador == correta_codificada:
            pontos = 150 # Recompensa maior por ser a última e mais complexa de digitar
            messagebox.showinfo("Codificação Correta!", 
                                f"Transmissão Perfeita, Comandante! A mensagem foi codificada com precisão usando o mínimo de bits.\n"
                                f"Informação vital enviada ao Alto Comando! Você ganhou {pontos} pontos de influência.", 
                                parent=self.base_content_frame)
            self.game_manager.add_score(pontos)
            self.game_manager.mission_completed("Missao7")
        else:
            self.dica_count += 1
            self.game_manager.add_score(-30) # Penalidade por erro
            messagebox.showwarning("Codificação Incorreta", 
                                   f"RZ-479, a transmissão falhou. A sequência binária não corresponde à codificação Huffman ótima para a mensagem.\n"
                                   "Houve uma perda de 30 pontos de influência. Analise os códigos e tente novamente.",
                                   parent=self.base_content_frame)
            
            if self.dica_count >= 3: # Ou um limite de tentativas
                # Para mostrar a resposta correta após algumas falhas
                messagebox.showerror("Falha Crítica na Codificação", 
                                     f"Comandante, após múltiplas tentativas, a mensagem não pôde ser enviada corretamente.\n"
                                     f"A sequência binária correta seria: {correta_codificada}\n"
                                     "Precisaremos encontrar outro método para esta transmissão. A missão de codificação falhou.",
                                     parent=self.base_content_frame)
                self.game_manager.mission_failed_options(self, "A transmissão não pôde ser completada. O Império pode ter interceptado fragmentos.", 
                                                        "Fulcrum: \"Perdemos a janela de oportunidade para esta transmissão segura. Uma lástima.\"")
            else:
                 # Reabilita para nova tentativa
                if self.btn_validar and self.btn_validar.winfo_exists(): self.btn_validar.config(state=tk.NORMAL)
                if self.btn_dica_m7 and self.btn_dica_m7.winfo_exists(): self.btn_dica_m7.config(state=tk.NORMAL)


    def mostrar_dica(self):
        # Seu método de dica original
        dicas = [
            "DICA 1 - Fulcrum: \"Comandante, substitua cada letra da sua mensagem original pelo código binário correspondente da tabela. Concatene todos os códigos sem espaços.\"",
            "DICA 2 - Fulcrum: \"Verifique se não houve erros de digitação. Um único bit errado pode corromper toda a mensagem. A atenção aos detalhes é crucial.\"",
            f"DICA FINAL - Fulcrum: \"A mensagem codificada corretamente deve ter exatamente {len(self.mensagem_codificada)} bits. Se a sua for maior ou menor, algo está errado.\""
        ]
        indice_dica = min(self.dica_count, len(dicas) - 1) # Usa dica_count para progredir as dicas
        messagebox.showinfo("Conselho Estratégico de Fulcrum", dicas[indice_dica], parent=self.base_content_frame)
        if self.dica_count >= len(dicas) -1 and self.btn_dica_m7 and self.btn_dica_m7.winfo_exists(): # Desabilita após a última dica específica
            self.btn_dica_m7.config(state=tk.DISABLED)


    def retry_mission(self):
        print("Missao7: retry_mission chamada.")
        self.iniciar_missao_contexto() # Reinicia a missão do zero, com nova entrada de mensagem