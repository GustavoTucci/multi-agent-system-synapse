from __future__ import annotations
from typing import List, Optional
# pyrefly: ignore [missing-import]
from pydantic import BaseModel, Field


class CreditoAtivo(BaseModel):
    """Representa um único crédito ativo do cliente no bureau."""

    sk_id_bureau: Optional[int] = Field(
        default=None,
        description="Identificador único do registro no bureau."
    )
    credit_type: Optional[str] = Field(
        default=None,
        description="Tipo do crédito (ex.: Consumer credit, Car loan, Mortgage, etc.)."
    )
    credit_active: Optional[str] = Field(
        default=None,
        description="Status do crédito: Active, Closed, Bad debt, Sold."
    )
    amt_credit_sum: Optional[float] = Field(
        default=None,
        description="Valor total do crédito contratado."
    )
    amt_credit_sum_debt: Optional[float] = Field(
        default=None,
        description="Saldo devedor atual do crédito."
    )
    amt_credit_sum_limit: Optional[float] = Field(
        default=None,
        description="Limite disponível do crédito (aplicável a crédito rotativo)."
    )
    credit_day_overdue: Optional[int] = Field(
        default=None,
        description="Número de dias em atraso no momento da consulta."
    )
    status: Optional[str] = Field(
        default=None,
        description="Status mensal mais recente no bureau_balance (0–5, C, X)."
    )


class RespostaCreditosAtivos(BaseModel):
    """Resposta estruturada de get_active_credits."""

    creditos_ativos: Optional[List[CreditoAtivo]] = Field(
        default=None,
        description="Lista de créditos ativos encontrados para o cliente."
    )
    status: Optional[str] = Field(
        default=None,
        description="Mensagem de status quando nenhum crédito ativo for encontrado."
    )

class ResumoDividaSimples(BaseModel):
    """Linha de resumo de dívida retornada por get_debt_summary (tool_bureau)."""

    total_divida_ativa: Optional[float] = Field(
        default=None,
        description="Soma total da dívida ativa do cliente em todos os créditos ativos."
    )
    max_dias_atraso: Optional[int] = Field(
        default=None,
        description="Maior número de dias em atraso registrado entre os créditos ativos."
    )


class RespostaResumoDividaSimples(BaseModel):
    """Resposta estruturada de get_debt_summary (tool_bureau)."""

    creditos_ativos: Optional[List[ResumoDividaSimples]] = Field(
        default=None,
        description="Resumo consolidado de dívida ativa e maior atraso do cliente."
    )
    status: Optional[str] = Field(
        default=None,
        description="Mensagem de status quando nenhum crédito ativo for encontrado."
    )


class RespostaTendenciaScore(BaseModel):
    """Resposta estruturada de get_status_trend (tool_bureau)."""

    media_recente: Optional[float] = Field(
        default=None,
        description=(
            "Média do status de pagamento nos meses mais recentes "
            "(valores menores indicam melhor situação)."
        )
    )
    media_antiga: Optional[float] = Field(
        default=None,
        description=(
            "Média do status de pagamento nos meses mais antigos "
            "(usada como referência para comparação)."
        )
    )
    tendencia: Optional[str] = Field(
        default=None,
        description=(
            "Tendência do comportamento de pagamento do cliente: "
            "'Melhorando', 'Piorando', 'Estável' ou 'Indeterminada'."
        )
    )
    status: Optional[str] = Field(
        default=None,
        description="Mensagem de status quando nenhum histórico for encontrado."
    )

class ResumoDividaPorTipo(BaseModel):
    """Resumo de dívida agrupado por tipo de crédito (tool_analysis)."""

    tipo_credito: Optional[str] = Field(
        default=None,
        description="Tipo do crédito (ex.: Consumer credit, Car loan, Mortgage)."
    )
    quantidade_creditos: Optional[int] = Field(
        default=None,
        description="Total de contratos desse tipo de crédito encontrados."
    )
    total_valor_credito: Optional[float] = Field(
        default=None,
        description="Soma dos valores contratados para esse tipo de crédito."
    )
    total_divida: Optional[float] = Field(
        default=None,
        description="Soma da dívida atual para esse tipo de crédito."
    )
    total_limite: Optional[float] = Field(
        default=None,
        description="Soma dos limites disponíveis para esse tipo de crédito."
    )
    creditos_ativos: Optional[int] = Field(
        default=None,
        description="Quantidade de contratos com status 'Active' nesse tipo."
    )
    creditos_fechados: Optional[int] = Field(
        default=None,
        description="Quantidade de contratos encerrados nesse tipo."
    )


class RespostaResumoDividaAgrupada(BaseModel):
    """Resposta estruturada de get_debt_summary (tool_analysis)."""

    resumo_dividas: Optional[List[ResumoDividaPorTipo]] = Field(
        default=None,
        description="Resumo das dívidas agrupado por tipo de crédito."
    )
    status: Optional[str] = Field(
        default=None,
        description="Mensagem de status quando nenhum dado for encontrado."
    )


class TendenciaStatusMensal(BaseModel):
    """Linha de tendência de status por mês e tipo de crédito (tool_analysis)."""

    mes: Optional[int] = Field(
        default=None,
        description="Mês relativo ao mês atual (0 = mês atual, -1 = mês anterior, etc.)."
    )
    status_pagamento: Optional[str] = Field(
        default=None,
        description=(
            "Status de pagamento registrado: "
            "0=em dia, 1=1-29d atraso, 2=30-59d, 3=60-89d, 4=90-119d, "
            "5=120+d, C=quitado, X=sem informação."
        )
    )
    quantidade: Optional[int] = Field(
        default=None,
        description="Quantidade de ocorrências desse status nesse mês."
    )
    tipo_credito: Optional[str] = Field(
        default=None,
        description="Tipo de crédito associado ao registro."
    )


class RespostaTendenciaStatusMensal(BaseModel):
    """Resposta estruturada de get_status_trend (tool_analysis)."""

    tendencia_status: Optional[List[TendenciaStatusMensal]] = Field(
        default=None,
        description="Histórico mensal de status de pagamento por tipo de crédito."
    )
    status: Optional[str] = Field(
        default=None,
        description="Mensagem de status quando nenhum histórico for encontrado."
    )


class RespostaBureauAgente(BaseModel):
    """
    Schema de saída consolidado do agente bureau.

    Agrupa todas as informações que o agente pode retornar em uma única resposta
    estruturada, permitindo que o orquestrador (root_agent) processe os dados
    de forma determinística.
    """

    sk_id_curr: int = Field(
        description="ID do cliente consultado."
    )
    creditos_ativos: Optional[RespostaCreditosAtivos] = Field(
        default=None,
        description="Resultado de get_active_credits — lista de créditos ativos."
    )
    resumo_divida: Optional[RespostaResumoDividaAgrupada] = Field(
        default=None,
        description="Resultado de get_debt_summary — resumo por tipo de crédito."
    )
    tendencia_score: Optional[RespostaTendenciaScore] = Field(
        default=None,
        description="Resultado de get_status_trend (bureau) — tendência do score de pagamento."
    )
    tendencia_status_mensal: Optional[RespostaTendenciaStatusMensal] = Field(
        default=None,
        description="Resultado de get_status_trend (analysis) — histórico mensal detalhado."
    )
    observacoes: Optional[str] = Field(
        default=None,
        description="Observações adicionais ou síntese textual produzida pelo agente."
    )
