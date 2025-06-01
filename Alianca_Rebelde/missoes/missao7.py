import tkinter as tk
from tkinter import ttk, messagebox, font as tkFont
from algoritmos.huffman import construir_arvore_huffman, gerar_codigos_huffman

class Missao7:
    def __init__(self, root, game_manager, content_frame_para_missao):
        self.root = root
        self.game_manager = game_manager
        self.base_content_frame = content_frame_para_missao

        self.header_font = self.game_manager.header_font
        self.narrative_font = self.game_manager.narrative_font
        self.button_font = self.game_manager.button_font
        self.item_font = tkFont.Font(family="Arial", size=10)

        self.codigos_gerados = {}
        self.mensagem_original = ""
        self.mensagem_codificada = ""
        self.dica_count = 0

    def _clear_frame(self):
        for widget in self.base_content_frame.winfo_children():
            widget.destroy()

    def iniciar_missao_contexto(self):
        self._clear_frame()

        ttk.Label(self.base_content_frame, text="MISSÃO 7: Comunicação Segura", font=self.header_font).pack(pady=10)

        contexto = (
            "Fulcrum: \"Comandante, precisamos transmitir uma mensagem de forma segura. "
            "Use a Codificação de Huffman para codificar sua mensagem. "
            "Após gerar os códigos, substitua cada letra da mensagem pelo respectivo código binário.\""
        )
        texto = tk.Text(self.base_content_frame, wrap=tk.WORD, height=6, relief=tk.FLAT,
                        background=self.root.cget('bg'), font=self.narrative_font, padx=10, pady=10)
        texto.insert(tk.END, contexto)
        texto.config(state=tk.DISABLED)
        texto.pack(pady=10, padx=10, fill=tk.X)

        ttk.Label(self.base_content_frame, text="Digite a mensagem a ser codificada: ", font=self.narrative_font).pack()
        self.input_mensagem = tk.Entry(self.base_content_frame, width=50, font=self.item_font)
        self.input_mensagem.pack(pady=5)

        ttk.Button(self.base_content_frame, text="Gerar Códigos Huffman", command=self.gerar_codificacao, style="Accent.TButton").pack(pady=10)

    def gerar_codificacao(self):
        self.mensagem_original = self.input_mensagem.get().strip().upper()
        if not self.mensagem_original or not all(c.isalpha() or c == " " for c in self.mensagem_original):
            messagebox.showerror("Erro", "Digite apenas letras e espaços.")
            return

        raiz = construir_arvore_huffman(self.mensagem_original)
        self.codigos_gerados = gerar_codigos_huffman(raiz)
        self.mensagem_codificada = ''.join(self.codigos_gerados[c] for c in self.mensagem_original)

        self.exibir_interface_codificacao()

    def exibir_interface_codificacao(self):
        self._clear_frame()

        ttk.Label(self.base_content_frame, text="Códigos Gerados por Huffman:", font=self.button_font).pack(pady=(5, 0))
        codigos_frame = ttk.Frame(self.base_content_frame)
        codigos_frame.pack(pady=5)
        for char in sorted(self.codigos_gerados.keys()):
            ttk.Label(codigos_frame, text=f"'{char}': {self.codigos_gerados[char]}", font=self.item_font).pack(anchor="w")

        ttk.Label(self.base_content_frame, text=f"Mensagem original: {self.mensagem_original}", font=self.item_font).pack(pady=(10, 5))

        instrucoes = "Agora, substitua manualmente cada caractere da mensagem por seu código binário."
        ttk.Label(self.base_content_frame, text=instrucoes, font=self.narrative_font, wraplength=600).pack(pady=5)

        ttk.Label(self.base_content_frame, text="Digite a mensagem codificada (em binário):", font=self.narrative_font).pack()
        self.input_codificada = tk.Entry(self.base_content_frame, width=80, font=self.item_font)
        self.input_codificada.pack(pady=5)

        botoes = ttk.Frame(self.base_content_frame)
        botoes.pack(pady=10)
        ttk.Button(botoes, text="Validar Codificação", command=self.verificar_codificacao, style="Accent.TButton").pack(side=tk.LEFT, padx=5)
        ttk.Button(botoes, text="Pedir Dica", command=self.mostrar_dica).pack(side=tk.LEFT, padx=5)

    def verificar_codificacao(self):
        tentativa = self.input_codificada.get().strip().replace(" ", "")
        correta = self.mensagem_codificada

        if tentativa == correta:
            pontos = 90
            messagebox.showinfo("Codificação Correta!", f"Mensagem codificada corretamente!\nPontos: {pontos}")
            self.game_manager.add_score(pontos)
            self.game_manager.mission_completed("Missao7")
        else:
            self.dica_count += 1
            if self.dica_count < 3:
                messagebox.showwarning("Codificação Incorreta", "Algo não bate. Verifique se usou todos os códigos corretamente.")
            else:
                messagebox.showerror("Falha na Codificação", f"A mensagem correta seria:\n{correta}")
                self.game_manager.add_score(30)
                self.game_manager.mission_completed("Missao7")

    def mostrar_dica(self):
        dicas = [
            "DICA 1 - Substitua letra por letra, da esquerda para a direita.",
            "DICA 2 - Verifique se todos os códigos usados estão iguais aos da tabela.",
            f"DICA FINAL - A mensagem resultante deve ter {len(self.mensagem_codificada)} bits."
        ]
        indice = min(self.dica_count, len(dicas) - 1)
        messagebox.showinfo("Conselho Estratégico de Fulcrum", dicas[indice])
