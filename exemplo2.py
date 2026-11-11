# UFC/DEMA, 2026.2
# Exemplo de uso da restrição 'regular' ('AddAutomaton').
# 
# Agendamento de enfermeiros de acordo com as seguinte regras:
# 1. Máximo de 4 dias consecutivos de trabalho;
# 2. Não é permitido um dia de trabalho isolado;
# 3. Máximo de 3 dias consecutivos de trabalho noturno;
# 4. Não é permitido trabalho noturno seguido de trabalho diurno (virar noite).

from ortools.sat.python import cp_model


def gerar_escala(num_dias):
    
    FOLGA, DIURNO, NOTURNO = 0, 1, 2
    turnos = [FOLGA, DIURNO, NOTURNO]
    nomes = {FOLGA: "FOLGA",
             DIURNO: "DIURNO",
             NOTURNO: "NOTURNO"}
    # ----------------------------------------------------------------------
    # Variáveis de decisão
    
    modelo = cp_model.CpModel()
    escala = [modelo.NewIntVar(FOLGA, NOTURNO, f"escala_{d}") \
              for d in range(num_dias)]

    # ----------------------------------------------------------------------
    # Montagem do autômato
    
    # Estado: (último turno,
    #          dias consecutivos trabalhados,
    #          noites consecutivas trabalhadas).
    inicial = (FOLGA, 0, 0)
    estados = {inicial}
    fila = list([inicial])
    transicoes = []

    # A partir do estado inicial, obter os demais estados possíveis, por
    # das transações permitidas. Isso descreve implicitamente a linguagem de
    # vetores permitidos (viáveis).
    while fila:
        # Estado no final do dia anterior
        ultimo, dias_trabalhados, noites = estado = fila.pop(0)

        # Para cada turno possível no dia atual
        for turno in turnos:
            if turno == FOLGA:
                # Regra 2: dia de trabalho isolado
                if dias_trabalhados == 1:
                    continue
                proximo = (FOLGA, 0, 0)
            else:
                # <turno> em {DIURNO, NOTURNO}
                
                # Regra 1: 4 dias de trabalho consecutivos
                if dias_trabalhados >= 4:
                    continue
                # Regra 4: virar noite
                if ultimo == NOTURNO and turno == DIURNO:
                    continue

                novas_noites = noites + 1 if turno == NOTURNO else 0
                # Regra 3: dias consecutivos de trabalho noturno
                if novas_noites > 3:
                    continue

                proximo = (turno, dias_trabalhados + 1, novas_noites)

            transicao = (estado, turno, proximo)
            transicoes.append( transicao )
            
            if proximo not in estados:
                estados.add(proximo)
                fila.append(proximo)

    # Identificar cada estado com um número inteiro
    ids = {estado: i for i, estado in enumerate(sorted(estados))}
    # Expressar transições por meio das respectivas ids
    transicoes_ids = [(ids[a], t, ids[b]) for a, t, b in transicoes]
    
    # A folga adicional é uma variável artificial (fixada em FOGLA), que
    # permite ao autômato rejeitar uma escala na qual o último dia real
    # trabalhado é isolado.
    folga_final = modelo.NewIntVar(FOLGA, FOLGA, "folga_final")

    # Restrição regular.
    # Não inserimos a variável artificial no vetor <escala> para
    # evitar tratá-la como verdadeira parte da escala.
    modelo.AddAutomaton(escala + [folga_final],
                        ids[inicial],
                        [ids[inicial]],
                        transicoes_ids)

    # ----------------------------------------------------------------------
    # Tentamos resolver a criação de uma escala individual
    
    solver = cp_model.CpSolver()
    status = solver.Solve(modelo)

    if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        return None
    return [nomes[solver.Value(turno)] for turno in escala]


if __name__ == "__main__":

    # Exemplo de uso
    escala = gerar_escala(14)

    if escala is None:
        print("Não foi encontrada uma escala viável.")
    else:
        print("Escala encontrada:")
        print(f"Semana 1: {escala[:7]}")
        print(f"Semana 2: {escala[7:]}")

