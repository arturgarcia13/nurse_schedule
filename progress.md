# progress.md — Atividade 3 (PPR 2026.2)

## Contrato
- Resultado: `escala_enfermeiros.py` (OR-Tools CP-SAT) que imprime uma escala válida de 8 enfermeiros x 14 dias, ou informa inviabilidade.
- Escopo: `escala_enfermeiros.py`, `verificar.py`, `README.md`, `requirements.txt`, `feature_list.json`, `progress.md`, `receipts/`, `.gitignore`. Não-objetivos: otimização, bibliotecas fora de OR-Tools/itertools.
- Base obrigatória: `exemplo2.py` (aula 27/10) — autômato gerado por BFS sobre estados; `AddAutomaton` é exigido.
- Evidência de aceite: `verificar.py` rodado com OR-Tools instalado (comandos no `README.md`) sai com código 0, cobrindo:
  1. verificador independente das regras (escrito a partir do PDF, sem reutilizar o autômato) aprova a escala;
  2. enumeração exaustiva das 3^14 sequências: aceitação do autômato == regras individuais 1-7;
  3. instância inviável (cobertura 3 por turno) gera a mensagem de inviabilidade.
- Ações que exigem aprovação humana: nenhuma (trabalho publicado em 2026-11-11).
- Teto de iteração: 3 tentativas de reparo; parar se o mesmo teste falhar 2x com o mesmo erro.

## Decisões
- Regras individuais (1-7) ficam todas dentro do autômato; o estado carrega o dia, então as regras de calendário (fim de semana) e de contagem (máx. 7 dias) também são impostas por `AddAutomaton`. Cobertura (entre enfermeiros) fica em somas lineares, pois não é uma propriedade de uma sequência individual.
- Fim do horizonte: em vez da folga artificial do exemplo, usam-se estados finais (dia 14, fim de semana cumprido, último bloco de trabalho não isolado).
- Observação de factibilidade: demanda = 14 dias x 4 = 56 turnos; capacidade = 8 x 7 = 56. Cada enfermeiro trabalha exatamente 7 dias.

## Estado (2026-11-11)
- Repositório: `nurse_schedule/` (origin `github.com/arturgarcia13/nurse_schedule`); o trabalho fica em um commit sobre o "Initial commit" do GitHub.
- Arquivos: `escala_enfermeiros.py` (modelo), `verificar.py` (juiz independente), `exemplo2.py` (ponto de partida), `README.md` e `requirements.txt` (execução reproduzível), `feature_list.json`, `progress.md`, `receipts/`, `Como funciona a escala de enfermeiros.md` (explicação didática, não exigida).
- Autômato: 818 estados, 1273 transições, 50 finais; aceita 8.420 das 4.782.969 sequências.
- Checagens (2026-11-11): `verificar.py` -> exit 0 (4/4 OK, ~30 s) com `uv run --python 3.12 --with ortools`, e também a partir de venv 3.12 criado com `requirements.txt` (ortools 9.15.6755). Saída do modelo idêntica em 3 execuções (seed fixa).
- Ambiente: o Python 3.14 do sistema não tem OR-Tools; use Python 3.12/3.13 conforme o README.
- Todos os 9 itens de `feature_list.json` com `passes: true`.
- Riscos residuais: o professor pode esperar a folga artificial do exemplo no lugar de estados finais (equivalentes; ver verificação exaustiva). Prazo confirmado pelo autor em 2026-11-11 (o PDF traz 09/10/2026, data anterior ao próprio PDF).
- Próxima ação: nenhuma — trabalho encerrado, publicado (`efec34c`) e prazo confirmado.
