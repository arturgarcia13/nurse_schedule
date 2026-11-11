# Verificação determinística da Atividade 3.
# O verificador de regras abaixo foi escrito diretamente a partir do texto do
# enunciado e NÃO reutiliza o autômato: ele serve de juiz independente.
#   python3 verificar.py           -> sai com código 0 se tudo passar
import itertools
import sys

import escala_enfermeiros as m

F, D, N = m.FOLGA, m.DIURNO, m.NOTURNO
SABADOS_DOMINGOS = [(5, 6), (12, 13)]  # índices base 0 (início numa segunda)


def blocos(seq, pred):
    """Comprimentos dos blocos maximais de posições que satisfazem pred."""
    return [len(list(g)) for k, g in itertools.groupby(seq, key=pred) if k]


def violacoes_individuais(seq):
    """Lista de regras (1.3) violadas por uma escala individual."""
    v = []
    if any(t not in (F, D, N) for t in seq):
        v.append("1: atribuição inválida")
    trabalha = lambda t: t != F
    if sum(map(trabalha, seq)) > 7:
        v.append("2: mais de 7 dias")
    bt = blocos(seq, trabalha)
    if any(b >= 5 for b in bt):
        v.append("3: 5+ dias consecutivos")
    if any(b == 1 for b in bt):  # bloco de tamanho 1 = dia isolado (bordas inclusas)
        v.append("4: dia isolado")
    if any(b >= 4 for b in blocos(seq, lambda t: t == N)):
        v.append("5: 4+ noites consecutivas")
    if any(a == N and b == D for a, b in zip(seq, seq[1:])):
        v.append("6: N seguido de D")
    if not any(seq[s] == F and seq[d] == F for s, d in SABADOS_DOMINGOS):
        v.append("7: sem fim de semana de folga")
    return v


def checar_escala(escala):
    erros = []
    if len(escala) != 8 or any(len(l) != 14 for l in escala):
        erros.append("dimensão diferente de 8 x 14")
    for e, linha in enumerate(escala):
        for r in violacoes_individuais(linha):
            erros.append(f"enfermeiro {e + 1}: regra {r}")
    for d in range(14):
        for t, k in ((D, 2), (N, 2)):
            c = sum(l[d] == t for l in escala)
            if c != k:
                erros.append(f"dia {d + 1}: {c} no turno {m.SIGLAS[t]} (esperado {k})")
    return erros


def checar_automato():
    """Compara o autômato com as regras em todas as 3^14 sequências."""
    inicial, finais, transicoes, _ = m.construir_automato(14)
    delta = {(a, t): b for a, t, b in transicoes}
    finais = set(finais)
    aceitas = divergencias = 0
    exemplos = []
    # Busca em profundidade sobre os prefixos, guardando o estado do autômato
    # (None = estado morto) para não refazer a simulação desde o início.
    pilha = [((), inicial)]
    while pilha:
        prefixo, s = pilha.pop()
        if len(prefixo) == 14:
            pelo_automato = s is not None and s in finais
            pelas_regras = not violacoes_individuais(prefixo)
            aceitas += pelo_automato
            if pelo_automato != pelas_regras:
                divergencias += 1
                if len(exemplos) < 5:
                    exemplos.append((prefixo, pelo_automato, pelas_regras))
            continue
        for t in (F, D, N):
            prox = None if s is None else delta.get((s, t))
            pilha.append((prefixo + (t,), prox))
    return aceitas, divergencias, exemplos


def main():
    ok = True

    escala = m.gerar_escala()
    if escala is None:
        print("[FALHA] instância do enunciado: solver não encontrou escala")
        ok = False
    else:
        erros = checar_escala(escala)
        print(f"[{'OK' if not erros else 'FALHA'}] escala do solver: "
              f"{len(erros)} violações")
        for e in erros:
            print("   ", e)
        ok &= not erros

    aceitas, div, exemplos = checar_automato()
    print(f"[{'OK' if div == 0 else 'FALHA'}] autômato vs regras em 3^14 = "
          f"{3 ** 14} sequências: {aceitas} aceitas, {div} divergências")
    for ex in exemplos:
        print("   ", "".join(m.SIGLAS[t] for t in ex[0]),
              "autômato:", ex[1], "regras:", ex[2])
    ok &= div == 0

    inviavel = m.gerar_escala(cobertura={D: 3, N: 3})
    print(f"[{'OK' if inviavel is None else 'FALHA'}] cobertura 3+3 "
          f"(demanda 84 > capacidade 56) é declarada inviável")
    ok &= inviavel is None

    # Sanidade do próprio verificador: casos que DEVEM ser rejeitados.
    ruins = {
        "dia isolado no início": [D, F] + [F] * 12,
        "dia isolado no fim": [F] * 12 + [F, D],
        "N seguido de D": [N, D] + [F] * 12,
        "5 dias seguidos": [D] * 5 + [F] * 9,
        "4 noites": [N] * 4 + [F] * 10,
        "8 dias": [D, D, F, D, D, F, F, D, D, F, D, D, F, F],
        "sem fim de semana": [F, F, F, F, D, D, D, F, F, F, F, D, D, D],
    }
    falsos_ok = [k for k, s in ruins.items() if not violacoes_individuais(s)]
    print(f"[{'OK' if not falsos_ok else 'FALHA'}] verificador rejeita "
          f"{len(ruins)} casos inválidos conhecidos {falsos_ok or ''}")
    ok &= not falsos_ok

    print("\nRESULTADO:", "APROVADO" if ok else "REPROVADO")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
