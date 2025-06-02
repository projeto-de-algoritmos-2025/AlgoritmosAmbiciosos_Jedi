# missoes/missao6.py
import tkinter as tk
from tkinter import ttk, messagebox, font as tkFont
import random # Importado para a geração de dados aleatórios da missão
from algoritmos.selecting_breakpoints import calcular_paradas_reabastecimento

class Missao6:
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
        except AttributeError:
            print("AVISO Missao6: Cores do GameManager não encontradas. Usando fallbacks.")
            self.cor_fundo_base = "black"
            self.cor_texto_principal = "white"
            self.cor_texto_titulo_missao = "orangered"
            self.cor_texto_info = "lightblue"

        # Fontes (acessando os objetos de fonte corretos do GameManager com _obj)
        try:
            self.narrative_font_obj = self.game_manager.narrative_font_obj
            self.button_font_obj = self.game_manager.button_font_obj
            self.header_font_obj = self.game_manager.header_font_obj
            self.small_bold_font_obj = self.game_manager.small_bold_font_obj 
            
            default_family_for_local_fonts = "Arial" 
            if hasattr(self.game_manager, 'default_font_family'):
                default_family_for_local_fonts = self.game_manager.default_font_family
            self.item_font_obj = tkFont.Font(family=default_family_for_local_fonts, size=10) # CORRIGIDO: item_font_obj
        except AttributeError:
            print("AVISO Missao6: Falha ao carregar fontes _obj do GameManager. Usando fallbacks.")
            default_family_fallback = "Arial"
            self.narrative_font_obj = tkFont.Font(family=default_family_fallback, size=12)
            self.button_font_obj = tkFont.Font(family=default_family_fallback, size=11, weight="bold")
            self.header_font_obj = tkFont.Font(family=default_family_fallback, size=20, weight="bold")
            self.small_bold_font_obj = tkFont.Font(family=default_family_fallback, size=10, weight="bold")
            self.item_font_obj = tkFont.Font(family=default_family_fallback, size=10) # CORRIGIDO: item_font_obj

        
        # Dados da Missão (serão recalculados)
        self.distancia_total = 0
        self.localizacoes_postos = []
        self.capacidade_nave = 0
        self.breakpoints = []
        self.paradas_otimas_indices = []
        self.paradas_otimas_localizacoes = []

        # Estado
        self.postos_selecionados_vars = {} 
        self.falhas_na_missao6 = 0
        self.dica_count_m6 = 0
        
        # Referências UI
        self.btn_dica_m6 = None 
        self.btn_avaliar_m6 = None

    def _recalcular_dados_missao(self):
        """Recalcula os dados da missão para cada nova tentativa."""
        self.distancia_total = random.randint(800, 1200)
        num_postos = random.randint(7, 12)
        postos_set = set()
        min_dist_entre_postos = int(self.distancia_total / (num_postos * 2)) 
        
        primeiro_posto_min = int(self.distancia_total * 0.05) # Não muito perto do início
        primeiro_posto_max = int(self.distancia_total * 0.2)  # Mas não muito longe
        if primeiro_posto_min >= primeiro_posto_max: primeiro_posto_min = 1

        primeiro_posto = random.randint(primeiro_posto_min, primeiro_posto_max)
        if primeiro_posto < self.distancia_total: # Garante que o primeiro posto não seja o destino
            postos_set.add(primeiro_posto)

        # Garante que a capacidade da nave seja gerada antes de usá-la para min_dist_entre_postos
        # (embora min_dist_entre_postos não dependa diretamente da capacidade_nave na lógica atual)
        # A capacidade será definida após os postos para melhor adequação.

        max_tentativas_geracao_postos = num_postos * 5 # Evita loop infinito
        tentativas_atuais = 0
        while len(postos_set) < num_postos and tentativas_atuais < max_tentativas_geracao_postos:
            posto_candidato = random.randint(1, self.distancia_total - 1)
            valido = True
            if not postos_set: # Se for o primeiro posto a ser adicionado (além do 'primeiro_posto' já talvez adicionado)
                 postos_set.add(posto_candidato)
                 continue

            for p_existente in postos_set:
                if abs(posto_candidato - p_existente) < min_dist_entre_postos:
                    valido = False
                    break
            if valido:
                postos_set.add(posto_candidato)
            tentativas_atuais +=1
        
        self.localizacoes_postos = sorted(list(postos_set))
        
        # Define capacidade da nave após os postos serem definidos
        max_gap = 0
        temp_rota_para_gap = [0] + self.localizacoes_postos + [self.distancia_total]
        if len(temp_rota_para_gap) > 1: # Evita erro se temp_rota_para_gap tiver só um elemento (improvável)
            for i in range(len(temp_rota_para_gap) - 1):
                max_gap = max(max_gap, temp_rota_para_gap[i+1] - temp_rota_para_gap[i])
        else: # Fallback se só houver origem e destino (sem postos intermediários)
            max_gap = self.distancia_total

        if max_gap == 0 : max_gap = 100 # Segurança para evitar capacidade 0

        self.capacidade_nave = random.randint(int(max_gap * 1.05), int(max_gap * 1.7)) # Garante que pode fazer o maior salto
        self.capacidade_nave = max(self.capacidade_nave, 50) # Mínimo absoluto de capacidade

        self.breakpoints = [0] + self.localizacoes_postos + [self.distancia_total]
        
        try:
            self.paradas_otimas_indices = calcular_paradas_reabastecimento(self.capacidade_nave, self.breakpoints)
            if self.paradas_otimas_indices is None: 
                 print("AVISO Missao6: Não foi possível calcular uma rota ótima com os dados gerados.")
                 self.paradas_otimas_localizacoes = ["Cálculo da Rota Ótima Falhou"]
            else:
                self.paradas_otimas_localizacoes = [self.breakpoints[i] for i in self.paradas_otimas_indices]
        except Exception as e: 
            print(f"Erro ao calcular paradas ótimas: {e}")
            self.paradas_otimas_indices = [] 
            self.paradas_otimas_localizacoes = ["Erro no Cálculo da Rota Ótima"]

        print("--- Missão 6: Novos Dados Gerados ---")
        print(f"Distância Total: {self.distancia_total}")
        print(f"Postos: {self.localizacoes_postos}")
        print(f"Capacidade Nave: {self.capacidade_nave}")
        print(f"Paradas Ótimas (locais): {self.paradas_otimas_localizacoes}")
        print("-----------------------------------")

    def _clear_mission_frame(self):
        if self.base_content_frame and self.base_content_frame.winfo_exists():
            for widget in self.base_content_frame.winfo_children():
                widget.destroy()

    def limpar_interface_missao_completa(self):
        self._clear_mission_frame()

    def _reset_mission_state(self):
        """Reseta o estado interno da missão para uma nova tentativa ou início."""
        self.grupos_extracao_base = list(self.grupos_extracao_base_original) # Recarrega os dados base se precisar
        self.localizacoes_postos = [] # Será recalculado
        self.capacidade_nave = 0    # Será recalculado
        self.breakpoints = []
        self.paradas_otimas_indices = []
        self.paradas_otimas_localizacoes = []
        self.postos_selecionados_vars = {} 
        self.falhas_na_missao6 = 0
        self.dica_count_m6 = 0
        
    def iniciar_missao_contexto(self):
        self._clear_mission_frame()
        self._recalcular_dados_missao() 
        self.falhas_na_missao6 = 0  
        self.dica_count_m6 = 0

        tk.Label(self.base_content_frame, text="MISSÃO 6: Rota Crítica - Abastecimento Estratégico", 
                 font=self.header_font_obj, fg=self.cor_texto_titulo_missao, bg=self.cor_fundo_base, pady=5).pack(pady=(0,15), fill=tk.X, padx=20)

        contexto = (
            "Fulcrum: \"Comandante, a expansão de nossas operações exige novas rotas de suprimento seguras através de território hostil. "
            "Nossas naves de transporte têm uma autonomia limitada e paradas frequentes aumentam o risco de detecção.\n\n"
            f"Sua tarefa é traçar uma rota de **{self.distancia_total} unidades estelares**.\n"
            f"Os postos de reabastecimento seguros identificados estão nas seguintes distâncias da origem: **{', '.join(map(str, self.localizacoes_postos))}**.\n"
            f"A autonomia máxima da sua nave após cada reabastecimento é de **{self.capacidade_nave} unidades estelares**.\n\n"
            "Selecione o MÍNIMO de postos de reabastecimento para completar a jornada. Cada parada é um risco!\""
        )
        
        text_context_container = tk.Frame(self.base_content_frame, bg=self.cor_fundo_base)
        text_context_container.pack(pady=10, padx=30, fill=tk.X)
        texto_contexto_widget = tk.Text(text_context_container, wrap=tk.WORD, height=10, relief=tk.FLAT,
                                 font=self.narrative_font_obj, padx=10, pady=10,
                                 borderwidth=0, highlightthickness=0,
                                 background=self.cor_fundo_base, fg=self.cor_texto_principal, insertbackground=self.cor_texto_principal)
        texto_contexto_widget.insert(tk.END, contexto)
        texto_contexto_widget.config(state=tk.DISABLED)
        texto_contexto_widget.pack(fill=tk.X, expand=True)

        button_container = ttk.Frame(self.base_content_frame, style="Black.TFrame")
        button_container.pack(pady=20)
        ttk.Button(button_container, text="Selecionar Postos de Abastecimento...",
                   command=self.exibir_selecao_postos, style="Accent.Dark.TButton").pack()

    def exibir_selecao_postos(self):
        self._clear_mission_frame()
        
        tk.Label(self.base_content_frame, text="Selecione os Postos de Abastecimento", 
                 font=self.header_font_obj, fg=self.cor_texto_titulo_missao, bg=self.cor_fundo_base, pady=5).pack(pady=(0,10), fill=tk.X, padx=20)
        
        instrucoes = f"Marque os postos onde você deseja reabastecer. Capacidade da nave: {self.capacidade_nave} unidades."
        tk.Label(self.base_content_frame, text=instrucoes, 
                 font=self.narrative_font_obj, fg=self.cor_texto_principal, bg=self.cor_fundo_base, wraplength=700).pack(pady=10)

        checkbuttons_container = tk.Frame(self.base_content_frame, bg=self.cor_fundo_base)
        checkbuttons_container.pack(pady=10, padx=20)
        
        self.postos_selecionados_vars = {} 
        max_cols = 3 
        col_count = 0
        current_row_frame = None

        for i, posto in enumerate(self.localizacoes_postos):
            if col_count % max_cols == 0:
                current_row_frame = ttk.Frame(checkbuttons_container, style="Black.TFrame")
                current_row_frame.pack(fill=tk.X, anchor="center") 
            
            var = tk.BooleanVar()
            cb = ttk.Checkbutton(current_row_frame, text=f"Parar no posto em {posto}", 
                                 variable=var, style="Dark.TCheckbutton") # Estilo definido no GameManager
            cb.pack(side=tk.LEFT, anchor="w", padx=10, pady=2)
            self.postos_selecionados_vars[posto] = var
            col_count +=1

        botoes_frame = ttk.Frame(self.base_content_frame, style="Black.TFrame")
        botoes_frame.pack(pady=20, fill=tk.X, padx=20)

        self.btn_avaliar_m6 = ttk.Button(botoes_frame, text="Confirmar Seleção e Avaliar Rota...",
                                         command=self.avaliar_escolhas_jogador, style="Accent.Dark.TButton")
        self.btn_avaliar_m6.pack(side=tk.LEFT, padx=5, expand=True) 
        
        self.btn_dica_m6 = ttk.Button(botoes_frame, text="Pedir Dica", command=self.dar_dica_m6, style="Dark.TButton")
        self.btn_dica_m6.pack(side=tk.RIGHT, padx=5, expand=True)

    def avaliar_escolhas_jogador(self):
        if hasattr(self, 'btn_avaliar_m6') and self.btn_avaliar_m6 and self.btn_avaliar_m6.winfo_exists():
            self.btn_avaliar_m6.config(state=tk.DISABLED)
        if hasattr(self, 'btn_dica_m6') and self.btn_dica_m6 and self.btn_dica_m6.winfo_exists():
            self.btn_dica_m6.config(state=tk.DISABLED)
        
        postos_escolhidos_pelo_jogador = sorted([posto for posto, var in self.postos_selecionados_vars.items() if var.get()])
        rota_valida, ultimo_ponto_alcancado, _ = self.simular_rota_jogador(postos_escolhidos_pelo_jogador)

        if not rota_valida:
            self.falhas_na_missao6 += 1
            msg_falha_base = (f"Falha na Rota! Sua nave ficou sem combustível após o ponto {ultimo_ponto_alcancado}, "
                              f"antes de alcançar o próximo destino ou o final da rota ({self.distancia_total}).\n"
                              "Não subestime a vastidão do espaço (e a capacidade do tanque), Comandante!")
            fulcrum_msg = ""
            if self.falhas_na_missao6 == 1:
                fulcrum_msg = "\n\nFulcrum: \"RZ-479, um erro de cálculo pode acontecer. Reavalie sua estratégia. Pode tentar novamente.\""
            else:
                fulcrum_msg = "\n\nFulcrum (com impaciência): \"Comandante, estamos contando com sua perícia. A Aliança não pode arcar com perdas de naves. Ajuste o plano!\""
            self.game_manager.mission_failed_options(self, msg_falha_base + fulcrum_msg, 
                                                     "Fulcrum: \"Talvez uma calculadora de rotas da Orla Exterior fosse útil? Ou apenas mais atenção aos limites da nave.\"")
            return 
        else:
            self._avaliar_eficiencia(postos_escolhidos_pelo_jogador)

    def _avaliar_eficiencia(self, postos_escolhidos_pelo_jogador):
        num_paradas_jogador = len(postos_escolhidos_pelo_jogador)
        
        houve_erro_no_calculo_otimo = False
        if not self.paradas_otimas_localizacoes: 
            pass 
        elif isinstance(self.paradas_otimas_localizacoes[0], str) and "Cálculo" in self.paradas_otimas_localizacoes[0]:
            houve_erro_no_calculo_otimo = True

        if houve_erro_no_calculo_otimo:
             messagebox.showerror("Erro de Planejamento Interno", 
                                 "Não foi possível determinar a rota ótima para comparação. A missão será reiniciada.", 
                                 parent=self.base_content_frame)
             self.retry_mission()
             return

        num_paradas_otimas = len(self.paradas_otimas_localizacoes)
        msg = f"Rota Concluída!\nSua rota utilizou {num_paradas_jogador} paradas: {', '.join(map(str, postos_escolhidos_pelo_jogador)) if postos_escolhidos_pelo_jogador else 'Nenhuma'}.\n"
        msg += f"O plano ótimo exigiria {num_paradas_otimas} paradas: {', '.join(map(str, self.paradas_otimas_localizacoes)) if self.paradas_otimas_localizacoes else 'Nenhuma (rota direta)'}.\n\n"
        pontos_ganhos_m6 = 0
        penalidade_aplicada = False

        if sorted(postos_escolhidos_pelo_jogador) == sorted(self.paradas_otimas_localizacoes):
            msg += "Fulcrum: \"Estratégia perfeita, Comandante! Rota ótima. Mínimo de paradas, máxima eficiência.\""
            pontos_ganhos_m6 = 120 
        elif num_paradas_jogador == num_paradas_otimas:
            msg += "Fulcrum: \"Bom trabalho. Mesmo número de paradas do ideal. Sucesso tático.\""
            pontos_ganhos_m6 = 100
        elif num_paradas_jogador < num_paradas_otimas + 2 : 
            msg += "Fulcrum: \"Missão concluída. Rota com algumas paradas a mais, risco ligeiramente aumentado, mas objetivo alcançado.\" "
            pontos_ganhos_m6 = 70 
        else: 
            if self.primeira_falha_nesta_tentativa_m6:
                self.game_manager.add_score(-50) 
                messagebox.showwarning("Penalidade", "Rota ineficiente resultou em penalidade de 50 pontos.", parent=self.base_content_frame)
                self.primeira_falha_nesta_tentativa_m6 = False
                penalidade_aplicada = True 
            msg += "Fulcrum (com um suspiro): \"Comandante, rota concluída, mas com paradas excessivas. Cada parada extra é um risco. Precisamos ser mais eficientes.\" "
            pontos_ganhos_m6 = 30 
        self.game_manager.add_score(pontos_ganhos_m6)
        if not penalidade_aplicada: 
            msg += f"\n\nVocê ganhou {pontos_ganhos_m6} pontos de influência!"
            messagebox.showinfo("Análise Final da Rota", msg, parent=self.base_content_frame)
        else: 
            messagebox.showinfo("Análise Final da Rota", msg + f"\n\nVocê recebeu {pontos_ganhos_m6} pontos por completar a missão, apesar da ineficiência.", parent=self.base_content_frame)
        self.game_manager.mission_completed("Missao6")

    def simular_rota_jogador(self, postos_escolhidos_pelo_jogador):
        # ... (Este método permanece EXATAMENTE o mesmo da sua versão anterior) ...
        # Certifique-se que a lógica aqui é robusta para os dados gerados.
        local_atual_sim = 0
        paradas_jogador_com_inicio_fim = [0] + sorted(list(set(postos_escolhidos_pelo_jogador))) + [self.distancia_total]
        paradas_unicas = []
        for p in paradas_jogador_com_inicio_fim:
            if not paradas_unicas or p > paradas_unicas[-1]: # Garante ordem crescente e unicidade
                paradas_unicas.append(p)
        paradas_jogador_com_inicio_fim = paradas_unicas

        for i in range(len(paradas_jogador_com_inicio_fim) - 1):
            dist_segmento = paradas_jogador_com_inicio_fim[i+1] - paradas_jogador_com_inicio_fim[i]
            if dist_segmento < 0: 
                 print(f"DEBUG: Erro na lógica de simulação - distância negativa {dist_segmento}")
                 return False, paradas_jogador_com_inicio_fim[i], 0
            if dist_segmento > self.capacidade_nave:
                print(f"DEBUG Rota Inválida (Jogador): De {paradas_jogador_com_inicio_fim[i]} para {paradas_jogador_com_inicio_fim[i+1]} ({dist_segmento}) > Capacidade ({self.capacidade_nave})")
                return False, paradas_jogador_com_inicio_fim[i], 0 
        return True, self.distancia_total, 0 


    def dar_dica_m6(self):
        # ... (Este método permanece EXATAMENTE o mesmo da sua versão anterior) ...
        self.dica_count_m6 += 1; dica = ""
        if self.dica_count_m6 == 1:
            dica = (f"DICA 1 - Fulcrum:\n\"Sua nave parte com tanque cheio. Após cada parada, considere o tanque cheio novamente. O crucial é que a distância até a PRÓXIMA PARADA (ou destino) não exceda a autonomia de {self.capacidade_nave} unidades.\"")
        elif self.dica_count_m6 == 2:
            dica = ("DICA 2 - Estratégia Gulosa:\n\"Para minimizar paradas, do seu local atual, avance o MÁXIMO que seu combustível permitir. O posto ideal para a PRÓXIMA parada é o SEGURO MAIS DISTANTE alcançável. Repita.\"")
        else:
            dica = ("DICA FINAL:\n\"Não basta alcançar o próximo posto. Garanta que, DELE, você ainda alcance o seguinte ou o destino final. Às vezes, parar um pouco antes é a chave.\"")
            if self.btn_dica_m6 and self.btn_dica_m6.winfo_exists(): self.btn_dica_m6.config(state=tk.DISABLED)
        messagebox.showinfo("Conselho Estratégico de Fulcrum", dica, parent=self.base_content_frame)

    def retry_mission(self):
        print(f"Missao6: retry_mission chamada.")
        self.game_manager.set_game_state("START_MISSION_6")