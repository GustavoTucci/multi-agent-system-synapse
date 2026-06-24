from pydantic import BaseModel, Field, model_serializer
from typing import List, Optional, Union


class PerfilBase(BaseModel):
    renda_anual: Optional[float] = Field(None, description="Renda anual total do cliente.")
    tipo_renda: Optional[str] = Field(None, description="Tipo de renda/vínculo empregatício.")
    anos_emprego: Optional[float] = Field(None, description="Tempo de emprego em anos.")


class DadosBureau(BaseModel):
    creditos_ativos: Optional[int] = Field(None, description="Quantidade de créditos ativos em outras instituições.")
    divida_total: Optional[float] = Field(None, description="Soma total da dívida ativa externa.")
    max_dias_atraso: Optional[int] = Field(None, description="Máximo de dias em atraso histórico registrado no bureau.")
    tendencia_status: Optional[str] = Field(None, description="Tendência de evolução do status mensal.")


class DadosPagamento(BaseModel):
    media_dias_atraso: Optional[float] = Field(default=None, description="Media de dias de atraso nas parcelas.")
    pct_subpago: Optional[float] = Field(default=None, description="Percentual de parcelas pagas abaixo do valor previsto.")
    pct_meses_dpd: Optional[float] = Field(default=None, description="Percentual de meses com atraso no POS Cash.")


class DadosCartao(BaseModel):
    utilizacao_media: Optional[float] = Field(None, description="Taxa média de utilização do limite de crédito do cartão.")
    pct_pagamento_minimo: Optional[float] = Field(None, description="Percentual de meses em que apenas o pagamento mínimo foi efetuado.")
    tendencia_saldo: Optional[str] = Field(None, description="Tendência cronológica de evolução do saldo.")


class DadosContratos(BaseModel):
    taxa_aprovacao: Optional[float] = Field(None, description="Taxa de aprovação de contratos anteriores.")
    motivos_rejeicao: Optional[List[str]] = Field(None, description="Lista de principais códigos de motivo de rejeição.")
    produtos_top3: Optional[Union[str, List[str]]] = Field(None, description="Top 3 tipos de produtos mais contratados anteriormente.")
    razao_valor_aprovado: Optional[float] = Field(None, description="Relação entre valor aprovado e valor solicitado.")


class ErrorReport(BaseModel):
    sk_id_curr: Optional[int] = Field(None, description="ID do cliente consultado.")
    erro: bool = Field(True, description="Sempre True quando este schema é usado.")
    codigo_erro: str = Field(..., description="Código do erro.")
    mensagem: str = Field(..., description="Mensagem descritiva do erro.")
    agentes_disponiveis: List[str] = Field(
        default=["bureau", "cartao", "contratos", "pagamento"],
        description="Lista dos domínios que o sistema cobre para orientar o usuário."
    )


class ConsolidatedReport(BaseModel):
    sk_id_curr: int = Field(..., description="ID identificador único do cliente consultado.")
    
    perfil: PerfilBase = Field(
        ..., description="Dados do perfil demográfico e financeiro base do cliente."
    )
    bureau: Optional[DadosBureau] = Field(
        default_factory=DadosBureau, 
        description="Análise de birô externo."
    )
    pagamento: Optional[DadosPagamento] = Field(
        default_factory=DadosPagamento, 
        description="Análise de histórico de pagamentos internos."
    )
    cartao: Optional[DadosCartao] = Field(
        default_factory=DadosCartao, 
        description="Análise de comportamento no cartão rotativo."
    )
    contratos: Optional[DadosContratos] = Field(
        default_factory=DadosContratos, 
        description="Análise de contratos e solicitações anteriores."
    )
    agentes_acionados: list[str] = Field(
        ..., description="Lista estrita contendo as tags dos sub-agentes que foram invocados."
    )
    narrativa: str = Field(
        ..., description="Texto analítico e dissertativo conectando os achados de todos os agentes acionados, traçando o perfil de risco do cliente."
    )