import streamlit as st

from data_service import carregar_eleicao, listar_eleicoes, resumo_eleicao
from version import __version__


st.set_page_config(
    page_title="ESTELEIÇÃO Intelligence",
    page_icon="🗳️",
    layout="wide",
    initial_sidebar_state="expanded",
)


st.markdown(
    """
    <style>
        .block-container {
            padding-top: 1.4rem;
            padding-bottom: 2rem;
        }

        .est-title {
            font-size: 2.2rem;
            font-weight: 800;
            margin-bottom: 0;
        }

        .est-subtitle {
            color: #8b949e;
            margin-top: 0.2rem;
            margin-bottom: 1.5rem;
        }

        .status-card {
            border: 1px solid rgba(128,128,128,.25);
            border-radius: 12px;
            padding: 16px;
            min-height: 110px;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------
# Dados disponíveis
# ---------------------------------------------------------

arquivos_eleicao = listar_eleicoes()

arquivo_selecionado = None
base = None
resumo_atual = None


# ---------------------------------------------------------
# Sidebar
# ---------------------------------------------------------

with st.sidebar:
    st.title("🗳️ ESTELEIÇÃO")
    st.caption(f"Intelligence v{__version__}")

    st.divider()

    if arquivos_eleicao:
        arquivo_selecionado = st.selectbox(
            "Eleição / turno",
            arquivos_eleicao,
            format_func=lambda p: p.stem.replace("secoes_", "").upper(),
        )

        with st.spinner("Carregando dados eleitorais..."):
            base = carregar_eleicao(arquivo_selecionado)
            resumo_atual = resumo_eleicao(base)

    else:
        st.warning("Nenhuma eleição instalada.")

    st.divider()

    pagina = st.radio(
        "Navegação",
        [
            "🏠 Visão Geral",
            "🗺️ Mapa Eleitoral",
            "🗳️ Resultados",
            "📊 Estatística",
            "🚩 Anomalias",
            "⏰ Horário dos votos",
            "🖐️ Biometria",
            "🔀 Cruzamento",
            "🔎 Seção eleitoral",
            "📈 Histórico",
            "📥 Dados",
            "⚙️ Configurações",
        ],
    )

    st.divider()
    st.caption("Fonte principal: Tribunal Superior Eleitoral")


# ---------------------------------------------------------
# Cabeçalho
# ---------------------------------------------------------

st.markdown(
    '<p class="est-title">ESTELEIÇÃO Intelligence</p>',
    unsafe_allow_html=True,
)

st.markdown(
    '<p class="est-subtitle">'
    'Plataforma de inteligência e análise estatística de dados eleitorais brasileiros.'
    '</p>',
    unsafe_allow_html=True,
)


# ---------------------------------------------------------
# Visão Geral
# ---------------------------------------------------------

if pagina == "🏠 Visão Geral":
    st.subheader("Visão Geral")

    nome_eleicao = (
        arquivo_selecionado.stem.replace("secoes_", "").upper()
        if arquivo_selecionado
        else "—"
    )

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.metric(
            "Eleição",
            nome_eleicao,
        )

    with c2:
        st.metric(
            "Seções analisadas",
            f"{resumo_atual['secoes']:,}".replace(",", ".")
            if resumo_atual
            else "—",
        )

    with c3:
        st.metric(
            "UFs com dados",
            resumo_atual["ufs"]
            if resumo_atual
            else "—",
        )

    with c4:
        st.metric(
            "Abstenção",
            f"{resumo_atual['taxa_abstencao']:.2%}"
            if resumo_atual
            else "—",
        )

    if resumo_atual:
        st.divider()

        k1, k2, k3 = st.columns(3)

        with k1:
            st.metric(
                "Eleitores aptos",
                f"{resumo_atual['aptos']:,}".replace(",", "."),
            )

        with k2:
            st.metric(
                "Municípios",
                f"{resumo_atual['municipios']:,}".replace(",", "."),
            )

        with k3:
            st.metric(
                "Abstenções",
                f"{resumo_atual['abstencoes']:,}".replace(",", "."),
            )

    st.divider()

    dados_status = (
        "🟢 Carregados"
        if resumo_atual
        else "🟡 Aguardando leitura"
    )

    logs_status = (
        "🟢 Disponíveis"
        if resumo_atual and resumo_atual["tem_logs"]
        else "🟡 Não carregados"
    )

    s1, s2, s3, s4 = st.columns(4)

    with s1:
        st.markdown(
            """
            <div class="status-card">
                <b>🧠 Motor estatístico</b><br><br>
                🟢 Disponível
            </div>
            """,
            unsafe_allow_html=True,
        )

    with s2:
        st.markdown(
            f"""
            <div class="status-card">
                <b>🗳️ Dados eleitorais</b><br><br>
                {dados_status}
            </div>
            """,
            unsafe_allow_html=True,
        )

    with s3:
        st.markdown(
            f"""
            <div class="status-card">
                <b>🧾 Logs de urna</b><br><br>
                {logs_status}
            </div>
            """,
            unsafe_allow_html=True,
        )

    with s4:
        st.markdown(
            """
            <div class="status-card">
                <b>🔍 Cruzamento</b><br><br>
                🟢 Disponível
            </div>
            """,
            unsafe_allow_html=True,
        )

    if resumo_atual:
        st.success(
            "Base eleitoral carregada com sucesso. "
            "O ESTELEIÇÃO Intelligence já está lendo os dados reais."
        )
    else:
        st.info(
            "Nenhuma base eleitoral foi encontrada. "
            "Quando os dados forem instalados, esta tela será preenchida automaticamente."
        )


# ---------------------------------------------------------
# Demais módulos
# ---------------------------------------------------------

else:
    st.subheader(pagina)

    st.info(
        "Módulo preparado. As funcionalidades existentes serão migradas para esta área "
        "sem alterar o painel original."
    )


# ---------------------------------------------------------
# Rodapé
# ---------------------------------------------------------

st.divider()

st.caption(
    "ESTELEIÇÃO Intelligence apresenta indicadores estatísticos e dados públicos. "
    "Uma anomalia estatística não constitui, por si só, evidência de fraude."
)
