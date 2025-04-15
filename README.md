# 📊 Dashboard de Análise de Vendas de Macarrão com Publicidade

Este projeto consiste em um painel interativo desenvolvido com **Streamlit** e **Plotly** para analisar o impacto de campanhas publicitárias nas vendas de macarrão entre os anos de **2018 a 2024**. Os dados são integrados a partir de arquivos `.csv` gerados com base em consultas a um banco SQL Server.

---

## 🚀 Funcionalidades

- 📈 **Análises de Vendas por Ano e Mês**
- 🔍 **Comparativo entre vendas com e sem publicidade**
- 🧠 **Geração automática de insights**
- 🤊 **Gráficos interativos (Boxplot, Violin, Barras empilhadas)**
- 🗕️ **Série temporal com tendência mensal**
- 🔮 **Previsão de vendas com Prophet (opcional)**

---

## 📂 Estrutura dos Dados

O sistema espera arquivos no formato:

```bash
Data/vendas_macarrao_tratadas_*.csv
```

Cada arquivo deve conter as seguintes colunas:

- `Ano`
- `Mes` (nome do mês, ex: "Janeiro")
- `Publicidade` (0 ou 1)
- `Vendas` (valor numérico)

---

## 🧪 Requisitos

### Pacotes Python

```txt
streamlit
pandas
plotly
prophet
pyodbc
```

📦 Instale com:

```bash
pip install -r requirements.txt
```

---

## ▶️ Como Executar

1. Clone o repositório:
   ```bash
   git clone https://github.com/Isaac-A-Rocha/dashboard-vendas-macarrao.git
   cd dashboard-vendas-macarrao
   ```

2. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

3. Coloque os arquivos `.csv` tratados na pasta `Data`.

4. Inicie o dashboard:
   ```bash
   streamlit run app.py
   ```

---

## 📌 Observações

- Para habilitar a funcionalidade de **forecasting**, instale o pacote Prophet:
  ```bash
  pip install prophet
  ```
- Os gráficos são responsivos e podem ser exportados interativamente.
- O sistema permite seleção dinâmica de ano, mês e tipo de visualização.

---

## 👨‍💼 Autor

**Isaac A. Rocha**  
🔗 [LinkedIn](www.linkedin.com/in/isaac-alves-2980152b8)  
🍝 Projeto desenvolvido para estudo e apresentação de dados reais de vendas.

