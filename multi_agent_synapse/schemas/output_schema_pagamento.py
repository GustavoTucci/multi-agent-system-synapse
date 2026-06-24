from typing import Optional
from pydantic import BaseModel, Field


class RespostaPagamentoAgente(BaseModel):
    media_dias_atraso: Optional[float] = Field(
        default=None,
        description="Media de dias de atraso nas parcelas."
    )
    pct_subpago: Optional[float] = Field(
        default=None,
        description="Percentual de parcelas pagas abaixo do valor previsto (0.0 a 1.0)."
    )
    pct_meses_dpd: Optional[float] = Field(
        default=None,
        description="Percentual de meses com atraso (SK_DPD > 0) no POS Cash (0.0 a 1.0)."
    )
