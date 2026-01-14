import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime

# Configuração da página
st.set_page_config(page_title="Dashboard de Clientes", layout="wide", initial_sidebar_state="expanded")

# Carregar dados
@st.cache_data
def load_data():
    # No Streamlit Cloud, o arquivo CSV estará no mesmo diretório que o script
    df_monthly = pd.read_csv('monthly_metrics.csv')
    df_monthly['Month'] = pd.to_datetime(df_monthly['Month'])
    df_monthly['TotalInactive'] = df_monthly['TotalEver'] - df_monthly['TotalActive']
    return df_monthly

df_monthly = load_data()

# Título e descrição
st.title("📊 Dashboard Interativo de Clientes")
st.markdown("Análise completa de clientes ativos, inativos e composição de planos ao longo do tempo.")

# Sidebar com filtros
st.sidebar.header("🔍 Filtros")

# Seletor de mês
meses_disponiveis = df_monthly['Month'].unique()
mes_selecionado = st.sidebar.selectbox(
    "Selecione um mês para análise detalhada:",
    options=meses_disponiveis,
    format_func=lambda x: pd.to_datetime(x).strftime('%B/%Y')
)

# Filtrar dados para o mês selecionado
dados_mes = df_monthly[df_monthly['Month'] == mes_selecionado].iloc[0]

# Seletor de intervalo de datas para gráficos
st.sidebar.markdown("---")
st.sidebar.subheader("Intervalo de Datas para Gráficos")
data_inicio = st.sidebar.date_input("Data de início:", value=df_monthly['Month'].min())
data_fim = st.sidebar.date_input("Data de fim:", value=df_monthly['Month'].max())

# Filtrar dados para o intervalo
df_filtrado = df_monthly[(df_monthly['Month'] >= pd.Timestamp(data_inicio)) & 
                         (df_monthly['Month'] <= pd.Timestamp(data_fim))]

# KPIs - Métricas principais do mês selecionado
st.markdown("---")
st.subheader(f"📈 Indicadores do Mês: {pd.to_datetime(mes_selecionado).strftime('%B de %Y')}")

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric(
        label="Novos Clientes",
        value=int(dados_mes['NewCustomers']),
        delta=None
    )

with col2:
    st.metric(
        label="Clientes Ativos",
        value=int(dados_mes['TotalActive']),
        delta=None
    )

with col3:
    st.metric(
        label="Clientes Inativos",
        value=int(dados_mes['TotalInactive']),
        delta=None
    )

with col4:
    st.metric(
        label="Total Acumulado",
        value=int(dados_mes['TotalEver']),
        delta=None
    )

with col5:
    taxa_atividade = (dados_mes['TotalActive'] / dados_mes['TotalEver'] * 100) if dados_mes['TotalEver'] > 0 else 0
    st.metric(
        label="Taxa de Atividade",
        value=f"{taxa_atividade:.1f}%",
        delta=None
    )

st.markdown("---")

# Gráficos
col_graph1, col_graph2 = st.columns(2)

# Gráfico 1: Evolução Ativos vs Inativos
with col_graph1:
    st.subheader("📊 Evolução: Ativos vs Inativos")
    fig1 = go.Figure()
    fig1.add_trace(go.Scatter(
        x=df_filtrado['Month'], y=df_filtrado['TotalActive'],
        mode='lines+markers',
        name='Clientes Ativos',
        line=dict(color='#1f77b4', width=3),
        marker=dict(size=8)
    ))
    fig1.add_trace(go.Scatter(
        x=df_filtrado['Month'], y=df_filtrado['TotalInactive'],
        mode='lines+markers',
        name='Clientes Inativos',
        line=dict(color='#ff7f0e', width=3),
        marker=dict(size=8)
    ))
    fig1.update_layout(
        hovermode='x unified',
        template='plotly_white',
        height=400,
        xaxis_title='Mês',
        yaxis_title='Número de Clientes'
    )
    st.plotly_chart(fig1, use_container_width=True)

# Gráfico 2: Composição de Planos (Mês Selecionado)
with col_graph2:
    st.subheader(f"🎯 Composição de Planos - {pd.to_datetime(mes_selecionado).strftime('%b/%Y')}")
    plan_data = {
        'Plano': ['Basic\nMensal', 'Basic\nSemestral', 'Basic\nAnual', 'Premium\nMensal', 'Premium\nSemestral', 'Premium\nAnual'],
        'Quantidade': [
            dados_mes['Basic_1'], dados_mes['Basic_6'], dados_mes['Basic_12'],
            dados_mes['Premium_1'], dados_mes['Premium_6'], dados_mes['Premium_12']
        ]
    }
    df_plans = pd.DataFrame(plan_data)
    df_plans = df_plans[df_plans['Quantidade'] > 0]  # Filtrar planos com 0 clientes
    
    fig2 = px.pie(df_plans, values='Quantidade', names='Plano',
                  color_discrete_sequence=px.colors.qualitative.Set3)
    fig2.update_traces(textposition='inside', textinfo='percent+label')
    fig2.update_layout(height=400)
    st.plotly_chart(fig2, use_container_width=True)

st.markdown("---")

# Gráfico 3: Novos Clientes por Mês
st.subheader("🆕 Aquisição de Novos Clientes")
fig3 = px.bar(df_filtrado, x='Month', y='NewCustomers',
             labels={'NewCustomers': 'Novos Clientes', 'Month': 'Mês'},
             color_discrete_sequence=['#2E8B57'])
fig3.update_layout(
    template='plotly_white',
    height=400,
    hovermode='x unified'
)
st.plotly_chart(fig3, use_container_width=True)

st.markdown("---")

# Gráfico 4: Acumulado Total
st.subheader("📈 Crescimento Acumulado de Clientes")
fig4 = go.Figure()
fig4.add_trace(go.Scatter(
    x=df_filtrado['Month'], y=df_filtrado['TotalEver'],
    mode='lines+markers',
    name='Total Acumulado',
    line=dict(color='#d62728', width=3),
    marker=dict(size=8),
    fill='tozeroy',
    fillcolor='rgba(214, 39, 40, 0.2)'
))
fig4.update_layout(
    template='plotly_white',
    height=400,
    hovermode='x unified',
    xaxis_title='Mês',
    yaxis_title='Total de Clientes'
)
st.plotly_chart(fig4, use_container_width=True)

st.markdown("---")

# Tabela de Detalhes
st.subheader("📋 Detalhamento por Tipo de Plano")

col_basic, col_premium = st.columns(2)

with col_basic:
    st.write("**Planos Basic**")
    basic_data = {
        'Tipo': ['Mensal', 'Semestral', 'Anual'],
        'Clientes': [
            int(dados_mes['Basic_1']),
            int(dados_mes['Basic_6']),
            int(dados_mes['Basic_12'])
        ]
    }
    st.dataframe(pd.DataFrame(basic_data), use_container_width=True, hide_index=True)

with col_premium:
    st.write("**Planos Premium**")
    premium_data = {
        'Tipo': ['Mensal', 'Semestral', 'Anual'],
        'Clientes': [
            int(dados_mes['Premium_1']),
            int(dados_mes['Premium_6']),
            int(dados_mes['Premium_12'])
        ]
    }
    st.dataframe(pd.DataFrame(premium_data), use_container_width=True, hide_index=True)

st.markdown("---")

# Rodapé
st.markdown("""
<div style='text-align: center; color: #888; font-size: 12px; margin-top: 20px;'>
    <p>Dashboard de Análise de Clientes | Dados atualizados até {}</p>
</div>
""".format(df_monthly['Month'].max().strftime('%B de %Y')), unsafe_allow_html=True)
