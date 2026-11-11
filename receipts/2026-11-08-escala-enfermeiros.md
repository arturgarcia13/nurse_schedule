# Recibo — escala de enfermeiros com AddAutomaton (2026-11-08)

**O que mudou:** criados `escala_enfermeiros.py` (CP-SAT: 8 `AddAutomaton`, um por enfermeiro, para as regras 1-7; somas lineares para cobertura 2D+2N) e `verificar.py`.

**Evidência:**
```
$ python3 verificar.py
[OK] escala do solver: 0 violações
[OK] autômato vs regras em 3^14 = 4782969 sequências: 8420 aceitas, 0 divergências
[OK] cobertura 3+3 (demanda 84 > capacidade 56) é declarada inviável
[OK] verificador rejeita 7 casos inválidos conhecidos
RESULTADO: APROVADO   (exit 0)
```

**Custo:** solução em ~2,4 s; verificação exaustiva ~31 s. Sem subagentes (o juiz é código determinístico).

**Commit inicial:** o repositório no GitHub (`arturgarcia13/nurse_schedule`) já tinha um "Initial commit" (README + `.gitignore` do template Python); o trabalho entra em um commit sobre ele.

**Riscos residuais:** estados finais no lugar da folga artificial do exemplo (equivalência comprovada pela enumeração); interpretação "fim de semana" = sáb+dom dos dias 6-7 ou 13-14.

**Atualização (2026-11-11):** criados `README.md`, `requirements.txt`, `feature_list.json` e `.gitignore`; este recibo foi movido para `receipts/`. O trabalho passou para o repositório `nurse_schedule/`, clonado de `github.com/arturgarcia13/nurse_schedule`. Evidência repetida: `uv run --python 3.12 --with ortools python verificar.py` e venv 3.12 criado a partir de `requirements.txt` -> exit 0, mesmo resultado (4/4 OK).
