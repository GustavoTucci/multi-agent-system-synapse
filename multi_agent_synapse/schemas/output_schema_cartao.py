from typing import List, Optional
from pydantic import BaseModel, Field

class ToolResponse(BaseModel):
    """
    Classe Base (Mãe). Todas as ferramentas herdam esses campos.
    Serve para padronizar o tratamento de erros: se não houver dados ou o banco cair,
    a IA intercepta os campos 'sem_dados' e 'mensagem' de forma universal.
    """
    sem_dados: bool = False
    mensagem: Optional[str] = None

class LimitUtilizationResponse(ToolResponse):
    """Contrato de saída para a ferramenta de cálculo de limite de crédito."""
    utilizacao_media: Optional[float] = Field(default=None, description="Média de AMT_BALANCE / AMT_CREDIT_LIMIT_ACTUAL")

class MinPaymentRateResponse(ToolResponse):
    """Contrato de saída para a ferramenta de taxa de atraso de pagamentos."""
    taxa_pagamento_minimo: Optional[float] = Field(default=None, description="Proporção de meses em atraso (SK_DPD > 0)")

class BalanceRecord(BaseModel):
    """Sub-modelo: Define a estrutura de uma única linha do histórico de saldo."""
    MONTHS_BALANCE: int
    AMT_BALANCE: float

class BalanceTrendResponse(ToolResponse):
    """Contrato de saída que agrupa uma lista histórica de saldos (BalanceRecord)."""
    tendencia_saldo: Optional[List[BalanceRecord]] = Field(default=None, description="Histórico cronológico de saldos")

class RespostaCartaoAgente(BaseModel):
    """Schema de saída consolidado do agente de cartão de crédito."""
    possui_historico_cartao: bool = Field(description="Indica se o cliente possui histórico de cartão de crédito rotativo.")
    utilizacao_limite: Optional[float] = Field(default=None, description="Média de utilização do limite do cartão (AMT_BALANCE / AMT_CREDIT_LIMIT_ACTUAL) ou null se sem histórico.")
    taxa_pagamento_minimo: Optional[float] = Field(default=None, description="Proporção de meses em atraso (SK_DPD > 0) ou null se sem histórico.")
    tendencia_saldo_6m: Optional[List[BalanceRecord]] = Field(default=None, description="Histórico de evolução do saldo nos últimos 6 meses ou null se sem histórico.")
