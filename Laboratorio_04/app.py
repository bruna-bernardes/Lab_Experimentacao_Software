from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
from scipy.stats import norm, binom, binomtest
from src.estatistica import simular, testar, META, ALFA
from src.simulacoes import executar_simulacoes, REPETICOES
from src.analise_reais import tabela_dados_reais

st.set_page_config(page_title='LAB04 | Sprint 2', layout='wide')
st.title('LAB04 — Testes de hipótese por dentro')
st.caption('Sprint 2 | Teste Z para proporção × teste binomial exato')
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

# G1 — Comparação agrupada das frequências reais e simuladas.
# Como os dados são binários, as barras agrupadas facilitam a comparação.
freq_reais = np.bincount(reais.astype(int), minlength=2)
freq_simulados = np.bincount(simulados.astype(int), minlength=2)
categorias = ['Sucesso (0)', 'Falha (1)']
x_g1 = np.arange(len(categorias))
largura_g1 = 0.34

fig_g1, ax_g1 = plt.subplots(figsize=(11, 4.5))
barras_reais = ax_g1.bar(
    x_g1 - largura_g1 / 2, freq_reais, width=largura_g1,
    color='#5278aa', label='Dados reais'
)
barras_simulados = ax_g1.bar(
    x_g1 + largura_g1 / 2, freq_simulados, width=largura_g1,
    color='#e27a45', label='Dados simulados'
)
ax_g1.set_xticks(x_g1, categorias)
ax_g1.set_xlabel('Resultado da execução (categoria)')
ax_g1.set_ylabel('Frequência (execuções)')
ax_g1.set_title('G1 — Comparação das frequências de resultados de CI')
ax_g1.set_ylim(0, max(freq_reais.max(), freq_simulados.max()) * 1.18)
ax_g1.legend(loc='upper center', ncol=2)
ax_g1.grid(axis='y', alpha=0.15)
ax_g1.set_axisbelow(True)
for barras in (barras_reais, barras_simulados):
    for barra in barras:
        altura = barra.get_height()
        ax_g1.annotate(
            f'{int(altura)}',
            (barra.get_x() + barra.get_width() / 2, altura),
            xytext=(0, 4), textcoords='offset points',
            ha='center', va='bottom', fontsize=10
        )
fig_g1.tight_layout()
st.pyplot(fig_g1)
plt.close(fig_g1)
st.write(
    f'O G1 compara {n} execuções reais com {n} simuladas. '
    f'Nos dados reais, a taxa de falhas foi de {taxa_real:.1%}, '
    'valor utilizado como parâmetro da simulação Bernoulli. '
    'O resumo horizontal mostra as proporções de sucesso e falha. '
    'Como os resultados são binários (0 = sucesso e 1 = falha), '
    'utilizamos barras agrupadas para comparar suas frequências, '
    'preservando a informação que seria apresentada em histogramas '
    'com duas classes discretas.'
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


# Sprint 2 — Monte Carlo: Q1, Q2, Q3 e gráficos G3/G4.
# Mantém-se a mesma cor por teste no G2, G3 e G4.
CORES_TESTES = {'Teste Z': '#2563a6', 'Binomial exato': '#2e8b57'}
ESTILOS_AMOSTRA = {'Amostra real': '-', 'Amostra pequena': '--'}

@st.cache_data(show_spinner='Executando simulações da Sprint 2...')
def carregar_simulacoes(n_observacoes):
    return executar_simulacoes(n_observacoes, repeticoes=REPETICOES, seed=42)

resultados = carregar_simulacoes(n)

st.header('4. Erro tipo I — G3')
q1 = resultados[np.isclose(resultados['efeito'], 0)]
situacoes = ['Amostra real', 'Amostra pequena']

# G3 — Gráfico de pontos para comparação do erro tipo I
fig_g3, ax_g3 = plt.subplots(figsize=(11, 4.5))

situacoes = ['Amostra real', 'Amostra pequena']
posicoes = np.arange(len(situacoes))
deslocamentos = {'Teste Z': -0.08, 'Binomial exato': 0.08}

for teste, cor in CORES_TESTES.items():
    taxas = [
        float(q1[
            (q1.situacao == situacao) &
            (q1.teste == teste)
        ].taxa_rejeicao.iloc[0]) * 100
        for situacao in situacoes
    ]

    x_pontos = posicoes + deslocamentos[teste]

    ax_g3.scatter(
        x_pontos, taxas,
        s=180,
        color=cor,
        edgecolor='white',
        linewidth=1.5,
        label=teste,
        zorder=3
    )

    for x, taxa in zip(x_pontos, taxas):
        ax_g3.annotate(
            f'{taxa:.2f}%',
            (x, taxa),
            xytext=(0, 12),
            textcoords='offset points',
            ha='center',
            fontsize=11,
            fontweight='bold',
            color=cor
        )

ax_g3.axhline(
    ALFA * 100,
    color='#666666',
    linestyle='--',
    linewidth=1.7,
    label='Referência nominal de 5%',
    zorder=1
)

ax_g3.set_xticks(
    posicoes,
    [f'Amostra principal (n={n})', 'Amostra pequena (n=20)']
)

ax_g3.set_xlim(-0.4, 1.4)
ax_g3.set_ylim(0, 10)
ax_g3.set_ylabel('Erro tipo I (% de rejeições)')
ax_g3.set_xlabel('Situação simulada')
ax_g3.set_title('G3 — Comparação do erro tipo I sob H₀ (p = 5%)')

ax_g3.grid(axis='y', linestyle=':', alpha=0.25)
ax_g3.set_axisbelow(True)

ax_g3.legend(
    loc='upper center',
    bbox_to_anchor=(0.5, -0.17),
    ncol=3,
    frameon=True,
    fontsize=10
)

fig_g3.subplots_adjust(bottom=0.28, top=0.88)

st.pyplot(fig_g3)
plt.close(fig_g3)


for situacao in situacoes:
    recorte = q1[q1.situacao == situacao]
    rz = float(recorte[recorte.teste == 'Teste Z'].taxa_rejeicao.iloc[0])
    re = float(recorte[recorte.teste == 'Binomial exato'].taxa_rejeicao.iloc[0])
    st.write(f'**{situacao}:** o teste Z rejeitou H₀ em {rz:.2%} das {REPETICOES:,} '
             f'repetições e o binomial exato em {re:.2%}. O nível nominal é 5%. '
             + ('A amostra pequena torna frágil a aproximação normal do teste Z (n × 0,05 = 1).'
                if situacao == 'Amostra pequena' else
                'A amostra principal permite comparar o controle do erro tipo I pelos dois métodos.'))

st.header('5. Poder estatístico — G4')
fig_g4, ax_g4 = plt.subplots(figsize=(11, 5.3))
for situacao in situacoes:
    for teste, cor in CORES_TESTES.items():
        recorte = resultados[(resultados.situacao == situacao) &
                            (resultados.teste == teste)].sort_values('efeito')
        ax_g4.plot(recorte.efeito * 100, recorte.taxa_rejeicao * 100,
                   marker='o', markersize=5, linewidth=2,
                   color=cor, linestyle=ESTILOS_AMOSTRA[situacao],
                   label=f'{teste} — {situacao}')
ax_g4.axhline(80, color='#777777', linestyle=':', linewidth=1.4,
              label='Referência: poder de 80%')
ax_g4.set_xlabel('Tamanho do efeito (pontos percentuais acima da meta de 5%)')
ax_g4.set_ylabel('Taxa de rejeição de H₀ (%)')
ax_g4.set_title('G4 — Curvas de poder por teste e tamanho da amostra')
ax_g4.set_ylim(0, 105)
ax_g4.set_xticks(sorted(resultados.efeito.unique() * 100))
ax_g4.grid(axis='y', alpha=.2)
ax_g4.legend(ncol=2, loc='upper center', bbox_to_anchor=(.5, -.20), fontsize=9)
fig_g4.subplots_adjust(bottom=.30, top=.91)
st.pyplot(fig_g4)
plt.close(fig_g4)

st.write('O G4 mostra a proporção de rejeições de H₀ para taxas verdadeiras de falha '
         'entre 5% e 15%. **Na origem (efeito zero), a taxa é erro tipo I, não poder.** '
         'Nos demais pontos, ela estima o poder de detectar o aumento da taxa de falhas. '
         'A cor identifica o teste; linha contínua indica a amostra principal, '
         'e linha tracejada indica a amostra pequena (n = 20).')
st.write('O teste Z pode apresentar mais rejeições com amostras pequenas, mas isso não '
         'significa necessariamente melhor desempenho: é preciso considerar também '
         'se o erro tipo I permanece dentro do nível de 5%.')

# 6. Dados reais
st.header('6. Aplicação dos testes aos dados reais')

tabela = tabela_dados_reais(df)

st.dataframe(
    tabela,
    use_container_width=True,
    hide_index=True
)

st.write(
    f'Nas {n} execuções reais, foram observadas {int(df.falha.sum())} '
    f'falhas ({taxa_real:.1%}), uma diferença de '
    f'{(taxa_real - META) * 100:+.1f} pontos percentuais '
    'em relação à meta de 5%. '
    'Os dois testes apresentaram p-valores superiores a 0,05, '
    'portanto não rejeitamos H₀. '
    'Isso não significa que a taxa verdadeira seja exatamente 5%, '
    'mas que a amostra não forneceu evidência estatística suficiente '
    'para afirmar que ela é diferente da meta.'
)

# 7. Conclusão
st.header('7. Conclusão e recomendação')

st.write(
    '**Expectativa inicial:** esperávamos que o teste binomial exato '
    'controlasse melhor o erro tipo I em amostras pequenas, '
    'enquanto o teste Z poderia apresentar problemas devido '
    'à aproximação normal.'
)

st.write(
    '**Resultados encontrados:** nas simulações com n = 100, '
    'os dois testes apresentaram taxas de rejeição equivalentes. '
    'Com n = 20, o teste Z apresentou erro tipo I de 7,77%, '
    'acima dos 5% nominais, enquanto o binomial exato '
    'apresentou 1,60%, demonstrando comportamento conservador.'
)

st.write(
    '**Recomendação:** para avaliar taxas de falhas pequenas, '
    'especialmente em amostras reduzidas, recomendamos o teste '
    'binomial exato, pois ele não depende da aproximação normal '
    'e controla o nível de significância. '
    'O teste Z pode ser considerado quando as condições '
    'da aproximação normal forem adequadas.'
)

st.write(
    '**Limitações:** utilizamos dados de apenas um repositório '
    'e assumimos independência entre as execuções e probabilidade '
    'constante de falha. Além disso, as simulações de poder '
    'consideraram apenas aumentos na taxa de falhas, '
    'e os resultados podem variar conforme o tamanho da amostra.'
)