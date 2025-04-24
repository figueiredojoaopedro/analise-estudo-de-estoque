import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Button
from matplotlib.ticker import FuncFormatter
from sklearn.preprocessing import MinMaxScaler
from matplotlib.ticker import FuncFormatter

def main():
    estoque, vendas = carregar_dados()
    vendas_agg = calcular_demanda(vendas)
    dados = pd.merge(estoque, vendas_agg, on=['Código'])
    dados = calcular_metricas(dados)
    dados = normalizar_e_score(dados)
    top5 = dados.head(5)
    labels_pizza, sizes_pizza, vendas_mensal = preparar_graficos(dados, vendas)

    chart_functions = [
        chart_risco_ruptura,
        chart_top5,
        chart_vendas_mensal,
        chart_estoque_atual_ideal,
        chart_custo_total,
        chart_pizza
    ]

    chart_args = [
        (dados,),
        (top5,),
        (vendas_mensal,),
        (dados,),
        (dados,),
        (labels_pizza, sizes_pizza)
    ]

    fig, axs = plt.subplots(1, 2, figsize=(18, 8))
    plt.subplots_adjust(bottom=0.2)
    page = [0]

    # Buttons
    axprev = plt.axes([0.3, 0.05, 0.1, 0.075])
    axnext = plt.axes([0.6, 0.05, 0.1, 0.075])
    bnext = Button(axnext, 'Próximo')
    bprev = Button(axprev, 'Anterior')

    def next_page(event):
        if page[0] < (len(chart_functions) - 1) // 2:
            page[0] += 1
            show_page(fig, axs, page[0], chart_functions, chart_args)
        update_buttons()

    def prev_page(event):
        if page[0] > 0:
            page[0] -= 1
            show_page(fig, axs, page[0], chart_functions, chart_args)
        update_buttons()

    def update_buttons():
        bprev.ax.set_visible(page[0] > 0)
        bnext.ax.set_visible(page[0] < (len(chart_functions) - 1) // 2)
        fig.canvas.draw_idle()

    bnext.on_clicked(next_page)
    bprev.on_clicked(prev_page)
    update_buttons()

    show_page(fig, axs, page[0], chart_functions, chart_args)
    plt.show()
def chart_risco_ruptura(ax, dados):
    ax.set_title("Risco de Ruptura por Local", fontweight='bold')
    media_risco = dados.groupby('Nome', sort=False)['risco_ruptura'].mean()
    bars = ax.bar(media_risco.index.tolist(), media_risco.values, color='orange')
    ax.set_ylabel("Proporção de Risco")
    ax.set_xticks([])
    ax.grid(axis='y', linestyle='--', alpha=0.6)
    for bar, label in zip(bars, media_risco.index):
        ax.text(bar.get_x() + bar.get_width()/2, 0.02, label, ha='center', va='bottom', fontsize=7, rotation=90)

def chart_top5(ax, top5):
    ax.set_title("Top 5 Produtos com Maior Score de Reposição", fontweight='bold')
    ax.bar(top5['Código'].astype(str), top5['score_reposicao'], color='green')
    ax.set_ylabel("Score de Reposição")
    ax.grid(axis='y', linestyle='--', alpha=0.6)

def chart_vendas_mensal(ax, vendas_mensal):
    month_names = {
        1: "Janeiro", 2: "Fevereiro", 3: 'Março', 4: 'Abril',
        5: 'Maio', 6: 'Junho', 7: 'Julho', 8: 'Agosto',
        9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'
    }
    ax.set_title("Quantidade de produtos vendidos por Mês", fontsize=12, fontweight='bold')
    bars = ax.bar(vendas_mensal['Mes'], vendas_mensal['Quantidade Vendida'], color=["blue", "green"])
    ax.set_xticks(vendas_mensal['Mes'])
    ax.set_xticklabels([month_names[mes] for mes in vendas_mensal['Mes']], rotation=0)
    ax.grid(axis='y', linestyle='--', alpha=0.6)
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width() / 2, height, int(height),
                ha='center', va='bottom', fontsize=10, fontweight='bold')

def chart_estoque_atual_ideal(ax, dados):
    ax.set_title("Estoque Atual vs Estoque Ideal (Média)", fontweight='bold')
    
    valores = [dados['Quantidade em Estoque'].mean(), dados['estoque_ideal'].mean()]
    categorias = ['Atual', 'Ideal']
    
    bars = ax.barh(categorias, valores, color=['#3498db', '#e74c3c'], height=0.5)
    
    ax.grid(axis='x', linestyle='--', alpha=0.6)
    
    for bar in bars:
        width = bar.get_width()
        ax.text(width + (width * 0.01), bar.get_y() + bar.get_height()/2, 
                f'{width:.0f}', va='center', fontsize=10, fontweight='bold')
    
    diff_percent = ((valores[1] - valores[0]) / valores[0]) * 100
    ax.text(max(valores) * 0.5, 0.5, 
            f'Diferença: {diff_percent:.1f}%', 
            ha='center', va='center', 
            bbox=dict(facecolor='yellow', alpha=0.3),
            fontweight='bold')
    
    ax.set_xlabel("Quantidade Média")
    ax.set_facecolor('#f8f9fa')
    
    return ax



def chart_custo_total(ax, dados):
    
    ax.set_title("Custo Total por Mercadoria", fontweight='bold')
    custo_local = dados.groupby('Nome')['custo_total'].sum().sort_values()
    bars = ax.barh(custo_local.index, custo_local.values, color='cyan')
    ax.tick_params(axis='y', left=False, labelleft=False)
    ax.grid(axis='x', linestyle='--', alpha=0.6)

    formatter = FuncFormatter(lambda x, _: f'{int(x):,}'.replace(",", "."))
    ax.xaxis.set_major_formatter(formatter)

    for bar, label in zip(bars, custo_local.index):
        ax.text(
            x=bar.get_width() * 0.01,
            y=bar.get_y() + bar.get_height() / 2,
            s=label,
            va='center',
            ha='left',
            fontsize=8,
            color='black' if bar.get_width() > custo_local.max() * 0.15 else 'black',
            fontweight='bold'
        )

    ax.set_xlabel("Custo Estimado (R$)")
    ax.tick_params(axis='x', labelsize=7)

def chart_pizza(ax, labels_pizza, sizes_pizza):
    ax.pie(sizes_pizza, labels=labels_pizza, autopct='%1.2f%%', startangle=120)
    ax.axis('equal')
    ax.set_title('Gráfico de Pizza do Estoque (04-2025)', fontsize=12, fontweight='bold')
def show_page(fig, axs, page, chart_functions, chart_args):
    for ax in axs:
        ax.clear()

    for i in range(2):
        idx = page * 2 + i
        if idx < len(chart_functions):
            chart_functions[idx](axs[i], *chart_args[idx])
        else:
            axs[i].axis('off')

    fig.suptitle("Dashboard de Estoque e Vendas", fontsize=22, fontweight='bold', color='red', y=0.98)
    fig.canvas.draw_idle()
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
