import streamlit as st
import pandas as pd
import plotly.express as px
import glob
import os
from datetime import datetime


try:
    from prophet import Prophet
    has_prophet = True
except ImportError:
    has_prophet = False


MESES_MAP = {
    'Janeiro': 1, 'Fevereiro': 2, 'Março': 3, 'Abril': 4, 'Maio': 5,
    'Junho': 6, 'Julho': 7, 'Agosto': 8, 'Setembro': 9, 'Outubro': 10,
    'Novembro': 11, 'Dezembro': 12
}
REVERSE_MESES_MAP = {v: k for k, v in MESES_MAP.items()}


def load_data(pattern):
    files = glob.glob(pattern)
    if not files:
        return None
    latest = max(files, key=os.path.getmtime)
    return pd.read_csv(latest)

@st.cache_data
def get_data():
    df = load_data("Data/vendas_macarrao_tratadas_*.csv")
    if df is None:
        return None
    df = df.copy()
    df['MesCodigo'] = df['Mes'].map(MESES_MAP)
    df['Data'] = pd.to_datetime(df['Ano'].astype(str) + '-' + df['MesCodigo'].astype(str) + '-01', errors='coerce')
    df['Publicidade'] = df['Publicidade'].fillna(0).astype(int)
    return df

@st.cache_resource
def train_prophet(ts_df):
    m = Prophet()
    m.fit(ts_df)
    return m

df = get_data()
if df is None:
    st.error("❌ Nenhum arquivo CSV encontrado na pasta Data.")
    st.stop()

st.sidebar.header("🎛️ Filtros")
with st.sidebar.expander("Seleção de Período", expanded=True):
    anos = sorted(df['Ano'].unique())
    meses_disponiveis = [m for m in MESES_MAP.keys() if MESES_MAP[m] in df['MesCodigo'].unique()]
    ano_sel = st.selectbox("Ano", anos, index=len(anos)-1)
    mes_sel_nome = st.selectbox("Mês", meses_disponiveis, index=len(meses_disponiveis)-1)
    mes_sel = MESES_MAP[mes_sel_nome]

with st.sidebar.expander("Visualização", expanded=False):
    chart_type = st.selectbox("Tipo de comparativo", ['Boxplot', 'Violin'], index=0)
    show_stacked = st.checkbox("Mostrar vendas empilhadas por Publicidade", value=True)

if has_prophet:
    with st.sidebar.expander("Forecasting", expanded=False):
        horizon = st.slider("Horizonte (meses)", min_value=1, max_value=12, value=6)
        show_forecast = st.checkbox("Exibir previsão", value=True)
else:
    st.sidebar.info("📦 Instale prophet para habilitar forecasting.")


filtered = df[(df['Ano'] == ano_sel) & (df['MesCodigo'] == mes_sel)]
all_month = df[df['MesCodigo'] == mes_sel]

def main():
    st.title("📈 Dashboard de Vendas de Macarrão")
    st.subheader(f"{mes_sel_nome} de {ano_sel}")

    if filtered.empty:
        st.warning("⚠️ Nenhum dado para o período selecionado.")
        return

    # Tabela e download
    st.dataframe(filtered, use_container_width=True)
    csv = filtered.drop(columns=['MesCodigo']).to_csv(index=False).encode('utf-8')
    st.download_button("⬇️ Baixar CSV", data=csv, file_name=f"vendas_{ano_sel}_{mes_sel_nome}.csv")

    total = filtered['Vendas'].sum()
    mean = filtered['Vendas'].mean()
    prev_year = df[(df['Ano'] == ano_sel-1) & (df['MesCodigo'] == mes_sel)]['Vendas'].sum() or 0
    yoy = (total - prev_year) / prev_year * 100 if prev_year else None
    col1, col2, col3 = st.columns(3)
    col1.metric("Total de Vendas", f"R${total:,.2f}")
    col2.metric("Média de Vendas", f"R${mean:,.2f}")
    col3.metric("Variação YoY", f"{yoy:.1f}%" if yoy is not None else "-")

    pub_vals = filtered[filtered['Publicidade'] == 1]['Vendas']
    no_vals = filtered[filtered['Publicidade'] == 0]['Vendas']
    if not pub_vals.empty and not no_vals.empty:
        diff = pub_vals.mean() - no_vals.mean()
        if no_vals.mean():
            diff_pct = diff / no_vals.mean() * 100
            st.markdown(f"**Insight:** Vendas com publicidade foram **{diff_pct:.1f}%** ({diff:.0f} unidades) {'maiores' if diff>=0 else 'menores'} que sem publicidade.")
        else:
            st.markdown("**Insight:** Sem dados suficientes de vendas sem publicidade para comparação.")
    else:
        st.markdown("**Insight:** Dados insuficientes para gerar insight de publicidade.")

    
    st.subheader("🔹 Análises Gráficas")
    if chart_type == 'Boxplot':
        fig_comp = px.box(all_month, x='Publicidade', y='Vendas', points='all', title='Comparativo Publicidade vs Não')
    else:
        fig_comp = px.violin(all_month, x='Publicidade', y='Vendas', points='all', title='Comparativo Publicidade vs Não')
    st.plotly_chart(fig_comp, use_container_width=True)

    if show_stacked:
        st.subheader("🔹 Vendas por Ano (Publicidade vs Não)")
        df_stack = all_month.groupby(['Ano', 'Publicidade'])['Vendas'].sum().reset_index()
        fig_stack = px.bar(df_stack, x='Ano', y='Vendas', color='Publicidade', title='Vendas Empilhadas por Publicidade')
        st.plotly_chart(fig_stack, use_container_width=True)

   
    st.subheader("🔹 Série Temporal de Vendas Mensais")
    ts = df.groupby('Data')['Vendas'].sum().reset_index()
    fig_ts = px.line(ts, x='Data', y='Vendas', markers=True, title='Vendas Mensais (2018-2024)')
    st.plotly_chart(fig_ts, use_container_width=True)

    # Forecasting
    if has_prophet and 'show_forecast' in locals() and show_forecast:
        st.subheader(f"🔹 Previsão de Vendas ({horizon} meses)")
        ts_df = ts.rename(columns={'Data':'ds','Vendas':'y'})
        model = train_prophet(ts_df)
        future = model.make_future_dataframe(periods=horizon, freq='M')
        forecast = model.predict(future)
        fig_fc = px.line(forecast, x='ds', y='yhat', title='Forecast Prophet')
        st.plotly_chart(fig_fc, use_container_width=True)

    st.caption("Desenvolvido por Isaac A. Rocha 🍝")

if __name__ == '__main__':
    main()
