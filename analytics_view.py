"""Render the preserved analytical dashboard inside Intelligence."""
from pathlib import Path
import runpy


def render():
    runpy.run_path(str(Path(__file__).with_name("painel.py")),
                   init_globals={"INTELLIGENCE_EMBEDDED": True})
