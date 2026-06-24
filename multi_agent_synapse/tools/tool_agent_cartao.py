import pandas as pd
import pandas_gbq
from typing import Dict, Any
from ..schemas.output_schema_cartao import RespostaCartaoAgente

PROJETO = "prj-data-ps-us"
DATASET = "home_credit_default_risk"
TABELA  = "credit_card_balance"


def get_limit_utilization(sk_id_curr: int) -> dict:
    """Busca os dados do banco e calcula o percentual médio de uso do limite do cartão."""
    
    query = f"""
        SELECT AMT_BALANCE, AMT_CREDIT_LIMIT_ACTUAL 
        FROM `{PROJETO}.{DATASET}.{TABELA}`
        WHERE SK_ID_CURR = {sk_id_curr}
    """
    try:
        # Executa a query no BigQuery e armazena em um DataFrame 
        df = pandas_gbq.read_gbq(query, project_id=PROJETO)
    except Exception as e:
        return {"sem_dados": True, "mensagem": f"Erro ao conectar ao banco: {str(e)}"}

    if df.empty:
        return {"sem_dados": True, "mensagem": "Cliente sem histórico de cartão."}
    
    # Evita divisão por zero filtrando apenas limites válidos 
    limite_valido = df['AMT_CREDIT_LIMIT_ACTUAL'] > 0
    if not limite_valido.any():
        return {"utilizacao_media": 0.0}
        
    # Divide o saldo devedor pelo limite do cartão de cada mês
    utilizacao = df.loc[limite_valido, 'AMT_BALANCE'] / df.loc[limite_valido, 'AMT_CREDIT_LIMIT_ACTUAL']
    
    return {"utilizacao_media": float(utilizacao.mean())}


def get_min_payment_rate(sk_id_curr: int) -> dict:
    """Calcula a proporção de meses em que o cliente ficou inadimplente/atrasou o cartão."""
                
    query = f"""
        SELECT SK_DPD 
        FROM `{PROJETO}.{DATASET}.{TABELA}`
        WHERE SK_ID_CURR = {sk_id_curr}
    """
    try:
        df = pandas_gbq.read_gbq(query, project_id=PROJETO)
    except Exception as e:
        return {"sem_dados": True, "mensagem": f"Erro ao conectar ao banco: {str(e)}"}

    if df.empty:
        return {"sem_dados": True, "mensagem": "Cliente sem histórico de cartão."}
    
    # Conta em quantos registros/meses a coluna 'Dias em Atraso' (SK_DPD) foi maior que zero
    meses_com_atraso = df[df['SK_DPD'] > 0].shape[0]
    
    # Pega o total de linhas retornadas
    total_meses = df.shape[0]
    
    taxa = meses_com_atraso / total_meses if total_meses > 0 else 0.0
    
    return {"pct_pagamento_minimo": taxa}


def get_balance_trend(sk_id_curr: int) -> dict:
    """Busca a tendência de evolução do saldo devedor nos últimos 6 meses cadastrados."""
            
    query = f"""
        SELECT MONTHS_BALANCE, AMT_BALANCE 
        FROM `{PROJETO}.{DATASET}.{TABELA}`
        WHERE SK_ID_CURR = {sk_id_curr}
        ORDER BY MONTHS_BALANCE ASC
    """
    try:
        df = pandas_gbq.read_gbq(query, project_id=PROJETO)
    except Exception as e:
        return {"sem_dados": True, "mensagem": f"Erro ao conectar ao banco: {str(e)}"}

    if df.empty:
        return {"sem_dados": True, "mensagem": "Cliente sem histórico de cartão."}
    
    # Extrai os 6 meses mais recentes
    ultimos_meses = df.tail(6)
    
    if len(ultimos_meses) < 2:
        return {"tendencia_saldo": "Estável"}
        
    # Lógica simples para definir a tendência textual baseada no primeiro e último mês do corte
    saldo_inicial = ultimos_meses.iloc[0]['AMT_BALANCE']
    saldo_final = ultimos_meses.iloc[-1]['AMT_BALANCE']
    
    if saldo_final > saldo_inicial * 1.05:  # Margem de 5%
        tendencia = "Crescente"
    elif saldo_final < saldo_inicial * 0.95:
        tendencia = "Reduzindo"
    else:
        tendencia = "Estável"
        
    return {"tendencia_saldo": tendencia}


def get_cartao_consolidated(sk_id_curr: int) -> dict:
    """
    Retorna todas as informações consolidadas do cartão de crédito do cliente.
    """
    utilizacao = get_limit_utilization(sk_id_curr)
    min_payment = get_min_payment_rate(sk_id_curr)
    trend = get_balance_trend(sk_id_curr)
   
    # Se qualquer uma das consultas indicar falta de dados, retorna o dicionário com a flag
    if utilizacao.get("sem_dados") or min_payment.get("sem_dados") or trend.get("sem_dados"):
        return {"sem_dados": True}
       
    return {
        "utilizacao_media": utilizacao.get("utilizacao_media"),
        "pct_pagamento_minimo": min_payment.get("pct_pagamento_minimo"),
        "tendencia_saldo": trend.get("tendencia_saldo")
    }