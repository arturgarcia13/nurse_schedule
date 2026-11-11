# Como funciona a escala de enfermeiros

Nov 8, 2026 · @Artur Garcia

## 1. O problema, em palavras simples

O programa monta a escala de 8 enfermeiros por 14 dias, e a gente descobre logo de cara que cada um precisa trabalhar exatamente 7 dias. Vamos entender por quê antes de abrir o código.

Imagine uma tabela grande. Cada linha é um enfermeiro e cada coluna é um dia, de segunda (dia 1) até o domingo da segunda semana (dia 14). Em cada quadradinho escrevemos uma letra:

- **F** = folga (não trabalha);
- **D** = diurno (trabalha das 6h às 18h);
- **N** = noturno (trabalha das 18h às 6h do dia seguinte).

São 8 × 14 = 112 quadradinhos, e cada um tem 3 letras possíveis. O total de tabelas diferentes é 3 multiplicado por ele mesmo 112 vezes: cerca de 2,7 × 10^53. É um número com 54 algarismos. Nem todos os computadores do mundo juntos conseguiriam testar uma por uma. Por isso precisamos de um método esperto, e é isso que este documento explica.

**A conta que fecha.** Todo dia precisa de 2 pessoas no D e 2 no N, ou seja, 4 turnos por dia. Em 14 dias são 4 × 14 = 56 turnos para preencher. Cada enfermeiro pode trabalhar no máximo 7 dias, então a equipe inteira oferece no máximo 8 × 7 = 56 turnos. Como 56 = 56, não sobra nenhuma folga extra: cada enfermeiro trabalha exatamente 7 dias. Guarde essa conta, ela explica por que o problema é "apertado".

As regras que toda escala precisa obedecer (seção 1.3 do enunciado), com o número que vamos usar no texto inteiro:

| Regra | O que diz | Em linguagem de criança |
| --- | --- | --- |
| 1 | Não trabalhar D e N no mesmo dia | Uma letra por quadradinho |
| 2 | No máximo 7 dias trabalhados | No máximo 7 letras D ou N na linha |
| 3 | Nunca 5 ou mais dias seguidos de trabalho | No máximo 4 letras de trabalho grudadas |
| 4 | Nenhum dia de trabalho isolado, nem no começo nem no fim | Um trabalho sozinho entre folgas é proibido |
| 5 | Nunca 4 ou mais noites seguidas | No máximo 3 letras N grudadas |
| 6 | N não pode ser seguido de D | Depois de virar a noite, não pode pegar às 6h |
| 7 | Pelo menos um fim de semana inteiro de folga | Sábado e domingo com F, na semana 1 ou na 2 |
| Cobertura | Exatamente 2 D e 2 N por dia | Em cada coluna: dois D e dois N |

Por que existe a regra 6? O turno N do dia 3 termina às 6h do dia 4. Um turno D no dia 4 começaria exatamente às 6h. A pessoa sairia de um plantão e entraria em outro sem dormir.

## 2. Os arquivos e o caminho que o programa percorre

Só um arquivo resolve o problema (`escala_enfermeiros.py`). Os outros servem para provar que a resposta está certa e para registrar o trabalho.

| Arquivo | Para que serve | Quem lê |
| --- | --- | --- |
| `exemplo2.py` | Exercício da aula de 27/10, ponto de partida. Monta um autômato para 4 regras de um único enfermeiro. | O professor e a gente, como modelo |
| `escala_enfermeiros.py` | O programa da atividade: constrói o autômato, monta o modelo, chama o solver e imprime a tabela. | Quem roda `python3 escala_enfermeiros.py` |
| `verificar.py` | O "juiz": confere a resposta com regras escritas de outro jeito e testa o autômato contra todas as 4.782.969 sequências possíveis de um enfermeiro. | Quem roda `python3 verificar.py` |
| `progress.md` | O "caderno de bordo": o combinado (contrato), as decisões tomadas e o estado atual. | Quem continuar o trabalho depois |
| `feature_list.json` | A lista de itens a cumprir, cada um com `passes` (falso ou verdadeiro) e a prova. | Quem quer saber o que já foi comprovado |
| `receipts/…md` | O "recibo": o que mudou, a saída dos testes e os riscos que sobraram, para ler em 15 segundos. | Quem revisa |

Os três últimos vêm do seu documento de harness (seções 1 a 3): a ideia é que tudo que importa fique escrito em arquivo, e não só na conversa.

O caminho dentro de `escala_enfermeiros.py` tem quatro paradas:

1. `construir_automato()` cria a "máquina de regras" de um enfermeiro (seções 5 a 7).
2. `gerar_escala()` cria as 112 variáveis, prende uma cópia da máquina em cada enfermeiro (seção 8) e acrescenta a cobertura de cada dia (seção 9).
3. O solver procura uma tabela que obedeça a tudo (seção 10).
4. `imprimir_escala()` mostra a tabela de um jeito fácil de ler (seção 10).

O `verificar.py` fica de fora desse caminho de propósito. Ele importa o programa, pede a resposta e confere tudo sozinho (seção 11).

## 3. Programação por restrições: dizer *o quê*, não *como*

Na programação por restrições, a gente descreve como a resposta tem de ser, e um programa pronto, o *solver*, se encarrega de achar essa resposta.

Pense num Sudoku. Você não recebe instruções do tipo "coloque 5 na casa B3". Recebe regras: cada linha, coluna e quadrado tem os números de 1 a 9 sem repetir. Quem resolve é você. Aqui é igual, só que quem resolve é o computador.

Todo modelo tem três peças:

- **Variáveis**: as casas vazias, ou seja, o que não sabemos ainda. Aqui são os 112 quadradinhos da tabela.
- **Domínio**: os valores que cada variável pode receber. Aqui é {0, 1, 2}, que significa {F, D, N}.
- **Restrições**: as regras que ligam as variáveis. Aqui são as regras 1 a 7 e a cobertura.

No código, essas peças aparecem assim:

```python
from ortools.sat.python import cp_model   # traz a biblioteca
modelo = cp_model.CpModel()               # um "caderno" vazio onde anotamos o problema
# ... criamos variáveis e restrições no modelo ...
solver = cp_model.CpSolver()              # o "detetive" que vai resolver
status = solver.Solve(modelo)             # manda resolver
```

**OR-Tools** é uma biblioteca gratuita do Google para problemas de decisão. **CP-SAT** é o solver dela que usamos. O nome junta duas famílias de técnicas:

- **CP (Constraint Programming)**: cada regra "corta" valores que não podem mais dar certo. Isso se chama *propagação*. Exemplo: se um enfermeiro já tem 7 dias de trabalho marcados, a regra 2 apaga D e N de todos os dias que faltam e só sobra F.
- **SAT (satisfatibilidade)**: quando o solver chuta um valor e chega num beco sem saída, ele volta atrás e anota o motivo do erro, para nunca mais cair na mesma armadilha. Isso se chama *aprendizado de conflitos*.

O solver alterna entre "cortar o impossível" e "chutar com cuidado" até encontrar uma tabela completa, ou até provar que nenhuma existe. É por isso que ele não precisa olhar as 2,7 × 10^53 tabelas: cortes cedo eliminam bilhões de tabelas de uma vez só.

O enunciado não pede a "melhor" escala, só uma que valha. Por isso o modelo não tem *função objetivo* (uma nota para maximizar ou minimizar). Esse tipo de problema se chama *problema de satisfação*.

## 4. Como o computador enxerga a tabela

O solver só trabalha com números inteiros, então trocamos cada letra por um número e guardamos a tabela numa "lista de listas".

**Constantes no topo do arquivo.** São nomes fixos para números, para o código ficar legível:

```python
FOLGA, DIURNO, NOTURNO = 0, 1, 2           # F=0, D=1, N=2
TURNOS = [FOLGA, DIURNO, NOTURNO]          # a lista das 3 opções
SIGLAS = {FOLGA: "F", DIURNO: "D", NOTURNO: "N"}   # número -> letra, só para imprimir
NUM_DIAS = 14
NUM_ENFERMEIROS = 8
COBERTURA = {DIURNO: 2, NOTURNO: 2}        # quantas pessoas por turno
MAX_DIAS_TRABALHADOS = 7                   # regra 2
MAX_CONSECUTIVOS = 4                       # regra 3 ("5 ou mais" proibido = no máximo 4)
MAX_NOITES = 3                             # regra 5 ("4 ou mais" proibido = no máximo 3)
```

A primeira linha usa *atribuição múltipla*: o Python dá 0 para FOLGA, 1 para DIURNO e 2 para NOTURNO de uma vez. `SIGLAS` e `COBERTURA` são *dicionários*: guardam pares chave → valor, como uma agenda de telefones.

Se o professor mudar um limite, basta trocar o número no topo. O resto do código usa o nome, nunca o número solto.

**Contagem a partir do zero.** No Python, o primeiro item de uma lista tem índice 0. Então o "dia 1" do enunciado é `d = 0` no código, e o "enfermeiro 1" é `e = 0`. Só na hora de imprimir somamos 1 de volta.

**Onde caem os fins de semana.** O período começa numa segunda, então os dias se repetem de 7 em 7:

```python
DIAS_SEMANA = ["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"]
DOMINGOS = [d for d in range(NUM_DIAS) if d % 7 == 6]   # resultado: [6, 13]
```

- `range(14)` gera 0, 1, 2, …, 13.
- `d % 7` é o *resto da divisão* por 7. Segunda tem resto 0, terça 1, …, domingo 6.
- `[ ... for ... if ... ]` é uma *compreensão de lista*: "monte a lista dos `d` que passam no teste". Sobram 6 e 13, que são os dias 7 e 14 do enunciado.
- O sábado é sempre o dia antes do domingo: 5 e 12.

**As variáveis de decisão.** Dentro de `gerar_escala()`:

```python
escala = [[modelo.NewIntVar(FOLGA, NOTURNO, f"escala_{e}_{d}")
           for d in range(num_dias)]
          for e in range(num_enfermeiros)]
```

- `modelo.NewIntVar(0, 2, nome)` cria uma variável inteira que só pode valer 0, 1 ou 2. Ela ainda não tem valor: é uma casa vazia do Sudoku.
- O nome, como `"escala_3_10"`, é só uma etiqueta para depuração. O `f` antes das aspas cria uma *f-string*, que troca `{e}` e `{d}` pelos valores.
- São duas compreensões de lista, uma dentro da outra: para cada enfermeiro, uma lista de 14 variáveis. Resultado: 8 linhas × 14 colunas = 112 variáveis. `escala[2][5]` é "o que o enfermeiro 3 faz no dia 6".

**A regra 1 já está cumprida aqui.** Cada quadradinho é uma única variável com um único valor. Não existe jeito de ela valer D e N ao mesmo tempo. Por isso a regra 1 nunca aparece como um `if`: ela vem de graça da forma como montamos as variáveis.

## 5. O que é um autômato

Um autômato é um jogo de tabuleiro que lê uma fileira de letras, uma de cada vez, e no fim responde "aceito" ou "rejeito". É a ferramenta que o enunciado exige (`AddAutomaton`), e serve para julgar a linha de um enfermeiro, do dia 1 ao dia 14.

O tabuleiro tem quatro tipos de peça:

- **Estados**: as casas do tabuleiro. Cada casa é uma "lembrança" do que já aconteceu.
- **Transições**: setas entre as casas, cada uma com uma letra. "Estando na casa A e lendo N, vá para a casa B."
- **Estado inicial**: a casa onde o peão começa.
- **Estados finais** (ou de aceitação): as casas onde o peão pode terminar.

As regras do jogo são três:

1. O peão começa no estado inicial.
2. Para cada letra da fileira, ele segue a seta com aquela letra. **Se não existir seta, o jogo acaba na hora e a fileira é rejeitada.**
3. Lidas todas as letras, se o peão está num estado final, a fileira é aceita. Se não está, é rejeitada.

Repare na regra 2: **proibir algo é simplesmente não desenhar a seta.** Esse é o truque que o código inteiro usa.

**Um exemplo pequeno: só a regra 6** (N não pode ser seguido de D). Bastam duas casas:

- Casa A = "ontem não foi N". É a casa inicial.
- Casa B = "ontem foi N".
- De A: F vai para A, D vai para A, N vai para B.
- De B: F vai para A, N fica em B, e **D não tem seta**.
- As duas casas são finais.

&#91;embedded content: autômato de exemplo · só a regra 6 · 2 casas\]

Cada seta é uma letra permitida. A letra D, saindo de B, simplesmente não tem seta: é assim que o autômato proíbe algo.

Vamos ler `F D N N F D`: A → A → A → B → B → A → A. Terminou em casa final: aceita. Agora `D N D`: A → A → B → e o D não tem seta saindo de B. Rejeitada.

**A memória do autômato é só a casa onde ele está.** Ele não volta para reler letras antigas. Por isso, tudo que uma regra precisa lembrar (quantos dias seguidos, quantas noites, se já teve fim de semana livre) tem que estar escrito *dentro* do nome da casa. Esse é o desafio da seção 6.

Um nome técnico que aparece no `exemplo2.py`: a restrição *regular*. O conjunto de todas as fileiras que um autômato aceita se chama *linguagem regular*. Dizer "esta variável deve formar uma palavra da linguagem" é exatamente o que `AddAutomaton` faz.

## 6. Construindo o autômato no código

Não desenhamos as 818 casas à mão: o programa parte da casa inicial, testa as 3 letras, cria as casas novas que aparecem e repete até não surgir nenhuma casa nova. É a mesma técnica do `exemplo2.py`, com mais informação em cada casa.

### 6.1 O que cada casa lembra

Cada estado é uma *tupla* (um pacotinho de valores entre parênteses) com 6 informações, descrevendo a situação **ao final de um dia**:

| Campo | Valores | O que lembra | Regra que precisa dele |
| --- | --- | --- | --- |
| `dia` | 0 a 14 | Quantos dias já foram lidos | 7 (saber quando é domingo) e o fim do horizonte |
| `ultimo` | F, D ou N | O turno do dia anterior | 6 (N antes de D) e 7 (folga no sábado) |
| `consecutivos` | 0 a 4 | Dias de trabalho seguidos até agora | 3 (máx. 4) e 4 (dia isolado) |
| `noites` | 0 a 3 | Noites seguidas até agora | 5 (máx. 3) |
| `total` | 0 a 7 | Dias trabalhados até agora | 2 (máx. 7) |
| `fds` | `False` ou `True` | Já houve um fim de semana inteiro de folga? | 7 |

O `exemplo2.py` tinha só os três do meio (`ultimo`, `consecutivos`, `noites`), porque só tinha as regras 3 a 6. Acrescentamos `total` por causa da regra 2. Acrescentamos `dia` e `fds` por causa da regra 7: um autômato não sabe que dia é hoje, a menos que a casa conte isso para ele.

### 6.2 A busca em largura

```python
inicial = (0, FOLGA, 0, 0, 0, False)
estados = {inicial}        # conjunto: casas já descobertas
fila = [inicial]           # casas que ainda precisamos visitar
transicoes = []            # setas encontradas

while fila:                               # enquanto houver casa para visitar
    estado = fila.pop(0)                  # tira a PRIMEIRA da fila
    dia, ultimo, consecutivos, noites, total, fds = estado
    if dia == num_dias:
        continue                          # dia 14 já lido: essa casa não tem setas de saída
    for turno in TURNOS:                  # testa F, D e N
        ...                               # (regras, logo abaixo)
        transicoes.append((estado, turno, proximo))
        if proximo not in estados:        # casa nova?
            estados.add(proximo)
            fila.append(proximo)          # entra no FIM da fila
```

Peça por peça:

- **Fila**: como a fila do lanche. Quem chega vai para o fim (`append`), quem é atendido sai do começo (`pop(0)`). Atender sempre o mais antigo faz o programa explorar o tabuleiro "em camadas": primeiro todas as casas do dia 1, depois as do dia 2, e assim por diante. Isso se chama **busca em largura** (BFS, em inglês).
- **Conjunto** (`set`, escrito com chaves `{ }`): uma coleção sem repetição. Ele impede que a mesma casa entre duas vezes na fila. Sem ele, o programa visitaria casas repetidas para sempre.
- **Desempacotar**: a linha `dia, ultimo, ... = estado` abre a tupla e dá um nome a cada pedaço.
- **`continue`**: "pule o resto desta volta e vá para a próxima". No meio das regras, `continue` quer dizer "essa letra não ganha seta", ou seja, **proibido**.

Por que o laço termina? Cada campo tem um teto (dia até 14, total até 7, e assim por diante). Então o número de casas possíveis é finito, e uma hora não aparece mais casa nova. Ao final, sobram **818 estados e 1.273 transições**.

### 6.3 Cada regra vira um `if`

**Se a letra é F (folga):**

```python
if consecutivos == 1:
    continue                      # Regra 4: deixaria um dia de trabalho isolado
novo_fds = fds or (dia in DOMINGOS and ultimo == FOLGA)   # Regra 7
proximo = (dia + 1, FOLGA, 0, 0, total, novo_fds)
```

- **Regra 4**: `consecutivos == 1` quer dizer "ontem trabalhei, mas anteontem não". Folgar hoje deixaria ontem sozinho entre duas folgas. Então a seta F não é criada.
- **Regra 7**: o `dia` da casa é o índice do dia que estamos lendo agora. Se ele é domingo (6 ou 13) e `ultimo` (o sábado) foi folga, acabamos de completar um fim de semana livre. O `or` faz o `True` "grudar": uma vez cumprido, `fds` continua verdadeiro até o fim.
- Folgar zera `consecutivos` e `noites`, e `total` não muda.

**Se a letra é D ou N (trabalho):**

```python
if consecutivos >= MAX_CONSECUTIVOS:            # Regra 3: já tenho 4 seguidos
    continue
if ultimo == NOTURNO and turno == DIURNO:       # Regra 6: N seguido de D
    continue
novas_noites = noites + 1 if turno == NOTURNO else 0
if novas_noites > MAX_NOITES:                   # Regra 5: seria a 4ª noite
    continue
if total + 1 > MAX_DIAS_TRABALHADOS:            # Regra 2: seria o 8º dia
    continue
proximo = (dia + 1, turno, consecutivos + 1, novas_noites, total + 1, fds)
```

- A linha `novas_noites = noites + 1 if turno == NOTURNO else 0` é um *if de uma linha*: se hoje é N, soma 1 às noites; se é D, a sequência de noites quebra e volta a 0.
- Cada `continue` apaga a seta. Se nenhum `continue` disparou, a seta é criada e a casa de destino é `proximo`.
- Trabalhar soma 1 em `consecutivos` e em `total`.

Como fica cada regra no autômato:

| Regra | Onde está |
| --- | --- |
| 1 | Na forma das variáveis: uma por dia (seção 4) |
| 2 | `if total + 1 > MAX_DIAS_TRABALHADOS` |
| 3 | `if consecutivos >= MAX_CONSECUTIVOS` |
| 4 | `if consecutivos == 1` na folga + estado inicial + estados finais (seção 7) |
| 5 | `if novas_noites > MAX_NOITES` |
| 6 | `if ultimo == NOTURNO and turno == DIURNO` |
| 7 | `novo_fds = ...` na folga + estados finais (seção 7) |

## 7. As pontas da fileira: começo e fim

As bordas do período são resolvidas em dois lugares: na casa onde o peão começa e nas casas onde ele pode terminar.

### 7.1 O começo: "fingir que ontem foi folga"

```python
inicial = (0, FOLGA, 0, 0, 0, False)
```

A casa inicial diz: dia 0 lido, "ontem" foi F, nenhum dia seguido, nenhuma noite, nenhum trabalho, nenhum fim de semana ainda. É como se existisse uma folga imaginária antes do dia 1.

Isso resolve a regra 4 no começo sem nenhum código extra. Veja a fileira `D F ...`:

1. Dia 1 é D: `consecutivos` passa de 0 para 1.
2. Dia 2 é F: o `if consecutivos == 1` dispara e não há seta. Rejeitada.

Foi exatamente o que o enunciado pediu: "não podemos ter um enfermeiro trabalhando no primeiro dia e folgando no segundo".

O `ultimo = FOLGA` também não atrapalha as outras regras. A regra 6 só olha `ultimo == NOTURNO`, e a regra 7 só usa `ultimo` quando o dia lido é domingo.

### 7.2 O fim: os estados finais

```python
finais = [e for e in estados
          if e[0] == num_dias and e[5] and e[2] != 1]
```

Uma casa é final quando cumpre três condições (`e[0]` é o primeiro campo da tupla, `e[2]` o terceiro, `e[5]` o sexto):

| Condição | Campo | Por quê |
| --- | --- | --- |
| `e[0] == num_dias` | `dia == 14` | A fileira tem que ter os 14 dias inteiros |
| `e[5]` | `fds` é `True` | Regra 7: o fim de semana livre já aconteceu |
| `e[2] != 1` | `consecutivos` diferente de 1 | Regra 4 no último dia |

A última condição pega o caso "folga no dia 13 e trabalho no dia 14". Nesse caso o peão termina com `consecutivos = 1`, ou seja, um dia de trabalho sozinho no fim. Se os dias 13 e 14 forem trabalho, termina com 2 e está tudo certo.

Por que a regra 4 precisa de cuidado no fim? No meio da fileira, um dia isolado é pego quando chega a folga seguinte. No dia 14 não existe "dia seguinte", então alguém precisa conferir na saída. Essa conferência é o estado final.

No total, 50 das 818 casas são finais.

### 7.3 A diferença em relação ao `exemplo2.py`

O exemplo da aula resolveu o fim de outro jeito. Ele colava uma variável extra, `folga_final`, presa no valor F, no fim da fileira. Ao ler essa folga, o `if dias_trabalhados == 1` barrava um último dia isolado. Então só a casa `(FOLGA, 0, 0)` precisava ser final.

Aqui isso não funcionaria do mesmo jeito: nossas casas guardam `dia`, `total` e `fds`, então não existe uma única casa "depois da folga" para ser a final. Além disso, a regra 7 também precisa ser conferida na saída. Então usamos estados finais. As duas formas aceitam exatamente as mesmas fileiras de 14 dias, e a seção 11 mostra a prova. A nossa ainda economiza uma variável por enfermeiro.

## 8. Ligando o autômato ao modelo

O `AddAutomaton` só entende casas numeradas, então primeiro trocamos cada tupla por um número. Depois prendemos uma cópia do autômato em cada um dos 8 enfermeiros.

### 8.1 Dando um número a cada casa

```python
ids = {estado: i for i, estado in enumerate(sorted(estados))}
transicoes_ids = [(ids[a], t, ids[b]) for a, t, b in transicoes]
return ids[inicial], [ids[e] for e in finais], transicoes_ids, ids
```

- `sorted(estados)` coloca as tuplas em ordem. Sem isso, a ordem de um conjunto pode variar, e os números mudariam de uma execução para outra.
- `enumerate(...)` entrega pares (posição, item): (0, primeira tupla), (1, segunda), e assim por diante.
- `{estado: i ...}` é uma *compreensão de dicionário*. Monta a "agenda" tupla → número.
- A segunda linha reescreve cada seta trocando as tuplas pelos números. A letra `t` já é número (0, 1 ou 2).
- A função devolve quatro coisas: o número da casa inicial, a lista dos números das casas finais, as setas numeradas e a agenda `ids`. A agenda só serve para imprimir o tamanho do autômato e para o `verificar.py`.

### 8.2 Uma máquina para cada enfermeiro

```python
inicial, finais, transicoes, _ = construir_automato(num_dias)
for e in range(num_enfermeiros):
    modelo.AddAutomaton(escala[e], inicial, finais, transicoes)
```

- O `_` (sublinhado) é o jeito Python de dizer "recebo esse valor, mas não vou usar". Aqui é a agenda `ids`.
- O autômato é construído **uma vez só**. Todos os enfermeiros seguem as mesmas regras, então o mesmo tabuleiro serve para todos.
- `escala[e]` é a linha do enfermeiro `e`: suas 14 variáveis, na ordem dos dias. `AddAutomaton(linha, inicial, finais, setas)` diz ao modelo: "a fileira de valores desta linha tem que ser aceita por este autômato".

### 8.3 O que acontece por dentro (versão simplificada)

O solver não "joga" o tabuleiro depois de escolher os valores. Ele trata o peão como incógnita também. Para cada enfermeiro, cria variáveis escondidas q0, q1, …, q14, uma para a casa do peão depois de cada dia, e impõe:

- q0 é a casa inicial;
- q14 está entre as casas finais;
- para cada dia d, o trio (q\_d, valor do dia d+1, q\_{d+1}) tem que ser uma das setas da lista.

Como tudo vira restrição, o solver consegue raciocinar nos dois sentidos. Exemplo: se ele já sabe que a casa depois do dia 10 tem `total = 7`, a única seta que sai dali é F, então os dias 11 a 14 viram F na hora. Esse é o "cortar o impossível" da seção 3, aplicado ao autômato.

## 9. A cobertura: olhando a coluna, não a linha

O autômato lê a **linha** de um enfermeiro. A cobertura ("2 D e 2 N em cada dia") fala da **coluna** de um dia, misturando os 8 enfermeiros. Nenhum autômato de uma linha consegue ver a coluna, então essa regra entra no modelo como contas de somar.

### 9.1 Interruptores liga/desliga

Para contar quantas pessoas estão no D num dia, é mais fácil ter um "interruptor" que vale 1 quando o enfermeiro está no D e 0 quando não está. Esse tipo de variável se chama **booleana** (só aceita 0 ou 1, falso ou verdadeiro).

```python
x = [[[modelo.NewBoolVar(f"x_{e}_{d}_{t}") for t in TURNOS]
      for d in range(num_dias)]
     for e in range(num_enfermeiros)]
```

São três interruptores por quadradinho: `x[e][d][0]` (é folga?), `x[e][d][1]` (é D?) e `x[e][d][2]` (é N?). No total, 8 × 14 × 3 = 336 interruptores.

### 9.2 Ligando os interruptores ao quadradinho

Os interruptores são variáveis novas. Precisamos amarrá-los a `escala[e][d]`, senão o solver poderia escolher valores que não combinam.

```python
modelo.AddExactlyOne(x[e][d])
modelo.Add(escala[e][d] == sum(t * x[e][d][t] for t in TURNOS))
```

- `AddExactlyOne(...)`: dos 3 interruptores, exatamente 1 está ligado.
- A segunda linha diz: escala = 0 × (é F) + 1 × (é D) + 2 × (é N). Como só um interruptor está ligado, a soma dá exatamente o número do turno escolhido.

Exemplo: se o enfermeiro está no N, os interruptores são (0, 0, 1) e a conta dá 0 + 0 + 2 = 2 = NOTURNO. Se tentasse ligar o interruptor de D com `escala = 2`, a conta daria 1, diferente de 2, e o solver rejeitaria. As duas descrições sempre contam a mesma história. Técnicos chamam isso de *channeling* (canalizar uma informação entre duas representações).

### 9.3 As contas de cada dia

```python
for d in range(num_dias):
    for turno, k in cobertura.items():       # (DIURNO, 2) e (NOTURNO, 2)
        modelo.Add(sum(x[e][d][turno] for e in range(num_enfermeiros)) == k)
```

- `cobertura.items()` percorre os pares do dicionário `{DIURNO: 2, NOTURNO: 2}`.
- Para cada dia e cada turno, somamos os interruptores daquele turno nos 8 enfermeiros e exigimos que a soma seja exatamente 2. Isso cobre "nem falta nem sobra".
- O `sum(...)` aqui não calcula um número na hora. Como os interruptores ainda não têm valor, o Python monta uma *expressão linear* (uma conta com incógnitas) e o `==` vira uma restrição.
- Folga não precisa de conta própria. Se 2 estão no D e 2 no N, sobram 8 − 4 = 4 de folga automaticamente.

São 14 dias × 2 turnos = 28 contas de cobertura.

## 10. Resolver e mostrar a resposta

Com o modelo pronto, o solver acha uma escala em cerca de 2,4 segundos, e o programa a imprime como uma tabela.

### 10.1 Chamando o solver

```python
solver = cp_model.CpSolver()
solver.parameters.num_workers = 8
solver.parameters.random_seed = 0
status = solver.Solve(modelo)

if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
    return None
return [[solver.Value(v) for v in linha] for linha in escala]
```

- `num_workers = 8`: o CP-SAT põe 8 "detetives" para trabalhar ao mesmo tempo, cada um com uma estratégia diferente. O primeiro que achar a resposta encerra a busca.
- `random_seed = 0`: fixa a "semente" dos sorteios internos. A ideia é o resultado se repetir. Nas nossas 3 execuções, a saída foi idêntica. Com vários detetives em paralelo, o OR-Tools não garante isso em toda máquina; se precisar de repetição garantida, use `num_workers = 1`.
- `Solve(modelo)` devolve um **status**, uma etiqueta com o resultado da busca:

| Status | Significado | O que o programa faz |
| --- | --- | --- |
| `OPTIMAL` | Achou uma resposta. Sem função objetivo, "ótima" quer dizer só "válida". | Devolve a escala |
| `FEASIBLE` | Achou uma resposta válida. | Devolve a escala |
| `INFEASIBLE` | Provou que nenhuma tabela obedece a tudo. | Devolve `None` |
| `MODEL_INVALID` | O modelo foi escrito errado. | Devolve `None` |
| `UNKNOWN` | Parou antes de decidir (por exemplo, limite de tempo). | Devolve `None` |

Um cuidado honesto: o programa trata `UNKNOWN` e `MODEL_INVALID` do mesmo jeito que `INFEASIBLE` e imprime "inviável". Como não definimos limite de tempo e o modelo é válido, o solver sempre vai até o fim e só pode responder "achei" ou "provei que não existe". Se um dia alguém acrescentar `max_time_in_seconds`, vale separar `UNKNOWN` com uma mensagem própria ("tempo esgotado").

- `solver.Value(v)` lê o valor que o solver escolheu para a variável `v`. A compreensão de lista dupla monta a tabela 8 × 14 com números 0, 1 e 2.
- `None` é o "nada" do Python: a função avisa que não há escala.

### 10.2 O ponto de partida do programa

```python
if __name__ == "__main__":
    inicial, finais, transicoes, ids = construir_automato()
    print(f"Autômato: {len(ids)} estados, ...")
    escala = gerar_escala()
    if escala is None:
        print("O problema é inviável: ...")
    else:
        imprimir_escala(escala)
```

`if __name__ == "__main__":` quer dizer "só rode isto quando o arquivo for executado diretamente". Quando o `verificar.py` faz `import escala_enfermeiros`, esse bloco não roda: o juiz só pega as funções emprestadas, sem imprimir nada. As funções têm valores padrão (`num_enfermeiros=NUM_ENFERMEIROS`, …), então `gerar_escala()` sem argumentos resolve o problema do enunciado, e `gerar_escala(cobertura={...})` resolve uma variante.

### 10.3 Imprimindo a tabela

`imprimir_escala` usa *f-strings* com alinhamento: `f"{valor:>5}"` escreve o valor encostado à direita num espaço de 5 caracteres, para as colunas ficarem retinhas. Também usa um truque de contagem: `sum(t != FOLGA for t in linha)` soma verdadeiros e falsos, e no Python `True` vale 1 e `False` vale 0. Assim, a soma conta quantos dias não são folga.

Esta é a saída real do programa:

```text
                  1    2    3    4    5    6    7    8    9   10   11   12   13   14   Trab  Noites
                Seg  Ter  Qua  Qui  Sex  Sáb  Dom  Seg  Ter  Qua  Qui  Sex  Sáb  Dom
Enfermeiro 1      F    F    F    N    N    F    F    N    N    N    F    F    N    N      7       7
Enfermeiro 2      D    D    N    F    F    D    D    N    N    F    F    F    F    F      7       3
Enfermeiro 3      F    F    D    N    F    F    F    F    D    N    N    F    D    D      7       3
Enfermeiro 4      N    N    F    F    F    N    N    F    F    D    D    N    F    F      7       5
Enfermeiro 5      F    F    F    F    D    D    D    D    F    D    D    D    F    F      7       0
Enfermeiro 6      F    F    D    D    D    F    F    D    D    F    F    F    D    D      7       0
Enfermeiro 7      N    N    N    F    F    N    N    F    F    F    N    N    F    F      7       7
Enfermeiro 8      D    D    F    D    N    F    F    F    F    F    F    D    N    N      7       3
Diurno (D)        2    2    2    2    2    2    2    2    2    2    2    2    2    2
Noturno (N)       2    2    2    2    2    2    2    2    2    2    2    2    2    2
```

Confira com os olhos: todo mundo tem 7 na coluna "Trab", como a conta da seção 1 previa. As duas últimas linhas mostram 2 em todos os dias. O enfermeiro 5 trabalha `D D D D` nos dias 5 a 8: são 4 seguidos, o máximo permitido. O enfermeiro 3 faz `D N` nos dias 3 e 4. Isso é permitido: a regra 6 só proíbe N seguido de D, não o contrário, porque o D termina às 18h e o N do dia seguinte só começa às 18h do outro dia.

## 11. Como sabemos que está certo: o `verificar.py`

O `verificar.py` termina com "APROVADO" e código de saída 0 depois de quatro provas, e nenhuma delas confia no autômato.

**Por que um juiz separado?** Quem faz a prova não deve corrigir a própria prova. Se o autômato tivesse um erro e o juiz usasse o mesmo autômato, o erro passaria duas vezes sem ninguém ver. Por isso o juiz escreve as regras de novo, de um jeito completamente diferente: olhando a linha inteira de uma vez, sem casas nem setas.

### 11.1 A ferramenta principal: blocos

```python
def blocos(seq, pred):
    return [len(list(g)) for k, g in itertools.groupby(seq, key=pred) if k]
```

`itertools.groupby` junta itens vizinhos que dão a mesma resposta para a pergunta `pred`. Com a pergunta "é trabalho?", a linha `D D F N N N F` vira os grupos `[D D] [F] [N N N] [F]`. Ficamos só com os grupos de trabalho (`if k`) e medimos o tamanho de cada um: `[2, 3]`.

Com isso, cada regra vira uma pergunta simples:

| Regra | Pergunta do juiz |
| --- | --- |
| 1 | Todo valor é F, D ou N? |
| 2 | Somando os dias de trabalho, dá no máximo 7? |
| 3 | Algum bloco de trabalho tem 5 ou mais? |
| 4 | Algum bloco de trabalho tem tamanho 1? |
| 5 | Algum bloco de N tem 4 ou mais? |
| 6 | Em algum par de dias vizinhos (`zip(seq, seq[1:])`) aparece (N, D)? |
| 7 | Os pares (5, 6) ou (12, 13) são ambos F? |
| Cobertura | Em cada dia, há exatamente 2 D e 2 N? |

A regra 4 fica bem simples aqui: um dia isolado é um bloco de tamanho 1, esteja ele no meio, no começo ou no fim. O `groupby` não precisa de "folga imaginária" porque os blocos da ponta já terminam na borda da lista.

`zip(seq, seq[1:])` junta a lista com ela mesma deslocada uma posição, formando os pares (dia 1, dia 2), (dia 2, dia 3), e assim por diante.

### 11.2 As quatro provas

1. **A escala do solver**: `checar_escala` confere o tamanho 8 × 14, as regras 1 a 7 em cada linha e a cobertura em cada coluna. Resultado: 0 violações.
2. **O autômato inteiro**: o juiz testa **todas** as fileiras possíveis de 14 dias de um enfermeiro, 3^14 = 4.782.969. Para cada uma, pergunta ao autômato e às regras do juiz, e compara as respostas. Resultado: 8.420 aceitas pelos dois e **0 divergências**. Isso prova que o autômato é igual às regras para qualquer escala, e não só para a que o solver achou.
3. **O caso impossível**: pedimos 3 D e 3 N por dia. Seriam 6 × 14 = 84 turnos, mas a equipe só oferece 56. O programa responde `None`, como deveria.
4. **O juiz do juiz**: 7 escalas erradas de propósito, uma para cada tipo de erro (dia isolado no início, no fim, N seguido de D, 5 dias seguidos, 4 noites, 8 dias, sem fim de semana). O juiz rejeita as 7. Se o juiz deixasse alguma passar, ele mesmo estaria quebrado.

### 11.3 Como a prova 2 cabe em 30 segundos

```python
pilha = [((), inicial)]
while pilha:
    prefixo, s = pilha.pop()               # tira o ÚLTIMO da pilha
    if len(prefixo) == 14:
        pelo_automato = s is not None and s in finais
        pelas_regras = not violacoes_individuais(prefixo)
        ...                                # compara os dois
        continue
    for t in (F, D, N):
        prox = None if s is None else delta.get((s, t))
        pilha.append((prefixo + (t,), prox))
```

- `delta` é um dicionário (casa, letra) → próxima casa, montado a partir das setas. `delta.get(...)` devolve `None` quando a seta não existe.
- `None` aqui significa **casa morta**: o autômato já rejeitou. Mesmo assim a fileira continua sendo montada até 14 letras, porque o juiz precisa ver todas as 4.782.969 e confirmar que ele também rejeita.
- **Pilha** é o contrário da fila: quem entra por último sai primeiro (`pop()` sem número), como uma pilha de pratos. Isso faz a busca ir fundo primeiro, completando uma fileira antes de começar outra. Chama-se **busca em profundidade**.
- Guardar a casa do autômato junto com o começo da fileira evita reler tudo desde o dia 1 a cada vez.

### 11.4 O placar final

```python
ok &= not erros          # ok = ok E (não houve erros)
...
sys.exit(0 if ok else 1)
```

`&=` quer dizer "continua verdadeiro só se esta prova também passou": uma única falha derruba o placar. `sys.exit(0)` avisa o sistema operacional que deu tudo certo, e `sys.exit(1)` avisa que algo falhou. É assim que ferramentas automáticas (um script, um corretor) sabem o resultado sem ler o texto.

## 12. Glossário e perguntas que costumam ficar soltas

### 12.1 Glossário

| Termo | Em uma frase | Onde aparece |
| --- | --- | --- |
| Programação por restrições | Descrever as regras da resposta e deixar um solver encontrá-la | Seção 3 |
| Solver / CP-SAT | O programa do OR-Tools que procura a resposta, cortando o impossível e chutando com cuidado | `cp_model.CpSolver()` |
| Variável de decisão | Uma casa vazia que o solver vai preencher | `NewIntVar`, `NewBoolVar` |
| Domínio | Os valores que uma variável pode receber | `NewIntVar(0, 2, ...)` |
| Restrição | Uma regra que liga variáveis | `Add`, `AddExactlyOne`, `AddAutomaton` |
| Problema de satisfação | Basta achar uma resposta válida, sem nota para melhorar | Todo o modelo |
| Propagação | Apagar valores que já não podem dar certo | Dentro do solver |
| Autômato | Tabuleiro de casas e setas que aceita ou rejeita uma fileira de letras | `construir_automato` |
| Estado / transição | Casa do tabuleiro / seta com uma letra | Tuplas e `transicoes` |
| Estado inicial / finais | Onde o peão começa / onde pode terminar | `inicial`, `finais` |
| Restrição regular | Exigir que uma lista de variáveis seja aceita por um autômato | `AddAutomaton` |
| Busca em largura | Explorar em camadas usando uma fila | `fila.pop(0)` |
| Busca em profundidade | Ir até o fim de um caminho antes de voltar, usando uma pilha | `pilha.pop()` no `verificar.py` |
| Variável booleana | Interruptor que vale 0 ou 1 | `x[e][d][t]` |
| Channeling | Amarrar duas descrições da mesma informação | `escala == soma de t × x` |
| Expressão linear | Uma soma de variáveis vezes números | `sum(...) == k` |
| Status | A etiqueta com o resultado da busca | `OPTIMAL`, `INFEASIBLE`, ... |
| Tupla, lista, conjunto, dicionário | Pacote fixo, sequência, coleção sem repetição, agenda chave → valor | `( )`, `[ ]`, `{a}`, `{a: b}` |
| Compreensão de lista | Montar uma lista com um `for` dentro de colchetes | `[d for d in ... if ...]` |
| Código de saída | O número que o programa devolve ao sistema: 0 = deu certo | `sys.exit` |

### 12.2 Perguntas que costumam ficar soltas

**Por que não existe um `if` para a regra 1?** Porque cada dia de cada enfermeiro é uma única variável com um único valor (seção 4). D e N no mesmo dia não dá nem para escrever.

**D num dia e N no dia seguinte pode?** Pode. O D termina às 18h e o N do dia seguinte começa às 18h do outro dia, com 24 horas de descanso. Só o contrário (N e depois D) é proibido pela regra 6.

**E o N do dia 14, que termina no dia 15?** O dia 15 está fora do período, e nenhuma regra fala dele. O autômato para no dia 14.

**E se o enfermeiro folgar nos dois fins de semana?** Sem problema. A regra pede "pelo menos um". O `or` em `novo_fds` mantém `True` depois do primeiro.

**Todas as 818 casas levam a uma casa final?** Não. Algumas são becos sem saída, por exemplo uma casa do dia 14 sem fim de semana livre. Elas não atrapalham: o solver percebe que não há caminho até um estado final e as descarta sozinho. Removê-las deixaria o autômato menor, mas não mudaria a resposta.

**Os 8 enfermeiros são iguais. Isso atrapalha?** Trocar duas linhas de uma escala válida dá outra escala válida. Isso se chama *simetria*. Em problemas de otimização, ela pode deixar a busca lenta, e a gente acrescentaria regras para "quebrar" a simetria. Aqui queremos uma resposta só e o solver acha em 2,4 segundos, então não foi preciso.

**Por que a cobertura não está no autômato?** Porque o autômato lê a linha de um enfermeiro e a cobertura fala da coluna de um dia (seção 9).

**Posso mudar o número de dias?** Com cuidado. `DOMINGOS` é calculado a partir da constante `NUM_DIAS` no topo do arquivo, e não do parâmetro `num_dias` da função. Para mudar o horizonte, troque `NUM_DIAS` no topo. O `verificar.py` foi escrito para os 14 dias do enunciado (pares de fim de semana e 3^14 fixos) e também precisaria ser ajustado.

**Posso mudar limites ou cobertura?** Sim. `MAX_DIAS_TRABALHADOS`, `MAX_CONSECUTIVOS`, `MAX_NOITES`, `NUM_ENFERMEIROS` e `COBERTURA` são lidos pelo resto do código. Rode o `verificar.py` de novo depois de mudar; os limites dele estão escritos à parte, de propósito, então precisam ser atualizados também.

**O que o programa imprime se não houver escala?** "O problema é inviável: não existe escala que satisfaça todas as restrições." A prova 3 da seção 11 testa esse caminho.

**Usamos alguma biblioteca além das permitidas?** Não. Só OR-Tools, `itertools` e `sys`, que vem com o Python.
