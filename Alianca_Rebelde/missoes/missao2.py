import tkinter as tk
from tkinter import ttk, messagebox, font as tkFont
import random # Para gerar valores aleatórios
from algoritmos.coin_changing import calcular_troco

class Missao2:
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
        
        # Dados da Missão Coin Changing
        self.valor_a_pagar_informante = 0 # Será definido dinamicamente
        self.denominacoes_imperiais = [100, 50, 25, 10, 5, 1] # Créditos Imperiais
        
        self.player_cedulas_usadas = {} 
        self.entry_widgets_cedulas = {}
        self.btn_confirmar_pagamento = None # Referência para o botão

    def _clear_mission_frame(self):
        if self.base_content_frame and self.base_content_frame.winfo_exists():
            for widget in self.base_content_frame.winfo_children():
                widget.destroy()

    def limpar_interface_missao_completa(self):
        self._clear_mission_frame()

    def iniciar_missao_contexto(self):
        self._clear_mission_frame()
        
        # GERA O VALOR ALEATÓRIO PARA ESTA TENTATIVA DA MISSÃO
        self.valor_a_pagar_informante = random.randint(100, 1000) 

        ttk.Label(self.base_content_frame, text="MISSÃO 2: Pagamento Discreto", font=self.header_font).pack(pady=10)

        context_text = (
            "Fulcrum lhe informou sobre o pagamento necessário ao informante que garantiu a rota segura para Atravis.\n"
            f"Desta vez, o valor negociado com o contato foi de {self.valor_a_pagar_informante} créditos imperiais. "
            "Este informante é notoriamente paranoico e opera em áreas sob intensa vigilância imperial. Um volume grande ou incomum de cédulas pode levantar suspeitas fatais.\n\n"
            "Sua tarefa: efetuar o pagamento exato usando o MENOR NÚMERO POSSÍVEL de cédulas de crédito imperial padrão para garantir a discrição."
        )
        
        text_widget = tk.Text(self.base_content_frame, wrap=tk.WORD, height=9, relief=tk.FLAT, 
                              background=self.root.cget('bg'), font=self.narrative_font, padx=10, pady=10)
        text_widget.insert(tk.END, context_text)
        text_widget.config(state=tk.DISABLED)
        text_widget.pack(pady=15, padx=10, fill=tk.X)

        ttk.Button(self.base_content_frame, text="Analisar Denominações e Preparar Pagamento...",
                   command=self.iniciar_coin_changing_interativo, style="Accent.TButton").pack(pady=20)

    def iniciar_coin_changing_interativo(self):
        self._clear_mission_frame()
        self.player_cedulas_usadas.clear()
        self.entry_widgets_cedulas.clear()

        top_frame = ttk.Frame(self.base_content_frame)
        top_frame.pack(fill=tk.X, pady=(10,5), padx=10)
        ttk.Label(top_frame, text="Pagamento ao Informante (Minimizar Cédulas)", font=self.button_font).pack(side=tk.LEFT, padx=(0,10))
        
        self.status_pagamento_label = ttk.Label(top_frame, text="", font=self.status_label_font)
        self.status_pagamento_label.pack(side=tk.RIGHT)
        
        ttk.Label(self.base_content_frame, text=f"Valor Total a Pagar: {self.valor_a_pagar_informante} créditos", font=self.narrative_font).pack(pady=10)

        cedulas_frame = ttk.Frame(self.base_content_frame, padding=10)
        cedulas_frame.pack(pady=10)

        ttk.Label(cedulas_frame, text="Denominações Disponíveis (Créditos Imperiais):", font=self.status_label_font).grid(row=0, column=0, columnspan=2, pady=(0,10), sticky="w")

        row_num = 1
        for den in sorted(self.denominacoes_imperiais, reverse=True):
            ttk.Label(cedulas_frame, text=f"Cédulas de {den}:", font=self.item_font).grid(row=row_num, column=0, padx=5, pady=5, sticky="e")
            
            spin_var = tk.StringVar(value="0")
            max_spin_val = self.valor_a_pagar_informante // den if den > 0 else 0
            spinbox = ttk.Spinbox(cedulas_frame, from_=0, to=max_spin_val + 5, width=5, textvariable=spin_var, command=self._atualizar_status_pagamento, wrap=False) # wrap=False pode ser melhor
            spinbox.grid(row=row_num, column=1, padx=5, pady=5, sticky="w")
            self.entry_widgets_cedulas[den] = spin_var
            
            row_num += 1
        
        self._atualizar_status_pagamento() 

        action_frame = ttk.Frame(self.base_content_frame)
        action_frame.pack(fill=tk.X, pady=20, padx=10)
        
        self.btn_dica_m2 = ttk.Button(action_frame, text="Pedir Dica (Estratégia de Pagamento)", command=self.mostrar_dica_coin_changing)
        self.btn_dica_m2.pack(side=tk.LEFT, padx=(0,10))
        
        self.btn_confirmar_pagamento = ttk.Button(action_frame, text="Confirmar e Realizar Pagamento", command=self.avaliar_pagamento_jogador, style="Accent.TButton")
        self.btn_confirmar_pagamento.pack(side=tk.RIGHT)


    def _atualizar_status_pagamento(self):
        total_pago_pelo_jogador = 0
        total_cedulas_usadas = 0
        temp_cedulas_usadas = {}
        try:
            for den, str_var in self.entry_widgets_cedulas.items():
                try:
                    quantidade = int(str_var.get())
                except ValueError:
                    quantidade = 0 
                    str_var.set("0") 

                if quantidade < 0: 
                    str_var.set("0")
                    quantidade = 0
                
                if quantidade > 0: # Só adiciona ao dicionário se a quantidade for > 0
                    temp_cedulas_usadas[den] = quantidade

                total_pago_pelo_jogador += den * quantidade # Soma ao total pago mesmo se for 0 para o display
                total_cedulas_usadas += quantidade 
            
            self.player_cedulas_usadas = temp_cedulas_usadas 

        except Exception as e: 
            print(f"Erro em _atualizar_status_pagamento: {e}")
            pass 

        cor_valor = "red" if total_pago_pelo_jogador != self.valor_a_pagar_informante else "dark green"
        status_texto = (f"Total Montado para Pagamento: {total_pago_pelo_jogador} créditos\n"
                        f"Número de Cédulas Usadas: {total_cedulas_usadas}")
        
        if hasattr(self, 'status_pagamento_label') and self.status_pagamento_label and self.status_pagamento_label.winfo_exists():
            self.status_pagamento_label.config(text=status_texto, foreground=cor_valor)

    def _desabilitar_controles_missao2(self):
        if self.btn_confirmar_pagamento and self.btn_confirmar_pagamento.winfo_exists():
            self.btn_confirmar_pagamento.config(state=tk.DISABLED)
        if hasattr(self, 'btn_dica_m2') and self.btn_dica_m2 and self.btn_dica_m2.winfo_exists():
            self.btn_dica_m2.config(state=tk.DISABLED)
        for str_var_key in self.entry_widgets_cedulas:
            pass 


    def mostrar_dica_coin_changing(self):
        messagebox.showinfo("Dica da Rebelião", 
                            "Comandante, para minimizar o número de cédulas e evitar atenção, comece sempre tentando usar as cédulas de MAIOR VALOR disponíveis que não excedam o montante restante a pagar.\n\n"
                            "Pague o máximo possível com elas antes de passar para a próxima denominação menor. Essa é a essência da estratégia gulosa para este problema.")

    def avaliar_pagamento_jogador(self):
        self._atualizar_status_pagamento() 
        self._desabilitar_controles_missao2()

        # Recalcula a partir de self.player_cedulas_usadas que SÓ contém entradas > 0
        total_pago_pelo_jogador = sum(den * qtd for den, qtd in self.player_cedulas_usadas.items())
        numero_cedulas_jogador = sum(self.player_cedulas_usadas.values())

        # --- INÍCIO DOS PRINTS DE DEPURAÇÃO ---
        print("-" * 30)
        print("DEPURAÇÃO - AVALIAR PAGAMENTO JOGADOR (MISSÃO 2):")
        print(f"  Valor a Pagar (Objetivo da Missão): {self.valor_a_pagar_informante}")
        print(f"  Total Efetivamente Pago pelo Jogador (calculado a partir de player_cedulas_usadas): {total_pago_pelo_jogador}")
        print(f"  Cédulas Usadas pelo Jogador (detalhe, apenas >0): {self.player_cedulas_usadas}")
        print(f"  Número de Cédulas do Jogador (soma das quantidades >0): {numero_cedulas_jogador}")
        # --- FIM DOS PRINTS DE DEPURAÇÃO ---

        if total_pago_pelo_jogador > self.valor_a_pagar_informante:
            self.game_manager.add_score(-100) 
            falha_msg1 = (
                f"Pagamento Excessivo! Comandante, você pagou {total_pago_pelo_jogador} créditos, mas o combinado era {self.valor_a_pagar_informante}.\n"
                "Fulcrum (via comunicador, irritado): \"RZ-479, qual parte de 'pagamento exato' não ficou clara? "
                "Essa 'gorjeta' não autorizada compromete a discrição e nossos orçamentos! Você perdeu 100 pontos de confiança por essa imprudência.\""
            )
            falha_msg2_criativa = (
                "O informante parece confuso com o dinheiro extra, depois sorri de forma gananciosa. Más notícias viajam rápido. "
                "Outros contatos agora esperam 'bônus', tornando futuras negociações um pesadelo."
            )
            self.game_manager.mission_failed_options(self, falha_msg1, falha_msg2_criativa)
            return

        elif total_pago_pelo_jogador < self.valor_a_pagar_informante:
            falha_msg1 = (
                f"Pagamento Insuficiente! Comandante, você pagou apenas {total_pago_pelo_jogador} créditos dos {self.valor_a_pagar_informante} devidos.\n"
                "O informante se sente insultado e se recusa a cooperar no futuro. Perdemos um contato valioso por sua negligência."
            )
            falha_msg2_criativa = (
                "O informante conta o dinheiro, franze a testa e cospe no chão. \"Acha que sou algum tipo de pedinte da Orla Exterior? "
                "A Aliança Rebelde vai precisar de mais do que trocados para comprar minha lealdade... ou meu silêncio.\" "
                "A comunicação é cortada. Uma oportunidade perdida."
            )
            self.game_manager.mission_failed_options(self, falha_msg1, falha_msg2_criativa)
            return

        print(f"  Valor sendo passado para calcular_troco: {self.valor_a_pagar_informante}")
        
        cedulas_otimas_dict, numero_otimo_cedulas = calcular_troco(
            self.denominacoes_imperiais, self.valor_a_pagar_informante
        )

        if cedulas_otimas_dict is not None:
            print(f"  Solução Ótima Calculada (Detalhe): {cedulas_otimas_dict}")
            print(f"  Número Ótimo de Cédulas: {numero_otimo_cedulas}")
        else:
            print("  Não foi possível calcular a solução ótima com calcular_troco.")
        print("-" * 30)


        if numero_otimo_cedulas == -1: 
            messagebox.showerror("Erro de Cálculo Interno", 
                                 "Houve um problema ao calcular o pagamento ótimo com as denominações fornecidas. Contacte o suporte da Aliança (desenvolvedor).")
            if self.btn_confirmar_pagamento and self.btn_confirmar_pagamento.winfo_exists():
                self.btn_confirmar_pagamento.config(state=tk.NORMAL) # Reabilita para tentar corrigir
            return

        if numero_cedulas_jogador == numero_otimo_cedulas:
            self.game_manager.add_score(150) 
            messagebox.showinfo("Pagamento Efetuado!",
                                f"Pagamento realizado com sucesso e discrição, Comandante!\n"
                                f"Você usou {numero_cedulas_jogador} cédulas, a forma mais eficiente possível.\n"
                                "O informante está satisfeito e Fulcrum elogia sua prudência.")
            self.game_manager.mission_completed("Missao2")
        else:
            falha_msg1 = (
                "PAGAMENTO SUSPEITO! Comandante, o valor está correto, mas você usou "
                f"{numero_cedulas_jogador} cédulas, quando era possível com {numero_otimo_cedulas}. "
                "Um volume desnecessário de créditos pode ter chamado a atenção de observadores Imperiais. O informante sumiu... tememos o pior."
            )
            falha_msg2_criativa = (
                "Fulcrum (voz tensa): \"RZ-479, nosso contato foi detido por uma 'transação suspeita de grande volume'. "
                "Seus métodos precisam ser mais sutis. A vida de nossos agentes depende disso.\""
            )
            self.game_manager.mission_failed_options(self, falha_msg1, falha_msg2_criativa)

    def retry_mission(self):
        self.game_manager.set_game_state("START_MISSION_2")