"""Install official files using the existing downloaders."""
from pathlib import Path
import os
import tempfile
from paths import DATA_DIR


def gravar_novo(df, destino: Path):
    """Publish a complete parquet atomically without replacing installed data."""
    fd, nome = tempfile.mkstemp(suffix=".parquet.part", dir=destino.parent)
    os.close(fd)
    tmp = Path(nome)
    try:
        df.to_parquet(tmp, index=False)
        os.link(tmp, destino)
    finally:
        tmp.unlink(missing_ok=True)


def instalar_eleicao(ano: int, turno: int, cargo: int, progresso=None, zip_local=None):
    from baixar_dados import baixar, ler_zip, limpar
    if not 1932 <= ano <= 2100 or turno not in (1, 2) or cargo < 1:
        raise ValueError("Ano, turno ou cargo inválido.")
    destino = DATA_DIR / f"secoes_{ano}_t{turno}.parquet"
    if destino.exists():
        raise FileExistsError(f"{destino.name} já está instalado. A base existente foi preservada.")
    caminho = Path(zip_local) if zip_local else baixar(ano, progresso)
    df = limpar(ler_zip(caminho, turno, cargo))
    if df.empty:
        raise ValueError("O TSE não retornou seções para esta seleção.")
    gravar_novo(df, destino)
    return destino


def instalar_logs(ano: int, turno: int, uf: str):
    from baixar_logs import URL, EXT_LOG, UFS, processar_zip
    from download_tse import SemDownloadParcial, baixar_completo, baixar_so_logs
    if uf not in UFS or turno not in (1, 2):
        raise ValueError("UF ou turno inválido.")
    destino = DATA_DIR / f"logs_{ano}_t{turno}_{uf}.parquet"
    if destino.exists():
        raise FileExistsError(f"{destino.name} já está instalado.")
    url = URL.format(ano=ano, turno=turno, uf=uf)
    completo = DATA_DIR / f"arqurna_{ano}_{turno}t_{uf}.zip"
    if completo.exists():
        caminho = completo
    else:
        try:
            caminho, total, falhas = baixar_so_logs(
                url, DATA_DIR / f"logs_brutos_{ano}_{turno}t_{uf}.zip", EXT_LOG, 4)
        except SemDownloadParcial:
            caminho = baixar_completo(url, completo)
        else:
            if falhas:
                raise OSError(f"{falhas} de {total} logs faltam. Tente novamente para retomar.")
    df = processar_zip(caminho, uf, 1)
    if df.empty:
        raise ValueError("Nenhum log válido encontrado no arquivo do TSE.")
    gravar_novo(df, destino)
    return destino
