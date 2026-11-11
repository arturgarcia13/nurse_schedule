# Atividade 3 — Escala de enfermeiros (PPR 2026.2)

Programa em Python/OR-Tools (CP-SAT) que monta a escala de 8 enfermeiros em
14 dias (segunda a domingo da segunda semana), com cobertura de 2 diurnos e
2 noturnos por dia e as 7 regras individuais de trabalho/descanso do
enunciado (seção 1.3). As regras individuais são impostas com
`AddAutomaton`; a cobertura, que envolve vários enfermeiros ao mesmo tempo,
com somas lineares.

## Como executar

Requisito: OR-Tools. Verificado com **Python 3.12** e **ortools 9.15.6755**
(no Python 3.14 do sistema o pacote ainda não está instalado).

Com [uv](https://docs.astral.sh/uv/), sem instalar nada no sistema:

```bash
uv run --python 3.12 --with ortools python escala_enfermeiros.py
uv run --python 3.12 --with ortools python verificar.py   # sai com 0 se tudo passar
```

Ou com um ambiente virtual próprio:

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
python escala_enfermeiros.py
python verificar.py
```

A verificação exaustiva leva cerca de 30 s; o solver acha a escala em ~2 s.

## Arquivos

| Arquivo | Papel |
| --- | --- |
| `escala_enfermeiros.py` | Modelo CP-SAT e impressão da escala |
| `verificar.py` | Juiz independente: regras lidas do enunciado, equivalência autômato ↔ regras em 3^14 sequências, prova de inviabilidade e casos inválidos |
| `exemplo2.py` | Exercício da aula de 27/10, ponto de partida |
| `Como funciona a escala de enfermeiros.md` | Explicação didática do modelo (material de estudo, não exigido) |
| `feature_list.json`, `progress.md`, `receipts/` | Registro do trabalho |
