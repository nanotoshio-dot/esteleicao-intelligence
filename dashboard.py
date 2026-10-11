import streamlit as st

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


with st.sidebar:
    st.title("🗳️ ESTELEIÇÃO")
    st.caption(f"Intelligence v{__version__}")

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


if pagina == "🏠 Visão Geral":
    st.subheader("Visão Geral")

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.metric("Eleição", "—")

    with c2:
        st.metric("Seções analisadas", "—")

    with c3:
        st.metric("UFs com dados", "—")

    with c4:
        st.metric("Sinais estatísticos", "—")

    st.divider()

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
            """
            <div class="status-card">
                <b>🗳️ Dados eleitorais</b><br><br>
                🟡 Aguardando leitura
            </div>
            """,
            unsafe_allow_html=True,
        )

    with s3:
        st.markdown(
            """
            <div class="status-card">
                <b>🧾 Logs de urna</b><br><br>
                🟡 Aguardando leitura
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

    st.info(
        "Esta tela será alimentada progressivamente pelo motor analítico já existente."
    )

else:
    st.subheader(pagina)
    st.info(
        "Módulo preparado. As funcionalidades existentes serão migradas para esta área "
        "sem alterar o painel original."
    )


st.divider()

st.caption(
    "ESTELEIÇÃO Intelligence apresenta indicadores estatísticos e dados públicos. "
    "Uma anomalia estatística não constitui, por si só, evidência de fraude."
)
