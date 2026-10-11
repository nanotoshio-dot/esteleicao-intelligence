import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import zipfile

# Test data never enters the user's installed election directory.
_root = tempfile.TemporaryDirectory()
os.environ["LOCALAPPDATA"] = _root.name

import numpy as np
import pandas as pd
import data_service
import data_install
import baixar_dados
from paths import DATA_DIR, CACHE_DIR, LOG_DIR
from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).resolve().parents[1]


def fixture():
    return pd.DataFrame([dict(uf=uf, cd_municipio=mun, municipio=f"Município {mun}",
                             zona=1, secao=s, aptos=100, comparecimento=80+s%4,
                             abstencoes=20-s%4, taxa_abstencao=(20-s%4)/100,
                             local=(s-1)//4+1, nome_local="Escola")
                         for uf, mun in [("SP", 1), ("CE", 2)] for s in range(1, 13)])


class ApplicationTests(unittest.TestCase):
    def setUp(self):
        for p in DATA_DIR.glob("*"):
            if p.is_file():
                p.unlink()
        data_service._carregar.clear()

    def install_fixture(self):
        path = DATA_DIR / "secoes_1999_t1.parquet"
        fixture().to_parquet(path, index=False)
        return path

    def test_version_and_paths(self):
        from version import __version__
        self.assertEqual(__version__, (ROOT / "VERSION").read_text().strip())
        for p in (DATA_DIR, CACHE_DIR, LOG_DIR):
            self.assertTrue(p.is_dir())
            self.assertTrue(p.is_relative_to(Path(_root.name)))

    def test_discovery_and_summary(self):
        path = self.install_fixture()
        (DATA_DIR / "secoes_bad.parquet").touch()
        self.assertEqual(data_service.listar_eleicoes(), [path])
        summary = data_service.resumo_eleicao(data_service.carregar_eleicao(path))
        self.assertEqual(summary["secoes"], 24)
        self.assertEqual(summary["municipios"], 2)
        self.assertAlmostEqual(summary["taxa_abstencao"], fixture().abstencoes.sum()/2400)
        self.assertFalse(summary["tem_logs"])
        fixture().iloc[:12].to_parquet(path, index=False)
        self.assertEqual(len(data_service.carregar_eleicao(path)), 12)

    def test_install_zip_and_no_overwrite(self):
        raw = pd.DataFrame([dict(NR_TURNO=1, SG_UF="SP", CD_MUNICIPIO=1,
            NM_MUNICIPIO="Teste", NR_ZONA=1, NR_SECAO=1, CD_CARGO=1,
            DS_CARGO="Presidente", QT_APTOS=100, QT_COMPARECIMENTO=80, QT_ABSTENCOES=20)])
        zip_path = DATA_DIR / "sample.zip"
        with zipfile.ZipFile(zip_path, "w") as archive:
            archive.writestr("BRASIL.csv", raw.to_csv(sep=";", index=False).encode("latin-1"))
        result = data_install.instalar_eleicao(1999, 1, 1, zip_local=zip_path)
        self.assertEqual(pd.read_parquet(result).aptos.sum(), 100)
        with self.assertRaises(FileExistsError):
            data_install.instalar_eleicao(1999, 1, 1, zip_local=zip_path)
        with self.assertRaises(ValueError):
            data_install.instalar_eleicao(1999, 2, 1, zip_local=zip_path)
        self.assertFalse((DATA_DIR / "secoes_1999_t2.parquet").exists())

    def test_empty_dashboard_pages(self):
        app = AppTest.from_file(str(ROOT / "dashboard.py")).run(timeout=30)
        self.assertFalse(app.exception)
        for page in ["📊 Análises", "📥 Dados", "⚙️ Configurações"]:
            app.sidebar.radio[0].set_value(page).run(timeout=30)
            self.assertFalse(app.exception, str(app.exception))

    def test_analytics_and_drilldown(self):
        self.install_fixture()
        app = AppTest.from_file(str(ROOT / "dashboard.py")).run(timeout=30)
        self.assertFalse(app.exception)
        app.sidebar.radio[0].set_value("📊 Análises").run(timeout=30)
        self.assertFalse(app.exception, str(app.exception))
        app.sidebar.selectbox[1].set_value("SP").run(timeout=30)
        app.sidebar.selectbox[2].set_value(1).run(timeout=30)
        app.sidebar.selectbox[3].set_value(1).run(timeout=30)
        app.sidebar.selectbox[4].set_value(1).run(timeout=30)
        self.assertFalse(app.exception, str(app.exception))

    def test_logs_and_analytical_pages(self):
        self.install_fixture()
        from gerar_dados_teste import montar_log
        from baixar_logs import processar_zip
        archive_path = DATA_DIR / "sample_logs.zip"
        with zipfile.ZipFile(archive_path, "w") as archive:
            for s in range(1, 13):
                votos = np.linspace(8.1*3600, (17.5 if s == 1 else 16.5)*3600, 80+s%4).astype(int)
                hab = np.arange(len(votos)) % 3
                content = montar_log(1, 1, s, votos, hab, 0, 100+s)
                import io
                buf = io.BytesIO()
                with zipfile.ZipFile(buf, "w") as inner:
                    inner.writestr("logd.dat", content)
                archive.writestr(f"o00999sp000010001{s:04d}-log.jez", buf.getvalue())
        logs = processar_zip(archive_path, "SP", 1)
        self.assertEqual(len(logs), 12)
        logs.to_parquet(DATA_DIR / "logs_1999_t1_SP.parquet", index=False)
        app = AppTest.from_file(str(ROOT / "dashboard.py")).run(timeout=30)
        self.assertFalse(app.exception, str(app.exception))
        app.sidebar.radio[0].set_value("📊 Análises").run(timeout=30)
        self.assertFalse(app.exception, str(app.exception))

    def test_occupied_port(self):
        import socket
        from launcher import escolher_porta
        with socket.socket() as sock:
            sock.bind(("127.0.0.1", 0))
            occupied = sock.getsockname()[1]
            self.assertNotEqual(escolher_porta(occupied), occupied)

    def test_data_manager_install_button(self):
        app = AppTest.from_file(str(ROOT / "dashboard.py")).run(timeout=30)
        app.sidebar.radio[0].set_value("📥 Dados").run(timeout=30)
        with patch("data_manager.instalar_eleicao", side_effect=lambda *args: self.install_fixture()) as install:
            app.button[1].click().run(timeout=30)
            app.session_state["download_job"].result(timeout=10)
            app.run(timeout=30)
            install.assert_called_once()
            self.assertFalse(app.exception, str(app.exception))
            self.assertTrue(any("Instalado:" in item.value for item in app.success))
        app.sidebar.radio[0].set_value("🏠 Visão Geral").run(timeout=30)
        self.assertEqual(len(app.metric), 8)

    def test_data_manager_download_failure(self):
        app = AppTest.from_file(str(ROOT / "dashboard.py")).run(timeout=30)
        app.sidebar.radio[0].set_value("📥 Dados").run(timeout=30)
        with patch("data_manager.instalar_eleicao", side_effect=OSError("TSE indisponível")):
            app.button[1].click().run(timeout=30)
            app.run(timeout=30)
            self.assertFalse(app.exception, str(app.exception))
            self.assertTrue(any("TSE indisponível" in item.value for item in app.error))


if __name__ == "__main__":
    unittest.main()
