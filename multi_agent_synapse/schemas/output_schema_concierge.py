# pyrefly: ignore [missing-import]
from pydantic import BaseModel, Field
from typing import List, Optional

class Perfil(BaseModel):
    renda_anual: float
    tipo_renda: str
    anos_emprego: float

class Bureau(BaseModel):
    creditos_ativos: Optional[int] = None
    divida_total: Optional[float] = None
    max_dias_atraso: Optional[int] = None
    tendencia_status: Optional[str] = None

class Pagamento(BaseModel):
    media_dias_atraso: Optional[float] = None
    pct_subpago: Optional[float] = None
    pct_meses_dpd: Optional[float] = None

class Cartao(BaseModel):
    utilizacao_media: Optional[float] = None
    pct_pagamento_minimo: Optional[float] = None
    tendencia_saldo: Optional[str] = None

class Contratos(BaseModel):
    taxa_aprovacao: float
    motivos_rejeicao: List[str]
    produtos_top3: List[str]
    razao_valor_aprovado: float

class ConsolidatedReport(BaseModel):
    sk_id_curr: int
    perfil: Perfil
    bureau: Optional[Bureau] = None
    pagamento: Optional[Pagamento] = None
    cartao: Optional[Cartao] = None
    contratos: Optional[Contratos] = None
    agentes_acionados: List[str] = Field(default_factory=list)
    narrativa: str