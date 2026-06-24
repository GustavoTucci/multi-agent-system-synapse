from typing import Optional
from pydantic import BaseModel, Field
 
 
class RespostaBureauAgente(BaseModel): 
    creditos_ativos: Optional[int] = Field(
        default=None,
        description="Quantidade de créditos com CREDIT_ACTIVE='Active'."
    )
    divida_total: Optional[float] = Field(
        default=None,
        description="Soma total da dívida ativa (AMT_CREDIT_SUM_DEBT) dos créditos ativos."
    )
    max_dias_atraso: Optional[int] = Field(
        default=None,
        description="Maior CREDIT_DAY_OVERDUE registrado entre os créditos ativos."
    )
    tendencia_status: Optional[str] = Field(
        default=None,
        description="Tendência de pagamento: 'Melhorando', 'Piorando', 'Estável' ou 'Indeterminada'."
    )
    status: Optional[str] = Field(
        default=None,
        description="Mensagem de status quando o cliente não tiver dados no bureau."
    )