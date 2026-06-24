from typing import Optional
from pydantic import BaseModel, Field


class RespostaCartaoAgente(BaseModel):
    utilizacao_media: Optional[float] = Field(
        default=None,
        description="Taxa média de utilização do limite."
    )
    pct_pagamento_minimo: Optional[float] = Field(
        default=None,
        description="Proporção de meses com atraso."
    )
    tendencia_saldo: Optional[str] = Field(
        default=None,
        description="Tendência do saldo nos últimos 6 meses: Crescente, Reduzindo ou Estável."
    )