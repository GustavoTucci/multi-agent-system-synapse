import pandas as pd
import pandas_gbq
import math
from ..queries.queries_agent_bureal import QUERY_CREDITOS_ATIVOS, QUERY_DEBT_SUMMARY, QUERY_STATUS_TREND

def _sanitize(value):
    """Converte NaN e Inf para None, tornando o valor seguro para JSON."""
    if isinstance(value, float) and (math.isnan(value) or math.isinf(value)):
        return None
    return value

def get_active_credits(sk_id_curr: int) -> dict:
    """Lista os créditos ativos de um cliente, incluindo tipo e valor de cada crédito.

    Realiza a junção das tabelas application_train, bureau e bureau_balance
    para retornar apenas os registros com CREDIT_ACTIVE = 'Active'.

    Args:
        sk_id_curr: ID único do cliente (SK_ID_CURR).

    Returns:
        Um dicionário com a lista de créditos ativos do cliente,
        cada item contendo: tipo de crédito, valor, dívida, limite e status mensal.
        Retorna mensagem de status caso nenhum crédito ativo seja encontrado.
    """
    sql = QUERY_CREDITOS_ATIVOS.format(sk_id_curr=sk_id_curr)
    df = pandas_gbq.read_gbq(sql, project_id='prj-data-ps-us')

    if df.empty:
        return {"status": f"Nenhum crédito ativo localizado para o cliente {sk_id_curr}"}

    records = [
        {k: _sanitize(v) for k, v in row.items()}
        for row in df.to_dict(orient='records')
    ]

    return {"creditos_ativos": records}

def get_debt_summary(sk_id_curr: int) -> dict:
    """Retorna um resumo consolidado das dívidas de um cliente, agrupado por tipo de crédito.

    Mostra o total de créditos, valor total, dívida acumulada, limite disponível e
    a quantidade de créditos ativos vs. fechados por tipo.

    Args:
        sk_id_curr: ID único do cliente (SK_ID_CURR).

    Returns:
        Um dicionário com o resumo das dívidas agrupado por tipo de crédito.
        Cada item contém: tipo_credito, quantidade_creditos, total_valor_credito,
        total_divida, total_limite, creditos_ativos e creditos_fechados.
        Retorna mensagem de status caso nenhum dado seja encontrado.
    """
    sql = QUERY_DEBT_SUMMARY.format(sk_id_curr=sk_id_curr)
    df = pandas_gbq.read_gbq(sql, project_id='prj-data-ps-us')

    if df.empty:
        return {"status": f"Nenhuma informação de dívida encontrada para o cliente {sk_id_curr}"}

    records = [
        {k: _sanitize(v) for k, v in row.items()}
        for row in df.to_dict(orient='records')
    ]

    return {"resumo_dividas": records}

def get_status_trend(sk_id_curr: int) -> dict:
    """Retorna a tendência mensal de status de pagamento de um cliente.

    Analisa o histórico de status dos últimos meses (bureau_balance) para
    identificar padrões de adimplência ou inadimplência ao longo do tempo.

    Legenda dos status:
        0 = em dia, 1 = 1-29 dias atrasado, 2 = 30-59 dias atrasado,
        3 = 60-89 dias atrasado, 4 = 90-119 dias atrasado, 5 = 120+ dias atrasado,
        C = quitado, X = sem informação.

    Args:
        sk_id_curr: ID único do cliente (SK_ID_CURR).

    Returns:
        Um dicionário com a tendência de status por mês e tipo de crédito.
        Cada item contém: mes (relativo ao mês atual), status_pagamento,
        quantidade de ocorrências e tipo_credito.
        Retorna mensagem de status caso nenhum histórico seja encontrado.
    """
    sql = QUERY_STATUS_TREND.format(sk_id_curr=sk_id_curr)
    df = pandas_gbq.read_gbq(sql, project_id='prj-data-ps-us')

    if df.empty:
        return {"status": f"Nenhum histórico de status encontrado para o cliente {sk_id_curr}"}

    records = [
        {k: _sanitize(v) for k, v in row.items()}
        for row in df.to_dict(orient='records')
    ]

    return {"tendencia_status": records}
