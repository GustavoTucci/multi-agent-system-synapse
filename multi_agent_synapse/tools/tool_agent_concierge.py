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
    query = f"""
        SELECT 
            AMT_INCOME_TOTAL as renda_anual,
            NAME_INCOME_TYPE as tipo_renda,  
            ROUND (ABS(DAYS_EMPLOYED)/365.0, 1) as anos_emprego, 
            EXT_SOURCE_1, EXT_SOURCE_2, EXT_SOURCE_3 as analise_credito
        FROM prj-data-ps-us.home_credit_default_risk.application_train
        WHERE SK_ID_CURR = {sk_id}
    """
    
    df = pandas_gbq.read_gbq(query, project_id="prj-data-ps-us")
    
    if df.empty:
        raise ValueError(f"Cliente {sk_id} não encontrado")
    
    row = df.iloc[0]
    return {
        "renda_anual": float(row["renda_anual"]),
        "tipo_renda": str(row["tipo_renda"]),
        "anos_emprego": float(row["anos_emprego"])
    }