# Star Wars: Aliança Rebelde - Operações Críticas

#### Em meio ao caos da Guerra Galáctica, você é o cérebro por trás das operações secretas da Aliança Rebelde. Como Coordenador de Operações Críticas, sua missão é utilizar táticas avançadas de planejamento para sabotar instalações imperiais, alocar recursos limitados e  planejar resgates arriscados.

#### Cada fase do jogo representa uma missão crítica onde decisões rápidas, mas otimizadas, podem significar a diferença entre vitória e destruição. Com o apoio da Força — e de algoritmos gananciosos — você vai enfrentar dilemas complexos e testar sua capacidade de agir com eficiência sob pressão.

### A REBELIÃO PRECISA DE VOCÊ!

## Descrição do Jogo

"Aliança Rebelde - Operações Críticas" é um jogo de estratégia e puzzle narrativo, onde o jogador assume o papel de um(a) Coordenador(a) de Operações da Aliança Rebelde. Com uma atmosfera inspirada na seriedade e tensão de narrativas como "Andor" e "Rogue One", o jogo desafia o jogador a aplicar **algoritmos gananciosos** para resolver problemas complexos em diversas missões. Cada nível é uma etapa crucial na campanha contra o Império, exigindo lógica e precisão.

## Público-Alvo

- Estudantes da disciplina de Projeto de Algoritmos;
- Entusiastas de jogos de puzzle e estratégia
- Fãs de ficção científica com temas de rebelião, espionagem e operações táticas.

## Objetivos do Jogo

- **Para o Jogador**: Concluir com sucesso todas as missões ao utilizar os algoritmos gananciosos para otimizar os resultados e avançar na narrativa a medida que enfraquece o Império e fortalece a causa Rebelde.
- **Educacional:** Proporcionar uma compreensão intuitiva e prática da aplicação e do funcionamento de diferentes algoritmos gananciosos em contextos variados e significativos.

## Missões

### MISSÃO 1: "A Rota do Contrabando" 

 - **Algoritmo Ganancioso**: Knapsack
 - **Contexto:** Nossas células em setores remotos precisam desesperadamente de suprimentos – de medicamentos a componentes tecnológicos. Sua primeira tarefa é otimizar o carregamento de um transporte clandestino e garantir que nossos contatos sejam pagos discretamente, sem levantar suspeitas imperiais.
 - **Descrição**: Você tem acesso a uma lista de suprimentos essenciais, cada um com seu "valor estratégico" para a Rebelião e seu "volume/peso".
 - **Desafio:** Escolher a combinação de itens que maximize o "valor estratégico" total sem exceder a capacidade de carga.

## MISSÃO 2: "Pagamento ao Informante"
 
- **Algoritmo Ganancioso**: Coin Changing (Problema do Troco)
 - **Contexto:** Após o sucesso da Missão 1, Fulcrum informa que a rota segura para Atravis foi garantida por um informante volátil que agora espera seu pagamento em créditos imperiais. O Império monitora transações financeiras suspeitas.
 - **Descrição**: Você precisa pagar um valor exato ao informante usando o sistema monetário imperial padrão, que possui cédulas de diferentes denominações.
 - **Desafio:** Realizar o pagamento utilizando o menor número possível de "cédulas" de crédito para evitar levantar suspeitas devido a um volume grande de dinheiro transacionado.


## MISSÃO 3: "Sincronia Secreta"

- **Algoritmo Ganancioso**: Interval Scheduling
 - **Contexto:** A coordenação é a chave para a sobrevivência. Temos múltiplas janelas de oportunidade para ações de inteligência e sabotagem, mas nossos recursos humanos e técnicos são limitados. Precisamos agir com precisão cirúrgica.
 - **Descrição**: Você recebe uma lista de potenciais "operações" (coleta de inteligência, inserção de agentes, sabotagem de comunicação), cada uma com um horário de início e fim específico para ser executada por uma equipe especializada ou usando um equipamento específico 
 - **Desafio:** Selecionar o maior número de operações não conflitantes que podem ser realizadas pela equipe/equipamento.

## MISSÃO 4: "Contagem Regressiva em Kessel "

- **Algoritmo Ganancioso**: Scheduling to Minimize Lateness (Minimizar Atraso Máximo)
 - **Contexto:** Emergência Nível Alfa! Uma rebelião em massa na prisão de especiarias de Kessel serve de distração para a fuga de prisioneiros políticos e cientistas vitais. O Império respondeu rápido, e uma frota de bloqueio chegará em breve. Temos apenas UMA nave de extração rápida, processando um grupo de resgate por vez.
 - **Descrição**: Cada "Grupo de Extração" requer um tempo específico para preparo e transporte (tj) e tem um prazo final crítico (dj) antes que sua rota de fuga seja cortada. Se uma extração atrasar, as chances de sobrevivência caem drasticamente.
 - **Desafio:** Ordenar a execução das tarefas de extração para minimizar o maior atraso individual (Lmax) de qualquer grupo, garantindo que as operações mais críticas sofram o menor impacto possível e que a operação total não exceda o tempo limite antes da chegada da frota imperial.
   
## MISSÃO 5: "Estabelecendo a Rede Sombra"

- **Algoritmo Ganancioso**: Interval Partitioning
 - **Contexto:** Para expandir nosso alcance, precisamos estabelecer rotas seguras e postos avançados discretos. Isso requer um planejamento meticuloso para evitar patrulhas e otimizar o uso de nossas poucas naves de transporte e equipes de reconhecimento.
 - **Descrição**:  Um setor estratégico precisa de vigilância constante através de múltiplas "janelas de tempo" (intervalos) para monitorar movimentações imperiais. Você tem um número limitado de esquadrões de patrulha ou droides de reconhecimento.
 - **Desafio:** Atribuir o menor número possível de esquadrões/droides para cobrir todas as janelas de vigilância necessárias. Um esquadrão/droide pode iniciar uma nova tarefa assim que a anterior for concluída

 ## MISSÃO 6: "Estabelecendo Rotas Clandestinas"

- **Algoritmo Ganancioso**: Selecting Breakpoints (Seleção de Pontos de Parada)
 - **Contexto:** Com a expansão das operações da Aliança, graças à sua coordenação, é crucial estabelecer novas rotas de abastecimento seguras e rotas de fuga através de territórios hostis ou não mapeados. Nossas naves de transporte têm autonomia limitada.
 - **Descrição**:  Você precisa planejar uma rota de longo alcance através de um sistema ou setor perigoso. Sua nave de transporte (ou um batedor) pode viajar uma distância máxima específica antes de precisar parar para reabastecer, recalcular saltos no hiperespaço ou evitar detecção. Você tem uma lista de potenciais "pontos seguros" (estações abandonadas, campos de asteroides densos, luas desabitadas) ao longo da rota designada.
 - **Desafio:** Escolher o menor número possível de paradas (breakpoints) necessárias para completar a rota com segurança, garantindo que nenhum trecho da viagem exceda a autonomia da nave.


## MISSÃO 7: "A Voz da Resistência"

- **Algoritmo Ganancioso**: Algoritmo de Huffman
 - **Contexto:** A informação é nossa arma mais poderosa. Precisamos transmitir dados críticos – códigos de acesso, relatórios de inteligência, propaganda Rebelde – de forma compacta e segura, burlando os censores e sistemas de vigilância do Império.
 - **Descrição**:  Uma mensagem vital, contendo vários símbolos ou fragmentos de informação com diferentes frequências de ocorrência, precisa ser enviada. O canal de comunicação é instável e tem largura de banda limitada.
 - **Desafio:** Desenvolver um esquema de codificação (construir a árvore de Huffman e derivar os códigos) para a mensagem, minimizando o número total de bits necessários para a transmissão. 












