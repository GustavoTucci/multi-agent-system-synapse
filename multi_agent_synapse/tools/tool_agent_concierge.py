import pandas as pd
import pandas_gbq

def get_client_profile(sk_id: int) -> dict:
    """
    Lê o perfil base do cliente da tabela application_train do BigQuery.
    Retorna: renda anual, tipo de renda, anos no emprego.
    
    Args:
        sk_id: SK_ID_CURR do cliente (ex: 100002)
    
    Returns:
        dict com campos: renda_anual, tipo_renda, anos_emprego
    """
    PROJETO = "prj-data-ps-us"
    DATASET = "home_credit_default_risk"
    TABELA  = "application_train"
    query = f"""
        SELECT 
            AMT_INCOME_TOTAL as renda_anual,
            NAME_EMPLOYMENT_TYPE as tipo_renda,  # ← Corrigir nome da coluna
            YEARS_EMPLOYED as anos_emprego       # ← Corrigir nome da coluna
        FROM '{PROJETO}.{DATASET}.{TABELA}'
        WHERE SK_ID_CURR = {sk_id}
    """
    
    df = pandas_gbq.read_query(query, project_id=PROJETO)
    
    if df.empty:
        raise ValueError(f"Cliente {sk_id} não encontrado")
    
    row = df.iloc[0]
    return {
        "renda_anual": float(row["renda_anual"]),
        "tipo_renda": str(row["tipo_renda"]),
        "anos_emprego": float(row["anos_emprego"])
    }