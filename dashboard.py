"""Windows dashboard; analytical behavior is preserved in painel.py."""
import logging
import streamlit as st
from data_service import carregar_eleicao, listar_eleicoes, resumo_eleicao
from paths import CACHE_DIR, DATA_DIR, LOG_DIR
from version import __version__

st.set_page_config(page_title="ESTELEIÇÃO Intelligence", page_icon="🗳️", layout="wide")
st.title("ESTELEIÇÃO Intelligence")
st.caption(f"Versão {__version__} · Fonte: Tribunal Superior Eleitoral")
st.warning("Indicadores estatísticos não constituem, por si só, evidência de fraude.")
pagina = st.sidebar.radio("Intelligence", ["🏠 Visão Geral", "📊 Análises", "📥 Dados", "⚙️ Configurações"])
if pagina == "📥 Dados":
    from data_manager import render
    render()
elif pagina == "⚙️ Configurações":
    st.subheader("Armazenamento e diagnóstico")
    for nome, pasta in [("Dados", DATA_DIR), ("Cache", CACHE_DIR), ("Logs", LOG_DIR)]:
        st.text(f"{nome}: {pasta}")
    st.info("Dados persistem entre atualizações e desinstalações. Logs de execução ficam na pasta acima.")
    if st.button("Limpar cache e recarregar"):
        st.cache_data.clear()
        st.cache_resource.clear()
        st.rerun()
elif pagina == "📊 Análises":
    if not listar_eleicoes():
        st.info("Instale uma eleição em 📥 Dados para começar.")
    else:
        from analytics_view import render
        render()
else:
    arquivos = listar_eleicoes()
    if not arquivos:
        st.info("Nenhuma eleição instalada. Abra 📥 Dados para baixar e processar dados oficiais do TSE.")
    else:
        arquivo = st.selectbox("Eleição / turno", arquivos, format_func=lambda p: p.stem.replace("secoes_", ""))
        try:
            with st.spinner("Carregando o motor estatístico…"):
                base = carregar_eleicao(arquivo)
                r = resumo_eleicao(base)
        except (OSError, ValueError, KeyError) as exc:
            logging.exception("Falha ao carregar %s", arquivo)
            st.error(f"Não foi possível carregar {arquivo.name}: {exc}. Confira os dados em 📥 Dados.")
        else:
            campos = [("Seções", r["secoes"]), ("UFs", r["ufs"]), ("Municípios", r["municipios"]),
                      ("Eleitores aptos", r["aptos"]), ("Abstenções", r["abstencoes"]),
                      ("Abstenção agregada", f'{r["taxa_abstencao"]:.2%}'),
                      ("Seções com log", r["secoes_com_log"]), ("Seções sinalizadas", r["sinalizadas"])]
            for i in range(0, len(campos), 4):
                for col, (nome, valor) in zip(st.columns(4), campos[i:i+4]):
                    col.metric(nome, valor)
            st.success("Motor estatístico: base carregada e pontuada.")
            st.caption("Sinalização padrão: z ajustado ≤ −3 e ≥50 aptos; votação tardia ≥15% e ≥10 votos, "
                       "destoando ≥30 minutos da escola quando disponível; liberação manual z≥3 e ≥5 casos. "
                       "Em 📊 Análises você pode ajustar os limites e explorar cada seção.")
