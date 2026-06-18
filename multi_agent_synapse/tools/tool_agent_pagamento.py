import os
from dotenv import load_dotenv
from google.cloud import bigquery

load_dotenv()

PROJECT = os.getenv("GOOGLE_CLOUD_PROJECT", "prj-data-ps-us")
DATASET = f"{PROJECT}.home_credit_default_risk"

client = bigquery.Client(project=PROJECT)


def get_avg_delay_days(sk_id_curr: int) -> dict:
    """
    Calcula a media de dias de atraso nas parcelas do cliente.
    Formula: media de (DAYS_ENTRY_PAYMENT - DAYS_INSTALMENT).

    Args:
        sk_id_curr: ID unico do cliente (SK_ID_CURR).
    """
    query = f"""
        SELECT
            DAYS_ENTRY_PAYMENT,
            DAYS_INSTALMENT
        FROM `{DATASET}.installments_payments`
        WHERE SK_ID_CURR = {int(sk_id_curr)}
    """
    try:
        df = client.query(query).to_dataframe()
    except Exception as e:
        return {"status": f"Erro ao consultar installments_payments: {str(e)}"}

    if df.empty:
        return {"status": f"Cliente {sk_id_curr} sem historico em installments_payments."}

    df["atraso"] = (df["DAYS_ENTRY_PAYMENT"] - df["DAYS_INSTALMENT"]).clip(lower=0)
    media = round(float(df["atraso"].mean()), 2)

    return {"media_dias_atraso": media}


def get_underpayment_rate(sk_id_curr: int) -> dict:
    """
    Calcula o percentual de parcelas pagas abaixo do valor previsto.
    Formula: count(AMT_PAYMENT < AMT_INSTALMENT) / total de parcelas.

    Args:
        sk_id_curr: ID unico do cliente (SK_ID_CURR).
    """
    query = f"""
        SELECT
            AMT_INSTALMENT,
            AMT_PAYMENT
        FROM `{DATASET}.installments_payments`
        WHERE SK_ID_CURR = {int(sk_id_curr)}
    """
    try:
        df = client.query(query).to_dataframe()
    except Exception as e:
        return {"status": f"Erro ao consultar installments_payments: {str(e)}"}

    if df.empty:
        return {"status": f"Cliente {sk_id_curr} sem historico em installments_payments."}

    total = len(df)
    subpagos = int((df["AMT_PAYMENT"] < df["AMT_INSTALMENT"]).sum())
    pct = round(subpagos / total, 2)

    return {"pct_subpago": pct}


def get_pos_dpd_history(sk_id_curr: int) -> dict:
    """
    Calcula o percentual de meses com atraso (SK_DPD > 0) na tabela POS_CASH_balance.
    Formula: count(SK_DPD > 0) / total de meses.

    Args:
        sk_id_curr: ID unico do cliente (SK_ID_CURR).
    """
    query = f"""
        SELECT SK_DPD
        FROM `{DATASET}.pos_cash_balance`
        WHERE SK_ID_CURR = {int(sk_id_curr)}
    """
    try:
        df = client.query(query).to_dataframe()
    except Exception as e:
        return {"status": f"Erro ao consultar pos_cash_balance: {str(e)}"}

    if df.empty:
        return {"status": f"Cliente {sk_id_curr} sem historico em pos_cash_balance."}

    total = len(df)
    meses_dpd = int((df["SK_DPD"] > 0).sum())
    pct = round(meses_dpd / total, 2)

    return {"pct_meses_dpd": pct}


def get_active_pos_contracts(sk_id_curr: int) -> dict:
    """
    Conta quantos contratos POS ainda estao com status Active.

    Args:
        sk_id_curr: ID unico do cliente (SK_ID_CURR).
    """
    query = f"""
        SELECT SK_ID_PREV, NAME_CONTRACT_STATUS
        FROM `{DATASET}.pos_cash_balance`
        WHERE SK_ID_CURR = {int(sk_id_curr)}
          AND NAME_CONTRACT_STATUS = 'Active'
    """
    try:
        df = client.query(query).to_dataframe()
    except Exception as e:
        return {"status": f"Erro ao consultar pos_cash_balance: {str(e)}"}

    if df.empty:
        return {"status": f"Cliente {sk_id_curr} sem contratos POS ativos."}

    contratos = df["SK_ID_PREV"].nunique()

    return {"contratos_ativos_pos": int(contratos)}
