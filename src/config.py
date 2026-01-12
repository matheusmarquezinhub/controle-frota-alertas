from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    arquivo: Path
    aba_mov: str = "Movimentacao"
    aba_man: str = "Manutencao"
    km_alerta: int = 800
    pct_aviso_oleo: float = 0.90
    palavras_alerta: tuple[str, ...] = (
        "MANUTENÇÃO",
        "REVISÃO",
        "TROCA",
        "AGENDADA",
        "RECADO",
        "IMPORTANTE",
        "ATENÇÃO",
        "URGENTE",
        "ALERTA",
    )
