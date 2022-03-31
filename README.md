# Lethal Virus on Network

## Informações Gerais do Aluno
    Nome: João Víctor Siqueira de Araujo
    Matrícula: 19/0031026
    Disciplina: Computação Experimental - CIC0203
    Turma: A
    Período: 2021/2
    Exemplo utilizado: virus_on_network

## Apresentação do Novo Modelo

Para esse projeto, foi escolhido o exemplo do modelo de Vírus em uma rede (Virus on a Network) e, a partir, dele foi implementada uma modificação com relação ao modelo original, a qual se trata da adição da variável controlável chamada de letalidade (lethality).

O objetivo de adicionar essa nova variável é para estudar como vírus capazes de matar seu hospedeiro interfeririam com a dispersão do mesmo pelo modelo.

## Hipótese Causal

Quanto maior for a transmissão de um vírus, maior vai ser a proporção de mortos em relação à indivíduos saudáveis no sistema. Ou seja, dado 2 vírus que possuem a mesma letalidade, o vírus que consegue se espalhar mais entre os agentes acabará por matar um número maior de indivíduos do que o vírus que se espalha menos.

## Justificativas para as Mudanças

Foram realizadas mudanças tanto no arquivo server.py quanto no arquivo model.py. A seguir temos a explicação de cada uma.

model.py:
1. Foi criado um novo estado para indicar que o agente morreu, o que chamei de estado morto (DECEASED). Anteriormente, os estados eram suscetível (SUSCEPTIBLE), infectado (INFECTED) e resistente (RESISTANT).

2. Foi criada a função number_deceased que conta quantos nós da rede estão no estado morto (DECEASED). Essa função não interfere no modelo, é apenas uma função de auxílio.

3. Foi adicionado um novo parâmetro que é justamente a variável letalidade (lethality). Essa variável vai indicar qual a probabilidade, entre 0.0 a 1.0, do vírus matar seu hospedeiro. Seu valor inicial é de 0.1, ou seja, o vírus tem 10% de chance de matar seu hospedeiro.

4. Foi removida a variável virus_check_frequency por ela não fazer mais sentido com o modelo sendo uma simulação de um vírus humano. Ela representava a probabilidade do agente se autodiagnosticar, o que faz mais sentido para computadores e não humanos.

5. Foram criadas duas variáveis globais chamadas: INCUBATION_PERIOD e ACUTE_PERIOD, que indicam o período em dias que o vírus fica em incubação e o período em que a infecção está em seu pico. Agora para o agente morrer ou se recuperar do vírus, é preciso que ele tenha passado do período de incubação. Já para ele ganhar resistência, é preciso que ele tenha passado do período agudo da infecção.

6. Para a classe dos agentes, foi criada uma nova variável própria para o agente, que eu chamei de time_infected que conta há quantos dias o agente está infectado pelo vírus. Ela é iniciada com zero e incrementada por 1 à cada passo da simulação em que o agente está infectado e é zerada quando esse se recupera ou se torna resistente. O intuito dessa variável é deixar o modelo mais fiel à situação real de contágio.

7. Foi removida a função try_check_situation() por causa da remoção da variável virus_check_frequency. A sua lógica, entretanto, foi mantida na função step() do agente.

8. Foi criada uma nova função para o agente, chamada de try_kill_agent que representa a situação na qual o vírus tenta matar o seu hospedeiro baseando-se na probabilidade do vírus matar um agente, que é justamente o valor da variável letalidade (lethality).

9. Por fim, a função step() do agente foi modificada de tal forma que para que todo agente infectado, o vírus tenta matar esse agente, e, caso o agente não morra, ele tenta remover a infecção e caso não consiga, aí sim, o vírus tenta infectar os vizinhos.

10. Foi criado um batch_run() para executar simulações do modelo. Esse batch_run() captura as variáveis de controle, independentes e dependentes tanto para agente quanto para o modelo e gera um arquivo .csv.

server.py:
1. Foi adicionado o parâmetro de modelo "lethality" que é do tipo slider. Essa alteração que permitirá que o usuário altere o valor desse parâmetro por meio da interface gráfica.

2. Foi removido o parâmetro "virus_check_frequency" como especificado anteriormente.

3. Foi feita também a inserção de uma cor para representar os agentes no estado morto (DECEASED). E por fim, esse estado também foi inserido no gráfico que mostrava a quantidade de agentes em um determinado estado a cada iteração.

4. Foram adicionadas as variáveis dependentes: Dead Healthy Ratio, Death Rate e Susceptible Rate no texto da simulação.

## Orientações Sobre Como Usar o Simulador

Ao executar o modelo, a interface apresentará no lado esquerdo uma série de parâmetros que podem ser manipulados pelo usuário. Grande maioria deles é do modelo original, mas temos a seguir o significado de cada parâmetro.

- Number of agents: a quantidade de nós (agentes) na rede.
- Avg Node Degree: a quantidade média de arestas (links) que saem de cada nó (agente).
- Initial Outbreak Size: a quantidade de nós (agentes) infectados inicialmente.
- Virus Spread Chance: a probabilidade de um nó (agente) espalhar o vírus para os seus vizinhos.
- Recovery Chance: a probabilidade de um nó (agente) infectado se recuperar e voltar ao estado suscetível
- Gain Resistance Chance: a probabilidade de um nó (agente) suscetível, que anteriormente foi infectado, de se tornar resistente ao vírus.
- Lethality: a probabilidade de um nó (agente) infectado ser morto pelo vírus.

No centro, temos a rede dos agentes em si, com um número pré-determinado de agentes infectados (Initial Outbreak Size) e a partir de cada passo, um agente infectado pode ou acabar morrendo pelo vírus ou infectar os agentes suscetíveis na sua vizinhança ou pode se recuperar do vírus voltando a ser suscetível e, talvez, ficar resistente ao vírus. Abaixo dessa rede, temos um gráfico que mostra a quantidade de agentes de cada estado (SUSCEPTIBLE, INFECTED, RESISTANT, DECEASED) para cada um dos passos de iteração. Também abaixo da rede, temos as variáveis dependetes mostrando a proporção de mortos em relação aos agentes saudáveis (Dead Healthy Ratio), a porcentagem de mortos (Death Rate), a proporção entre os agentes resistentes e os agentes suscetíveis (Resistant Susceptible Ratio) e a porcentagem de agentes suscetíveis (Susceptible Rate).

## Descrição das Variáveis Armazenadas no Arquivo CSV

Os dados contidos na pasta data_collection seguem a descrição abaixo:

O datacollector coletava dados da simulação a nível de modelo e a nível do agente. Esses dados foram salvos em arquivos CSV que podem ser vistos dentro da pasta data_collection. Os dados referentes ao modelo foram salvos nos arquivos iniciados com model_data. Já os dados referentes ao agente foram salvos nos arquivos iniciados com agent_data. A seguir temos a descrição de cada uma das variáveis dentro desses arquivos CSV.

Para os dados a nível de modelo temos as seguintes variáveis:
- Death Rate: indica a proporção de agentes mortos com relação ao total de agentes na rede. O objetivo dessa variável é verificar como o aumento da letalidade acaba por influenciar na quantidade de mortos total na rede.
- Susceptible Rate: indica a proporção de agentes suscetíveis com relação ao total de agentes na rede. Para essa variável, o objetivo seria visualizar que à medida que a letalidade aumenta, a quantidade de agentes suscetíveis ao final da execução também aumenta. O que indicaria que a transmissão do vírus dentro da rede está decaindo.

Para os dados a nível de agente temos a seguinte variável:
- Total Infected: indica a quantidade de vizinhos infectados pelo agente. A ideia de armazenar essa variável é ver que a medida que a letalidade aumenta, menor vai ser o número de agentes que tenham infectado algum vizinho, e também menor vai ser a quantidade de vizinhos infectados pelo agente.


Já os CSVs da pasta batch_data_collection seguem a descrição abaixo:

Os dados a nível de modelo:
- Variáveis de Controle:
    - num_nodes: quantidade de agentes presentes na rede.
    - avg_node_degree: número médio de arestas por vértice no gráfico.
    - initial_outbreak_size: quantidade de agentes infectados ao início da simulação.
    - lethality: probabilidade do vírus matar um agente, é a nova variável adicionada ao modelo.
    - recovery_chance: probabilidade do agente se recuperar do vírus (voltar a ser suscetível).
    - gain_resistance_chance:} probabilidade do agente adquirir resistência ao vírus, após se recuperar.
- Variáveis Independentes:
    - virus_spread_chance: probabilidade de um agente infectado infectar os seus vizinhos.
- Variáveis Dependentes:
    - Dead Healthy Ratio: variável que indica a proporção da quantidade de mortos em relação à quantidade de agentes saudáveis (suscetíveis e resistentes).
    - Death Rate: variável que indica a porcentagem de mortos totais na rede.
    - Resistant Susceptible Ratio: variável que indica a proporção da quantidade de resistentes em relação à quantidade de agentes suscetíveis.
    - Susceptible Rate: variável que indica a porcentagem do total agentes suscetíveis na rede.

Os dados a nível do agente eram muito grandes para enviar para o GitHub e por isso foram enviados em formato .zip, mas não há muito problema visto que os dados que serão usados para a análise exploratória são os dados do modelo. De resto, esses dados continham as mesmas variáveis de controle do modelo e o estado do agente a cada passo.

# README Original do Modelo

# Virus on a Network

## Summary

This model is based on the NetLogo model "Virus on Network".

For more information about this model, read the NetLogo's web page: http://ccl.northwestern.edu/netlogo/models/VirusonaNetwork.

JavaScript library used in this example to render the network: [d3.js](https://d3js.org/).

## Installation

To install the dependencies use pip and the requirements.txt in this directory. e.g.

```
    $ pip install -r requirements.txt
```

## How to Run

To run the model interactively, run ``mesa runserver`` in this directory. e.g.

```
    $ mesa runserver
```

Then open your browser to [http://127.0.0.1:8521/](http://127.0.0.1:8521/) and press Reset, then Run.

## Files

* ``run.py``: Launches a model visualization server.
* ``model.py``: Contains the agent class, and the overall model class.
* ``server.py``: Defines classes for visualizing the model (network layout) in the browser via Mesa's modular server, and instantiates a visualization server.

## Further Reading

The full tutorial describing how the model is built can be found at:
http://mesa.readthedocs.io/en/master/tutorials/intro_tutorial.html


[Stonedahl, F. and Wilensky, U. (2008). NetLogo Virus on a Network model](http://ccl.northwestern.edu/netlogo/models/VirusonaNetwork).
Center for Connected Learning and Computer-Based Modeling, Northwestern University, Evanston, IL.


[Wilensky, U. (1999). NetLogo](http://ccl.northwestern.edu/netlogo/)
Center for Connected Learning and Computer-Based Modeling, Northwestern University, Evanston, IL.
