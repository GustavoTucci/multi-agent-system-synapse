from __future__ import annotations
from typing import Optional
# pyrefly: ignore [missing-import]
from pydantic import BaseModel, Field


class HistoricoParcelas(BaseModel):
    """Dados retornados por buscar_historico_parcelas (installments_payments)."""

    encontrado: bool = Field(
        description="Indica se foram encontrados registros de parcelas para o cliente."
    )
    total_parcelas: Optional[int] = Field(
        default=None,
        description="Número total de parcelas registradas para o cliente."
    )
    parcelas_com_atraso: Optional[int] = Field(
        default=None,
        description="Quantidade de parcelas pagas com atraso (dias > 0)."
    )
    media_dias_atraso: Optional[float] = Field(
        default=None,
        description="Média de dias de atraso entre todas as parcelas."
    )
    total_financeiro_devido: Optional[float] = Field(
        default=None,
        description="Soma total dos valores devidos (AMT_INSTALMENT)."
    )
    total_financeiro_pago: Optional[float] = Field(
        default=None,
        description="Soma total dos valores efetivamente pagos (AMT_PAYMENT)."
    )
    diferenca_pagamento: Optional[float] = Field(
        default=None,
        description=(
            "Diferença entre o total pago e o total devido. "
            "Positivo indica pagamento excedente; negativo indica déficit."
        )
    )


class RespostaHistoricoParcelas(BaseModel):
    """Resposta estruturada de buscar_historico_parcelas."""

    historico_parcelas: Optional[HistoricoParcelas] = Field(
        default=None,
        description="Dados consolidados do histórico de parcelas do cliente."
    )
    status: Optional[str] = Field(
        default=None,
        description="Mensagem de status em caso de erro ou ausência de dados."
    )


class SaldoPOS(BaseModel):
    """Dados retornados por buscar_saldo_pos (pos_cash_balance)."""

    encontrado: bool = Field(
        description="Indica se foram encontrados registros de POS Cash para o cliente."
    )
    meses_analisados: Optional[int] = Field(
        default=None,
        description="Número total de meses com registros na tabela pos_cash_balance."
    )
    meses_com_atraso: Optional[int] = Field(
        default=None,
        description="Quantidade de meses em que o cliente apresentou atraso (SK_DPD > 0)."
    )
    max_dias_atraso_registrado: Optional[int] = Field(
        default=None,
        description="Maior número de dias em atraso (SK_DPD) registrado no POS Cash."
    )
    status_contrato_mais_recente: Optional[str] = Field(
        default=None,
        description=(
            "Status do contrato no mês mais recente "
            "(ex.: Active, Completed, Returned to the store, etc.)."
        )
    )


class RespostaSaldoPOS(BaseModel):
    """Resposta estruturada de buscar_saldo_pos."""

    saldo_pos: Optional[SaldoPOS] = Field(
        default=None,
        description="Dados consolidados do saldo POS Cash do cliente."
    )
    status: Optional[str] = Field(
        default=None,
        description="Mensagem de status em caso de erro ou ausência de dados."
    )


class SaldoCartao(BaseModel):
    """Dados retornados por buscar_saldo_cartao (credit_card_balance)."""

    encontrado: bool = Field(
        description="Indica se foram encontrados registros de cartão de crédito para o cliente."
    )
    meses_analisados: Optional[int] = Field(
        default=None,
        description="Número total de meses com registros na tabela credit_card_balance."
    )
    saldo_atual: Optional[float] = Field(
        default=None,
        description="Saldo devedor atual do cartão de crédito (AMT_BALANCE mais recente)."
    )
    limite_atual: Optional[float] = Field(
        default=None,
        description="Limite de crédito atual do cartão (AMT_CREDIT_LIMIT_ACTUAL mais recente)."
    )
    utilizacao_percentual: Optional[float] = Field(
        default=None,
        description=(
            "Percentual de utilização do limite do cartão "
            "(saldo_atual / limite_atual * 100)."
        )
    )
    faturas_com_atraso: Optional[int] = Field(
        default=None,
        description="Quantidade de meses em que houve atraso no cartão (SK_DPD > 0)."
    )
    max_dias_atraso: Optional[int] = Field(
        default=None,
        description="Maior número de dias em atraso (SK_DPD) registrado no cartão."
    )


class RespostaSaldoCartao(BaseModel):
    """Resposta estruturada de buscar_saldo_cartao."""

    saldo_cartao: Optional[SaldoCartao] = Field(
        default=None,
        description="Dados consolidados do saldo de cartão de crédito do cliente."
    )
    status: Optional[str] = Field(
        default=None,
        description="Mensagem de status em caso de erro ou ausência de dados."
    )


class BureauExterno(BaseModel):
    """Dados retornados por buscar_bureau (bureau — créditos externos)."""

    encontrado: bool = Field(
        description="Indica se foram encontrados registros de crédito externo para o cliente."
    )
    total_contratos: Optional[int] = Field(
        default=None,
        description="Número total de contratos de crédito registrados em bureaus externos."
    )
    contratos_ativos: Optional[int] = Field(
        default=None,
        description="Quantidade de contratos com status 'Active' em bureaus externos."
    )
    divida_total_externa: Optional[float] = Field(
        default=None,
        description="Soma total da dívida pendente em todos os créditos externos."
    )
    valor_atraso_externo: Optional[float] = Field(
        default=None,
        description="Soma total dos valores em atraso nos créditos externos (AMT_CREDIT_SUM_OVERDUE)."
    )
    max_dias_atraso_externo: Optional[int] = Field(
        default=None,
        description="Maior número de dias em atraso nos créditos externos (CREDIT_DAY_OVERDUE)."
    )


class RespostaBureauExterno(BaseModel):
    """Resposta estruturada de buscar_bureau."""

    bureau_externo: Optional[BureauExterno] = Field(
        default=None,
        description="Dados consolidados de créditos externos (bureau) do cliente."
    )
    status: Optional[str] = Field(
        default=None,
        description="Mensagem de status em caso de erro ou ausência de dados."
    )


class RespostaPagamentoAgente(BaseModel):
    """
    Schema de saída consolidado do agente de pagamentos.

    Agrupa todas as informações que o agente pode retornar em uma única resposta
    estruturada, permitindo que o orquestrador (root_agent) processe os dados
    de forma determinística.
    """

    sk_id_curr: int = Field(
        description="ID do cliente consultado."
    )
    historico_parcelas: Optional[RespostaHistoricoParcelas] = Field(
        default=None,
        description="Resultado de buscar_historico_parcelas — histórico de parcelas e balanço financeiro."
    )
    saldo_pos: Optional[RespostaSaldoPOS] = Field(
        default=None,
        description="Resultado de buscar_saldo_pos — saldo POS Cash e atrasos."
    )
    saldo_cartao: Optional[RespostaSaldoCartao] = Field(
        default=None,
        description="Resultado de buscar_saldo_cartao — saldo, limite e utilização do cartão."
    )
    bureau_externo: Optional[RespostaBureauExterno] = Field(
        default=None,
        description="Resultado de buscar_bureau — créditos externos e atrasos em outros bureaus."
    )
    classificacao_risco: Optional[str] = Field(
        default=None,
        description=(
            "Classificação de risco sugerida pelo agente: "
            "'BOM' (🟢), 'REGULAR' (🟡) ou 'RUIM' (🔴)."
        )
    )
    observacoes: Optional[str] = Field(
        default=None,
        description="Observações adicionais ou síntese textual produzida pelo agente."
    )
