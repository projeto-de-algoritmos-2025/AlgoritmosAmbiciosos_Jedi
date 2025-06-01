import tkinter as tk
from tkinter import ttk, messagebox, font as tkFont

from algoritmos.selecting_breakpoints import calcular_paradas_reabastecimento


class Missao6:
    def __init__(self, root, game_manager, content_frame_para_missao):
        self.root = root
        self.game_manager = game_manager
        self.base_content_frame = content_frame_para_missao

        # Fontes
        self.narrative_font = self.game_manager.narrative_font
        self.button_font = self.game_manager.button_font
        self.header_font = self.game_manager.header_font
        self.item_font = tkFont.Font(family="Arial", size=10)

        # Dados da Missão
        self.distancia_total = 100
        self.localizacoes_postos = sorted([15, 30, 45, 60, 80, 90])
        self.capacidade_nave = 25
        self.breakpoints = [0] + self.localizacoes_postos + [self.distancia_total]
        self.paradas_otimas_indices = calcular_paradas_reabastecimento(self.capacidade_nave, self.breakpoints)
        self.paradas_otimas_localizacoes = [self.breakpoints[i] for i in self.paradas_otimas_indices] if self.paradas_otimas_indices else []

        # Estado
        self.postos_selecionados = []
        self.lista_checkbuttons = []
        self.status_label = None
        self.falhas_na_missao6 = 0
        self.dica_count_m6 = 0

    def _clear_mission_frame(self):
        if self.base_content_frame and self.base_content_frame.winfo_exists():
            for widget in self.base_content_frame.winfo_children():
                widget.destroy()

    def iniciar_missao_contexto(self):
        self._clear_mission_frame()
        self.falhas_na_missao6 = 0  # Reset
        ttk.Label(self.base_content_frame, text="MISSÃO 6: Rota Crítica - Abastecimento Estratégico", font=self.header_font).pack(pady=10)

        contexto = (
            "Fulcrum: \"Comandante, sua missão é crucial. Planeje cuidadosamente onde reabastecer ao longo da rota para minimizar as paradas e evitar detecções.\n\n"
            f"Distância total: {self.distancia_total} unidades estelares.\n"
            f"Postos de reabastecimento disponíveis nas distâncias: {', '.join(map(str, self.localizacoes_postos))}.\n"
            f"Capacidade da sua nave: {self.capacidade_nave} unidades.\""
        )
        texto_contexto = tk.Text(self.base_content_frame, wrap=tk.WORD, height=6, relief=tk.FLAT,
                                 background=self.root.cget('bg'), font=self.narrative_font, padx=10, pady=10)
        texto_contexto.insert(tk.END, contexto)
        texto_contexto.config(state=tk.DISABLED)
        texto_contexto.pack(pady=15, padx=10, fill=tk.X)

        ttk.Button(self.base_content_frame, text="Selecionar Postos de Abastecimento...",
                   command=self.exibir_selecao_postos, style="Accent.TButton").pack(pady=20)

    def exibir_selecao_postos(self):
        self._clear_mission_frame()
        ttk.Label(self.base_content_frame, text="Selecione os Postos de Abastecimento", font=self.header_font).pack(pady=10)
        instrucoes = "Marque os postos onde você deseja reabastecer. Lembre-se de considerar a capacidade da sua nave de 25."
        ttk.Label(self.base_content_frame, text=instrucoes, font=self.narrative_font).pack(pady=10)

        self.postos_selecionados = []
        checkbuttons_frame = ttk.Frame(self.base_content_frame)
        checkbuttons_frame.pack(pady=10)
        self.lista_checkbuttons = []

        for i, posto in enumerate(self.localizacoes_postos):
            var = tk.BooleanVar()
            cb = ttk.Checkbutton(checkbuttons_frame, text=f"Parar no posto em {posto}", variable=var)
            cb.pack(anchor="w")
            self.lista_checkbuttons.append((posto, var))

        botoes_frame = ttk.Frame(self.base_content_frame)
        botoes_frame.pack(pady=20)

        ttk.Button(botoes_frame, text="Confirmar Seleção e Avaliar Rota...",
                   command=self.avaliar_escolhas_jogador, style="Accent.TButton").pack(side=tk.LEFT, padx=5)
        ttk.Button(botoes_frame, text="Pedir Dica", command=self.dar_dica_m6).pack(side=tk.LEFT, padx=5)

    def avaliar_escolhas_jogador(self):
        postos_escolhidos = sorted([posto for posto, var in self.lista_checkbuttons if var.get()])
        rota_completa = self.simular_rota_jogador(postos_escolhidos)

        if not rota_completa:
            self.falhas_na_missao6 += 1
            msg = "Sua rota é inválida! A nave ficou sem combustível.\n"
            if self.falhas_na_missao6 == 1:
                msg += "\nFulcrum: \"Reavalie sua estratégia, Comandante. Pode tentar novamente.\""
            else:
                msg += "\nFulcrum: \"Estamos comprometidos com o sucesso da missão. Ajuste o plano.\""
            messagebox.showerror("Falha na Rota", msg)
            self.exibir_selecao_postos()
        else:
            self._avaliar_eficiencia(postos_escolhidos)

    def _avaliar_eficiencia(self, postos_escolhidos):
        num_paradas = len(postos_escolhidos)
        num_otimas = len(self.paradas_otimas_localizacoes)

        msg = f"Rota concluída com {num_paradas} paradas: {', '.join(map(str, postos_escolhidos))}.\n"
        msg += f"Plano ótimo: {num_otimas} paradas (nos postos {', '.join(map(str, self.paradas_otimas_localizacoes))}).\n\n"

        if sorted(postos_escolhidos) == sorted(self.paradas_otimas_localizacoes):
            msg += "Estratégia perfeita! Coincide com o plano ótimo."
            self.game_manager.add_score(90)
        elif num_paradas == num_otimas:
            msg += "Bom trabalho! Mesmo número de paradas do plano ideal."
            self.game_manager.add_score(80)
        else:
            msg += "Missão concluída, mas sua rota teve mais paradas que o ideal."
            self.game_manager.add_score(60)

        messagebox.showinfo("Análise Final", msg)
        self.game_manager.mission_completed("Missao6")

    def simular_rota_jogador(self, postos):
        combustivel = self.capacidade_nave
        local = 0
        paradas = [0] + sorted(postos) + [self.distancia_total]

        for i in range(1, len(paradas)):
            distancia = paradas[i] - local
            if distancia > combustivel:
                return False
            combustivel -= distancia
            local = paradas[i]
            if i < len(paradas) - 1:
                combustivel = self.capacidade_nave
        return True

    def dar_dica_m6(self):
        self.dica_count_m6 += 1
        if self.dica_count_m6 == 1:
            dica = (
                "DICA 1 - Fulcrum:\n"
                "Comece sempre com o tanque cheio. Depois de cada parada, você pode reabastecer completamente.\n"
                "Planeje para nunca ultrapassar os 25 de autonomia entre dois postos."
            )
        elif self.dica_count_m6 == 2:
            dica = (
                "DICA 2 - Estratégia Ótima:\n"
                "Tente avançar o máximo possível até onde a nave alcança, sem parar em todos os postos.\n"
                "Pense como em um jogo de 'fuga': o mínimo de paradas possível, sem ficar sem combustível."
            )
        else:
            dica = (
                "DICA FINAL:\n"
                "Experimente simular manualmente com papel os trechos e veja onde precisa MESMO parar.\n"
                "Pense: de 0 até onde consigo? E depois, de lá até onde mais?"
            )

        messagebox.showinfo("Conselho Estratégico de Fulcrum", dica)
