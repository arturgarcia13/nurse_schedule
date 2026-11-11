# UFC/DEMA - Programação por Restrições (CC0335), 2026.2

from ortools.sat.python import cp_model

FOLGA, DIURNO, NOTURNO = 0, 1, 2
TURNOS = [FOLGA, DIURNO, NOTURNO]
SIGLAS = {FOLGA: "F", DIURNO: "D", NOTURNO: "N"}

NUM_DIAS = 14
NUM_ENFERMEIROS = 8
COBERTURA = {DIURNO: 2, NOTURNO: 2}

MAX_DIAS_TRABALHADOS = 7
MAX_CONSECUTIVOS = 4
MAX_NOITES = 3

DIAS_SEMANA = ["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"]
DOMINGOS = [d for d in range(NUM_DIAS) if d % 7 == 6]


def construir_automato(num_dias=NUM_DIAS):
    """Gera o autômato da escala individual.

    Estado ao final de um dia:
        (dia,                 número de dias já decididos, 0..num_dias
         ultimo,              turno do dia anterior
         consecutivos,        dias consecutivos trabalhados até agora
         noites,              noites consecutivas até agora
         total,               dias trabalhados até agora
         fds)                 True se já houve um fim de semana de folga

    Devolve (estado_inicial, estados_finais, transicoes, ids), com estados
    identificados por inteiros, como exige AddAutomaton.
    """
    inicial = (0, FOLGA, 0, 0, 0, False)
    estados = {inicial}
    fila = [inicial]
    transicoes = []

    while fila:
        estado = fila.pop(0)
        dia, ultimo, consecutivos, noites, total, fds = estado
        if dia == num_dias:
            continue
        for turno in TURNOS:
            if turno == FOLGA:
                if consecutivos == 1:
                    continue
                novo_fds = fds or (dia in DOMINGOS and ultimo == FOLGA)
                proximo = (dia + 1, FOLGA, 0, 0, total, novo_fds)
            else:
                if consecutivos >= MAX_CONSECUTIVOS:
                    continue
                if ultimo == NOTURNO and turno == DIURNO:
                    continue
                novas_noites = noites + 1 if turno == NOTURNO else 0
                if novas_noites > MAX_NOITES:
                    continue
                if total + 1 > MAX_DIAS_TRABALHADOS:
                    continue
                proximo = (
                    dia + 1,
                    turno,
                    consecutivos + 1,
                    novas_noites,
                    total + 1,
                    fds,
                )

            transicoes.append((estado, turno, proximo))
            if proximo not in estados:
                estados.add(proximo)
                fila.append(proximo)

    finais = [e for e in estados if e[0] == num_dias and e[5] and e[2] != 1]

    ids = {estado: i for i, estado in enumerate(sorted(estados))}
    transicoes_ids = [(ids[a], t, ids[b]) for a, t, b in transicoes]
    return ids[inicial], [ids[e] for e in finais], transicoes_ids, ids


def gerar_escala(
    num_enfermeiros=NUM_ENFERMEIROS, num_dias=NUM_DIAS, cobertura=COBERTURA
):
    """Devolve a escala como lista de listas de turnos, ou None se inviável."""
    modelo = cp_model.CpModel()

    escala = [
        [modelo.NewIntVar(FOLGA, NOTURNO, f"escala_{e}_{d}") for d in range(num_dias)]
        for e in range(num_enfermeiros)
    ]

    inicial, finais, transicoes, _ = construir_automato(num_dias)
    for e in range(num_enfermeiros):
        modelo.AddAutomaton(escala[e], inicial, finais, transicoes)

    # ----------------------------------------------------------------------
    x = [
        [[modelo.NewBoolVar(f"x_{e}_{d}_{t}") for t in TURNOS] for d in range(num_dias)]
        for e in range(num_enfermeiros)
    ]
    for e in range(num_enfermeiros):
        for d in range(num_dias):
            modelo.AddExactlyOne(x[e][d])
            modelo.Add(escala[e][d] == sum(t * x[e][d][t] for t in TURNOS))
    for d in range(num_dias):
        for turno, k in cobertura.items():
            modelo.Add(sum(x[e][d][turno] for e in range(num_enfermeiros)) == k)

    # ----------------------------------------------------------------------
    solver = cp_model.CpSolver()
    solver.parameters.num_workers = 8
    solver.parameters.random_seed = 0
    status = solver.Solve(modelo)

    if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        return None
    return [[solver.Value(v) for v in linha] for linha in escala]


def imprimir_escala(escala):
    num_dias = len(escala[0])
    largura = 5
    cab_dia = "".join(f"{d + 1:>{largura}}" for d in range(num_dias))
    cab_sem = "".join(f"{DIAS_SEMANA[d % 7]:>{largura}}" for d in range(num_dias))
    print(f"{'':14}{cab_dia}   Trab  Noites")
    print(f"{'':14}{cab_sem}")
    print("-" * (14 + largura * num_dias + 15))
    for e, linha in enumerate(escala):
        celulas = "".join(f"{SIGLAS[t]:>{largura}}" for t in linha)
        trab = sum(t != FOLGA for t in linha)
        noites = sum(t == NOTURNO for t in linha)
        print(f"Enfermeiro {e + 1:<3}{celulas}   {trab:>4}  {noites:>6}")
    print("-" * (14 + largura * num_dias + 15))
    for turno, nome in ((DIURNO, "Diurno (D)"), (NOTURNO, "Noturno (N)")):
        contagens = "".join(
            f"{sum(linha[d] == turno for linha in escala):>{largura}}"
            for d in range(num_dias)
        )
        print(f"{nome:<14}{contagens}")
    print("\nLegenda: F = folga, D = diurno (6h-18h), N = noturno (18h-6h)")


if __name__ == "__main__":
    inicial, finais, transicoes, ids = construir_automato()
    print(
        f"Autômato: {len(ids)} estados, {len(transicoes)} transições, "
        f"{len(finais)} estados finais.\n"
    )

    escala = gerar_escala()
    if escala is None:
        print(
            "O problema é inviável: não existe escala que satisfaça "
            "todas as restrições."
        )
    else:
        print("Escala encontrada:\n")
        imprimir_escala(escala)
