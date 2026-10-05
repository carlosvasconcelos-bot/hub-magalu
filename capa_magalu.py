import streamlit as st
import datetime
import importlib.util

# ==========================================
# 1. CONFIGURAÇÃO DA PÁGINA (Padrão Ouro)
# ==========================================
st.set_page_config(
    page_title="Hub Operacional | Magalu",
    page_icon="🛍️",
    layout="wide"
)

# ==========================================
# 2. CSS AVANÇADO (A "Surpresa" do Layout)
# ==========================================
def aplicar_css_magalu_premium():
    estilo = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    .stApp {
        background-color: #F4F6F9;
    }

    /* Banner Principal (Header Magalu) */
    .magalu-banner {
        background: linear-gradient(135deg, #0086FF 0%, #005bb5 100%);
        padding: 40px 20px;
        border-radius: 20px;
        color: white;
        text-align: center;
        box-shadow: 0 10px 30px rgba(0, 134, 255, 0.3);
        margin-bottom: 40px;
        animation: fadeInDown 0.8s ease-out;
    }
    .magalu-banner h1 {
        color: white !important;
        font-family: 'Arial', sans-serif;
        font-size: 3rem;
        font-weight: 900;
        margin: 0;
        padding: 0;
        letter-spacing: -1px;
    }
    .magalu-banner p {
        font-size: 1.2rem;
        opacity: 0.9;
        margin-top: 10px;
    }

    /* Cartões Interativos */
    .magalu-card {
        background-color: white;
        border-radius: 16px;
        padding: 25px;
        display: flex;
        align-items: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.04);
        border: 2px solid transparent;
        transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
        margin-bottom: 20px;
        cursor: pointer;
        text-decoration: none;
    }
    .magalu-card:hover {
        border-color: #0086FF;
        transform: translateY(-8px);
        box-shadow: 0 15px 30px rgba(0,134,255,0.15);
    }

    .card-icon {
        font-size: 2.5rem;
        margin-right: 20px;
        background: #E6F3FF;
        padding: 15px 20px;
        border-radius: 14px;
    }

    .card-text {
        flex-grow: 1;
    }
    .card-text h3 {
        color: #1A1A1A;
        margin: 0 0 5px 0;
        font-size: 1.3rem;
        font-weight: bold;
    }
    .card-text p {
        color: #666;
        margin: 0;
        font-size: 0.95rem;
    }

    .card-arrow {
        color: #0086FF;
        font-size: 1.8rem;
        font-weight: bold;
        transition: transform 0.3s;
    }
    .magalu-card:hover .card-arrow {
        transform: translateX(5px);
    }

    @keyframes fadeInDown {
        from { opacity: 0; transform: translateY(-20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    </style>
    """
    st.markdown(estilo, unsafe_allow_html=True)

# ==========================================
# 3. BASE DE DADOS DOS LINKS (Endpoints)
# ==========================================
LINKS_MAGALU = [
    {
        "titulo": "Indicadores Oficiais",
        "desc": "Acompanhamento geral das métricas da unidade",
        "icone": "📊",
        "url": "https://script.google.com/a/macros/magazineluiza.com.br/s/AKfycbzt2NPfm0oSu_mAqmHjBKXGhrYd4YpFx5Bd_a9kJg8_L6ZIwwKGJHIQlWpJKIKMlEJHVg/exec"
    },
    {
        "titulo": "Metas e Gerot",
        "desc": "Painel de resultados e batimento de metas",
        "icone": "🎯",
        "url": "https://script.google.com/a/macros/magazineluiza.com.br/s/AKfycbx0rDmv7GRCeJ5pGDOOgMcrZbeQ4sGzKFV_Q9ccORin7tOxGH6zLg-o1S-2EebJ9nut4g/exec"
    },
    {
        "titulo": "Gestão de Expedição (Google Sheets)",
        "desc": "App Interativo de Expedição com conexão ao Google Sheets e KPIs",
        "icone": "📦",
        "interna": True
    },
    {
        "titulo": "Torre de Transporte",
        "desc": "Monitoramento da frota e rotas de entrega",
        "icone": "🚚",
        "url": "https://script.google.com/macros/s/AKfycbydnRumhAEXucgJ3fLCrT2GbmaF4llJgR_L5rJoxPUY5Xq5ybwvy65vtL1wxIboD3_a/exec"
    }
]

def desenhar_cartao(item: dict):
    if item.get("interna"):
        if st.button(f"{item['icone']} {item['titulo']} - {item['desc']}", use_container_width=True, type="primary"):
            st.session_state["pagina_atual"] = "expedicao"
            st.rerun()
    else:
        html = f"""
        <a href="{item['url']}" target="_blank" style="text-decoration: none;">
            <div class="magalu-card">
                <div class="card-icon">{item['icone']}</div>
                <div class="card-text">
                    <h3>{item['titulo']}</h3>
                    <p>{item['desc']}</p>
                </div>
                <div class="card-arrow">➔</div>
            </div>
        </a>
        """
        st.markdown(html, unsafe_allow_html=True)

# ==========================================
# 4. CONSTRUÇÃO DA TELA (Front-End)
# ==========================================
def construir_hub():
    aplicar_css_magalu_premium()

    hora_atual = datetime.datetime.now().hour
    if hora_atual < 12:
        saudacao = "Bom dia"
    elif hora_atual < 18:
        saudacao = "Boa tarde"
    else:
        saudacao = "Boa noite"

    banner_html = f"""
    <div class="magalu-banner">
        <h1>{saudacao}, Equipe! 👋</h1>
        <p>Bem-vindo ao Hub Central de Operações Magalog CD050. O que vamos acessar agora?</p>
    </div>
    """
    st.markdown(banner_html, unsafe_allow_html=True)

    with st.container():
        col1, col2 = st.columns(2)

        with col1:
            desenhar_cartao(LINKS_MAGALU[0])
            desenhar_cartao(LINKS_MAGALU[2])

        with col2:
            desenhar_cartao(LINKS_MAGALU[1])
            desenhar_cartao(LINKS_MAGALU[3])

    st.markdown("<br><hr style='border:1px solid #E5E5E5;'>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #999; font-size: 0.9rem;'> Programado por Carlos Vasconcelos | Desenvolvido com Python 🐍</p>", unsafe_allow_html=True)

# ==========================================
# 5. GATILHO PRINCIPAL COM ROTEAMENTO
# ==========================================
if __name__ == "__main__":
    if "pagina_atual" not in st.session_state:
        st.session_state["pagina_atual"] = "hub"

    if st.session_state["pagina_atual"] == "expedicao":
        if st.sidebar.button("⬅️ Voltar ao Hub Central"):
            st.session_state["pagina_atual"] = "hub"
            st.rerun()

        try:
            import expedicao
            expedicao.main()
        except Exception as e:
            st.error(f"Erro ao carregar o aplicativo de expedição: {e}")
    else:
        construir_hub()
