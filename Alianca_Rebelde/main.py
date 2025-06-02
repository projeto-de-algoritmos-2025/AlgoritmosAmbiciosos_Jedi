# main.py
import tkinter as tk
from tkinter import ttk, messagebox, font as tkFont, PhotoImage
import random 
import os 

# Tenta importar as missões e os minigames.
try:
    from missoes.missao1 import Missao1
    from missoes.missao2 import Missao2
    from missoes.missao3 import Missao3
    from missoes.missao4 import Missao4
    from missoes.missao5 import Missao5 
    from missoes.missao6 import Missao6
    from missoes.missao7 import Missao7
    # Certifique-se que os nomes dos arquivos e classes dos minigames estão corretos:
    from missoes.minigame_bfs_extração import MinigameBFSExtracao 
    from missoes.minigame_rpg_kruskal import MinigameKruskalContraAtaque 
except ImportError as e:
    print(f"ALERTA DE IMPORTAÇÃO DE MÓDULO: {e}")
    print("Verifique se todas as classes de Missão e Minigame estão nos arquivos corretos dentro da pasta 'missoes/'")
    print("e se as pastas 'missoes/' e 'algoritmos/' contêm um arquivo __init__.py (pode ser vazio).")
    print("CRUCIAL: Verifique também se NENHUM arquivo em 'missoes/' está tentando fazer 'from main import ...'.")


class GameManager:
    def __init__(self, root_tk):
        self.root = root_tk
        self.root.title("Aliança Rebelde - Operações Críticas")
        self.root.configure(bg="black") 

        try:
            self.root.geometry("850x650") 
        except tk.TclError:
            print("Aviso: Não foi possível definir a geometria inicial da janela.")

        # --- Carregar Imagens ---
        self.alianca_simbolo_photo = None
        self.alianca_inicio_photo = None 
        self.alianca_visor_photo = None 
        self.alianca_comunicacao_photo = None # <<< NOVA IMAGEM PARA COMUNICAÇÃO

        try:
            simbolo_path = "alianca_simbolo.png" 
            if os.path.exists(simbolo_path):
                self.alianca_simbolo_photo = PhotoImage(file=simbolo_path)
                print(f"DEBUG: Imagem alianca_simbolo.png carregada.")
            else:
                # Lógica de fallback para assets/images (opcional)
                script_dir = os.path.dirname(os.path.abspath(__file__))
                fallback_path = os.path.join(script_dir, "assets", "images", "alianca_simbolo.png")
                if os.path.exists(fallback_path):
                    self.alianca_simbolo_photo = PhotoImage(file=fallback_path)
                    print(f"DEBUG: Imagem alianca_simbolo.png carregada de {fallback_path}.")
                else:
                    print(f"AVISO: Imagem alianca_simbolo.png NÃO ENCONTRADA.")
            
            inicio_path = "Alianca_Inicio.png" 
            if os.path.exists(inicio_path):
                self.alianca_inicio_photo = PhotoImage(file=inicio_path)
                print(f"DEBUG: Imagem Alianca_Inicio.png carregada.")
            else:
                print(f"AVISO: Imagem Alianca_Inicio.png NÃO ENCONTRADA.")

            visor_path = "alianca_visor.png" 
            if os.path.exists(visor_path):
                self.alianca_visor_photo = PhotoImage(file=visor_path)
                print(f"DEBUG: Imagem alianca_visor.png carregada.")
            else:
                print(f"AVISO: Imagem alianca_visor.png NÃO ENCONTRADA.")
            
            comunicacao_path = "alianca_comunicacao.png" # <<< CARREGA A NOVA IMAGEM
            if os.path.exists(comunicacao_path):
                self.alianca_comunicacao_photo = PhotoImage(file=comunicacao_path)
                print(f"DEBUG: Imagem alianca_comunicacao.png carregada.")
            else:
                print(f"AVISO: Imagem alianca_comunicacao.png NÃO ENCONTRADA.")


        except Exception as e_img:
            print(f"AVISO: Erro ao carregar uma das imagens: {e_img}")


        # --- Cores base para o modo escuro ---
        self.bg_color_dark = "black"
        self.fg_color_light = "white"
        self.title_color_accent = "orangered" 
        self.points_color = "#87CEFA" 
        self.button_bg_color_std = "#333333"
        self.button_text_color = "white"   
        self.button_active_bg_std = "#444444"
        self.accent_button_bg_color = "#0078D7" 
        self.accent_button_fg = "white"
        self.accent_button_active_bg = "#005A9E"

        # --- Configuração de Fontes ---
        self.default_font_family = "Arial" 
        try:
            self.default_font_obj = tkFont.Font(family=self.default_font_family, size=11)
            self.narrative_font_obj = tkFont.Font(family=self.default_font_family, size=12)
            self.button_font_obj = tkFont.Font(family=self.default_font_family, size=11, weight="bold")
            self.header_font_obj = tkFont.Font(family=self.default_font_family, size=20, weight="bold")
            self.small_bold_font_obj = tkFont.Font(family=self.default_font_family, size=10, weight="bold")
            self.points_font_obj = tkFont.Font(family=self.default_font_family, size=12, weight="bold", slant="italic")
        except tk.TclError: 
            print("Aviso: Fontes tkFont.Font não configuradas. Usando fallback.")
            self.default_font_obj = (self.default_font_family, 11)
            self.narrative_font_obj = (self.default_font_family, 12)
            self.button_font_obj = (self.default_font_family, 11, "bold")
            self.header_font_obj = (self.default_font_family, 20, "bold")
            self.small_bold_font_obj = (self.default_font_family, 10, "bold")
            self.points_font_obj = (self.default_font_family, 12, "bold", "italic")

        # --- Estilo ttk para Modo Escuro ---
        style = ttk.Style()
        available_themes = style.theme_names()
        preferred_themes = ['clam', 'alt', 'default', 'xpnative', 'vista'] 
        theme_to_use = next((t for t in preferred_themes if t in available_themes), 'default')
        try:
            style.theme_use(theme_to_use)
        except tk.TclError:
            print(f"Aviso: Tema ttk '{theme_to_use}' não pôde ser aplicado.")
        
        try: 
            style.configure("Black.TFrame", background=self.bg_color_dark)
            style.configure("TLabel", background=self.bg_color_dark, foreground=self.fg_color_light, font=self.default_font_obj)
            style.configure("Points.TLabel", background=self.bg_color_dark, foreground=self.points_color, font=self.points_font_obj)
            style.configure("Dark.TButton", font=self.button_font_obj, foreground=self.button_text_color, background=self.button_bg_color_std, padding=5)
            style.map("Dark.TButton", background=[('active', self.button_active_bg_std), ('pressed', self.button_bg_color_std)], relief=[('pressed', 'sunken'), ('!pressed', 'raised')])
            style.configure("Accent.Dark.TButton", font=self.button_font_obj, foreground=self.accent_button_fg, background=self.accent_button_bg_color, padding=10)
            style.map("Accent.Dark.TButton", background=[('active', self.accent_button_active_bg), ('pressed', self.accent_button_bg_color)])
        except tk.TclError:
            print("Aviso: Não foi possível configurar todos os estilos ttk para o modo escuro.")

        self.player_score = 0 
        self.current_mission_obj = None 
        self.content_frame = None 
        self.game_state = "INTRO_1A" 
        self.update_display()
        
    def _clear_content_frame(self):
        if self.content_frame:
            self.content_frame.pack_forget()
            for widget in self.content_frame.winfo_children():
                widget.destroy()
            self.content_frame.destroy()
        self.content_frame = ttk.Frame(self.root, padding="20", style="Black.TFrame") 
        self.content_frame.pack(fill=tk.BOTH, expand=True)

    def _display_text_screen(self, title_text, narrative_text_lines, button_text, 
                             next_state_or_command, button_style="Dark.TButton", 
                             image_to_display=None): 
        title_label = tk.Label(self.content_frame, text=title_text, 
                               font=self.header_font_obj, 
                               anchor="center", 
                               bg=self.bg_color_dark, 
                               fg=self.title_color_accent, 
                               pady=5) 
        title_label.pack(pady=(0, 15), fill=tk.X, padx=20)
        
        text_container_frame = tk.Frame(self.content_frame, bg=self.bg_color_dark)
        text_container_frame.pack(pady=5, padx=40, expand=True, fill=tk.BOTH) 
        full_narrative_text = "\n\n".join(narrative_text_lines)
        text_widget = tk.Text(text_container_frame, wrap=tk.WORD, height=10, 
                              relief=tk.FLAT, 
                              background=self.bg_color_dark, foreground=self.fg_color_light, 
                              insertbackground=self.fg_color_light, 
                              font=self.narrative_font_obj, padx=10, pady=10, 
                              borderwidth=0, highlightthickness=0)
        text_widget.insert(tk.END, full_narrative_text)
        text_widget.config(state=tk.DISABLED)
        text_widget.pack(expand=True, fill=tk.BOTH, padx=5, pady=5)
        
        if image_to_display: 
            try:
                imagem_label = tk.Label(self.content_frame, image=image_to_display, 
                                         bg=self.bg_color_dark) 
                imagem_label.pack(pady=(10, 5))
            except tk.TclError: 
                print(f"AVISO: Falha ao exibir imagem no _display_text_screen para o título '{title_text}'.")
        
        command_to_run = next_state_or_command
        if isinstance(next_state_or_command, str):
            command_to_run = lambda: self.set_game_state(next_state_or_command)

        button_container = ttk.Frame(self.content_frame, style="Black.TFrame")
        pady_button_container = (5 if image_to_display else 15, 10) 
        button_container.pack(pady=pady_button_container, side=tk.BOTTOM, fill=tk.X, anchor="s")
        
        actual_button_style = "Accent.Dark.TButton" if button_style == "Accent.TButton" else "Dark.TButton"
        ttk.Button(button_container, text=button_text, command=command_to_run, style=actual_button_style).pack(pady=5)

    def update_display(self):
        self._clear_content_frame() 

        if self.game_state == "INTRO_1A":
            narrativa = ["Seus olhos se abrem para uma escuridão quebrada apenas pelo brilho rubro das luzes de emergência.",
                         "O ar denso carrega o cheiro acre de metal superaquecido e circuitos queimados.",
                         "Sua cabeça lateja, a dor ecoando a violência de um impacto recente."]
            self._display_text_screen("Despertar", narrativa, "...", "INTRO_1B", 
                                      image_to_display=self.alianca_inicio_photo) 
        elif self.game_state == "INTRO_1B":
            narrativa = ["Fragmentos de memória turbilhonam: alarmes estrondosos, a vertigem de uma fuga desesperada, a escuridão da queda...",
                         "Você tenta se lembrar quem é. Emerge a identidade de um(a) estrategista.",
                         "Talvez um passado ligado ao Império, agora uma fonte de conhecimento perigoso. Ou a chama de um idealista, forjado(a) na luta de um mundo subjugado."]
            self._display_text_screen("Fragmentos", narrativa, "Lembrar o propósito...", "INTRO_1C", 
                                      image_to_display=self.alianca_inicio_photo) 
        elif self.game_state == "INTRO_1C":
            self.current_mission_obj = None 
            narrativa = ["Não importa o passado exato, uma convicção resiste à confusão: a opressão que consome a galáxia precisa ser combatida.",
                         "À sua frente, o painel da sua nave improvisada pisca erraticamente. Os sistemas de suporte de vida, teimosamente, ainda funcionam.",
                         "A nave está à deriva, um casco ferido, mas você está vivo(a)."]
            self._display_text_screen("Sobrevivência", narrativa, "Avaliar Danos e Sistemas...", "INTRO_2A", 
                                      button_style="Accent.Dark.TButton", image_to_display=self.alianca_inicio_photo)
        elif self.game_state == "INTRO_2A":
            narrativa = ["Com um gemido de esforço, você se arrasta até o console principal. Luzes de alerta vermelhas pintam seu rosto.",
                         "Um diagnóstico rápido revela sua posição: um setor pouco mapeado na Orla Exterior.",
                         "Por ora, uma sorte frágil; você está fora das rotas de patrulha imperiais."]
            self._display_text_screen("Diagnóstico Precário", narrativa, "Analisar a situação...", "INTRO_2B", 
                                      image_to_display=self.alianca_visor_photo) 
        elif self.game_state == "INTRO_2B":
            narrativa = ["Mas essa 'segurança' é uma ilusão. As memórias das últimas notícias antes do... incidente... são sombrias: o Império avança, implacável.",
                         "Cada sistema que cai é um grito silenciado, mais um passo da galáxia em direção a uma escuridão uniforme."]
            self._display_text_screen("A Sombra do Império", narrativa, "Considerar os próximos passos...", "INTRO_2C", 
                                      image_to_display=self.alianca_visor_photo) 
        elif self.game_state == "INTRO_2C":
            narrativa = ["Apesar da dor, sua mente analítica desperta. Logística, tática, a habilidade de encontrar saídas impossíveis... Essas ferramentas não podem se perder aqui.",
                         "Terminar à deriva não é uma opção. A Rebelião, por menor que seja sua chama, precisa de cada centelha."]
            self._display_text_screen("A Chama da Resistência", narrativa, "Tentar Contato com Aliados...", "INTRO_DIALOGUE_A", 
                                      button_style="Accent.Dark.TButton", image_to_display=self.alianca_comunicacao_photo) # <<< IMAGEM AQUI
        elif self.game_state == "INTRO_DIALOGUE_A":
            narrativa = ["Você desvia a pouca energia restante para os comunicadores de longo alcance. A estática domina, um mar de ruído cósmico.",
                         "Pacientemente, você varre as frequências de emergência conhecidas...",
                         "Quando a esperança começa a minguar, um padrão fraco, quase imperceptível, emerge. Um antigo código de autenticação da Aliança Rebelde. Seu transmissor de emergência, ativado na queda, deve ter sido detectado."]
            self._display_text_screen("Eco no Vazio", narrativa, "Aguardar identificação do sinal...", "INTRO_DIALOGUE_B",
                                      image_to_display=self.alianca_comunicacao_photo) # <<< IMAGEM AQUI
        elif self.game_state == "INTRO_DIALOGUE_B":
            self._display_fulcrum_dialogue() 
        elif self.game_state == "GAME_OVER_DECLINED":
            self.current_mission_obj = None 
            narrativa = ["Você desliga o comunicador. A luta... não é mais para você. Talvez um planeta pacato no Anel Externo.",
                         "A Rebelião terá que encontrar outro herói. A galáxia continua sua dança de guerra e paz, mas sua parte nela parece ter chegado ao fim.", "FIM DE JOGO"]
            self._display_text_screen("Fim da Linha... Ou Um Novo Começo?", narrativa, "Sair do Jogo", self.root.quit, button_style="Dark.TButton", image_to_display=self.alianca_simbolo_photo)
        
        elif self.game_state == "START_MISSION_1":
            if 'Missao1' in globals(): self.current_mission_obj = Missao1(self.root, self, self.content_frame); self.current_mission_obj.iniciar_missao_contexto()
            else: messagebox.showerror("Erro Crítico", "Missao1 não carregada."); self.root.quit()
        elif self.game_state == "MISSION_1_SUCCESS_DIALOGUE_A": 
            self.current_mission_obj = None; dialogo = ["Fulcrum (via comunicador): \"RZ-479, relatório recebido. A célula de Atravis confirma a chegada dos suprimentos.\"", "\"Sua eficiência na otimização da carga foi... notável. Salvou vidas e garantiu recursos essenciais para uma operação que estava por um fio. Bom trabalho, Comandante.\""]
            self._display_text_screen("Relatório de Atravis: Sucesso!", dialogo, "Agradecer. Às ordens, Fulcrum.", "MISSION_1_SUCCESS_DIALOGUE_B", image_to_display=self.alianca_simbolo_photo)
        elif self.game_state == "MISSION_1_SUCCESS_DIALOGUE_B":
            dialogo = ["Fulcrum: \"Há mais uma questão delicada referente a essa operação, Comandante.\"", "\"A inteligência para a rota segura de Atravis veio de um informante... um tanto quanto volátil e caro. Ele espera seu pagamento...\"", "\"Precisamos que esse pagamento seja o mais discreto possível – usando o menor número de cédulas...\""]
            self._display_text_screen("Pendência Urgente: O Informante", dialogo, "Entendido. Qual o procedimento?", "START_MISSION_2", button_style="Accent.Dark.TButton", image_to_display=self.alianca_simbolo_photo)
        elif self.game_state == "START_MISSION_2":
            if 'Missao2' in globals(): self.current_mission_obj = Missao2(self.root, self, self.content_frame); self.current_mission_obj.iniciar_missao_contexto()
            else: messagebox.showerror("Erro Crítico", "Missao2 não carregada."); self.root.quit()
        elif self.game_state == "MISSION_2_SUCCESS_FULCRUM_A": 
            self.current_mission_obj = None; dialogo = ["Fulcrum (com raro tom de aprovação): \"Excelente trabalho com o pagamento, RZ-479...\"", "\"O informante está satisfeito... Suas ações estão começando a construir uma reputação...\" "]
            self._display_text_screen("Pagamento Confirmado", dialogo, "Pronta para o próximo.", "MISSION_2_SUCCESS_FULCRUM_B", image_to_display=self.alianca_simbolo_photo)
        elif self.game_state == "MISSION_2_SUCCESS_FULCRUM_B":
            dialogo = ["Fulcrum: \"Contudo, não há tempo para descanso... alerta em Dantooine III...\"", "\"Acabei de receber um alerta... Preciso de alguém com sua capacidade tática...\" "]
            self._display_text_screen("Novos Rumores e Perigos", dialogo, "Relate a situação.", "RPG_SCENARIO_SETUP", button_style="Accent.Dark.TButton", image_to_display=self.alianca_simbolo_photo)
        elif self.game_state == "RPG_SCENARIO_SETUP": self._display_rpg_scenario_setup() 
        elif self.game_state == "RPG_CHOICE_PROMPT": self._display_rpg_choice_prompt() 
        elif self.game_state == "RPG_CHOICE_B_MINIGAME_SETUP": 
            if 'MinigameBFSExtracao' in globals(): self.current_mission_obj = MinigameBFSExtracao(self.root, self, self.content_frame, recompensa_sucesso=60, id_escolha_rpg="B"); self.current_mission_obj.iniciar_minigame_interface()
            else: messagebox.showerror("Erro Crítico", "MinigameBFSExtracao não carregado."); self.set_game_state("RPG_CHOICE_PROMPT")
        elif self.game_state == "RPG_CHOICE_C_MINIGAME_SETUP": 
            if 'MinigameKruskalContraAtaque' in globals(): self.current_mission_obj = MinigameKruskalContraAtaque(self.root, self, self.content_frame, recompensa_sucesso=150, id_escolha_rpg="C"); self.current_mission_obj.iniciar_minigame_interface()
            else: messagebox.showerror("Erro Crítico", "MinigameKruskalContraAtaque não carregado."); self.set_game_state("RPG_CHOICE_PROMPT")
        elif self.game_state == "RPG_CHOICE_A_RESULT": 
            narrativa = ["Com astúcia e nervos de aço, você guia a Patrulha Eco através de uma série de dutos de ventilação esquecidos, emergindo longe do combate principal. A retirada é tensa, com alguns arranhões, mas todos os membros da equipe estão a salvo e o equipamento essencial foi preservado.", "Fulcrum (pelo comunicador, após seu relatório): \"Sua prudência salvou vidas preciosas hoje, RZ-479. Uma retirada bem executada é, muitas vezes, a manobra mais corajosa. No entanto, a oportunidade de obter dados valiosos do terminal imperial no posto foi perdida. Não se pode ter tudo, suponho.\""]
            self._display_text_screen("Retirada Tática Concluída", narrativa, "Próxima designação.", "LEAD_IN_TO_MISSION_3", image_to_display=self.alianca_simbolo_photo)
        elif self.game_state == "RPG_CHOICE_B_MINIGAME_SUCCESS": 
            narrativa = [f"Os 30 Pontos de Influência foram cruciais! Com os canais de comunicação priorizados, você coordenou uma defesa sólida enquanto guiava a Patrulha Eco para o ponto de extração pelo caminho mais seguro, identificado por sua análise tática. A nave de resgate chegou sob fogo leve, mas conseguiu extrair todos.", "Alguns dados importantes foram recuperados do terminal antes da evacuação às pressas.", "Fulcrum: \"Impressionante, Comandante. Sua análise e coordenação foram impecáveis. Esta operação rendeu um bônus de 60 pontos para seus futuros esforços e inteligência valiosa.\""]
            self._display_text_screen("Extração Bem-Sucedida!", narrativa, "Aguardando ordens.", "LEAD_IN_TO_MISSION_3", image_to_display=self.alianca_simbolo_photo)
        elif self.game_state == "RPG_CHOICE_B_MINIGAME_FAIL":
             narrativa = ["Apesar dos seus esforços e do uso dos 30 Pontos de Influência para melhorar as comunicações, a rota de extração escolhida ou a coordenação da defesa se provou inadequada. A equipe sofreu baixas consideráveis e apenas fragmentos de dados foram recuperados antes que a situação se tornasse insustentável.", "Fulcrum: \"Uma pena, Comandante. Às vezes, mesmo com recursos adicionais, o campo de batalha é imprevisível. Os pontos de influência foram gastos, mas o resultado não foi o esperado. Precisamos analisar o que deu errado.\""]
             self._display_text_screen("Extração Complicada", narrativa, "Entendido. Próxima.", "LEAD_IN_TO_MISSION_3", image_to_display=self.alianca_simbolo_photo)
        elif self.game_state == "RPG_CHOICE_C_MINIGAME_SUCCESS": 
            narrativa = [f"Um investimento alto de 70 Pontos de Influência, mas com um retorno espetacular! Seu plano de contra-ataque, utilizando o equipamento adicional e a estratégia de rede de comunicação que você estabeleceu, foi brilhante. Os stormtroopers foram pegos de surpresa e neutralizados.", "A Patrulha Eco não apenas escapou, como também assegurou o posto de escuta, capturando informações vitais sobre movimentações de frotas imperiais.", "Fulcrum: \"Uma manobra audaciosa e recompensadora, RZ-479! Sua coragem e brilhantismo tático nos renderam um ganho estratégico imenso. Você ganhou um bônus de 150 pontos. Excelente!\""]
            self._display_text_screen("Vitória Decisiva!", narrativa, "Qual o próximo passo?", "LEAD_IN_TO_MISSION_3", image_to_display=self.alianca_simbolo_photo)
        elif self.game_state == "RPG_CHOICE_C_MINIGAME_FAIL":
            narrativa = ["O contra-ataque foi feroz, mas a estratégia para neutralizar as defesas ou superar a força inimiga falhou...", "Fulcrum: \"Uma aposta ousada, Comandante... Precisamos aprender com cada revés.\""]
            self._display_text_screen("Contra-Ataque Frustrado", narrativa, "Compreendido.", "LEAD_IN_TO_MISSION_3", image_to_display=self.alianca_simbolo_photo)
        elif self.game_state == "LEAD_IN_TO_MISSION_3": 
            self.current_mission_obj = None; fulcrum_mission3_brief = ("Fulcrum: \"Comandante, a situação no setor Arkanis se intensificou. Suas recentes ações, independentemente do resultado em Dantooine, nos mostraram a necessidade de operações mais amplas e coordenadas para desestabilizar o controle Imperial na região. Temos múltiplas janelas de oportunidade para inteligência e sabotagem, mas nossos recursos de campo são perigosamente limitados. Cada ação deve ser precisamente cronometrada para máximo impacto e, crucialmente, para a segurança de nossos agentes. Sua próxima tarefa é coordenar este complexo balé de operações secretas.\"")
            self._display_text_screen("Designação: Operação Sincronia Arkanis", [fulcrum_mission3_brief], "Aceito. Detalhes.", "START_MISSION_3", button_style="Accent.Dark.TButton", image_to_display=self.alianca_simbolo_photo)
        elif self.game_state == "START_MISSION_3":
            if 'Missao3' in globals(): self.current_mission_obj = Missao3(self.root, self, self.content_frame); self.current_mission_obj.iniciar_missao_contexto()
            else: messagebox.showerror("Erro Crítico", "Missao3 não carregada."); self.root.quit()
        elif self.game_state == "MISSION_3_SUCCESS_FULCRUM_A": 
            self.current_mission_obj = None; fulcrum_m3_praise = ("Fulcrum (impressionado): \"RZ-479, os relatórios do setor Arkanis são... exemplares...\"") 
            self._display_text_screen("Sucesso Estratégico em Arkanis", [fulcrum_m3_praise], "Agradeço.", "MISSION_3_SUCCESS_FULCRUM_B", image_to_display=self.alianca_simbolo_photo)
        elif self.game_state == "MISSION_3_SUCCESS_FULCRUM_B":
            fulcrum_m3_next_step = ("Fulcrum: \"Sua perícia em escalonamento tático é inegável e já está se tornando lendária em certos círculos. Com o Corredor de Arkanis mais instável para o Império, "
                                    "surge uma nova emergência que exige sua atenção imediata: uma evacuação crítica e de alto risco no sistema Kessel.\"") 
            self._display_text_screen("Nova Emergência: Kessel", [fulcrum_m3_next_step], "Kessel? Relate.", "START_MISSION_4", button_style="Accent.Dark.TButton", image_to_display=self.alianca_simbolo_photo)
        elif self.game_state == "START_MISSION_4":
            self.current_mission_obj = None 
            if 'Missao4' in globals(): self.current_mission_obj = Missao4(self.root, self, self.content_frame); self.current_mission_obj.iniciar_missao_contexto()
            else: messagebox.showerror("Erro Crítico", "Missao4 não carregada."); self.root.quit()
        elif self.game_state == "MISSION_4_SUCCESS_FULCRUM_A": 
            self.current_mission_obj = None ; fulcrum_m4_praise = ("Fulcrum (com um tom de alívio palpável): \"Comandante RZ-479, os últimos transportes de Kessel acabaram de sair do sistema, "
                                 "escapando por pouco do bloqueio imperial. Sua coordenação sob aquela contagem regressiva foi... magistral. "
                                 "Muitos operativos e civis importantes devem suas vidas à sua capacidade de tomar decisões rápidas e precisas sob pressão extrema.\"")
            self._display_text_screen("Evacuação de Kessel Concluída", [fulcrum_m4_praise], "Cumprimos o dever.", "MISSION_4_SUCCESS_FULCRUM_B", image_to_display=self.alianca_simbolo_photo)
        elif self.game_state == "MISSION_4_SUCCESS_FULCRUM_B": 
            fulcrum_m4_next_task = ("Fulcrum: \"De fato. Suas ações em Kessel nos deram não apenas pessoal valioso, mas também dados cruciais sobre as táticas de bloqueio imperiais. "
                                    "Com base nisso, identificamos uma nova frente de oportunidade: o Império está tentando expandir sua rede de vigilância no Setor Bryx. "
                                    "Precisamos otimizar nossos poucos recursos de patrulha para cobrir o máximo de território possível e monitorar essas movimentações com o mínimo de esquadrões.\" ")
            self._display_text_screen("Novos Desafios: Olhos no Setor Bryx", [fulcrum_m4_next_task], "Entendido. Plano para Bryx?", "START_MISSION_5", button_style="Accent.Dark.TButton", image_to_display=self.alianca_simbolo_photo)
        elif self.game_state == "START_MISSION_5":
            self.current_mission_obj = None 
            if 'Missao5' in globals(): self.current_mission_obj = Missao5(self.root, self, self.content_frame); self.current_mission_obj.iniciar_missao_contexto()
            else: messagebox.showerror("Erro Crítico", "Missao5 não carregada."); self.root.quit()
        elif self.game_state == "MISSION_5_SUCCESS_FULCRUM_A":
            self.current_mission_obj = None; fulcrum_m5_praise = ("Fulcrum: \"Comandante, seu gerenciamento de recursos no Setor Bryx foi exemplar. Conseguimos manter a vigilância necessária com um número mínimo de esquadrões, otimizando nossos ativos de forma crucial.\"")
            self._display_text_screen("Vigilância Otimizada no Setor Bryx", [fulcrum_m5_praise], "Próxima prioridade?", "MISSION_5_SUCCESS_FULCRUM_B", image_to_display=self.alianca_simbolo_photo)
        elif self.game_state == "MISSION_5_SUCCESS_FULCRUM_B":
            fulcrum_m5_next_task = ("Fulcrum: \"Sua capacidade de otimizar recursos será novamente testada. Recebemos informações sobre uma rota de suprimentos imperial crítica que passa por um setor com poucos postos de reabastecimento seguros para nós. Precisamos interceptar esse carregamento, mas o planejamento da rota de aproximação exigirá um gerenciamento cuidadoso do combustível.\"")
            self._display_text_screen("Nova Tarefa: Interceptação Crítica", [fulcrum_m5_next_task], "Prepare os detalhes.", "START_MISSION_6", button_style="Accent.Dark.TButton", image_to_display=self.alianca_simbolo_photo)
        elif self.game_state == "START_MISSION_6":
            self.current_mission_obj = None 
            if 'Missao6' in globals(): self.current_mission_obj = Missao6(self.root, self, self.content_frame); self.current_mission_obj.iniciar_missao_contexto()
            else: messagebox.showerror("Erro Crítico", "Missao6 não carregada."); self.root.quit()
        elif self.game_state == "MISSION_6_SUCCESS_FULCRUM_A":
            self.current_mission_obj = None; fulcrum_m6_praise = ("Fulcrum: \"Comandante, a eficiência do seu planejamento de reabastecimento foi notável. Evitamos patrulhas imperiais e alcançamos o destino com recursos mínimos, assegurando a interceptação.\"")
            self._display_text_screen("Rota Segura Estabelecida", [fulcrum_m6_praise], "Próxima missão?", "MISSION_6_SUCCESS_FULCRUM_B", image_to_display=self.alianca_simbolo_photo)
        elif self.game_state == "MISSION_6_SUCCESS_FULCRUM_B":
            fulcrum_m6_next_task = ("Fulcrum: \"Resta uma última tarefa, Comandante, de importância vital. Precisamos enviar um relatório completo de todas as nossas recentes operações para o Alto Comando. Os canais estão fortemente monitorados. A única forma segura é através de codificação avançada que reduza o tamanho da mensagem e dificulte a interceptação.\" ")
            self._display_text_screen("Desafio Final: Transmissão Segura", [fulcrum_m6_next_task], "Entendido. Preparar.", "START_MISSION_7", button_style="Accent.Dark.TButton", image_to_display=self.alianca_simbolo_photo)
        elif self.game_state == "START_MISSION_7":
            self.current_mission_obj = None 
            if 'Missao7' in globals(): self.current_mission_obj = Missao7(self.root, self, self.content_frame); self.current_mission_obj.iniciar_missao_contexto()
            else: messagebox.showerror("Erro Crítico", "Missao7 não carregada."); self.root.quit()
        elif self.game_state == "ALL_MISSIONS_COMPLETED":
             self.current_mission_obj = None; titulo_final = "Uma Nova Esperança Desperta"
             narrativa_final = [ 
                f"Comandante RZ-479, suas vitórias consecutivas ecoam pelos canais secretos da Aliança Rebelde. De Atravis a Kessel, do Setor Arkanis aos confins de Bryx, e além, sua liderança estratégica e sua capacidade de converter desafios aparentemente impossíveis em triunfos reacenderam a chama da esperança em inúmeros sistemas oprimidos.",
                f"O Império Galáctico sentiu o peso de suas ações. Embora a guerra pela liberdade da galáxia esteja longe de terminar, seus feitos provaram que a tirania pode ser desafiada, que a astúcia, a lógica e a coragem ainda podem alterar o curso das estrelas.",
                f"Com {self.player_score} Pontos de Influência acumulados, você não é apenas um(a) ativo(a) valioso(a), mas uma inspiração crescente dentro das fileiras da Aliança. Muitos agora olham para você como um símbolo do que podemos alcançar quando a estratégia encontra a determinação.",
                "Descanse, Comandante. Reabasteça suas forças e prepare seu espírito.",
                "A Aliança precisará de sua mente brilhante novamente, pois novas frentes se abrirão e a luta pela liberdade continuará... até que cada canto escuro da galáxia conheça a luz.",
                "Que a Força esteja com você, sempre."
             ]
             self._display_text_screen(titulo_final, narrativa_final, "A Luta Continua... (Encerrar Jogo)", self.root.quit, 
                                       button_style="Accent.Dark.TButton", image_to_display=self.alianca_simbolo_photo)
        else: 
            tk.Label(self.content_frame, text=f"Estado de jogo desconhecido: {self.game_state}", font=self.header_font_obj, fg="red", bg=self.bg_color_dark).pack(pady=20)


    def _display_fulcrum_dialogue(self): 
        self._clear_content_frame() 
        title = "Contato: Fulcrum"
        narrative_fulcrum_lines = [
            "Uma voz calma, com um tom pragmático e levemente cansado, corta a estática: \"Sinal de emergência RZ-479. Aqui é Fulcrum.\"",
            "\"Nossos registros são antigos, mas indicam que essa designação pertence a um(a) oficial de estratégia... marcado(a) como 'comprometido(a) e irrecuperável' após o incidente em Cygnus VII.\"",
            "\"Se for você, e se ainda estiver funcional, responda. Temos uma operação em andamento que demanda sua especialidade. A situação é... delicada. Precisamos de resultados, não de heróis. Confirme seu status.\""
        ]
        
        tk.Label(self.content_frame, text=title, 
                 font=self.header_font_obj, anchor="center", 
                 bg=self.bg_color_dark, fg=self.title_color_accent, pady=5).pack(pady=(0,15), fill=tk.X, padx=20)
        
        text_widget = tk.Text(self.content_frame, wrap=tk.WORD, height=8, relief=tk.FLAT,
                              background=self.bg_color_dark, foreground=self.fg_color_light, insertbackground=self.fg_color_light,
                              font=self.narrative_font_obj, padx=10, pady=10, borderwidth=0, highlightthickness=0)
        text_widget.insert(tk.END, "\n\n".join(narrative_fulcrum_lines))
        text_widget.config(state=tk.DISABLED)
        text_widget.pack(pady=10, padx=30, expand=True, fill=tk.BOTH)

        if self.alianca_simbolo_photo:
            simbolo_label = tk.Label(self.content_frame, image=self.alianca_simbolo_photo,
                                     bg=self.bg_color_dark) 
            simbolo_label.pack(pady=(10,5))

        button_frame = ttk.Frame(self.content_frame, style="Black.TFrame")
        pady_btn_cont = (5, 15) if self.alianca_simbolo_photo else (10, 20)
        button_frame.pack(pady=pady_btn_cont)

        btn_aceitar = ttk.Button(button_frame, text="Fulcrum, aqui RZ-479. Status: funcional, mas avariado. À disposição.",
                                 command=lambda: self.set_game_state("START_MISSION_1"), style="Accent.Dark.TButton")
        btn_aceitar.pack(side=tk.LEFT, padx=10, pady=5)
        btn_recusar = ttk.Button(button_frame, text="Silêncio. (O passado não pode me alcançar)",
                                 command=lambda: self.set_game_state("GAME_OVER_DECLINED"), style="Dark.TButton")
        btn_recusar.pack(side=tk.LEFT, padx=10, pady=5)

    def _display_rpg_scenario_setup(self): 
        self.current_mission_obj = None
        title = "Alerta Urgente!"
        narrativa = [
            "Fulcrum (a voz tensa): \"Comandante, interceptei uma transmissão de emergência! Uma de nossas equipes de reconhecimento avançado, a 'Patrulha Eco', foi emboscada no antigo posto de escuta imperial em Dantooine III. Estão sob fogo pesado de stormtroopers e completamente encurralados!\"",
            "\"Eles precisam de uma decisão tática IMEDIATA ou serão dizimados. Você é o(a) oficial de mais alta patente com contato no momento.\""
        ]
        self._display_text_screen(title, narrativa, "Analisar Opções Táticas...", "RPG_CHOICE_PROMPT", 
                                  button_style="Accent.Dark.TButton", image_to_display=self.alianca_simbolo_photo)

    def _display_rpg_choice_prompt(self):
        self._clear_content_frame() 
        title = "Decisão Crítica: Posto de Dantooine III"
        tk.Label(self.content_frame, text=title, font=self.header_font_obj, fg=self.title_color_accent, bg=self.bg_color_dark, pady=5).pack(pady=(0,15), fill=tk.X, padx=20)
        ttk.Label(self.content_frame, text=f"Seus Pontos de Influência Atuais: {self.player_score}", 
                  font=self.points_font_obj, style="Points.TLabel").pack(pady=(0,15))
        scenario_desc = "A Patrulha Eco está presa, com munição baixa. Stormtroopers avançam por dois flancos. As opções são limitadas e arriscadas:"
        desc_label_container = tk.Frame(self.content_frame, bg=self.bg_color_dark)
        desc_label_container.pack(pady=5, padx=30)
        desc_label = tk.Label(desc_label_container, text=scenario_desc, wraplength=700, 
                               justify=tk.CENTER, font=self.narrative_font_obj, 
                               bg=self.bg_color_dark, fg=self.fg_color_light)
        desc_label.pack()
        if self.alianca_simbolo_photo: 
            simbolo_label = tk.Label(self.content_frame, image=self.alianca_simbolo_photo, bg=self.bg_color_dark)
            simbolo_label.pack(pady=(5,10))
        options_button_frame = ttk.Frame(self.content_frame, style="Black.TFrame")
        options_button_frame.pack(pady=10) 
        choices_data = [
            {"id": "A", "text": "Retirada Tática pelos Dutos", "cost": 0, "next_state": "RPG_CHOICE_A_RESULT", "desc": "Busca uma rota de fuga alternativa. Menor risco, mas sem ganhos táticos diretos."},
            {"id": "B", "text": "Defesa Coordenada e Extração Urgente", "cost": 30, "next_state": "RPG_CHOICE_B_MINIGAME_SETUP", "desc": "Prioriza comunicadores para coordenar defesa e solicitar extração. Risco moderado, possível recuperação de dados."},
            {"id": "C", "text": "Contra-Ataque Ousado", "cost": 70, "next_state": "RPG_CHOICE_C_MINIGAME_SETUP", "desc": "Requisita blasters pesados e granadas para romper o cerco. Alto risco, mas potencial para ganhos de inteligência significativos."}
        ]
        for choice in choices_data: 
            choice_frame = ttk.Frame(options_button_frame, style="Black.TFrame") 
            choice_frame.pack(fill=tk.X, pady=3)
            btn_text = f"{choice['id']}: {choice['text']} (Custo: {choice['cost']} Pontos)"
            can_afford = self.player_score >= choice['cost']
            actual_button_style = "Accent.Dark.TButton" if can_afford and choice['cost'] > 0 else "Dark.TButton"
            if not can_afford and choice['id'] != "A": actual_button_style = "Dark.TButton"
            btn_state = tk.NORMAL if can_afford else tk.DISABLED
            btn = ttk.Button(choice_frame, text=btn_text, width=60, style=actual_button_style, state=btn_state,
                               command=lambda ch_id=choice['id'], ch_cost=choice['cost'], ch_next=choice['next_state']: self.handle_rpg_choice(ch_id, ch_cost, ch_next))
            btn.pack(pady=3, fill=tk.X)
            desc_choice_label = tk.Label(choice_frame, text=choice['desc'], font=self.small_bold_font_obj, wraplength=550, justify=tk.CENTER, bg=self.bg_color_dark, fg=self.fg_color_light)
            desc_choice_label.pack(pady=(0,8))

    def handle_rpg_choice(self, choice_id, cost, next_state_after_cost_check):
        if self.player_score >= cost:
            if cost > 0: self.add_score(-cost) 
            self.set_game_state(next_state_after_cost_check) 
        else: 
            messagebox.showwarning("Recursos Insuficientes", f"Você precisa de {cost} Pontos de Influência para esta ação, mas possui apenas {self.player_score}.\nEsta opção deveria estar desabilitada.")

    def handle_minigame_rpg_result(self, sucesso_minigame, choice_id_original, pontos_bonus_por_sucesso=0):
        if sucesso_minigame:
            if pontos_bonus_por_sucesso > 0: self.add_score(pontos_bonus_por_sucesso)
            if choice_id_original == "B": self.set_game_state("RPG_CHOICE_B_MINIGAME_SUCCESS")
            elif choice_id_original == "C": self.set_game_state("RPG_CHOICE_C_MINIGAME_SUCCESS")
        else: 
            if choice_id_original == "B": self.set_game_state("RPG_CHOICE_B_MINIGAME_FAIL")
            elif choice_id_original == "C": self.set_game_state("RPG_CHOICE_C_MINIGAME_FAIL")

    def set_game_state(self, new_state):
        print(f"Mudando estado de '{self.game_state}' para: {new_state}") 
        self.game_state = new_state
        self.root.after_idle(self.update_display)

    def add_score(self, points):
        self.player_score += points
        if points > 0: print(f"Pontos ganhos: {points}. Pontuação: {self.player_score}")
        elif points < 0: print(f"Pontos perdidos: {abs(points)}. Pontuação: {self.player_score}")

    def mission_completed(self, mission_id):
        print(f"GameManager: Missão {mission_id} concluída.") 
        if mission_id == "Missao1": self.set_game_state("MISSION_1_SUCCESS_DIALOGUE_A") 
        elif mission_id == "Missao2": self.set_game_state("MISSION_2_SUCCESS_FULCRUM_A")
        elif mission_id == "Missao3": self.set_game_state("MISSION_3_SUCCESS_FULCRUM_A")
        elif mission_id == "Missao4": self.set_game_state("MISSION_4_SUCCESS_FULCRUM_A")
        elif mission_id == "Missao5": self.set_game_state("MISSION_5_SUCCESS_FULCRUM_A") 
        elif mission_id == "Missao6": self.set_game_state("MISSION_6_SUCCESS_FULCRUM_A") 
        elif mission_id == "Missao7": self.set_game_state("ALL_MISSIONS_COMPLETED") 

    def mission_failed_options(self, mission_obj_que_falhou, failure_message_1, failure_message_2_creative):
        self._clear_content_frame() 
        tk.Label(self.content_frame, text="Falha na Missão!", font=self.header_font_obj, fg="red", 
                 bg=self.bg_color_dark).pack(pady=10)
        message = random.choice([failure_message_1, failure_message_2_creative])
        text_widget = tk.Text(self.content_frame, wrap=tk.WORD, height=8, width=70, relief=tk.FLAT,
                              background=self.bg_color_dark, foreground=self.fg_color_light, insertbackground=self.fg_color_light,
                              font=self.narrative_font_obj, padx=10, pady=10)
        text_widget.insert(tk.END, message)
        text_widget.config(state=tk.DISABLED)
        text_widget.pack(pady=15, padx=10, expand=True, fill=tk.BOTH)
        button_frame = ttk.Frame(self.content_frame, style="Black.TFrame")
        button_frame.pack(pady=20)
        can_retry = False
        if mission_obj_que_falhou and hasattr(mission_obj_que_falhou, 'retry_mission') and callable(getattr(mission_obj_que_falhou, 'retry_mission')):
            can_retry = True
        if can_retry:
            btn_tentar_novamente = ttk.Button(button_frame, text="Tentar Novamente", 
                                            command=mission_obj_que_falhou.retry_mission, style="Accent.Dark.TButton")
            btn_tentar_novamente.pack(side=tk.LEFT, padx=10)
        btn_abandonar = ttk.Button(button_frame, text="Abandonar Rebelião (Sair do Jogo)", 
                                   command=self.root.quit, style="Dark.TButton")
        btn_abandonar.pack(side=tk.LEFT, padx=10)

if __name__ == "__main__":
    root = None 
    try:
        root = tk.Tk()
        required_classes = ['Missao1', 'Missao2', 'Missao3', 'Missao4', 'Missao5', 'Missao6', 'Missao7',
                            'MinigameBFSExtracao', 'MinigameKruskalContraAtaque'] 
        missing_classes = [m_name for m_name in required_classes if m_name not in globals()]
        if missing_classes:
             messagebox.showerror("Erro de Inicialização", 
                                  f"As seguintes classes não puderam ser encontradas: {', '.join(missing_classes)}.\n"
                                  "Verifique as importações, nomes dos arquivos e nomes das classes.")
             if root and root.winfo_exists(): root.destroy() 
        else:
            app = GameManager(root)
            root.mainloop()
    except Exception as e:
        print(f"Erro fatal ao iniciar a aplicação: {e}")
        try:
            if tk._default_root and tk._default_root.winfo_exists(): 
                 messagebox.showerror("Erro Fatal", f"Ocorreu um erro crítico ao iniciar:\n{e}\nVerifique o console para mais detalhes.")
        except Exception: pass
        if root and root.winfo_exists(): 
            root.destroy()