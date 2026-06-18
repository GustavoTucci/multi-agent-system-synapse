from pydantic import BaseModel, Field
from typing import List, Optional



class PerfilBase(BaseModel):
    renda_anual: Optional[float] = Field(None, description="Renda anual total do cliente extraída da aplicação base.")
    tipo_renda: Optional[str] = Field(None, description="Tipo de renda/vínculo empregatício (ex: Working, Commercial associate).")
    anos_emprego: Optional[float] = Field(None, description="Tempo de emprego do cliente convertido em anos.")


class DadosBureau(BaseModel):
    creditos_ativos: Optional[int] = Field(None, description="Quantidade de créditos ativos em outras instituições.")
    divida_total: Optional[float] = Field(None, description="Soma total da dívida ativa externa.")
    max_dias_atraso: Optional[int] = Field(None, description="Máximo de dias em atraso histórico registrado no bureau.")
    tendencia_status: Optional[str] = Field(None, description="Tendência de evolução do status mensal (Melhorando, Estável, Piorando).")


class DadosPagamento(BaseModel):
    media_dias_atraso: Optional[float] = Field(None, description="Média de dias de atraso histórico no pagamento de parcelas.")
    pct_subpago: Optional[float] = Field(None, description="Percentual de parcelas pagas abaixo do valor previsto.")
    pct_meses_dpd: Optional[float] = Field(None, description="Percentual de meses com Days Past Due (DPD) > 0.")


class DadosCartao(BaseModel):
    utilizacao_media: Optional[float] = Field(None, description="Taxa média de utilização do limite de crédito do cartão.")
    taxa_pagamento_minimo: Optional[float] = Field(None, description="Percentual de meses em que apenas o pagamento mínimo foi efetuado.")
    tendencia_saldo_6m: Optional[str] = Field(None, description="Tendência cronológica de evolução do saldo (Crescente, Reduzindo, Estável).")


class DadosContratos(BaseModel):
    taxa_aprovacao: Optional[float] = Field(None, description="Taxa de aprovação de contratos anteriores na Home Credit.")
    motivos_rejeicao: Optional[str] = Field(None, description="Lista de principais códigos de motivo de rejeição (ex: HC, LIMIT).")
    produtos_top3: Optional[str] = Field(None, description="Top 3 tipos de produtos mais contratados anteriormente.")
    razao_valor_aprovado: Optional[float] = Field(None, description="Relação entre valor aprovado e valor solicitado.")

# class ConsolidatedReport(BaseModel):
#     sk_id_curr: int = Field(..., description="ID identificador único do cliente consultado.")
#     perfil: PerfilBase = Field(..., description="Dados do perfil demográfico e financeiro base do cliente extraídos da aplicação base.")
#     bureau: DadosBureau = Field(None, description="Análise de birô externo. Deve ser null se o agente não for consultado ou não houver dados.")
#     pagamento: DadosPagamento = Field(None, description="Análise de histórico de pagamentos internos. Deve ser null se não consultado.")
#     cartao: DadosCartao = Field(None, description="Análise de comportamento no cartão rotativo. Deve ser null se o cliente não possuir histórico de cartão de crédito.")
#     contratos: DadosContratos = Field(None, description="Análise de contratos e solicitações anteriores na Home Credit. Deve ser null se não consultado.")
#     agentes_acionados: str = Field(..., description="Lista estrita contendo as tags dos sub-agentes que foram efetivamente invocados durante a sessão (ex: ['bureau', 'pagamento'])."),
#     narrativa: str = Field(..., description="Texto analítico e dissertativo conectando os achados de todos os agentes acionados, traçando o perfil de risco do cliente.")
    



class ConsolidatedReport(BaseModel):
    sk_id_curr: int = Field(..., description="ID identificador único do cliente consultado.")
    
    perfil: PerfilBase = Field(
        ..., description="Dados do perfil demográfico e financeiro base do cliente."
    )
    bureau: DadosBureau | None = Field(
        default=None, 
        description="Análise de birô externo. Deve ser obrigatoriamente null se o agente correspondente não for consultado."
    )
    pagamento: DadosPagamento | None = Field(
        default=None, 
        description="Análise de histórico de pagamentos internos. Deve ser obrigatoriamente null se não consultado."
    )
    cartao: DadosCartao | None = Field(
        default=None, 
        description="Análise de comportamento no cartão rotativo. Deve ser obrigatoriamente null se o cliente não possuir histórico."
    )
    contratos: DadosContratos | None = Field(
        default=None, 
        description="Análise de contratos e solicitações anteriores na Home Credit. Deve ser obrigatoriamente null se não consultado."
    )
    agentes_acionados: list[str] = Field(
        ..., description="Lista estrita contendo as tags dos sub-agentes que foram efetivamente invocados durante a sessão (ex: ['bureau', 'cartao'])."
    )
    narrativa: str = Field(
        ..., description="Texto analítico e dissertativo conectando os achados de todos os agentes acionados, traçando o perfil de risco do cliente."
    )