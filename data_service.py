from pathlib import Path

import pandas as pd

from analise import juntar_horario, pontuar_secoes
from paths import DATA_DIR


def listar_eleicoes() -> list[Path]:
    """Retorna os arquivos eleitorais disponíveis, do mais recente para o mais antigo."""
    return sorted(
        DATA_DIR.glob("secoes_*.parquet"),
        reverse=True,
    )


def listar_logs(caminho_secoes: Path) -> list[Path]:
    """Localiza os logs correspondentes ao arquivo de seções."""
    sufixo = caminho_secoes.stem.replace("secoes_", "")
    return sorted(DATA_DIR.glob(f"logs_{sufixo}_*.parquet"))


def carregar_eleicao(caminho: Path) -> pd.DataFrame:
    """Carrega uma eleição e aplica o motor estatístico existente."""
    df = pd.read_parquet(caminho)

    df = pontuar_secoes(df)

    arquivos_log = listar_logs(caminho)

    if arquivos_log:
        logs = pd.concat(
            [pd.read_parquet(arquivo) for arquivo in arquivos_log],
            ignore_index=True,
        )
    else:
        logs = None

    return juntar_horario(df, logs)


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
        "municipios": int(df["cd_municipio"].nunique()) if "cd_municipio" in df else 0,
        "aptos": total_aptos,
        "abstencoes": abstencoes,
        "taxa_abstencao": taxa_abstencao,
        "tem_logs": bool(df["tem_log"].any()) if "tem_log" in df else False,
    }
