# pyrefly: ignore [missing-import]
"""
Tools do Sub-Agente de Pagamentos — consultas BigQuery
Dataset: prj-data-ps-us.home_credit_default_risk
"""

import os
from dotenv import load_dotenv
from google.cloud import bigquery
load_dotenv()

PROJECT = os.getenv("GOOGLE_CLOUD_PROJECT", "prj-data-ps-us")
DATASET = f"{PROJECT}.home_credit_default_risk"

client = bigquery.Client(project=PROJECT)


def buscar_historico_parcelas(sk_id_curr: int) -> dict:
    """
    Busca o histórico de pagamentos de parcelas na tabela installments_payments.
    Retorna totais, médias de atraso e balanço financeiro do cliente.

    Args:
        sk_id_curr: ID único do cliente (SK_ID_CURR).
    """
    query = f"""
        SELECT
            NUM_INSTALMENT_NUMBER,
            AMT_INSTALMENT,
            AMT_PAYMENT,
            DAYS_INSTALMENT,
            DAYS_ENTRY_PAYMENT
        FROM `{DATASET}.installments_payments`
        WHERE SK_ID_CURR = {int(sk_id_curr)}
        ORDER BY NUM_INSTALMENT_NUMBER
    """
    try:
        df = client.query(query).to_dataframe()
    except Exception as e:
        return {"erro": str(e), "tabela": "installments_payments"}

    if df.empty:
        return {"encontrado": False, "tabela": "installments_payments"}

    df["atraso_dias"] = (df["DAYS_ENTRY_PAYMENT"] - df["DAYS_INSTALMENT"]).clip(lower=0)

    return {
        "encontrado": True,
        "total_parcelas": int(len(df)),
        "parcelas_com_atraso": int((df["atraso_dias"] > 0).sum()),
        "media_dias_atraso": round(float(df["atraso_dias"].mean()), 2),
        "total_financeiro_devido": round(float(df["AMT_INSTALMENT"].sum()), 2),
        "total_financeiro_pago": round(float(df["AMT_PAYMENT"].sum()), 2),
        "diferenca_pagamento": round(
            float(df["AMT_PAYMENT"].sum() - df["AMT_INSTALMENT"].sum()), 2
        ),
    }


def buscar_saldo_pos(sk_id_curr: int) -> dict:
    """
    Busca o histórico de saldo POS Caixa na tabela pos_cash_balance.
    Retorna meses analisados, meses com atraso e status atual do contrato.

    Args:
        sk_id_curr: ID único do cliente (SK_ID_CURR).
    """
    query = f"""
        SELECT
            MONTHS_BALANCE,
            NAME_CONTRACT_STATUS,
            SK_DPD
        FROM `{DATASET}.pos_cash_balance`
        WHERE SK_ID_CURR = {int(sk_id_curr)}
        ORDER BY MONTHS_BALANCE DESC
    """
    try:
        df = client.query(query).to_dataframe()
    except Exception as e:
        return {"erro": str(e), "tabela": "pos_cash_balance"}

    if df.empty:
        return {"encontrado": False, "tabela": "pos_cash_balance"}

    return {
        "encontrado": True,
        "meses_analisados": int(len(df)),
        "meses_com_atraso": int((df["SK_DPD"] > 0).sum()),
        "max_dias_atraso_registrado": int(df["SK_DPD"].max()),
        "status_contrato_mais_recente": str(df.iloc[0]["NAME_CONTRACT_STATUS"]),
    }


def buscar_saldo_cartao(sk_id_curr: int) -> dict:
    """
    Busca saldos e limites de cartão de crédito na tabela credit_card_balance.
    Retorna saldo atual, limite, utilização e histórico de atrasos.

    Args:
        sk_id_curr: ID único do cliente (SK_ID_CURR).
    """
    query = f"""
        SELECT
            MONTHS_BALANCE,
            AMT_BALANCE,
            AMT_CREDIT_LIMIT_ACTUAL,
            SK_DPD
        FROM `{DATASET}.credit_card_balance`
        WHERE SK_ID_CURR = {int(sk_id_curr)}
        ORDER BY MONTHS_BALANCE DESC
    """
    try:
        df = client.query(query).to_dataframe()
    except Exception as e:
        return {"erro": str(e), "tabela": "credit_card_balance"}

    if df.empty:
        return {"encontrado": False, "tabela": "credit_card_balance"}

    saldo  = float(df.iloc[0]["AMT_BALANCE"])
    limite = float(df.iloc[0]["AMT_CREDIT_LIMIT_ACTUAL"])
    utilizacao = round((saldo / limite * 100), 2) if limite > 0 else 0.0

    return {
        "encontrado": True,
        "meses_analisados": int(len(df)),
        "saldo_atual": round(saldo, 2),
        "limite_atual": round(limite, 2),
        "utilizacao_percentual": utilizacao,
        "faturas_com_atraso": int((df["SK_DPD"] > 0).sum()),
        "max_dias_atraso": int(df["SK_DPD"].max()),
    }


def buscar_bureau(sk_id_curr: int) -> dict:
    """
    Busca o histórico de créditos externos do cliente na tabela bureau.
    Retorna quantidade de contratos, dívida total e atrasos em outros órgãos.

    Args:
        sk_id_curr: ID único do cliente (SK_ID_CURR).
    """
    query = f"""
        SELECT
            CREDIT_ACTIVE,
            AMT_CREDIT_SUM,
            AMT_CREDIT_SUM_DEBT,
            AMT_CREDIT_SUM_OVERDUE,
            CREDIT_DAY_OVERDUE
        FROM `{DATASET}.bureau`
        WHERE SK_ID_CURR = {int(sk_id_curr)}
    """
    try:
        df = client.query(query).to_dataframe()
    except Exception as e:
        return {"erro": str(e), "tabela": "bureau"}

    if df.empty:
        return {"encontrado": False, "tabela": "bureau"}

    contratos_ativos = int((df["CREDIT_ACTIVE"] == "Active").sum())
    divida_total = round(float(df["AMT_CREDIT_SUM_DEBT"].fillna(0).sum()), 2)
    valor_atraso = round(float(df["AMT_CREDIT_SUM_OVERDUE"].fillna(0).sum()), 2)
    max_dias_atraso = int(df["CREDIT_DAY_OVERDUE"].fillna(0).max())

    return {
        "encontrado": True,
        "total_contratos": int(len(df)),
        "contratos_ativos": contratos_ativos,
        "divida_total_externa": divida_total,
        "valor_atraso_externo": valor_atraso,
        "max_dias_atraso_externo": max_dias_atraso,
    }