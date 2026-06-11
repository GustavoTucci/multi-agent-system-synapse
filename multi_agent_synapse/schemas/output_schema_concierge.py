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



    from pydantic import BaseModel, Field
from typing import List, Optional

# --- Sub-schemas para garantir a tipagem de cada bloco ---

class PerfilBase(BaseModel):
    renda_anual: float = Field(..., description="Renda anual total do cliente extraída da aplicação base.")
    tipo_renda: str = Field(..., description="Tipo de renda/vínculo empregatício (ex: Working, Commercial associate).")
    anos_emprego: float = Field(..., description="Tempo de emprego do cliente convertido em anos.")

class DadosBureau(BaseModel):
    creditos_ativos: int = Field(..., description="Quantidade de créditos ativos em outras instituições.")
    divida_total: float = Field(..., description="Soma total da dívida ativa externa.")
    max_dias_atraso: int = Field(..., description="Máximo de dias em atraso histórico registrado no bureau.")
    tendencia_status: str = Field(..., description="Tendência de evolução do status mensal (Melhorando, Estável, Piorando).")

class DadosPagamento(BaseModel):
    media_dias_atraso: float = Field(..., description="Média de dias de atraso histórico no pagamento de parcelas.")
    pct_subpago: float = Field(..., description="Percentual de parcelas pagas abaixo do valor previsto.")
    pct_meses_dpd: float = Field(..., description="Percentual de meses com Days Past Due (DPD) > 0.")

class DadosCartao(BaseModel):
    utilizacao_media: float = Field(..., description="Taxa média de utilização do limite de crédito do cartão.")
    pct_pagamento_minimo: float = Field(..., description="Percentual de meses em que apenas o pagamento mínimo foi efetuado.")
    tendencia_saldo: str = Field(..., description="Tendência cronológica de evolução do saldo (Crescente, Reduzindo, Estável).")

class DadosContratos(BaseModel):
    taxa_aprovacao: float = Field(..., description="Taxa de aprovação de contratos anteriores na Home Credit.")
    motivos_rejeicao: List[str] = Field(..., description="Lista de principais códigos de motivo de rejeição (ex: HC, LIMIT).")
    produtos_top3: List[str] = Field(..., description="Top 3 tipos de produtos mais contratados anteriormente.")

# --- Schema Principal do Concierge ---

class ConsolidatedReport(BaseModel):
    sk_id_curr: int = Field(..., description="ID identificador único do cliente consultado.")
    perfil: PerfilBase = Field(..., description="Dados do perfil demográfico e financeiro base do cliente.")
    
    # Todos os especialistas abaixo aceitam None (null no JSON) por padrão
    bureau: Optional[DadosBureau] = Field(None, description="Análise de birô externo. Deve ser null se o agente não for consultado ou não houver dados.")
    pagamento: Optional[DadosPagamento] = Field(None, description="Análise de histórico de pagamentos internos. Deve ser null se não consultado.")
    cartao: Optional[DadosCartao] = Field(None, description="Análise de comportamento no cartão rotativo. Deve ser null se o cliente não possuir histórico de cartão de crédito.")
    contratos: Optional[DadosContratos] = Field(None, description="Análise de contratos e solicitações anteriores na Home Credit. Deve ser null se não consultado.")
    
    agentes_acionados: List[str] = Field(..., description="Lista estrita contendo as tags dos sub-agentes que foram efetivamente invocados durante a sessão (ex: ['bureau', 'pagamento']).")
    narrativa: str = Field(..., description="Texto analítico e dissertativo conectando os achados de todos os agentes acionados, traçando o perfil de risco do cliente.")
