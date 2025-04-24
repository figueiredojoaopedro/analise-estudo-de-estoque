import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from sklearn.preprocessing import MinMaxScaler

def main():
	estoque, vendas = carregar_dados()
	vendas_agg = calcular_demanda(vendas)
	dados = pd.merge(estoque, vendas_agg, on=['Código'])
	dados = calcular_metricas(dados)
	dados = normalizar_e_score(dados)
	top5 = dados.head(5)
	labels_pizza, sizes_pizza, vendas_mensal = preparar_graficos(dados, vendas)

	month_names = {
		1: "Janeiro", 2: "Fevereiro", 3: 'Março', 4: 'Abril',
		5: 'Maio', 6: 'Junho', 7: 'Julho', 8: 'Agosto',
		9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'
	}

	# === Gráficos na mesma tela ===
	fig, axs = plt.subplots(3, 2, figsize=(18, 11))
	fig.suptitle("Dashboard de Estoque e Vendas", fontsize=22, fontweight='bold', color='red', y=0.98)
	plt.subplots_adjust(hspace=0.5, wspace=1.5)

	# 1. Risco de ruptura por local
	axs[0, 0].set_title("Risco de Ruptura por Local", fontweight='bold')
	media_risco = dados.groupby('Nome', sort=False)['risco_ruptura'].mean()
	bars = axs[0, 0].bar(media_risco.index.tolist(), media_risco.values, color='orange')
	axs[0, 0].set_ylabel("Proporção de Risco")
	axs[0, 0].set_xticks([])
	axs[0, 0].grid(axis='y', linestyle='--', alpha=0.6)

	for bar, label in zip(bars, media_risco.index):
		axs[0, 0].text(bar.get_x() + bar.get_width()/2, 0.02, label, ha='center', va='bottom', fontsize=7, rotation=90)

	# 2. Top 5 produtos
	axs[0, 1].set_title("Top 5 Produtos com Maior Score de Reposição", fontweight='bold')
	axs[0, 1].bar(top5['Código'].astype(str), top5['score_reposicao'], color='green')
	axs[0, 1].set_ylabel("Score de Reposição")
	axs[0, 1].grid(axis='y', linestyle='--', alpha=0.6)

	# 3. Qtd. de produtos vendidos por mês
	axs[1, 0].set_title("Quantidade de produtos vendidos por Mês", fontsize=12, fontweight='bold')
	bars = axs[1, 0].bar(vendas_mensal['Mes'], vendas_mensal['Quantidade Vendida'], color=["blue", "green"])
	axs[1, 0].set_xticks(vendas_mensal['Mes'])
	axs[1, 0].set_xticklabels([month_names[mes] for mes in vendas_mensal['Mes']], rotation=0)
	axs[1, 0].grid(axis='y', linestyle='--', alpha=0.6)

	for bar in bars:
		height = bar.get_height()
		axs[1, 0].text(bar.get_x() + bar.get_width() / 2, height, int(height),
						ha='center', va='bottom', fontsize=10, fontweight='bold')

	# 4. Estoque atual vs ideal
	axs[1, 1].set_title("Estoque Atual vs Estoque Ideal (Média)", fontweight='bold')
	axs[1, 1].bar(['Atual', 'Ideal'],
					[dados['Quantidade em Estoque'].mean(), dados['estoque_ideal'].mean()],
					color=['blue', 'red'])
	axs[1, 1].grid(axis='y', linestyle='--', alpha=0.6)

	# 5. Custo Total por Mercadoria
	axs[2, 0].set_title("Custo Total por Mercadoria", fontweight='bold')
	custo_local = dados.groupby('Nome')['custo_total'].sum().sort_values()
	bars = axs[2, 0].barh(custo_local.index, custo_local.values, color='purple')
	axs[2, 0].tick_params(axis='y', left=False, labelleft=False)
	axs[2, 0].grid(axis='x', linestyle='--', alpha=0.6)

	# Formatar eixo x com pontos
	formatter = FuncFormatter(lambda x, _: f'{int(x):,}'.replace(",", "."))
	axs[2, 0].xaxis.set_major_formatter(formatter)

	for bar, label in zip(bars, custo_local.index):
		axs[2, 0].text(
			x=bar.get_width() * 0.01,
			y=bar.get_y() + bar.get_height() / 2,
			s=label,
			va='center',
			ha='left',
			fontsize=8,
			color='white' if bar.get_width() > custo_local.max() * 0.15 else 'black',
			fontweight='bold'
		)

	axs[2, 0].set_xlabel("Custo Estimado (R$)")
	axs[2, 0].tick_params(axis='x', labelsize=7)

	# 6. Gráfico de Pizza
	axs[2, 1].pie(sizes_pizza, labels=labels_pizza, autopct='%1.2f%%', startangle=120)
	axs[2, 1].axis('equal')
	axs[2, 1].set_title('Gráfico de Pizza do Estoque (04-2025)', fontsize=12, fontweight='bold')

	plt.tight_layout(rect=[0, 0, 1, 0.95])
	plt.show()
def carregar_dados():
    estoque = pd.read_csv("./data/estoque.csv")
    vendas = pd.read_csv("./data/log_vendas.csv")
    vendas['data'] = pd.to_datetime(vendas['Data da Venda'])
    return estoque, vendas

def calcular_demanda(vendas):
    vendas_agg = vendas.groupby('Código')['Quantidade Vendida'].agg(['mean', 'std']).rename(
        columns={'mean': 'media_demanda', 'std': 'std_demanda'}).reset_index()
    return vendas_agg

def calcular_metricas(dados):
    z = 1.65
    dados['estoque_seguranca'] = z * dados['std_demanda'] * np.sqrt(dados['Quantidade em Estoque'])
    dados['estoque_ideal'] = dados['media_demanda'] * dados['Quantidade em Estoque'] + dados['estoque_seguranca']
    dados['risco_ruptura'] = np.where(dados['Quantidade em Estoque'] < dados['estoque_ideal'], 1, 0)
    dados['custo_total'] = dados['estoque_ideal'] * dados['Preço Unitário (R$)']
    return dados

def normalizar_e_score(dados):
    scaler = MinMaxScaler()
    dados[['media_demanda_norm', 'Preço Unitário (R$)_norm', 'risco_norm']] = scaler.fit_transform(
        dados[['media_demanda', 'Preço Unitário (R$)', 'risco_ruptura']]
    )
    dados['score_reposicao'] = (
        0.5 * dados['media_demanda_norm'] +
        0.3 * dados['Preço Unitário (R$)_norm'] +
        0.2 * dados['risco_norm']
    )
    return dados.sort_values(by='score_reposicao', ascending=False)

def preparar_graficos(dados, vendas):
    pizza_data = dados.groupby('Nome')['Quantidade em Estoque'].sum()
    labels_pizza = pizza_data.index
    sizes_pizza = pizza_data.values

    vendas_filtrado = vendas[(vendas["data"] >= "2025-03-01")]
    vendas_filtrado['Mes'] = vendas_filtrado['data'].dt.month
    vendas_mensal = vendas_filtrado.groupby("Mes")["Quantidade Vendida"].sum().reset_index()

    return labels_pizza, sizes_pizza, vendas_mensal

if __name__ == "__main__":
    main();
