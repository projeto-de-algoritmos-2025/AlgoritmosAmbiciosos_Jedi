import tkinter as tk
from tkinter import ttk, messagebox, font as tkFont
import random # Para escolher mensagens de falha

# Importar as missões e os minigames.
try:
    from missoes.missao1 import Missao1
    from missoes.missao2 import Missao2
    from missoes.missao3 import Missao3
    from missoes.missao4 import Missao4
    from missoes.missao5 import Missao5 
    
    from missoes.minigame_bfs_extração import MinigameBFSExtracao 
    from missoes.minigame_rpg_kruskal import MinigameKruskalContraAtaque 
except ImportError as e:
    print(f"ALERTA DE IMPORTAÇÃO DE MÓDULO: {e}")
    print("Verifique se todas as classes de Missão e Minigame estão nos arquivos corretos dentro da pasta 'missoes/'")
    print("e se as pastas 'missoes/' e 'algoritmos/' contêm um arquivo __init__.py (pode ser vazio).")
    


class GameManager:
    def __init__(self, root_tk):
        self.root = root_tk
        self.root.title("Aliança Rebelde - Operações Críticas")
        try:
            self.root.geometry("850x650") 
        except tk.TclError:
            print("Aviso: Não foi possível definir a geometria inicial da janela.")

        # --- Configuração de Fontes ---
        try:
            self.default_font = tkFont.nametofont("TkDefaultFont")
            self.default_font.configure(family="Arial", size=11)
            self.root.option_add("*Font", self.default_font)
            
            self.narrative_font = tkFont.Font(family="Arial", size=12)
            self.button_font = tkFont.Font(family="Arial", size=11, weight="bold")
            self.header_font = tkFont.Font(family="Arial", size=16, weight="bold")
            self.small_bold_font = tkFont.Font(family="Arial", size=10, weight="bold")
            self.points_font = tkFont.Font(family="Arial", size=12, weight="bold", slant="italic")
        except tk.TclError: 
            print("Aviso: Não foi possível configurar fontes personalizadas. Usando fontes de fallback.")
            self.default_font = ("Arial", 11) 
            self.narrative_font = ("Arial", 12)
            self.button_font = ("Arial", 11, "bold")
            self.header_font = ("Arial", 16, "bold")
            self.small_bold_font = ("Arial", 10, "bold")
            self.points_font = ("Arial", 12, "bold", "italic")

        # --- Estilo ttk ---
        style = ttk.Style()
        available_themes = style.theme_names()
        preferred_themes = ['xpnative', 'vista', 'clam', 'alt', 'default'] 
        theme_to_use = next((t for t in preferred_themes if t in available_themes), 'default')
        try:
            style.theme_use(theme_to_use)
        except tk.TclError:
            print(f"Aviso: Tema ttk '{theme_to_use}' não pôde ser aplicado, usando tema default.")
        
        try: 
            style.configure("Accent.TButton", font=self.button_font, padding=10)
            style.configure("TButton", font=self.button_font) 
            style.configure("TLabel", font=self.default_font if isinstance(self.default_font, tkFont.Font) else ("Arial", 11))
            style.configure("Header.TLabel", font=self.header_font, anchor="center")
        except tk.TclError:
            print("Aviso: Não foi possível configurar estilos ttk para botões/labels.")

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
        self.content_frame = ttk.Frame(self.root, padding="20")
        self.content_frame.pack(fill=tk.BOTH, expand=True)

    def _display_text_screen(self, title_text, narrative_text_lines, button_text, next_state_or_command, button_style="TButton"):
        ttk.Label(self.content_frame, text=title_text, style="Header.TLabel").pack(pady=(10, 20))
        
        text_frame = ttk.Frame(self.content_frame)
        text_frame.pack(pady=10, padx=10, expand=True, fill=tk.BOTH) 

        full_narrative_text = "\n\n".join(narrative_text_lines)

        text_widget = tk.Text(text_frame, wrap=tk.WORD, height=10, 
                              relief=tk.FLAT, background=self.root.cget('bg'),
                              font=self.narrative_font, padx=10, pady=10, borderwidth=0, highlightthickness=0)
        text_widget.insert(tk.END, full_narrative_text)
        text_widget.config(state=tk.DISABLED)
        text_widget.pack(expand=True, fill=tk.BOTH) 
        
        command_to_run = next_state_or_command
        if isinstance(next_state_or_command, str):
            command_to_run = lambda: self.set_game_state(next_state_or_command)

        button_container = ttk.Frame(self.content_frame)
        button_container.pack(pady=(10,15)) 
        ttk.Button(button_container, text=button_text, command=command_to_run, style=button_style).pack()


    def update_display(self):
        self._clear_content_frame() 

        # --- INTRODUÇÃO ---
        if self.game_state == "INTRO_1A":
            self._display_text_screen("Despertar", 
                                      ["Seus olhos se abrem para uma escuridão quebrada apenas pelo brilho rubro das luzes de emergência.",
                                       "O ar denso carrega o cheiro acre de metal superaquecido e circuitos queimados.",
                                       "Sua cabeça lateja, a dor ecoando a violência de um impacto recente."], 
                                      "...", "INTRO_1B")
        elif self.game_state == "INTRO_1B":
            self._display_text_screen("Fragmentos",
                                      ["Fragmentos de memória turbilhonam: alarmes estrondosos, a vertigem de uma fuga desesperada, a escuridão da queda...",
                                       "Você tenta se lembrar quem é. Emerge a identidade de um(a) estrategista.",
                                       "Talvez um passado ligado ao Império, agora uma fonte de conhecimento perigoso. Ou a chama de um idealista, forjado(a) na luta de um mundo subjugado."],
                                      "Lembrar o propósito...", "INTRO_1C")
        elif self.game_state == "INTRO_1C":
            self.current_mission_obj = None 
            self._display_text_screen("Sobrevivência",
                                      ["Não importa o passado exato, uma convicção resiste à confusão: a opressão que consome a galáxia precisa ser combatida.",
                                       "À sua frente, o painel da sua nave improvisada pisca erraticamente. Os sistemas de suporte de vida, teimosamente, ainda funcionam.",
                                       "A nave está à deriva, um casco ferido, mas você está vivo(a)."],
                                      "Avaliar Danos e Sistemas...", "INTRO_2A", button_style="Accent.TButton")
        elif self.game_state == "INTRO_2A":
            self._display_text_screen("Diagnóstico Precário",
                                      ["Com um gemido de esforço, você se arrasta até o console principal. Luzes de alerta vermelhas pintam seu rosto.",
                                       "Um diagnóstico rápido revela sua posição: um setor pouco mapeado na Orla Exterior.",
                                       "Por ora, uma sorte frágil; você está fora das rotas de patrulha imperiais."],
                                      "Analisar a situação...", "INTRO_2B")
        elif self.game_state == "INTRO_2B":
            self._display_text_screen("A Sombra do Império",
                                      ["Mas essa 'segurança' é uma ilusão. As memórias das últimas notícias antes do... incidente... são sombrias: o Império avança, implacável.",
                                       "Cada sistema que cai é um grito silenciado, mais um passo da galáxia em direção a uma escuridão uniforme."],
                                      "Considerar os próximos passos...", "INTRO_2C")
        elif self.game_state == "INTRO_2C":
            self._display_text_screen("A Chama da Resistência",
                                      ["Apesar da dor, sua mente analítica desperta. Logística, tática, a habilidade de encontrar saídas impossíveis... Essas ferramentas não podem se perder aqui.",
                                       "Terminar à deriva não é uma opção. A Rebelião, por menor que seja sua chama, precisa de cada centelha."],
                                      "Tentar Contato com Aliados...", "INTRO_DIALOGUE_A", button_style="Accent.TButton")
        elif self.game_state == "INTRO_DIALOGUE_A":
            self._display_text_screen("Eco no Vazio",
                                      ["Você desvia a pouca energia restante para os comunicadores de longo alcance. A estática domina, um mar de ruído cósmico.",
                                       "Pacientemente, você varre as frequências de emergência conhecidas...",
                                       "Quando a esperança começa a minguar, um padrão fraco, quase imperceptível, emerge. Um antigo código de autenticação da Aliança Rebelde. Seu transmissor de emergência, ativado na queda, deve ter sido detectado."],
                                      "Aguardar identificação do sinal...", "INTRO_DIALOGUE_B")
        elif self.game_state == "INTRO_DIALOGUE_B":
            self._display_fulcrum_dialogue()
        elif self.game_state == "GAME_OVER_DECLINED":
            self.current_mission_obj = None 
            self._display_text_screen("Fim da Linha... Ou Um Novo Começo?",
                                      ["Você desliga o comunicador. A luta... não é mais para você. Talvez um planeta pacato no Anel Externo.",
                                       "A Rebelião terá que encontrar outro herói. A galáxia continua sua dança de guerra e paz, mas sua parte nela parece ter chegado ao fim.",
                                       "FIM DE JOGO"],
                                      "Sair do Jogo", self.root.quit)
        
        elif self.game_state == "START_MISSION_1":
            if 'Missao1' in globals(): 
                self.current_mission_obj = Missao1(self.root, self, self.content_frame)
                self.current_mission_obj.iniciar_missao_contexto()
            else: messagebox.showerror("Erro Crítico", "Missao1 não carregada."); self.root.quit()

        elif self.game_state == "MISSION_1_SUCCESS_DIALOGUE_A":
            self.current_mission_obj = None 
            dialogo = [
                "Fulcrum (via comunicador): \"RZ-479, relatório recebido. A célula de Atravis confirma a chegada dos suprimentos.\"",
                "\"Sua eficiência na otimização da carga foi... notável. Salvou vidas e garantiu recursos essenciais para uma operação que estava por um fio. Bom trabalho, Comandante.\""
            ]
            self._display_text_screen("Relatório de Atravis: Sucesso!", dialogo, "Agradecer. Às ordens, Fulcrum.", "MISSION_1_SUCCESS_DIALOGUE_B")
        
        elif self.game_state == "MISSION_1_SUCCESS_DIALOGUE_B":
            dialogo = [
                "Fulcrum: \"Há mais uma questão delicada referente a essa operação, Comandante.\"",
                "\"A inteligência para a rota segura de Atravis veio de um informante... um tanto quanto volátil e caro. Ele espera seu pagamento, e o Império tem olhos e ouvidos em todo tipo de transação financeira.\"",
                "\"Precisamos que esse pagamento seja o mais discreto possível – usando o menor número de cédulas de alto valor para não chamar atenção desnecessária.\""
            ]
            self._display_text_screen("Pendência Urgente: O Informante", dialogo, "Entendido. Qual o procedimento, Fulcrum?", "START_MISSION_2", button_style="Accent.TButton")
        
        elif self.game_state == "START_MISSION_2":
            if 'Missao2' in globals():
                self.current_mission_obj = Missao2(self.root, self, self.content_frame)
                self.current_mission_obj.iniciar_missao_contexto()
            else: messagebox.showerror("Erro Crítico", "Missao2 não carregada."); self.root.quit()

        elif self.game_state == "MISSION_2_SUCCESS_FULCRUM_A":
            self.current_mission_obj = None
            dialogo = [
                "Fulcrum (com um raro tom de aprovação): \"Excelente trabalho com o pagamento, RZ-479. Discreto, eficiente, exatamente como solicitado.\"",
                "\"O informante está satisfeito e, mais importante, continua sendo um recurso viável para futuras operações. Suas ações estão começando a construir uma reputação de confiabilidade e precisão.\" "
            ]
            self._display_text_screen("Pagamento Confirmado", dialogo, "É bom ouvir isso, Fulcrum. Pronta para o próximo desafio.", "MISSION_2_SUCCESS_FULCRUM_B")
        elif self.game_state == "MISSION_2_SUCCESS_FULCRUM_B":
            dialogo = [
                "Fulcrum: \"Contudo, não há tempo para descanso. A situação na galáxia se deteriora a cada ciclo. Nossas fontes indicam movimentação imperial suspeita perto de um antigo posto de escuta em Dantooine III.\"",
                "\"Acabei de receber um alerta... uma de nossas equipes de reconhecimento avançado na área pode estar em apuros. Preciso de alguém com sua capacidade tática para avaliar e, se necessário, intervir.\" "
            ]
            self._display_text_screen("Novos Rumores e Perigos", dialogo, "Relate a situação completa, Fulcrum.", "RPG_SCENARIO_SETUP", button_style="Accent.TButton")
        
        elif self.game_state == "RPG_SCENARIO_SETUP":
            self._display_rpg_scenario_setup()
        elif self.game_state == "RPG_CHOICE_PROMPT":
            self._display_rpg_choice_prompt()

        elif self.game_state == "RPG_CHOICE_B_MINIGAME_SETUP": 
            self.current_mission_obj = None 
            if 'MinigameBFSExtracao' in globals():
                self.current_mission_obj = MinigameBFSExtracao(self.root, self, self.content_frame, recompensa_sucesso=60, id_escolha_rpg="B")
                self.current_mission_obj.iniciar_minigame_interface()
            else: messagebox.showerror("Erro Crítico", "MinigameBFSExtracao não carregado."); self.set_game_state("RPG_CHOICE_PROMPT")
        elif self.game_state == "RPG_CHOICE_C_MINIGAME_SETUP": 
            self.current_mission_obj = None 
            if 'MinigameKruskalContraAtaque' in globals():
                self.current_mission_obj = MinigameKruskalContraAtaque(self.root, self, self.content_frame, recompensa_sucesso=150, id_escolha_rpg="C")
                self.current_mission_obj.iniciar_minigame_interface()
            else: messagebox.showerror("Erro Crítico", "MinigameKruskalContraAtaque não carregado."); self.set_game_state("RPG_CHOICE_PROMPT")

        elif self.game_state == "RPG_CHOICE_A_RESULT": 
            narrativa = ["Com astúcia e nervos de aço, você guia a Patrulha Eco através de uma série de dutos de ventilação esquecidos, emergindo longe do combate principal. A retirada é tensa, com alguns arranhões, mas todos os membros da equipe estão a salvo e o equipamento essencial foi preservado.",
                         "Fulcrum (pelo comunicador, após seu relatório): \"Sua prudência salvou vidas preciosas hoje, RZ-479. Uma retirada bem executada é, muitas vezes, a manobra mais corajosa. No entanto, a oportunidade de obter dados valiosos do terminal imperial no posto foi perdida. Não se pode ter tudo, suponho.\""]
            self._display_text_screen("Retirada Tática Concluída", narrativa, "Próxima designação, Fulcrum.", "LEAD_IN_TO_MISSION_3")
        elif self.game_state == "RPG_CHOICE_B_MINIGAME_SUCCESS": 
            narrativa = [f"Os 30 Pontos de Influência foram cruciais! Com os canais de comunicação priorizados, você coordenou uma defesa sólida enquanto guiava a Patrulha Eco para o ponto de extração pelo caminho mais seguro, identificado por sua análise tática. A nave de resgate chegou sob fogo leve, mas conseguiu extrair todos.",
                         "Alguns dados importantes foram recuperados do terminal antes da evacuação às pressas.",
                         "Fulcrum: \"Impressionante, Comandante. Sua análise e coordenação foram impecáveis. Esta operação rendeu um bônus de 60 pontos para seus futuros esforços e inteligência valiosa.\""]
            self._display_text_screen("Extração Bem-Sucedida!", narrativa, "Aguardando novas ordens, Fulcrum.", "LEAD_IN_TO_MISSION_3")
        elif self.game_state == "RPG_CHOICE_B_MINIGAME_FAIL":
             narrativa = ["Apesar dos seus esforços e do uso dos 30 Pontos de Influência para melhorar as comunicações, a rota de extração escolhida ou a coordenação da defesa se provou inadequada. A equipe sofreu baixas consideráveis e apenas fragmentos de dados foram recuperados antes que a situação se tornasse insustentável.",
                          "Fulcrum: \"Uma pena, Comandante. Às vezes, mesmo com recursos adicionais, o campo de batalha é imprevisível. Os pontos de influência foram gastos, mas o resultado não foi o esperado. Precisamos analisar o que deu errado.\""]
             self._display_text_screen("Extração Complicada", narrativa, "Entendido. Próxima designação.", "LEAD_IN_TO_MISSION_3")
        elif self.game_state == "RPG_CHOICE_C_MINIGAME_SUCCESS": 
            narrativa = [f"Um investimento alto de 70 Pontos de Influência, mas com um retorno espetacular! Seu plano de contra-ataque, utilizando o equipamento adicional e a estratégia de rede de comunicação que você estabeleceu, foi brilhante. Os stormtroopers foram pegos de surpresa e neutralizados.",
                         "A Patrulha Eco não apenas escapou, como também assegurou o posto de escuta, capturando informações vitais sobre movimentações de frotas imperiais.",
                         "Fulcrum: \"Uma manobra audaciosa e recompensadora, RZ-479! Sua coragem e brilhantismo tático nos renderam um ganho estratégico imenso. Você ganhou um bônus de 150 pontos. Excelente!\""]
            self._display_text_screen("Vitória Decisiva em Dantooine!", narrativa, "Qual o próximo passo, Fulcrum?", "LEAD_IN_TO_MISSION_3")
        elif self.game_state == "RPG_CHOICE_C_MINIGAME_FAIL":
            narrativa = ["O contra-ataque foi feroz, mas a estratégia para neutralizar as defesas ou superar a força inimiga falhou, mesmo com os 70 Pontos de Influência gastos em equipamento extra. Os stormtroopers eram mais numerosos e bem entrincheirados do que o previsto.",
                         "A Patrulha Eco conseguiu recuar com dificuldade, sofrendo perdas e sem alcançar o objetivo principal. O equipamento adicional foi perdido.",
                         "Fulcrum: \"Uma aposta ousada, Comandante. Infelizmente, nem todas as apostas se pagam. Os recursos se foram, e a vitória nos escapou desta vez. Precisamos aprender com cada revés.\""]
            self._display_text_screen("Contra-Ataque Frustrado", narrativa, "Compreendido. Aguardo novas diretrizes.", "LEAD_IN_TO_MISSION_3")
        
        elif self.game_state == "LEAD_IN_TO_MISSION_3":
            self.current_mission_obj = None
            fulcrum_mission3_brief = ("Fulcrum: \"Comandante, a situação no setor Arkanis se intensificou. Suas recentes ações, independentemente do resultado em Dantooine, nos mostraram a necessidade de operações mais amplas e coordenadas para desestabilizar o controle Imperial na região. "
                                      "Temos múltiplas janelas de oportunidade para inteligência e sabotagem, mas nossos recursos de campo são perigosamente limitados. Cada ação deve ser precisamente cronometrada para máximo impacto e, crucialmente, para a segurança de nossos agentes. Sua próxima tarefa é coordenar este complexo balé de operações secretas.\"")
            self._display_text_screen("Designação: Operação Sincronia Arkanis", [fulcrum_mission3_brief], "Aceito. Envie-me os parâmetros da missão.", "START_MISSION_3", button_style="Accent.TButton")
        
        elif self.game_state == "START_MISSION_3":
            if 'Missao3' in globals():
                self.current_mission_obj = Missao3(self.root, self, self.content_frame)
                self.current_mission_obj.iniciar_missao_contexto()
            else: messagebox.showerror("Erro Crítico", "Missao3 não carregada."); self.root.quit()
        
        elif self.game_state == "MISSION_3_SUCCESS_FULCRUM_A":
            self.current_mission_obj = None
            fulcrum_m3_praise = ("Fulcrum (impressionado): \"RZ-479, os relatórios do setor Arkanis são... exemplares. "
                                 "Sua coordenação das múltiplas operações desferiu um golpe significativo na capacidade imperial de controlar o corredor. "
                                 "Várias células rebeldes que estavam isoladas agora têm uma rota de fuga ou de recebimento de suprimentos graças à sua visão estratégica.\"")
            self._display_text_screen("Sucesso Estratégico em Arkanis", [fulcrum_m3_praise], "Fico feliz em ter sido útil à causa, Fulcrum.", "MISSION_3_SUCCESS_FULCRUM_B")
        elif self.game_state == "MISSION_3_SUCCESS_FULCRUM_B":
            fulcrum_m3_next_step = ("Fulcrum: \"Sua perícia em escalonamento tático é inegável e já está se tornando lendária em certos círculos. Com o Corredor de Arkanis mais instável para o Império, "
                                    "surge uma nova emergência que exige sua atenção imediata: uma evacuação crítica e de alto risco no sistema Kessel.\"") 
            self._display_text_screen("Nova Emergência: Kessel", [fulcrum_m3_next_step], "Kessel? Minas de especiarias... e prisões. Relate.", "START_MISSION_4", button_style="Accent.TButton")
        
        elif self.game_state == "START_MISSION_4":
            self.current_mission_obj = None 
            if 'Missao4' in globals():
                self.current_mission_obj = Missao4(self.root, self, self.content_frame)
                self.current_mission_obj.iniciar_missao_contexto()
            else: messagebox.showerror("Erro Crítico", "Missao4 não carregada."); self.root.quit()

        elif self.game_state == "MISSION_4_SUCCESS_FULCRUM_A":
            self.current_mission_obj = None 
            fulcrum_m4_praise = ("Fulcrum (com um tom de alívio palpável): \"Comandante RZ-479, os últimos transportes de Kessel acabaram de sair do sistema, "
                                 "escapando por pouco do bloqueio imperial. Sua coordenação sob aquela contagem regressiva foi... magistral. "
                                 "Muitos operativos e civis importantes devem suas vidas à sua capacidade de tomar decisões rápidas e precisas sob pressão extrema.\"")
            self._display_text_screen("Evacuação de Kessel Concluída", [fulcrum_m4_praise], "Cumprimos nosso dever, Fulcrum. Qual o próximo front?", "MISSION_4_SUCCESS_FULCRUM_B")
        elif self.game_state == "MISSION_4_SUCCESS_FULCRUM_B":
            fulcrum_m4_next_task = ("Fulcrum: \"De fato. Suas ações em Kessel nos deram não apenas pessoal valioso, mas também dados cruciais sobre as táticas de bloqueio imperiais. "
                                    "Com base nisso, identificamos uma nova frente de oportunidade: o Império está tentando expandir sua rede de vigilância no Setor Bryx. "
                                    "Precisamos otimizar nossos poucos recursos de patrulha para cobrir o máximo de território possível e monitorar essas movimentações com o mínimo de esquadrões.\" ")
            self._display_text_screen("Novos Desafios: Olhos no Setor Bryx", [fulcrum_m4_next_task], "Entendido. Qual o plano para Bryx, Fulcrum?", "START_MISSION_5", button_style="Accent.TButton")

        elif self.game_state == "START_MISSION_5":
            self.current_mission_obj = None 
            if 'Missao5' in globals(): 
                self.current_mission_obj = Missao5(self.root, self, self.content_frame)
                self.current_mission_obj.iniciar_missao_contexto()
            else:
                messagebox.showerror("Erro Crítico de Inicialização", "A classe Missao5 não foi carregada.")
                self.root.quit()

        elif self.game_state == "ALL_MISSIONS_COMPLETED":
             self.current_mission_obj = None
             titulo_final = "Uma Nova Esperança Desperta"
             narrativa_final = [
                f"Comandante RZ-479, suas vitórias consecutivas ecoam pelos canais secretos da Aliança Rebelde. De Atravis a Kessel, do Setor Arkanis aos confins de Bryx, sua liderança estratégica e sua capacidade de converter desafios aparentemente impossíveis em triunfos reacenderam a chama da esperança em inúmeros sistemas oprimidos.",
                f"O Império Galáctico sentiu o peso de suas ações. Embora a guerra pela liberdade da galáxia esteja longe de terminar, seus feitos provaram que a tirania pode ser desafiada, que a astúcia, a lógica e a coragem ainda podem alterar o curso das estrelas.",
                f"Com {self.player_score} Pontos de Influência acumulados, você não é apenas um(a) ativo(a) valioso(a), mas uma inspiração crescente dentro das fileiras da Aliança. Muitos agora olham para você como um símbolo do que podemos alcançar quando a estratégia encontra a determinação.",
                "Descanse, Comandante. Reabasteça suas forças e prepare seu espírito.",
                "A Aliança precisará de sua mente brilhante novamente, pois novas frentes se abrirão e a luta pela liberdade continuará... até que cada canto escuro da galáxia conheça a luz.",
                "Que a Força esteja com você, sempre."
             ]
             botao_texto_final = "A Luta Continua... (Encerrar Jogo)"
             self._display_text_screen(titulo_final, narrativa_final, botao_texto_final, 
                                       self.root.quit, button_style="Accent.TButton")
        else: 
            ttk.Label(self.content_frame, text=f"Estado de jogo desconhecido: {self.game_state}", style="Header.TLabel", foreground="orange red").pack(pady=20)


    def _display_fulcrum_dialogue(self):
        title = "Contato: Fulcrum"
        narrative_fulcrum = (
            "Uma voz calma, com um tom pragmático e levemente cansado, corta a estática: \"Sinal de emergência RZ-479. "
            "Aqui é Fulcrum. Nossos registros são antigos, mas indicam que essa designação pertence a um(a) oficial de estratégia... "
            "marcado(a) como 'comprometido(a) e irrecuperável' após o incidente em Cygnus VII. Se for você, e se ainda estiver funcional, responda. "
            "Temos uma operação em andamento que demanda sua especialidade. A situação é... delicada. "
            "Precisamos de resultados, não de heróis. Confirme seu status.\""
        )
        ttk.Label(self.content_frame, text=title, style="Header.TLabel").pack(pady=20)
        text_widget = tk.Text(self.content_frame, wrap=tk.WORD, height=10, width=70, relief=tk.FLAT,
                              background=self.root.cget('bg'), font=self.narrative_font, padx=10, pady=10)
        text_widget.insert(tk.END, narrative_fulcrum)
        text_widget.config(state=tk.DISABLED)
        text_widget.pack(pady=15, padx=10, expand=True, fill=tk.BOTH)
        button_frame = ttk.Frame(self.content_frame)
        button_frame.pack(pady=20)
        btn_aceitar = ttk.Button(button_frame, text="Fulcrum, aqui RZ-479. Status: funcional, mas avariado. À disposição.",
                                 command=lambda: self.set_game_state("START_MISSION_1"), style="Accent.TButton")
        btn_aceitar.pack(side=tk.LEFT, padx=10, pady=5)
        btn_recusar = ttk.Button(button_frame, text="Silêncio. (O passado não pode me alcançar)",
                                 command=lambda: self.set_game_state("GAME_OVER_DECLINED"))
        btn_recusar.pack(side=tk.LEFT, padx=10, pady=5)

    def _display_rpg_scenario_setup(self):
        self.current_mission_obj = None
        title = "Alerta Urgente!"
        narrative = [
            "Fulcrum (a voz tensa): \"Comandante, interceptei uma transmissão de emergência! Uma de nossas equipes de reconhecimento avançado, a 'Patrulha Eco', foi emboscada no antigo posto de escuta imperial em Dantooine III. Estão sob fogo pesado de stormtroopers e completamente encurralados!\"",
            "\"Eles precisam de uma decisão tática IMEDIATA ou serão dizimados. Você é o(a) oficial de mais alta patente com contato no momento.\""
        ]
        self._display_text_screen(title, narrative, "Analisar Opções Táticas...", "RPG_CHOICE_PROMPT", button_style="Accent.TButton")

    def _display_rpg_choice_prompt(self):
        title = "Decisão Crítica: Posto de Dantooine III"
        ttk.Label(self.content_frame, text=title, style="Header.TLabel").pack(pady=15)
        ttk.Label(self.content_frame, text=f"Seus Pontos de Influência Atuais: {self.player_score}", font=self.points_font, foreground="#0033cc").pack(pady=(0,15))
        scenario_desc = "A Patrulha Eco está presa, com munição baixa. Stormtroopers avançam por dois flancos. As opções são limitadas e arriscadas:"
        desc_label = ttk.Label(self.content_frame, text=scenario_desc, wraplength=700, justify=tk.CENTER, font=self.narrative_font)
        desc_label.pack(pady=10)
        options_button_frame = ttk.Frame(self.content_frame)
        options_button_frame.pack(pady=10) 
        choices_data = [
            {"id": "A", "text": "Retirada Tática pelos Dutos", "cost": 0, "next_state": "RPG_CHOICE_A_RESULT", 
             "desc": "Busca uma rota de fuga alternativa. Menor risco, mas sem ganhos táticos diretos."},
            {"id": "B", "text": "Defesa Coordenada e Extração Urgente", "cost": 30, "next_state": "RPG_CHOICE_B_MINIGAME_SETUP", 
             "desc": "Prioriza comunicadores para coordenar defesa e solicitar extração. Risco moderado, possível recuperação de dados."},
            {"id": "C", "text": "Contra-Ataque Ousado", "cost": 70, "next_state": "RPG_CHOICE_C_MINIGAME_SETUP", 
             "desc": "Requisita blasters pesados e granadas para romper o cerco. Alto risco, mas potencial para ganhos de inteligência significativos."}
        ]
        for choice in choices_data:
            choice_frame = ttk.Frame(options_button_frame)
            choice_frame.pack(fill=tk.X, pady=3)
            btn_text = f"{choice['id']}: {choice['text']} (Custo: {choice['cost']} Pontos)"
            can_afford = self.player_score >= choice['cost']
            btn_style = "Accent.TButton" if can_afford and choice['cost'] > 0 else ("TButton" if can_afford else "TButton")
            btn_state = tk.NORMAL if can_afford else tk.DISABLED
            btn = ttk.Button(choice_frame, text=btn_text, width=60, style=btn_style, state=btn_state,
                               command=lambda ch_id=choice['id'], ch_cost=choice['cost'], ch_next=choice['next_state']: self.handle_rpg_choice(ch_id, ch_cost, ch_next))
            btn.pack(pady=3, fill=tk.X)
            ttk.Label(choice_frame, text=choice['desc'], font=self.small_bold_font, wraplength=550, justify=tk.CENTER).pack(pady=(0,8))

    def handle_rpg_choice(self, choice_id, cost, next_state_after_cost_check):
        if self.player_score >= cost:
            if cost > 0:
                self.add_score(-cost) 
            self.set_game_state(next_state_after_cost_check) 
        else: 
            messagebox.showwarning("Recursos Insuficientes", 
                                   f"Você precisa de {cost} Pontos de Influência para esta ação, mas possui apenas {self.player_score}.\n"
                                   "Esta opção deveria estar desabilitada.")

    def handle_minigame_rpg_result(self, sucesso_minigame, choice_id_original, pontos_bonus_por_sucesso=0):
        if sucesso_minigame:
            if pontos_bonus_por_sucesso > 0:
                 self.add_score(pontos_bonus_por_sucesso)
            if choice_id_original == "B":
                self.set_game_state("RPG_CHOICE_B_MINIGAME_SUCCESS")
            elif choice_id_original == "C":
                self.set_game_state("RPG_CHOICE_C_MINIGAME_SUCCESS")
        else: 
            if choice_id_original == "B":
                self.set_game_state("RPG_CHOICE_B_MINIGAME_FAIL")
            elif choice_id_original == "C":
                self.set_game_state("RPG_CHOICE_C_MINIGAME_FAIL")

    def set_game_state(self, new_state):
        print(f"Mudando estado de '{self.game_state}' para: {new_state}") 
        self.game_state = new_state
        self.root.after_idle(self.update_display) # Adia a atualização para o próximo ciclo idle do Tkinter

    def add_score(self, points):
        self.player_score += points
        if points > 0:
            print(f"Pontos ganhos: {points}. Pontuação atualizada: {self.player_score}")
        elif points < 0:
            print(f"Pontos perdidos: {abs(points)}. Pontuação atualizada: {self.player_score}")

    def mission_completed(self, mission_id):
        print(f"GameManager notificado: Missão {mission_id} concluída.") 
        if mission_id == "Missao1":
            self.set_game_state("MISSION_1_SUCCESS_DIALOGUE_A") 
        elif mission_id == "Missao2":
            self.set_game_state("MISSION_2_SUCCESS_FULCRUM_A")
        elif mission_id == "Missao3": 
             self.set_game_state("MISSION_3_SUCCESS_FULCRUM_A")
        elif mission_id == "Missao4": 
             self.set_game_state("MISSION_4_SUCCESS_FULCRUM_A")
        elif mission_id == "Missao5": 
             self.set_game_state("ALL_MISSIONS_COMPLETED") 

    def mission_failed_options(self, mission_obj_que_falhou, failure_message_1, failure_message_2_creative):
        self._clear_content_frame() 
        ttk.Label(self.content_frame, text="Falha na Missão!", style="Header.TLabel", foreground="red").pack(pady=10)
        message = random.choice([failure_message_1, failure_message_2_creative])
        text_widget = tk.Text(self.content_frame, wrap=tk.WORD, height=8, width=70, relief=tk.FLAT,
                              background=self.root.cget('bg'), font=self.narrative_font, padx=10, pady=10)
        text_widget.insert(tk.END, message)
        text_widget.config(state=tk.DISABLED)
        text_widget.pack(pady=15, padx=10, expand=True, fill=tk.BOTH)
        button_frame = ttk.Frame(self.content_frame)
        button_frame.pack(pady=20)
        can_retry = False
        if mission_obj_que_falhou and hasattr(mission_obj_que_falhou, 'retry_mission') and callable(getattr(mission_obj_que_falhou, 'retry_mission')):
            can_retry = True
        if can_retry:
            btn_tentar_novamente = ttk.Button(button_frame, text="Tentar Novamente", 
                                            command=mission_obj_que_falhou.retry_mission, style="Accent.TButton")
            btn_tentar_novamente.pack(side=tk.LEFT, padx=10)
        btn_abandonar = ttk.Button(button_frame, text="Abandonar Rebelião (Sair do Jogo)", 
                                   command=self.root.quit)
        btn_abandonar.pack(side=tk.LEFT, padx=10)

if __name__ == "__main__":
    root = None 
    try:
        root = tk.Tk()
        required_classes = ['Missao1', 'Missao2', 'Missao3', 'Missao4', 'Missao5',
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
        messagebox.showerror("Erro Fatal", f"Ocorreu um erro crítico ao iniciar:\n{e}\nVerifique o console para mais detalhes.")
        if root and root.winfo_exists(): 
            root.destroy()