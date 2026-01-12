import re
from datetime import datetime
import pandas as pd


def extrair_data(texto: str):
    if not texto:
        return None
    m = re.search(r"\d{2}/\d{2}/\d{4}", str(texto))
    if m:
        try:
            return datetime.strptime(m.group(), "%d/%m/%Y").date()
        except ValueError:
            return None
    return None


def texto_tem_alerta(obs: str, palavras_alerta) -> bool:
    if not obs:
        return False
    obs_u = str(obs).upper().strip()
    return any(p in obs_u for p in palavras_alerta)


def add_alert(alertas: list[tuple[str, str]], severidade: str, msg: str) -> None:
    """severidade: 'crit', 'warn', 'info', 'cad'"""
    alertas.append((severidade, msg))


def ordenar_formatar(alertas: list[tuple[str, str]]) -> list[str]:
    ordem = {"crit": 1, "warn": 2, "cad": 3, "info": 4}
    prefixo = {"crit": "🔴", "warn": "🟠", "cad": "⚠️", "info": "ℹ️"}

    vistos = set()
    unicos = []
    for sev, msg in alertas:
        k = (sev, msg)
        if k not in vistos:
            vistos.add(k)
            unicos.append((sev, msg))

    unicos.sort(key=lambda x: (ordem.get(x[0], 9), x[1]))
    return [f"{prefixo.get(sev,'•')} {msg}" for sev, msg in unicos]


def preparar_mov(mov: pd.DataFrame) -> pd.DataFrame:
    mov = mov.copy()
    mov["Placa"] = mov["Placa"].astype(str).str.strip()
    mov["Modelo"] = mov["Modelo"].astype(str).str.strip()
    mov["Status"] = mov["Status"].astype(str).str.upper().str.strip()
    mov["Observações"] = mov["Observações"].astype(str).str.upper().str.strip()

    if "Km Inicial" in mov.columns:
        mov["Km Inicial"] = pd.to_numeric(mov["Km Inicial"], errors="coerce")

    mov["Km Final"] = pd.to_numeric(mov["Km Final"], errors="coerce")

    if "Data de Retorno" in mov.columns:
        mov["Data de Retorno"] = pd.to_datetime(mov["Data de Retorno"], errors="coerce")

    return mov


def preparar_man(man: pd.DataFrame) -> pd.DataFrame:
    man = man.copy()
    man["Placa"] = man["Placa"].astype(str).str.strip()
    man["Tipo"] = man["Tipo"].astype(str).str.upper().str.strip()
    man["Data"] = pd.to_datetime(man["Data"], errors="coerce")
    man["KM"] = pd.to_numeric(man["KM"], errors="coerce")
    man["KM Limite"] = pd.to_numeric(man["KM Limite"], errors="coerce")

    if "Observações" in man.columns:
        man["Observações"] = man["Observações"].astype(str).str.upper().str.strip()
    else:
        man["Observações"] = ""

    return man


def montar_base(mov: pd.DataFrame, man: pd.DataFrame) -> pd.DataFrame:
    # 1) KM atual por placa
    km_atual = (
        mov.groupby("Placa", as_index=False)["Km Final"]
        .max()
        .rename(columns={"Km Final": "Km Atual"})
    )

    # 2) Registro mais recente por placa
    if "Data de Retorno" in mov.columns:
        mov_best = mov.sort_values(
            ["Placa", "Data de Retorno", "Km Final"]
        ).drop_duplicates("Placa", keep="last")
    else:
        mov_best = mov.sort_values(["Placa", "Km Final"]).drop_duplicates(
            "Placa", keep="last"
        )

    base = mov_best.merge(km_atual, on="Placa", how="left")

    # 3) Última troca de óleo por placa
    man_oleo = man[(man["Tipo"] == "OLEO") & pd.notna(man["KM"])].copy()

    ult_oleo = (
        man_oleo.sort_values(["Placa", "KM"])
        .drop_duplicates("Placa", keep="last")
        .rename(
            columns={
                "KM": "KM Ult Oleo",
                "KM Limite": "Limite Oleo",
                "Data": "Data Ult Oleo",
            }
        )
    )

    base = base.merge(
        ult_oleo[["Placa", "KM Ult Oleo", "Limite Oleo", "Data Ult Oleo"]],
        on="Placa",
        how="left",
    )

    return base


def gerar_alertas(
    base: pd.DataFrame, km_alerta: int, pct_aviso_oleo: float, palavras_alerta
) -> list[str]:
    alertas: list[tuple[str, str]] = []

    for _, r in base.iterrows():
        placa = r["Placa"]
        modelo = r["Modelo"]
        status = r["Status"]
        obs = r["Observações"]
        km_atual_carro = r.get("Km Atual")

        # Observações
        if texto_tem_alerta(obs, palavras_alerta):
            data_obs = extrair_data(obs)
            if data_obs:
                add_alert(
                    alertas,
                    "info",
                    f"{placa} ({modelo}) aviso com data: {data_obs.strftime('%d/%m/%Y')} | {obs}",
                )
            else:
                add_alert(alertas, "info", f"{placa} ({modelo}) recado: {obs}")

        # KM rodado (só EM USO)
        if status == "EM USO":
            if (
                "Km Inicial" in base.columns
                and pd.notna(r.get("Km Inicial"))
                and pd.notna(km_atual_carro)
            ):
                km_rodado = km_atual_carro - r["Km Inicial"]
                if km_rodado >= km_alerta:
                    add_alert(
                        alertas, "info", f"{placa} ({modelo}) rodou {int(km_rodado)} km"
                    )

        # Óleo
        km_ult_oleo = r.get("KM Ult Oleo")
        limite_oleo = r.get("Limite Oleo")

        if pd.isna(km_atual_carro):
            if status == "EM USO":
                add_alert(
                    alertas,
                    "cad",
                    f"{placa} ({modelo}) sem KM atual (Km Final vazio na Movimentacao)",
                )
            continue

        if pd.isna(km_ult_oleo) or pd.isna(limite_oleo):
            add_alert(
                alertas,
                "cad",
                f"{placa} ({modelo}) SEM HISTÓRICO de troca de óleo (registre na aba Manutencao)",
            )
            continue

        km_desde = km_atual_carro - km_ult_oleo

        if km_desde >= limite_oleo:
            add_alert(
                alertas,
                "crit",
                f"{placa} ({modelo}) TROCA DE ÓLEO URGENTE ({int(km_desde)} km / limite {int(limite_oleo)})",
            )
        elif km_desde >= pct_aviso_oleo * limite_oleo:
            faltam = int(limite_oleo - km_desde)
            add_alert(
                alertas,
                "warn",
                f"{placa} ({modelo}) óleo perto do limite: faltam {faltam} km ({int(km_desde)} / {int(limite_oleo)})",
            )

    return ordenar_formatar(alertas)
