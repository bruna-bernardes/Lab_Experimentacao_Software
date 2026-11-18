# LAB05 — Experimento no portal GOV.BR

**Disciplina:** Laboratório de Experimentação de Software — PUC Minas
**Professor:** Danilo Maia
**Grupo:** Ana Luiza, Bruna Bernardes e Walter Louback
**Sprint em curso:** Lab05S01

**Repositório:** <https://github.com/bruna-bernardes/Lab_Experimentacao_Software>
**GitHub Projects:** <https://github.com/users/bruna-bernardes/projects/2/views/1>

## O estudo

O software é o portal GOV.BR em operação (`www.gov.br`), medido de fora como um visitante anônimo. A pergunta é quanto tempo e quantos bytes o HTML público leva para chegar, se as páginas enviam um conjunto mínimo de cabeçalhos de segurança, e se as páginas iniciais de quatro órgãos diferem das páginas de entrada do portal.

O objeto é o portal servido ao cidadão. Não é o repositório, nem commits, nem issues.

## Onde está cada parte da Sprint 1

| Entrega da Sprint 1 | Lugar |
|---|---|
| Software, três critérios, pergunta, caminhos | `planejamento/proposta_s01.md` |
| Primeira versão das 7 categorias, GQM, hipóteses, ameaças | `planejamento/proposta_s01.md` |
| Plano de coleta e regras de ética | `planejamento/proposta_s01.md` e `instrumentacao/protocolo_coleta.md` |
| Plano de análise | `planejamento/proposta_s01.md` e `analise/LEIA-ME.md` |
| Coleta piloto versionada e validada | `instrumentacao/dados/` |
| Descritiva, testes, tamanho de efeito, figuras e impacto | `analise/resultados/relatorio_piloto.md` |

## Divisão

O enunciado sugere três papéis. O grupo adotou essa divisão:

| Integrante | Papel | Pasta |
|---|---|---|
| Ana Luiza | Planejamento e método | `README.md` e `planejamento/` |
| Bruna Bernardes | Instrumentação e operação | `instrumentacao/` |
| Walter Louback | Análise e impacto | `analise/` |

Cada pasta é a parte que essa pessoa commita. O professor pode pedir a qualquer integrante que explique qualquer parte.

## Reproduzir

Os testes não acessam a rede:

```bash
python3 Laboratorio_05/instrumentacao/test_instrumentacao.py
python3 Laboratorio_05/analise/test_analise.py
```

A análise do piloto já versionado, sem novo acesso ao portal:

```bash
python3 Laboratorio_05/analise/analisar_piloto.py
```

Uma coleta nova substitui o CSV, leva cerca de um minuto e fica em uma requisição por segundo. O comando está em `instrumentacao/protocolo_coleta.md`.
