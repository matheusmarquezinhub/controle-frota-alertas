import argparse
import sys
from pathlib import Path

from config import Settings
from excel_io import ler_abas_excel, normalizar_colunas, checar_colunas
from rules import preparar_mov, preparar_man, montar_base, gerar_alertas
from ui import mostrar_popup


def parse_args():
    p = argparse.ArgumentParser(
        prog="controle-frota-alertas",
        description="Gera alertas de frota (óleo, KM, recados) a partir de um Excel.",
    )
    p.add_argument(
        "--arquivo",
        type=Path,
        default=Path("data/Controle_Frota_KM.xlsx"),
        help="Caminho do Excel (default: data/Controle_Frota_KM.xlsx)",
    )
    p.add_argument(
        "--aba-mov", default="Movimentacao", help="Nome da aba de movimentação"
    )
    p.add_argument("--aba-man", default="Manutencao", help="Nome da aba de manutenção")
    p.add_argument(
        "--km-alerta",
        type=int,
        default=800,
        help="KM mínimo pra aviso de rodagem (default: 800)",
    )
    p.add_argument(
        "--pct-aviso-oleo",
        type=float,
        default=0.90,
        help="Percentual do limite para aviso (default: 0.90)",
    )
    p.add_argument(
        "--sem-popup", action="store_true", help="Não exibe popup (somente terminal)"
    )
    return p.parse_args()


def main():
    args = parse_args()

    s = Settings(
        arquivo=args.arquivo,
        aba_mov=args.aba_mov,
        aba_man=args.aba_man,
        km_alerta=args.km_alerta,
        pct_aviso_oleo=args.pct_aviso_oleo,
    )

    if not s.arquivo.exists():
        print(f"❌ Arquivo não encontrado: {s.arquivo}")
        print(
            "📌 Dica: passe o caminho com --arquivo ou coloque o arquivo em data/Controle_Frota_KM.xlsx"
        )
        sys.exit(1)

    mov, man = ler_abas_excel(s.arquivo, s.aba_mov, s.aba_man)
    mov = normalizar_colunas(mov)
    man = normalizar_colunas(man)

    # Valida colunas mínimas
    col_mov = ["Placa", "Modelo", "Status", "Observações", "Km Final"]
    checar_colunas(mov, col_mov, s.aba_mov)

    col_man = ["Placa", "Tipo", "Data", "KM", "KM Limite"]
    checar_colunas(man, col_man, s.aba_man)

    mov = preparar_mov(mov)
    man = preparar_man(man)

    base = montar_base(mov, man)

    linhas = gerar_alertas(
        base=base,
        km_alerta=s.km_alerta,
        pct_aviso_oleo=s.pct_aviso_oleo,
        palavras_alerta=s.palavras_alerta,
    )

    if not linhas:
        print("✅ Nenhum alerta hoje.")
        return 0

    print("\n🚨 ALERTAS DA FROTA\n")
    for l in linhas:
        print(l)

    if not args.sem_popup:
        try:
            mostrar_popup(linhas)
        except Exception as e:
            # Em alguns ambientes, tkinter pode não estar disponível.
            print(f"\n⚠️ Popup indisponível (tkinter): {e}")
            print("➡️ Use --sem-popup para rodar só no terminal.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
