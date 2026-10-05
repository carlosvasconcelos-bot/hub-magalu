import streamlit as st
import datetime
import pandas as pd
import re

# ==========================================
# 1. CONFIGURAÇÃO DA PÁGINA (Padrão Ouro)
# ==========================================
# Definimos o título, ícone e dizemos para o layout usar o modo "wide"
# (tela mais larga) para os cartões respirarem melhor na tela.
st.set_page_config(
    page_title="Hub Operacional | Magalu",
    page_icon="🛍️",
    layout="wide"
)

# ==========================================
# 2. CSS AVANÇADO (A "Surpresa" do Layout)
# ==========================================
def aplicar_css_magalu_premium():
    """
    Injeta um CSS de alto nível. Escondemos elementos padrão do Streamlit
    e criamos classes personalizadas para cartões flutuantes, sombras e degradês.
    """
    estilo = """
    <style>
    /* 1. Esconder menus do Streamlit para parecer um sistema 100% próprio */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Fundo levemente acinzentado para destacar os cartões brancos */
    .stApp {
        background-color: #F4F6F9;
    }

    /* 2. Banner Principal (Header Magalu) */
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

    /* 3. Cartões Interativos (Cards) */
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
    /* Efeito Mágico Hover: O cartão sobe, ganha borda azul e sombra projetada */
    .magalu-card:hover {
        border-color: #0086FF;
        transform: translateY(-8px);
        box-shadow: 0 15px 30px rgba(0,134,255,0.15);
    }

    /* Ícone dentro do cartão */
    .card-icon {
        font-size: 2.5rem;
        margin-right: 20px;
        background: #E6F3FF; /* Fundo azul bem clarinho */
        padding: 15px 20px;
        border-radius: 14px;
    }

    /* Textos do cartão */
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

    /* Seta indicativa no final do cartão */
    .card-arrow {
        color: #0086FF;
        font-size: 1.8rem;
        font-weight: bold;
        transition: transform 0.3s;
    }
    .magalu-card:hover .card-arrow {
        transform: translateX(5px); /* A seta anda pra direita quando passa o mouse */
    }

    /* Animação de entrada da tela */
    @keyframes fadeInDown {
        from { opacity: 0; transform: translateY(-20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    </style>
    """
    st.markdown(estilo, unsafe_allow_html=True)

# ==========================================
# 3. BASE DE DADOS DOS LINKS (Endpoints & Fallback)
# ==========================================
DEFAULT_SHEET_URL = "https://docs.google.com/spreadsheets/d/1vcGVtgxeNOIPKYKTCa5Y47UQE-SLvfcAI0S1uQBXXAs/edit?gid=454063207#gid=454063207"

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
        "titulo": "Gestão de Expedição",
        "desc": "Controle de saída, faturamento e logística",
        "icone": "📦",
        "url": "https://script.google.com/a/macros/magazineluiza.com.br/s/AKfycbw3TmoCWUqu0CvbLFVBTqtMz3zkMSDCDEWVvUiGxE2zYXJqVYH84gpQoYJmE9ain8ZA9A/exec"
    },
    {
        "titulo": "Torre de Transporte",
        "desc": "Monitoramento da frota e rotas de entrega",
        "icone": "🚚",
        "url": "https://script.google.com/macros/s/AKfycbydnRumhAEXucgJ3fLCrT2GbmaF4llJgR_L5rJoxPUY5Xq5ybwvy65vtL1wxIboD3_a/exec"
    }
]

def extract_sheet_csv_url(url: str) -> str:
    """
    Extrai a URL de exportação CSV a partir de um link de planilha do Google Sheets.
    """
    sheet_id_match = re.search(r'/d/([a-zA-Z0-9-_]+)', url)
    gid_match = re.search(r'[?&]gid=([0-9]+)', url)

    if sheet_id_match:
        sheet_id = sheet_id_match.group(1)
        gid = gid_match.group(1) if gid_match else '0'
        return f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"
    return url

@st.cache_data(ttl=60)
def carregar_links_google_sheets(sheet_url: str):
    """
    Carrega os links a partir do Google Sheets.
    Retorna uma tupla (links, erro_msg). Se houver erro, utiliza os links de fallback.
    """
    try:
        csv_url = extract_sheet_csv_url(sheet_url)
        df = pd.read_csv(csv_url)

        # Mapeamento de colunas insensível a maiúsculas/minúsculas
        col_map = {}
        for col in df.columns:
            clean_col = str(col).strip().lower()
            if clean_col in ['titulo', 'title', 'nome']:
                col_map[col] = 'titulo'
            elif clean_col in ['desc', 'descricao', 'descrição', 'description']:
                col_map[col] = 'desc'
            elif clean_col in ['icone', 'ícone', 'icon']:
                col_map[col] = 'icone'
            elif clean_col in ['url', 'link', 'endpoint']:
                col_map[col] = 'url'

        df = df.rename(columns=col_map)

        required = ['titulo', 'url']
        if not all(k in df.columns for k in required):
            return LINKS_MAGALU, "Colunas obrigatórias ('titulo', 'url') não encontradas na planilha."

        if 'desc' not in df.columns:
            df['desc'] = ''
        if 'icone' not in df.columns:
            df['icone'] = '🔗'

        links = []
        for _, row in df.iterrows():
            if pd.notna(row['titulo']) and pd.notna(row['url']):
                links.append({
                    "titulo": str(row['titulo']).strip(),
                    "desc": str(row['desc']).strip() if pd.notna(row['desc']) else "",
                    "icone": str(row['icone']).strip() if pd.notna(row['icone']) else "🔗",
                    "url": str(row['url']).strip()
                })

        if not links:
            return LINKS_MAGALU, "Nenhum link válido encontrado na planilha."

        return links, None
    except Exception as e:
        return LINKS_MAGALU, f"Não foi possível carregar a planilha diretamente ({str(e)}). Exibindo dados padrão."

# ==========================================
# 4. FUNÇÃO DE RENDERIZAÇÃO DE CARTÕES
# ==========================================
def desenhar_cartao(item: dict):
    """
    Gera o HTML de um cartão individual com base no dicionário de dados.
    A tag <a> faz com que o cartão inteiro seja clicável e abra em nova aba (target="_blank").
    """
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
# 5. CONSTRUÇÃO DA TELA (Front-End)
# ==========================================
def construir_hub():
    aplicar_css_magalu_premium()

    # Painel Lateral para Fonte de Dados
    with st.sidebar:
        st.header("⚙️ Configurações")
        sheet_input = st.text_input("URL do Google Sheets", value=DEFAULT_SHEET_URL)
        if st.button("Atualizar Dados"):
            st.cache_data.clear()

    # Carrega os links do Google Sheets ou Fallback
    links, erro_msg = carregar_links_google_sheets(sheet_input)

    # Saudação dinâmica com base na hora do seu computador
    hora_atual = datetime.datetime.now().hour
    if hora_atual < 12:
        saudacao = "Bom dia"
    elif hora_atual < 18:
        saudacao = "Boa tarde"
    else:
        saudacao = "Boa noite"

    # Renderiza o Banner Topo
    banner_html = f"""
    <div class="magalu-banner">
        <h1>{saudacao}, Equipe! 👋</h1>
        <p>Bem-vindo ao Hub Central de Operações Magalog CD050. O que vamos acessar agora?</p>
    </div>
    """
    st.markdown(banner_html, unsafe_allow_html=True)

    if erro_msg:
        st.info(f"ℹ️ {erro_msg}")

    # st.container cria um bloco centralizado para os botões não ficarem esticados demais
    with st.container():
        # Criação de 2 colunas para alinhar os cartões lado a lado
        col1, col2 = st.columns(2)

        for idx, item in enumerate(links):
            if idx % 2 == 0:
                with col1:
                    desenhar_cartao(item)
            else:
                with col2:
                    desenhar_cartao(item)

    # Rodapé discreto estilo sistema interno
    st.markdown("<br><hr style='border:1px solid #E5E5E5;'>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #999; font-size: 0.9rem;'> Programado por Carlos Vasconcelos | Desenvolvido com Python 🐍</p>", unsafe_allow_html=True)

# ==========================================
# 6. GATILHO PRINCIPAL
# ==========================================
if __name__ == "__main__":
    construir_hub()
