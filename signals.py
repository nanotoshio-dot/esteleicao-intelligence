"""Original section flagging criteria shared by both dashboards."""
import numpy as np
import pandas as pd


def sinalizar(d: pd.DataFrame, medida="z_ajustado", limite=3.0, min_aptos=50,
              lim_17=.15, so_destoa=True, min_crit=1) -> pd.DataFrame:
    """Marca os três critérios de interesse e conta quantos cada seção cumpre."""
    f_abst = (d[medida] <= -limite) & (d["aptos"] >= min_aptos)
    if "votos_apos_17" in d:
        f_17 = (d["pct_apos_17"] >= lim_17) & (d["votos_apos_17"] >= 10)
        if so_destoa and "dif_local_min" in d:
            f_17 &= (d["dif_local_min"] >= 30) | d["dif_local_min"].isna()
        f_17 = f_17.fillna(False).astype(bool)
    else:
        f_17 = pd.Series(False, index=d.index)
    if "z_manual" in d:
        f_man = ((d["z_manual"] >= limite) & (d["votos_manual"] >= 5)).fillna(False).astype(bool)
    else:
        f_man = pd.Series(False, index=d.index)
    n = f_abst.astype(int) + f_17.astype(int) + f_man.astype(int)
    rot = pd.Series("", index=d.index, dtype=object)
    alguma = n > 0
    if alguma.any():  # monta o texto só para as poucas seções que cumprem algum critério
        partes = pd.concat([f_abst[alguma].map({True: "abstenção baixa", False: ""}),
                            f_17[alguma].map({True: "voto após 17h", False: ""}),
                            f_man[alguma].map({True: "liberação manual", False: ""})], axis=1)
        rot[alguma] = partes.apply(lambda r: " · ".join(x for x in r if x), axis=1)
    return d.assign(f_abst=f_abst, f_17=f_17, f_man=f_man, n_criterios=n, criterios_cumpridos=rot,
                    alerta=np.where(n >= min_crit, "sinalizada", "normal"))

