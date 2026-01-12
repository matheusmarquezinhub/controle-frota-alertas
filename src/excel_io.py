import sys
import pandas as pd


def normalizar_colunas(df: pd.DataFrame) -> pd.DataFrame:
    df.columns = (
        df.columns.astype(str).str.strip().str.replace("\u00a0", " ", regex=False)
    )
    return df


def checar_colunas(df: pd.DataFrame, obrigatorias: list[str], nome_aba: str) -> None:
    faltando = set(obrigatorias) - set(df.columns)
    if faltando:
        print(f"❌ Colunas faltando na aba '{nome_aba}': {', '.join(sorted(faltando))}")
        print("📌 Colunas encontradas:", ", ".join(df.columns))
        sys.exit(1)


def ler_abas_excel(caminho, aba_mov: str, aba_man: str):
    try:
        mov = pd.read_excel(caminho, sheet_name=aba_mov)
        man = pd.read_excel(caminho, sheet_name=aba_man)
        return mov, man
    except ValueError as e:
        print("❌ Erro ao ler abas. Confira os nomes das abas no Excel.")
        print("Detalhe:", e)
        sys.exit(1)
