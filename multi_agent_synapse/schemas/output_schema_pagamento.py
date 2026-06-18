from __future__ import annotations
from typing import Optional
# pyrefly: ignore [missing-import]
from pydantic import BaseModel, Field


class RespostaPagamentoAgente(BaseModel):

    sk_id_curr: int = Field(
        description="ID do cliente consultado."
    )
    media_dias_atraso: Optional[float] = Field(
        default=None,
        description="Media de dias de atraso nas parcelas (DAYS_ENTRY_PAYMENT - DAYS_INSTALMENT)."
    )
    pct_subpago: Optional[float] = Field(
        default=None,
        description="Percentual de parcelas pagas abaixo do valor previsto (0.0 a 1.0)."
    )
    pct_meses_dpd: Optional[float] = Field(
        default=None,
        description="Percentual de meses com atraso (SK_DPD > 0) no POS Cash (0.0 a 1.0)."
    )
    contratos_ativos_pos: Optional[int] = Field(
        default=None,
        description="Quantidade de contratos POS ainda com status Active."
    )
    status: Optional[str] = Field(
        default=None,
        description="Mensagem de status em caso de erro ou ausencia de dados."
    )
