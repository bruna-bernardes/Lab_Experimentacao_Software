from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
from scipy.stats import norm, binom, binomtest
from src.estatistica import simular, testar, META, ALFA

st.set_page_config(page_title='LAB04 | Sprint 1', layout='wide')
st.title('LAB04 — Testes de hipótese por dentro')
st.caption('Sprint 1 | Teste Z para proporção × teste binomial exato')
st.markdown('**Repositório:** https://github.com/bruna-bernardes/Lab_Experimentacao_Software  |  **GitHub Projects:** https://github.com/users/bruna-bernardes/projects/2/views/1')
st.header('1. Cenário')
st.write('Pergunta: a taxa de falhas de CI difere da meta de 5%? H₀: p = 0,05. H₁: p ≠ 0,05. Testes bicaudais, α = 0,05.')
try:
    df = pd.read_csv(Path(__file__).resolve().parent / 'dados' / 'execucoes_ci.csv')
    if 'falha' not in df or not df.falha.isin([0, 1]).all():
        raise ValueError('CSV precisa conter coluna falha com valores 0 ou 1.')
except FileNotFoundError:
    st.error('O CSV de dados reais está ausente. Execute: python -m src.coleta --repo pallets/flask --n 100')
    st.stop()
except ValueError as erro:
    st.error(str(erro))
    st.stop()

n = len(df)
taxa_real = float(df.falha.mean())
st.write(f'Dados reais: {n} execuções válidas; {int(df.falha.sum())} falhas ({taxa_real:.1%}). Origem: GitHub Actions, repositório {df.repositorio.iloc[0] if "repositorio" in df else "não informado"}.')
st.write('Simulação Bernoulli/binomial: cada execução é representada como sucesso (0) ou falha (1), com probabilidade de falha estimada pelos dados reais. Independência e taxa constante são simplificações.')
st.header('2. Os dados — G1')
simulados = simular(n, taxa_real)
reais = df.falha.to_numpy()

# Visão percentual adicional: comparação das proporções, sem substituir os histogramas exigidos.
fig_resumo, ax_resumo = plt.subplots(figsize=(11, 2.4))
for i, (nome, valores) in enumerate([('Dados reais', reais), ('Dados simulados', simulados)]):
    falhas = int(np.sum(valores))
    sucessos = len(valores) - falhas
    pct_sucesso = 100 * sucessos / len(valores)
    pct_falha = 100 * falhas / len(valores)
    ax_resumo.barh(i, pct_sucesso, color='#5278aa', height=0.55,
                   label='Sucesso' if i == 0 else None)
    ax_resumo.barh(i, pct_falha, left=pct_sucesso, color='#e27a45', height=0.55,
                   label='Falha' if i == 0 else None)
    ax_resumo.text(pct_sucesso / 2, i, f'{pct_sucesso:.0f}%',
                   ha='center', va='center', color='white', fontweight='bold')
    ax_resumo.text(101, i, f'{falhas} falhas de {len(valores)}',
                   va='center', fontsize=9)
ax_resumo.set_yticks([0, 1], ['Dados reais', 'Dados simulados'])
ax_resumo.invert_yaxis()
ax_resumo.set_xlim(0, 126)
ax_resumo.set_xticks([0, 25, 50, 75, 100])
ax_resumo.set_xlabel('Proporção de execuções (%)')
ax_resumo.set_title('Resumo percentual — sucesso e falha')
fig_resumo.tight_layout()
st.pyplot(fig_resumo)
plt.close(fig_resumo)
st.markdown(
    '<div style="text-align:center; font-size:14px; margin-top:-15px; margin-bottom:12px;">'
    '<span style="color:#5278aa;">■</span> Sucesso &nbsp;&nbsp;&nbsp;'
    '<span style="color:#e27a45;">■</span> Falha'
    '</div>',
    unsafe_allow_html=True
)

# Histogramas originais, exigidos no enunciado, com layout mais espaçado e padronizado.
fig, axes = plt.subplots(1, 2, figsize=(11, 4.8), sharey=True)

for ax, valores, nome in zip(
    axes,
    [reais, simulados],
    ['Dados reais', 'Dados simulados']
):
    ax.hist(
        valores,
        bins=[-.5, .5, 1.5],
        rwidth=.65,
        color='#5278aa',
        label='Frequência de execuções'
    )
    ax.set_xticks([0, 1], ['Sucesso (0)', 'Falha (1)'])
    ax.set_xlabel('Resultado da execução (categoria)')
    ax.set_ylabel('Frequência (execuções)')
    ax.set_title(nome)
    ax.set_ylim(0, max(np.bincount(valores, minlength=2)) * 1.12)

fig.suptitle('G1 — Distribuição de resultados de CI', fontsize=18)

# legenda única para os dois histogramas
handles, labels = axes[0].get_legend_handles_labels()
fig.legend(
    handles,
    labels,
    loc='lower center',
    bbox_to_anchor=(0.5, 0.02),
    ncol=1,
    frameon=True
)

fig.subplots_adjust(
    top=0.80,
    bottom=0.28,
    wspace=0.10
)

st.pyplot(fig)
plt.close(fig)
st.write(
    f'O G1 compara {n} execuções reais com {n} simuladas. '
    f'Nos dados reais, a taxa de falhas foi de {taxa_real:.1%}, '
    'valor utilizado como parâmetro da simulação Bernoulli. '
    'As barras horizontais resumem as proporções, enquanto os histogramas '
    'mostram as frequências de sucesso (0) e falha (1), sem pressupor normalidade.'
)

st.header('3. Como os testes funcionam — G2')
exemplo = testar(simular(n, META, seed=123))
st.write(f'Exemplo simulado sob H₀: {exemplo["falhas"]}/{n} falhas. Z = {exemplo["z"]:.3f}, p(Z) = {exemplo["p_z"]:.4f}; p(binomial exato) = {exemplo["p_exato"]:.4f}.')
fig, axes = plt.subplots(1, 2, figsize=(12, 4))
x = np.linspace(-4.5, 4.5, 800)
y = norm.pdf(x)
axes[0].plot(x, y, color='#2563a6', label='Distribuição Z sob H₀')
axes[0].fill_between(x, y, where=(abs(x) >= norm.ppf(1-ALFA/2)), alpha=.25, color='#e27a45', label='Região crítica (α = 5%)')
axes[0].fill_between(x, y, where=(abs(x) >= abs(exemplo['z'])), alpha=.22, color='#7b56a8', label=f'Área p = {exemplo["p_z"]:.3f}')
axes[0].axvline(exemplo['z'], color='#2563a6', ls='--', label='Z observado')
axes[0].set(title='Teste Z — aproximação normal', xlabel='Estatística Z (sem unidade)', ylabel='Densidade')
axes[0].legend(fontsize=8)
ks = np.arange(n+1)
probs = binom.pmf(ks, n, META)
# SciPy define o p-valor exato bicaudal pela soma das probabilidades <= à probabilidade do resultado observado.
p_observado = binom.pmf(exemplo['falhas'], n, META)
mascara_p = probs <= p_observado * (1 + 1e-12)
mascara_critica = np.array([binomtest(int(k), n, META, alternative="two-sided").pvalue < ALFA for k in ks])
axes[1].bar(ks, probs, color='#2e8b57', alpha=.6, label='Probabilidade sob H₀')
axes[1].bar(ks[mascara_critica], probs[mascara_critica], color='#e27a45', label='Região crítica (α = 5%)')
axes[1].bar(ks[mascara_p], probs[mascara_p], facecolor='none', edgecolor='#7b56a8', linewidth=1.5, label=f'Área p = {exemplo["p_exato"]:.3f}')
axes[1].axvline(exemplo['falhas'], color='#2e8b57', ls='--', label='Falhas observadas')
axes[1].set(xlim=(-.5, min(n, max(12, int(n*META+5*np.sqrt(n*META*(1-META)))))), title='Teste binomial exato — distribuição discreta', xlabel='Número de falhas (execuções)', ylabel='Probabilidade')
axes[1].legend(fontsize=8)
fig.suptitle('G2 — Distribuições sob H₀, regiões críticas e áreas do p-valor')
fig.tight_layout()
st.pyplot(fig)
st.write('O teste Z compara a proporção observada à meta usando uma aproximação normal; o binomial exato calcula probabilidades diretamente. O p-valor mede quão incompatível o resultado é com H₀, não a probabilidade de H₀ ser verdadeira.')
st.write('Conclusão do exemplo: Z ' + ('rejeita' if exemplo['rejeita_z'] else 'não rejeita') + ' H₀; binomial exato ' + ('rejeita' if exemplo['rejeita_exato'] else 'não rejeita') + ' H₀.')
