from pathlib import Path
import re

import pandas as pd
import streamlit as st

from analise import juntar_horario, pontuar_secoes
from paths import DATA_DIR


def listar_eleicoes() -> list[Path]:
    """Retorna os arquivos eleitorais disponíveis, do mais recente para o mais antigo."""
    return sorted((p for p in DATA_DIR.glob("secoes_*.parquet")
                   if re.fullmatch(r"secoes_\d{4}_t[12]", p.stem)), reverse=True)


def listar_logs(caminho_secoes: Path) -> list[Path]:
    """Localiza os logs correspondentes ao arquivo de seções."""
    sufixo = caminho_secoes.stem.replace("secoes_", "")
    return sorted(DATA_DIR.glob(f"logs_{sufixo}_*.parquet"))


def carregar_eleicao(caminho: Path) -> pd.DataFrame:
    """Carrega uma eleição e aplica o motor estatístico existente."""
    arquivos = [caminho, *listar_logs(caminho)]
    assinatura = tuple((str(p), p.stat().st_mtime_ns, p.stat().st_size) for p in arquivos)
    return _carregar(str(caminho), assinatura)


@st.cache_resource(max_entries=2, show_spinner=False)
def _carregar(caminho: str, assinatura: tuple) -> pd.DataFrame:
    df = pd.read_parquet(caminho)

    df = pontuar_secoes(df)

    arquivos_log = listar_logs(Path(caminho))

    if arquivos_log:
        logs = pd.concat(
            [pd.read_parquet(arquivo) for arquivo in arquivos_log],
            ignore_index=True,
        )
    else:
        logs = None

    return juntar_horario(df, logs)


def sinalizacao_padrao(df: pd.DataFrame) -> pd.Series:
    from signals import sinalizar
    return sinalizar(df)["alerta"].eq("sinalizada")


def resumo_eleicao(df: pd.DataFrame) -> dict:
    """Resumo básico usado pela tela inicial do Intelligence."""
    total_aptos = int(df["aptos"].sum()) if "aptos" in df else 0
    abstencoes = int(df["abstencoes"].sum()) if "abstencoes" in df else 0

    taxa_abstencao = (
        abstencoes / total_aptos
        if total_aptos
        else 0
    )

    return {
        "secoes": len(df),
        "ufs": int(df["uf"].nunique()) if "uf" in df else 0,
        "municipios": len(df[["uf", "cd_municipio"]].drop_duplicates()) if "cd_municipio" in df else 0,
        "aptos": total_aptos,
        "abstencoes": abstencoes,
        "taxa_abstencao": taxa_abstencao,
        "tem_logs": bool(df["tem_log"].any()) if "tem_log" in df else False,
        "secoes_com_log": int(df["tem_log"].sum()) if "tem_log" in df else 0,
        "sinalizadas": int(sinalizacao_padrao(df).sum()) if "z_ajustado" in df else 0,
    }
