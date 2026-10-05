import streamlit as st
import pandas as pd
import numpy as np
import datetime
import re
import plotly.express as px
import plotly.graph_objects as go

# ==========================================
# 1. CONFIGURAÇÃO DA PÁGINA
# ==========================================
st.set_page_config(
    page_title="Sistema de Expedição & Logística | Magalu",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# 2. CSS PERSONALIZADO (Estilo Magalu / Magalog)
# ==========================================
def aplicar_css_customizado():
    estilo = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    .stApp {
        background-color: #F8F9FA;
    }

    /* Banner da Expedição */
    .expedicao-header {
        background: linear-gradient(135deg, #0086FF 0%, #004299 100%);
        padding: 30px;
        border-radius: 16px;
        color: white;
        margin-bottom: 25px;
        box-shadow: 0 8px 20px rgba(0, 134, 255, 0.25);
    }
    .expedicao-header h1 {
        color: white !important;
        font-size: 2.3rem;
        font-weight: 800;
        margin: 0 0 8px 0;
    }
    .expedicao-header p {
        font-size: 1.1rem;
        opacity: 0.95;
        margin: 0;
    }

    /* KPI Cards */
    .kpi-card {
        background: white;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        border-left: 5px solid #0086FF;
        transition: transform 0.2s ease;
    }
    .kpi-card:hover {
        transform: translateY(-3px);
    }
    .kpi-title {
        color: #6C757D;
        font-size: 0.88rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .kpi-value {
        color: #111;
        font-size: 1.8rem;
        font-weight: 800;
        margin: 5px 0;
    }
    .kpi-sub {
        font-size: 0.82rem;
        color: #28A745;
        font-weight: 600;
    }

    /* Card de Gráfico */
    .chart-card {
        background: white;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.04);
        margin-bottom: 20px;
    }
    </style>
    """
    st.markdown(estilo, unsafe_allow_html=True)

# ==========================================
# 3. LÓGICA DE DADOS & GOOGLE SHEETS
# ==========================================
def converter_url_google_sheets(url: str) -> str:
    if not url:
        return ""
    if "export?format=csv" in url or "output=csv" in url:
        return url
    match_id = re.search(r'/d/([a-zA-Z0-9-_]+)', url)
    if not match_id:
        return url
    sheet_id = match_id.group(1)
    match_gid = re.search(r'[#&?]gid=([0-9]+)', url)
    gid = match_gid.group(1) if match_gid else "0"
    return f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"

@st.cache_data(ttl=300)
def gerar_dados_simulados() -> pd.DataFrame:
    np.random.seed(42)
    hoje = datetime.date.today()
    status_opcoes = ["Expedido", "Pendente", "Em Separação", "Entregue", "Atrasado"]
    status_weights = [0.45, 0.15, 0.15, 0.15, 0.10]
    transportadoras = ["Magalog Direct", "Correios Sedex", "Total Express", "Sequoia", "Loggi Enterprise"]
    cidades = ["São Paulo / SP", "Campinas / SP", "Rio de Janeiro / RJ", "Belo Horizonte / MG", "Curitiba / PR", "Salvador / BA", "Recife / PE"]
    produtos = ["Smartphone Samsung Galaxy", "Smart TV 55\" 4K", "Notebook Dell Inspiron", "Geladeira Brastemp", "Máquina de Lavar", "Console PlayStation 5", "Air Fryer"]

    qtd_registros = 180
    datas_pedido = [hoje - datetime.timedelta(days=int(np.random.randint(0, 15))) for _ in range(qtd_registros)]
    prazos_sla = [dt + datetime.timedelta(days=int(np.random.randint(2, 6))) for dt in datas_pedido]

    df = pd.DataFrame({
        "ID Pedido": [f"PED-{1000 + i}" for i in range(1, qtd_registros + 1)],
        "Nota Fiscal": [f"NF-{50000 + i}" for i in range(1, qtd_registros + 1)],
        "Data Pedido": pd.to_datetime(datas_pedido),
        "Prazo SLA": pd.to_datetime(prazos_sla),
        "Cliente": [f"Cliente {i}" for i in range(1, qtd_registros + 1)],
        "Produto": np.random.choice(produtos, size=qtd_registros),
        "Destino": np.random.choice(cidades, size=qtd_registros),
        "Transportadora": np.random.choice(transportadoras, size=qtd_registros),
        "Status": np.random.choice(status_opcoes, size=qtd_registros, p=status_weights),
        "Valor (R$)": np.round(np.random.uniform(150, 4500, size=qtd_registros), 2),
        "Volumes": np.random.randint(1, 5, size=qtd_registros)
    })
    return df

@st.cache_data(ttl=300)
def carregar_dados(url_sheets: str = "") -> pd.DataFrame:
    if not url_sheets:
        return gerar_dados_simulados()
    csv_url = converter_url_google_sheets(url_sheets)
    try:
        df = pd.read_csv(csv_url)
        if df.empty:
            st.sidebar.warning("⚠️ Planilha vazia. Usando dados fictícios.")
            return gerar_dados_simulados()

        for col in df.columns:
            if "data" in col.lower() or "prazo" in col.lower() or "sla" in col.lower():
                try:
                    df[col] = pd.to_datetime(df[col])
                except Exception:
                    pass
        return df
    except Exception as e:
        st.sidebar.error(f"⚠️ Não foi possível ler a URL. Exibindo demonstração. ({e})")
        return gerar_dados_simulados()

# ==========================================
# 4. INTERFACE PRINCIPAL
# ==========================================
def main():
    aplicar_css_customizado()

    # --- SIDEBAR DE FILTROS & CONFIGURAÇÕES ---
    st.sidebar.markdown("### 🛍️ Hub Magalog")
    st.sidebar.title("⚙️ Filtros & Conexão")

    url_input = st.sidebar.text_input(
        "🔗 Link da Planilha Google Sheets:",
        placeholder="Cole a URL pública da planilha aqui...",
        help="Certifique-se que o compartilhamento da planilha está configurado como 'Qualquer pessoa com o link pode ver'."
    )

    df_raw = carregar_dados(url_input)

    st.sidebar.markdown("---")
    st.sidebar.subheader("🔍 Filtrar Expedição")

    # Identificação Dinâmica de Colunas
    col_transp = [c for c in df_raw.columns if "transp" in c.lower()]
    transp_col = col_transp[0] if col_transp else None

    col_status = [c for c in df_raw.columns if "status" in c.lower()]
    status_col = col_status[0] if col_status else None

    col_data = [c for c in df_raw.columns if "data" in c.lower() or "dt" in c.lower()]
    data_col = col_data[0] if col_data else None

    # Filtro por Transportadora
    if transp_col and transp_col in df_raw.columns:
        todas_transp = ["Todas"] + list(df_raw[transp_col].dropna().unique())
        selected_transp = st.sidebar.selectbox("Transportadora:", todas_transp)
    else:
        selected_transp = "Todas"

    # Filtro por Status
    if status_col and status_col in df_raw.columns:
        todos_status = ["Todos"] + list(df_raw[status_col].dropna().unique())
        selected_status = st.sidebar.selectbox("Status:", todos_status)
    else:
        selected_status = "Todos"

    # Busca Textual
    busca = st.sidebar.text_input("🔎 Pesquisar Pedido / NF / Cliente:", "")

    # Aplicar Filtros ao DataFrame
    df_filtered = df_raw.copy()

    if transp_col and selected_transp != "Todas":
        df_filtered = df_filtered[df_filtered[transp_col] == selected_transp]

    if status_col and selected_status != "Todos":
        df_filtered = df_filtered[df_filtered[status_col] == selected_status]

    if busca:
        busca_lower = busca.lower()
        mascara = pd.Series([False] * len(df_filtered), index=df_filtered.index)
        for col in df_filtered.columns:
            mascara |= df_filtered[col].astype(str).str.lower().str.contains(busca_lower, na=False)
        df_filtered = df_filtered[mascara]

    # --- TOP BANNER ---
    st.markdown("""
        <div class="expedicao-header">
            <h1>📦 Gestão de Expedição & Logística</h1>
            <p>Painel operacional de acompanhamento em tempo real das saídas, SLAs e indicadores de transporte Magalog.</p>
        </div>
    """, unsafe_allow_html=True)

    # --- KPIS PRINCIPAIS ---
    tot_pedidos = len(df_filtered)

    val_col = [c for c in df_filtered.columns if "valor" in c.lower() or "price" in c.lower() or "total" in c.lower()]
    val_total = df_filtered[val_col[0]].sum() if val_col and pd.api.types.is_numeric_dtype(df_filtered[val_col[0]]) else 0

    expedidos_count = len(df_filtered[df_filtered[status_col] == "Expedido"]) if status_col else 0
    atrasados_count = len(df_filtered[df_filtered[status_col] == "Atrasado"]) if status_col else 0

    sla_rate = ((tot_pedidos - atrasados_count) / tot_pedidos * 100) if tot_pedidos > 0 else 100.0

    k1, k2, k3, k4, k5 = st.columns(5)

    with k1:
        st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-title">Total de Pedidos</div>
                <div class="kpi-value">{tot_pedidos:,}</div>
                <div class="kpi-sub">📋 Cadastrados</div>
            </div>
        """, unsafe_allow_html=True)

    with k2:
        st.markdown(f"""
            <div class="kpi-card" style="border-left-color: #28a745;">
                <div class="kpi-title">Expedidos</div>
                <div class="kpi-value">{expedidos_count:,}</div>
                <div class="kpi-sub" style="color: #28a745;">🚚 Despachados</div>
            </div>
        """, unsafe_allow_html=True)

    with k3:
        st.markdown(f"""
            <div class="kpi-card" style="border-left-color: #dc3545;">
                <div class="kpi-title">Atrasados</div>
                <div class="kpi-value">{atrasados_count:,}</div>
                <div class="kpi-sub" style="color: #dc3545;">⚠️ Alerta SLA</div>
            </div>
        """, unsafe_allow_html=True)

    with k4:
        st.markdown(f"""
            <div class="kpi-card" style="border-left-color: #ffc107;">
                <div class="kpi-title">SLA Geral</div>
                <div class="kpi-value">{sla_rate:.1f}%</div>
                <div class="kpi-sub" style="color: #b78103;">🎯 Cumprimento</div>
            </div>
        """, unsafe_allow_html=True)

    with k5:
        st.markdown(f"""
            <div class="kpi-card" style="border-left-color: #17a2b8;">
                <div class="kpi-title">Valor Em Rota</div>
                <div class="kpi-value">R$ {val_total:,.2f}</div>
                <div class="kpi-sub" style="color: #17a2b8;">💰 Total Filtrado</div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # --- GRÁFICOS ANALÍTICOS ---
    g1, g2 = st.columns(2)

    with g1:
        st.subheader("📊 Distribuição por Status")
        if status_col and status_col in df_filtered.columns and not df_filtered.empty:
            df_status = df_filtered[status_col].value_counts().reset_index()
            df_status.columns = [status_col, "Qtd"]
            fig_status = px.pie(
                df_status,
                values="Qtd",
                names=status_col,
                hole=0.4,
                color_discrete_sequence=px.colors.qualitative.Set1
            )
            fig_status.update_layout(margin=dict(t=10, b=10, l=10, r=10), height=320)
            st.plotly_chart(fig_status, use_container_width=True)
        else:
            st.info("Sem dados suficientes para o gráfico de status.")

    with g2:
        st.subheader("🚚 Carga por Transportadora")
        if transp_col and transp_col in df_filtered.columns and not df_filtered.empty:
            df_transp = df_filtered[transp_col].value_counts().reset_index()
            df_transp.columns = [transp_col, "Qtd"]
            fig_transp = px.bar(
                df_transp,
                x=transp_col,
                y="Qtd",
                text="Qtd",
                color=transp_col,
                color_discrete_sequence=px.colors.qualitative.Bold
            )
            fig_transp.update_layout(margin=dict(t=10, b=10, l=10, r=10), height=320, showlegend=False)
            st.plotly_chart(fig_transp, use_container_width=True)
        else:
            st.info("Sem dados suficientes para o gráfico de transportadoras.")

    # --- HISTÓRICO DE PEDIDOS AO LONGO DO TEMPO ---
    if data_col and data_col in df_filtered.columns and not df_filtered.empty:
        st.subheader("📈 Volume de Pedidos no Tempo")
        df_filtered[data_col] = pd.to_datetime(df_filtered[data_col])
        df_time = df_filtered.groupby(df_filtered[data_col].dt.date).size().reset_index(name="Volume")
        fig_time = px.area(
            df_time,
            x=data_col,
            y="Volume",
            markers=True,
            line_shape="spline",
            color_discrete_sequence=["#0086FF"]
        )
        fig_time.update_layout(margin=dict(t=10, b=10, l=10, r=10), height=280)
        st.plotly_chart(fig_time, use_container_width=True)

    # --- TABELA DE DADOS E EXPORTAÇÃO ---
    st.markdown("---")
    st.subheader("📋 Relatório Detalhado de Expedição")

    col_tb1, col_tb2 = st.columns([4, 1])
    with col_tb1:
        st.write(f"Exibindo **{len(df_filtered)}** registros filtrados.")
    with col_tb2:
        csv_data = df_filtered.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Baixar CSV",
            data=csv_data,
            file_name=f"expedicao_magalog_{datetime.date.today()}.csv",
            mime="text/csv",
            use_container_width=True
        )

    st.dataframe(df_filtered, use_container_width=True, height=350)

if __name__ == "__main__":
    main()
