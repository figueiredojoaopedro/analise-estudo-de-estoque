# 📦 Análise de Estoque e Vendas

Este projeto realiza uma análise completa de dados de estoque e vendas de produtos, gerando visualizações interativas que auxiliam na tomada de decisão sobre reposição de itens e controle de custos.

## 🔍 Funcionalidades

- Cálculo de demanda média e variação (desvio padrão)
- Estimativa de estoque de segurança e estoque ideal
- Cálculo do risco de ruptura e custo total por item
- Normalização de dados e geração de score de reposição
- Visualizações interativas com botões de navegação:
  - Risco de ruptura por local
  - Top 5 produtos com maior score de reposição
  - Vendas mensais
  - Comparativo de estoque atual vs ideal
  - Custo total por mercadoria
  - Distribuição de estoque em gráfico de pizza

## 📁 Estrutura esperada de arquivos

Coloque os arquivos `.csv` de dados na pasta `./data`:

- `estoque.csv`: deve conter colunas como `Código`, `Nome`, `Quantidade em Estoque`, `Preço Unitário (R$)`
- `log_vendas.csv`: deve conter colunas como `Código`, `Quantidade Vendida`, `Data da Venda`

## ▶️ Como executar

Certifique-se de ter o Python instalado (versão 3.7+ recomendada) e as bibliotecas necessárias:

```bash
pip install pandas numpy matplotlib scikit-learn
```

Para executar, basta:

```
python main.py
```

📌 Principais Funções
• carregar*dados(): Lê os arquivos CSV e prepara os dados de vendas
• calcular_demanda(): Calcula a demanda média e o desvio padrão por produto
• calcular_metricas(): Calcula estoque ideal, risco de ruptura e custo total
• normalizar_e_score(): Aplica normalização MinMax e calcula score de reposição
• preparar_graficos(): Prepara dados agregados para os gráficos
• Funções chart*\*: Geram os diferentes gráficos usando Matplotlib
• main(): Orquestra toda a execução do dashboard

📊 Navegação entre gráficos
O dashboard exibe dois gráficos por vez. Use os botões “Próximo” e “Anterior” na interface para navegar entre os painéis de visualização.

📌 Exemplo de uso

Ao executar o código, uma janela se abrirá com os gráficos. Eles ajudarão a responder perguntas como:
• Quais produtos estão com maior risco de ruptura?
• Quais produtos têm maior prioridade de reposição?
• Como está o desempenho das vendas mês a mês?
• O estoque atual está compatível com a demanda estimada?
