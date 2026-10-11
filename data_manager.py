"""Data manager UI; downloads run independently of Streamlit reruns."""
import logging
import time
from datetime import date
from concurrent.futures import ThreadPoolExecutor
import streamlit as st
from data_install import instalar_eleicao, instalar_logs
from data_service import listar_eleicoes, listar_logs
from paths import DATA_DIR


@st.cache_resource
def executor():
    return ThreadPoolExecutor(max_workers=1, thread_name_prefix="tse-download")


def render():
    st.subheader("Dados oficiais do TSE")
    st.code(str(DATA_DIR), language=None)
    linhas = []
    for p in listar_eleicoes():
        ano, turno = p.stem.removeprefix("secoes_").split("_t")
        linhas.append({"Ano": ano, "Turno": turno, "Arquivo": p.name,
                       "Tamanho (MB)": round(p.stat().st_size / 1e6, 2),
                       "Logs (UFs)": ", ".join(a.stem.rsplit("_", 1)[1] for a in listar_logs(p)) or "Não instalados"})
    if linhas:
        st.dataframe(linhas, hide_index=True, width="stretch")
    else:
        st.info("Nenhuma eleição instalada.")
    ocupado = "download_job" in st.session_state and not st.session_state.download_job.done()
    if st.button("Atualizar lista / recarregar dados", disabled=ocupado):
        st.cache_data.clear()
        st.cache_resource.clear()
        st.rerun()
    ano = int(st.number_input("Ano da eleição", 1932, 2100, date.today().year, 1))
    turno = st.selectbox("Turno", [1, 2])
    cargos = {1: "Presidente", 3: "Governador", 11: "Prefeito"}
    cargo = st.selectbox("Cargo", list(cargos), format_func=cargos.get)
    st.caption("Para eleições municipais escolha Prefeito. A disponibilidade depende da publicação pelo TSE. "
               "Uma base já instalada para o mesmo ano/turno será preservada.")
    if st.button("Baixar e processar seções oficiais", disabled=ocupado):
        progresso = {"feito": 0, "total": 0}
        def atualizar(feito, total):
            progresso.update(feito=feito, total=total)
        st.session_state.download_progress = progresso
        st.session_state.download_started = time.monotonic()
        st.session_state.download_job = executor().submit(instalar_eleicao, ano, turno, cargo, atualizar)
        st.session_state.download_description = f"Seções: {ano}, turno {turno}"
        st.rerun()
    st.subheader("Logs de urna — opcionais")
    st.warning("Podem ocupar vários GB e demorar bastante. Não são baixados automaticamente. "
               "Se houver interrupção, repita a operação para retomar os arquivos já recebidos.")
    from baixar_logs import UFS
    uf = st.selectbox("UF dos logs", UFS)
    if st.button("Baixar e processar logs desta UF", disabled=ocupado):
        st.session_state.download_progress = {}
        st.session_state.download_started = time.monotonic()
        st.session_state.download_job = executor().submit(instalar_logs, ano, turno, uf)
        st.session_state.download_description = f"Logs: {uf}, {ano}, turno {turno}"
        st.rerun()
    andamento()


@st.fragment(run_every="2s")
def andamento():
    job = st.session_state.get("download_job")
    if job is None:
        return
    if not job.done():
        segundos = int(time.monotonic() - st.session_state.download_started)
        st.info(f"Em andamento: {st.session_state.download_description}. "
                f"Tempo decorrido: {segundos // 60}min {segundos % 60}s. "
                "Baixando/processando no computador; aguarde. Você pode continuar navegando.")
        progresso = st.session_state.get("download_progress", {})
        feito, total = progresso.get("feito", 0), progresso.get("total", 0)
        if total:
            st.progress(min(feito / total, 1.0), text=f"{feito / 1e6:.1f} / {total / 1e6:.1f} MB recebidos; depois o CSV será processado.")
    else:
        try:
            caminho = job.result()
        except Exception as exc:
            logging.exception("Instalação de dados falhou")
            st.error(f"Falha: {exc}. Verifique a conexão e se o TSE publicou os dados selecionados.")
        else:
            st.success(f"Instalado: {caminho}. Use Atualizar lista / recarregar dados.")
